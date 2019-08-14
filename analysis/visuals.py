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

    # DUMMY figure
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    levels = np.arange(0, max_age + 60, 60)
    CS3 = ax.contourf([[0, 0], [0, 0]], levels, vmin=0, vmax=max_age, cmap=cmap)
    ax.clear()

    # create output image
    ax.imshow(image, cmap='gray', alpha=0.7)

    for contour, age in zip(contours, ages):
        normalized_age = min(0.98, np.divide(age, max_age))
        if simplify:
            contour = fit_ellipse(contour)
        ax.plot(*zip(*contour), lw=5, c='k')
        ax.add_patch(patches.Polygon(np.array(contour),
                                     linewidth=3,
                                     edgecolor="None",
                                     facecolor=cmap(normalized_age),
                                     alpha=0.5))
        ax.plot(*zip(*contour), lw=2.5, c=cmap(normalized_age))
    ax.axis('equal')
    ax.set_axis_off()

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
    response_out = build_image_path("response", data["timestamp"], "json")

    # load all inputs
    image = __load_image(input_im)
    response = __load_predictions(response_out)

    # build colormap
    cmap = plt.cm.get_cmap('Reds')

    # DUMMY figure
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    max_conf = 1
    levels = np.arange(0, max_conf + 0.05, 0.05)
    CS3 = ax.contourf([[0, 0], [0, 0]], levels, vmin=0, vmax=max_conf, cmap=cmap)
    ax.clear()

    ax.imshow(image, alpha=0.7)
    for ind, r in enumerate(response):
        w = r['x2'] - r['x1']
        h = r['y2'] - r['y1']
        ax.add_patch(patches.Rectangle((r["x1"], r["y1"]), w, h,
                                       linewidth=3,
                                       edgecolor=cmap(r['conf']),
                                       facecolor="None"))
    ax.axis('equal')
    ax.set_axis_off()

    # set colorbar for confidence
    cax = fig.add_axes([0.25, 0.05, 0.5, 0.025])
    cb1 = fig.colorbar(CS3, cax=cax, cmap=cmap,
                       ticks=[],
                       orientation='horizontal')
    cb1.set_label('Prediction Confidence', fontsize=20)

    # add logo
    if logo_path:
        logo_ax = fig.add_axes([0.68, 0.92, 0.3, 0.1], anchor='SW', zorder=1)
        logo_ax.imshow(__load_mask(logo_path))
        logo_ax.axis('off')

    plt.tight_layout()
    fig.savefig(output_im)
