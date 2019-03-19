import os
from slackbot.file_utils import get_latest_images


def is_door_closed():
    # Get latest 5 images
    images = get_latest_images("temp", 5)
    if len(images) < 5:
        return False

    # Check if every image size falls within the "approved" window
    for image in images:
        if not (140000 < os.path.getsize(image) < 155000):
            return False

    return True
