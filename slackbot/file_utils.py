from __future__ import print_function
import os
from time import gmtime

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_latest_image(type):
    path = "../data/{}".format(type)

    paths = [os.path.join(path, basename) for basename in os.listdir(path)]
    latest_file = max(paths, key=os.path.getctime)
    return latest_file


def get_current_inventory():
    path = "../data/inventory.txt"
    with open(os.path.join(__location__, path), "r") as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
        timestamp, count = last_line.split(",")
        return gmtime(int(timestamp)), int(count)

