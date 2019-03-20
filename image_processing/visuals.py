import json
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import exposure
from inventory.inventory import get_current_inventory
from util.file_utils import build_image_path


def show_results(output_im):
    data = get_current_inventory()
    input_im = build_image_path("raw", data["timestamp"], "png")
    x = []
    y = []
    age = []
    tstamp = int(data["timestamp"])
    curr = time.time()
    for d in data["bottles"]:
        x.append(float(d["x"]))
        y.append(float(d["y"]))
        age.append(float(d["age"]) + curr - tstamp)

    # load image
    with Image.open(input_im, "r").convert("L") as src:
        image = np.asarray(src)

    # create output image
    fig = plt.figure(frameon=False)
    fig.subplots_adjust(bottom=0.5)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    fig.add_axes(ax)

    ax.imshow(
        exposure.equalize_adapthist(image, clip_limit=0.03), cmap="gray", alpha=0.6
    )
    ax.set_axis_off()

    sc = ax.scatter(
        x, y, c=age, s=300, vmin=0, vmax=3600, cmap="Blues"
    )  # fixed on one hour

    cax = fig.add_axes([0.27, 0.075, 0.5, 0.05])
    cb1 = fig.colorbar(sc, cax=cax, cmap="Blues", ticks=[], orientation="horizontal")
    cb1.set_label("Beer Coldness", fontsize=16)

    plt.tight_layout()
    plt.text(10, 10, curr, fontsize=25)
    fig.savefig(output_im, dpi=250)

    return True


# if __name__ == "__main__":
#     show_results('./data/raw/1553013640.png', 'test.png', './data/inventory_details.json')
