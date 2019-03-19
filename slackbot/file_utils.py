from __future__ import print_function
import os
from time import gmtime


def get_latest_image(type):
    path = "{}/{}".format(os.getenv("DATA_DIR"), type)

    paths = [os.path.join(path, basename) for basename in os.listdir(path)]
    latest_file = max(paths, key=os.path.getctime)
    return latest_file


def get_current_inventory():
    path = "{}/inventory.txt".format(os.getenv("DATA_DIR"))
    with open(path, "r") as f:
        lines = f.read().splitlines()
        if lines == []:
            return None
        last_line = lines[-1]
        timestamp, count = last_line.split(",")
        return gmtime(int(timestamp)), int(count)

