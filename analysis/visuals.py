import time

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

from analysis.file_utils import build_image_path
from analysis.find_bottles import __load_image, __load_mask, __load_predictions
from analysis.inventory import get_current_inventory


def fit_ellipse(contour):
    contour = np.array(contour)
    mean = np.mean(contour, 0)
    contour -= mean
    N = len(contour[:, 0])

    U, S, V = np.linalg.svd(np.stack((contour[:, 0], contour[:, 1])))

    tt = np.linspace(0, 2 * np.pi, 1000)
    circle = np.stack((np.cos(tt), np.sin(tt)))  # unit circle
    transform = np.sqrt(2 / N) * U.dot(np.diag(S))  # transformation matrix
    fit = transform.dot(circle) + mean[:, None]
    return list(zip(*fit))


def cold_photo(output_im, simplify=False, logo_path=None):
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
    image = __load_image(input_im)

    # build colormap
    cmap = plt.cm.get_cmap('Blues')

    # DUMMY PLOT
    fig, ax = plt.subplots(figsize=(12,8), dpi=200)
    Z = [[0, 0], [0, 0]]
    levels = range(0, max_age, 60)
    CS3 = ax.contourf(Z, levels, vmin=0, vmax=max_age, cmap=cmap)
    ax.clear()

    # create output image
    ax.imshow(image, cmap='gray', alpha=0.7)
    ax.set_axis_off()

    # add contours around each bottle
    for contour, age in zip(contours, ages):
        normalized_age = min(0.98, np.divide(age, max_age))
        if simplify:
            contour = fit_ellipse(contour)
        ax.plot(*zip(*contour), lw=5, c='k')
        ax.plot(*zip(*contour), lw=2.5, c=cmap(normalized_age))
    plt.axis('off')

    # add colorbar
    cax = fig.add_axes([0.25, 0.05, 0.5, 0.025])
    cb1 = fig.colorbar(CS3, cax=cax, cmap=cmap,
                       ticks=[],
                       orientation='horizontal')
    cb1.set_label('Beer Coldness', fontsize=20)

    # add logo
    if logo_path:
        logo_ax = fig.add_axes([0.68, 0.92, 0.3, 0.1], anchor='SW', zorder=1)
        logo_ax.imshow(__load_mask(logo_path))
        logo_ax.axis('off')

    plt.tight_layout()
    fig.savefig(output_im, dpi=200)


def engine_photo(output_im, logo_path=None):
    # find latest image
    data = get_current_inventory()

    # get latest inputs
    input_im = build_image_path("raw", data["timestamp"], "png")
    input_mask = build_image_path("mask", data["timestamp"], "png")
    response_out = build_image_path("response", data["timestamp"], "json")

    # load all inputs
    image = __load_image(input_im)
    mask = __load_mask(input_mask)
    response = __load_predictions(response_out)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.imshow(image, alpha=0.7)
    for ind, r in enumerate(response):
        w = r['x2'] - r['x1']
        h = r['y2'] - r['y1']
        bbox = patches.Rectangle((r["x1"], r["y1"]), w, h,
                                 linewidth=3,
                                 edgecolor="y",
                                 facecolor="none")
        ax.add_patch(bbox)

    # add the refined mask of the bottle caps
    plt.imshow(np.ma.masked_where(mask == 0, mask), cmap='Reds_r', alpha=0.75)
    plt.axis('off')

    # add logo
    if logo_path:
        logo_ax = fig.add_axes([0.68, 0.92, 0.3, 0.1], anchor='SW', zorder=1)
        logo_ax.imshow(__load_mask(logo_path))
        logo_ax.axis('off')

    plt.tight_layout()
    fig.savefig(output_im)
