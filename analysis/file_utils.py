from __future__ import print_function

import os
from time import gmtime


def get_images(source):
    path = "{}/{}".format(os.getenv("DATA_DIR"), source)
    return [os.path.join(path, basename) for basename in os.listdir(path)]


def build_image_path(source, timestamp, extension="png"):
    return "{}/{}/{}.{}".format(os.getenv("DATA_DIR"), source, timestamp, extension)


def get_latest_image(source):
    paths = get_images(source)
    latest_file = max(paths, key=os.path.getctime)
    return latest_file


def get_latest_images(source, num_images):
    paths = get_images(source)
    paths = sorted(paths, key=os.path.getctime, reverse=True)
    return paths[0:num_images]


def get_current_inventory():
    path = "{}/inventory.txt".format(os.getenv("DATA_DIR"))
    if not os.path.exists(path):
        open(path, 'a').close()
    with open(path, "r") as f:
        lines = f.read().splitlines()
        if not lines:
            return None
        last_line = lines[-1]
        timestamp, count = last_line.split(",")
        return gmtime(int(timestamp)), int(count)
