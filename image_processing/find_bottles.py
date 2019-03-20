import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import exposure
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import binary_dilation, binary_erosion, disk, remove_small_holes


def find_bottles(input_im, output_im, centroids_out):
    # load image
    with Image.open(input_im, 'r').convert('L') as src:
        image = np.asarray(src)

    # define image processing parameters
    min_size = 5000

    # threshold image (OTSU)
    thresh = threshold_otsu(image)

    # convert to binary + cleanup
    bw = binary_erosion(image > thresh * 0.6, selem=disk(2))
    bw = binary_dilation(bw, selem=disk(5))
    bw = remove_small_holes(bw, area_threshold=min_size)

    # label image regions
    label_image = label(bw) + 1

    bounds = []
    centers = []
    for region in regionprops(label_image):
        if region.area > min_size and region.perimeter > 0:
            m = np.divide(4 * np.pi * region.area, np.power(region.perimeter, 2))
            if m > 0.6 and region.solidity > 0.925 and region.extent > 0.65:
                minr, minc, maxr, maxc = region.bbox
                bounds.append([minc, minr, maxc - minc, maxr - minr])
                centers.append(region.centroid)

    # create ouput image
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)

    ax.imshow(exposure.equalize_adapthist(image, clip_limit=0.03), cmap='gray', alpha=0.6)
    ax.set_axis_off()
    for b in bounds:
        rect = mpatches.Rectangle((b[0], b[1]), b[2], b[3],
                                  fill=False, edgecolor='red', linewidth=2)
        ax.add_patch(rect)

    for c in centers:
        ax.plot(c[1], c[0], 'ro')

    plt.tight_layout()
    fig.savefig(output_im, dpi=250)

    # write out the positions of each bottle
    with open(centroids_out, 'w') as src:
        for c in centers:
            src.write('{},{}\n'.format(c[1], c[0]))

    return len(centers)
