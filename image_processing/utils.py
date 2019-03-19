import os
import time

from picamera import PiCamera


def take_picture(template=False, q='high', out_dir='../data/raw', out_fmt='jpg', bw=False, sleep_time=0.2):

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with PiCamera() as camera:

        if q == 'high':
            camera.resolution = (1920, 1080)

        # Set ISO to the desired value
        camera.iso = 200
        # Wait for the automatic gain control to settle
        time.sleep(sleep_time)
        # Now fix the values
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'night'
        g = camera.awb_gains
        camera.awb_mode = 'shade'
        camera.awb_gains = g

        if bw:
            camera.color_effects = (128, 128)

        if not template:
            namer = '{}.{}'.format(round(time.time()), out_fmt)
        else:
            namer = 'template.{}'.format(out_fmt)
        camera.capture(os.path.join(out_dir, namer), format=out_fmt)
        camera.close()

    return namer


def update_inventory(inventory_file, tstamp, num):
    with open(inventory_file, 'a+') as out:
        out.write('{},{}\n'.format(tstamp, num))
