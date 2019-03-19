from image_processing.utils import take_picture
import time

event = False

while True:

    # TODO low res photo
    take_picture(out_dir='data/temp')

    # TODO check logic for event
    if event:
        take_picture(q='high', out_fmt='png', out_dir='data/raw')

        # TODO -> find bottles save to data/processed

        # TODO -> build inventory data/inventory

    time.sleep(5)

