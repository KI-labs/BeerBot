import os
import time

from picamera import PiCamera


def take_picture(out_dir='/home/pi/BeerBot/image_processing/ims', out_fmt='png'):
    """

    Args:
        out_dir:
        out_fmt:

    Returns:

    """

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with PiCamera() as camera:
        camera.resolution = (1920, 1080)
        namer = '{}.{}'.format(round(time.time()), out_fmt)
        camera.capture(os.path.join(out_dir, namer), format=out_fmt)
        camera.close()


if __name__ == "__main__":
    take_picture()
