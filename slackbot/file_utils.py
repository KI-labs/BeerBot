from __future__ import print_function
import os


def get_latest_image(type):
    path = "../data/{}".format(type)

    paths = [os.path.join(path, basename) for basename in os.listdir(path)]
    latest_file = max(paths, key=os.path.getctime)
    return latest_file
