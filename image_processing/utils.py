import os
import time

from picamera import PiCamera


def take_picture(q='low', out_dir='../data/raw', out_fmt='jpeg'):

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with PiCamera() as camera:

        if q == 'high':
            camera.resolution = (1920, 1080)

        # Set ISO to the desired value
        camera.iso = 200
        # Wait for the automatic gain control to settle
        time.sleep(0.2)
        # Now fix the values
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'night'
        g = camera.awb_gains
        camera.awb_mode = 'shade'
        camera.awb_gains = g

        namer = '{}.{}'.format(round(time.time()), out_fmt)
        camera.capture(os.path.join(out_dir, namer), format=out_fmt)
        camera.close()


if __name__ == "__main__":
    take_picture()
