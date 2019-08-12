# required imports
import json
import numpy as np
from PIL import Image, ImageEnhance
from scipy import ndimage
from skimage import segmentation, measure
from skimage.filters import threshold_otsu
from skimage.morphology import binary_erosion, binary_dilation, disk

from analysis.inventory import update_inventory


def adjust_bounds(x0, y0, x1, y1, im=None, fac=0):
    x0 = min(max(x0 - fac, 0), im.shape[0])
    x1 = min(max(x1 + fac, 0), im.shape[0])
    y0 = min(max(y0 - fac, 0), im.shape[1])
    y1 = min(max(y1 + fac, 0), im.shape[1])

    return x0, y0, x1, y1


def threshold_image(image, fac=0.7):
    thresh = threshold_otsu(image)
    bw = binary_erosion(image > thresh * fac, selem=disk(2))
    bw = binary_dilation(bw, selem=disk(5))
    bw = ndimage.binary_fill_holes(bw).astype(int)

    return bw


# calculate distance between all bottles
def _check_erroneous_bottles(centers):
    x = np.array(centers)
    subs = x[:, None] - x
    sq_euclidean_dist = np.einsum('ijk,ijk->ij', subs, subs)
    euclidean_dist = np.sqrt(sq_euclidean_dist)

    # get the "minimum" distance between all bottles
    minner = [np.min(e[e > 0]) for e in euclidean_dist]

    # calculate the z-score
    z = abs((minner - np.mean(minner)) / np.std(minner))

    # proceed to remove a bottle
    if any(z > 2):

        print('erroneous caps exist!')

        # get minimum distance
        min_dist = np.min(euclidean_dist[np.nonzero(euclidean_dist)])
        inds = np.where(euclidean_dist == min_dist)[0]

        # determine which to remove (based on next closest distance)
        dist = []
        for ind in inds:
            temp = euclidean_dist[ind]
            dist.append(np.min(temp[temp > min_dist]))

        # remove incorrect detection
        return inds[np.argmin(dist)]

    else:

        return None


# determine contours -> number of bottle caps
def get_contours(out):
    raw = measure.find_contours(out, level=0.5)
    num_caps = len(raw)
    print(num_caps, "caps found!")

    contours = []
    centers = []
    for cap in raw:
        # determine contours
        x = [x[1] for x in cap]
        y = [x[0] for x in cap]
        contours.append(list(zip(x, y)))

        # determine centroids
        cx = np.mean(x)
        cy = np.mean(y)
        centers.append([cx, cy])

    ind = _check_erroneous_bottles(centers)
    if ind:
        contours.pop(ind)

    return contours


def find_bottles(input_im, contours_out):
    # convert to grayscale + add brightness
    img = Image.open(input_im, 'r').convert('L')
    img = ImageEnhance.Brightness(img).enhance(3)
    image = np.asarray(img)

    # apply threshold
    area_limits = [5000, 25000]
    subarea_limit = 1000
    n_segments = 5
    m_thresh = 0.975
    eccentricity_thresh = 0.75

    bw = threshold_image(image)
    out = np.zeros(bw.shape, dtype=np.int)

    # label image regions
    label_image = measure.label(bw) + 1

    # iterate through raster regions
    for region in measure.regionprops(label_image):

        # investigate regions if within area
        if area_limits[0] < region.area < area_limits[1] and region.perimeter > 0:

            # simple metric for a circle
            m = region.filled_area / region.convex_area

            # get masked region
            x0, y0, x1, y1 = adjust_bounds(*region.bbox, im=label_image, fac=0)

            # confident circle
            if m > m_thresh:

                out[x0:x1, y0:y1] += region.filled_image

            # requires investigation
            else:

                x0, y0, x1, y1 = adjust_bounds(*region.bbox, im=label_image, fac=5)
                mask = label_image[x0:x1, y0:y1] == region.label
                masked_region = mask * image[x0:x1, y0:y1]

                # segment masked region with superpixels
                raw_labels = segmentation.slic(masked_region,
                                               sigma=2.5,
                                               compactness=0.1,
                                               n_segments=n_segments,
                                               multichannel=True,
                                               enforce_connectivity=True)

                # label subregion
                sublabels = measure.label(raw_labels)
                sublabels += 1
                sublabels *= mask

                # investigate subregions
                for subregion in measure.regionprops(sublabels):

                    # simple metric for a circle
                    m = subregion.filled_area / subregion.convex_area

                    # confident circle based on parameters
                    if subregion.area > subarea_limit and subregion.eccentricity < eccentricity_thresh and m > m_thresh:
                        sublabels[sublabels == subregion.label] = 1

                    # remove labels
                    else:
                        sublabels[sublabels == subregion.label] = 0

                # replace main image with sublabel filled image "part"
                sublabels = ndimage.binary_fill_holes(sublabels).astype(int)
                out[x0:x1, y0:y1] += sublabels

    # determine contours
    contours = get_contours(out)

    # format contours
    temp = {}
    for ind, c in enumerate(contours):
        temp[ind] = c

    # dump contours to JSON file
    with open(contours_out, 'w') as dst:
        json.dump(temp, dst)

    # update inventory with new bottles
    update_inventory()

    return len(contours)
