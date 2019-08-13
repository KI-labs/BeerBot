# required imports
def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn

import json
from PIL import Image, ImageEnhance
import numpy as np
import requests
from skimage import exposure, filters, morphology, measure
from scipy import ndimage

from analysis.inventory import update_inventory


def predict(url, input_im, response_out, conf=0.8, nms=0.2):
    r = requests.post(url, data=open(input_im, 'rb').read(), params={"conf": conf, "nms": nms})
    # TODO -> handle missing endpoint
    with open(response_out, 'w') as dst:
        json.dump(r.json(), dst, indent=2, default=str)


def __load_predictions(input_response):
    with open(input_response, 'r') as src:
        return json.load(src)


def __load_mask(input_mask):
    mask = Image.open(input_mask, 'r')
    return np.asarray(mask)


def __load_image(input_im):
    img = Image.open(input_im, 'r').convert('RGB')
    img = ImageEnhance.Brightness(img).enhance(2.5)
    return np.asarray(img)


def adjust_bounds(bounds, image_shape, fac=0):
    x0, y0, x1, y1 = bounds
    x0 = min(max(x0-fac, 0), image_shape[1])
    x1 = min(max(x1+fac, 0), image_shape[1])
    y0 = min(max(y0-fac, 0), image_shape[0])
    y1 = min(max(y1+fac, 0), image_shape[0])
    return x0, y0, x1, y1


def threshold_image(image, min_area):
    thresh = filters.threshold_otsu(image)
    bw = image > thresh
    bw = morphology.binary_dilation(bw, selem=morphology.disk(1))
    bw = morphology.remove_small_objects(bw, min_size=min_area)
    bw = ndimage.binary_fill_holes(bw).astype(int)
    return bw


def identify_bottles(input_im, response_out, output_mask, fac=10, min_area=1000, ecc_thresh=0.75, m_thresh=0.95):
    response = __load_predictions(response_out)
    img = __load_image(input_im)

    img_size = img.shape[:2]
    mask = np.zeros(img_size, dtype=np.int)

    for ind, r in enumerate(response):

        bounds = [int(r["x1"]), int(r["y1"]), int(r["x2"]), int(r["y2"])]

        # load portion of image
        img = Image.open(input_im, 'r').convert('L')
        x1, y1, x2, y2 = adjust_bounds(bounds, img_size, fac)
        img = img.crop([x1, y1, x2, y2])
        region = np.asarray(img)

        # image processing
        region = exposure.equalize_hist(region)
        region = filters.gaussian(region, 2.5)

        # get binary mask
        bw = threshold_image(region, min_area)
        labels = measure.label(bw)

        # investigate subregions
        for label in measure.regionprops(labels):

            # simple metric for a circle
            m = label.filled_area / label.convex_area
            if label.area > min_area and label.eccentricity < ecc_thresh and m > m_thresh:
                labels[labels == label.label] = 1
            else:
                labels[labels == label.label] = 0

        # if labels are empty
        if sum(labels.flatten()) == 0:
            labels[:] = 1
        mask[y1:y2, x1:x2] += labels

    # save mask
    Image.fromarray(np.uint8(255 * mask), 'L').save(output_mask)


def contour_bottles(input_mask, contours_out):
    mask = __load_mask(input_mask)
    raw = measure.find_contours(mask, level=0.5)

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

    # save to file
    save_contours(contours, contours_out)
    return len(contours)


def save_contours(contours, contours_out):
    # format contours
    temp = {}
    for ind, c in enumerate(contours):
        temp[ind] = c

    # dump contours to JSON file
    with open(contours_out, 'w') as dst:
        json.dump(temp, dst, indent=2, default=str)


def find_bottles(url, input_im, response_out, mask_out, contours_out):
    # call endpoint - get bottle locations
    print("predicting against endpoint")
    predict(url, input_im, response_out)

    # identify caps
    print("identifying bottles")
    identify_bottles(input_im, response_out, mask_out)

    # get actual bottle contours
    print("extracting contours from bottles")
    n_bottles = contour_bottles(mask_out, contours_out)

    # update inventory with new bottles
    update_inventory()

    return n_bottles
