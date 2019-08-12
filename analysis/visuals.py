import time

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageEnhance

from analysis.file_utils import build_image_path
from analysis.inventory import get_current_inventory


def cold_photo(output_im):
    # find latest image
    data = get_current_inventory()
    input_im = build_image_path("raw", data["timestamp"], "png")

    # set max age
    max_age = 3600

    # load bottle info + age
    contours = []
    ages = []
    tstamp = int(data["timestamp"])
    curr = time.time()
    for d in data["bottles"]:
        contours.append(d["contour"])
        ages.append(float(d["age"]) + curr - tstamp)

    # convert to grayscale + add brightness
    img = Image.open(input_im, 'r').convert('L')
    img = ImageEnhance.Brightness(img).enhance(4)
    image = np.asarray(img)

    # build colormap
    cmap = plt.cm.get_cmap('Blues')

    # DUMMY PLOT
    fig, ax = plt.subplots(frameon=False)
    Z = [[0, 0], [0, 0]]
    levels = range(0, max_age, 60)
    CS3 = ax.contourf(Z, levels, vmin=0, vmax=max_age, cmap=cmap)
    ax.clear()

    # create output image
    ax.imshow(image, cmap='gray', alpha=0.7, origin='upper')
    ax.set_axis_off()

    # add contours around each bottle
    for contour, age in zip(contours, ages):
        normalized_age = min(0.98, np.divide(age, max_age))
        ax.plot(*zip(*contour), lw=5, c='k')
        ax.plot(*zip(*contour), lw=3, c=cmap(normalized_age))
    plt.axis('off')
    # add colorbar
    cax = fig.add_axes([0.27, 0.075, 0.5, 0.05])
    cb1 = fig.colorbar(CS3, cax=cax, cmap=cmap,
                       ticks=[],
                       orientation='horizontal')
    cb1.set_label('Beer Coldness', fontsize=16)

    plt.tight_layout()
    fig.savefig(output_im, dpi=200)

    return None
