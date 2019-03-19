import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import exposure
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import binary_closing, disk, remove_small_holes


def find_bottles(input_im, output_im):

    # load image
    with Image.open(input_im, 'r').convert('L') as src:
        image = np.asarray(src)

    # define image processing parameters
    selem = disk(15)
    min_size = 5000

    # threshold image (OTSU)
    thresh = threshold_otsu(image)

    # convert to binary + cleanup
    bw = binary_closing(image > thresh * 0.8, selem=selem)
    bw = remove_small_holes(bw, area_threshold=min_size)

    # label image regions
    label_image = label(bw) + 1

    bounds = []
    centers = []
    bottles = np.zeros(label_image.shape)
    for region in regionprops(label_image):
        m = 4 * np.pi * region.area / np.power(region.perimeter, 2)
        if region.area > 750 and m > 0.7:
            bottles[label_image == region.label] = 1

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

    return len(centers)

