import os
import time

from dotenv import load_dotenv

from image_processing.find_bottles import find_bottles
from image_processing.utils import take_picture, update_inventory
from util.image_utils import is_door_open

load_dotenv()

current_door_state = "closed"
prev_door_state = "open"


# set template
print('creating template')
template_out = take_picture(template=True, q="low", bw=True, out_fmt='jpeg', sleep_time=0,
                     out_dir="{}".format(os.getenv("DATA_DIR")))
template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

while True:
    file_out = take_picture(q="low", bw=True, out_fmt='jpeg', sleep_time=0, out_dir="{}/temp".format(os.getenv("DATA_DIR")))
    file_path = os.path.join(os.getenv("DATA_DIR"), 'temp', file_out)

    # TODO - check with template
    print('checking template')

    prev_door_state = current_door_state
    current_door_state = "open" if is_door_open(template_path, file_path) else "closed"
    print("current_door_state: {}".format(current_door_state))
    print("prev_door_state: {}".format(prev_door_state))

    if current_door_state == "closed" and prev_door_state == "open":
        print('taking photo for analysis')
        file_out = take_picture(
            q="high", out_fmt="png", sleep_time=1, out_dir="{}/raw".format(os.getenv("DATA_DIR"))
        )

        # set template
        print('REcreating template')
        template_out = take_picture(template=True, q="low", bw=True, out_fmt='jpeg', sleep_time=0,
                                    out_dir="{}".format(os.getenv("DATA_DIR")))
        template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

        # find bottles save to data/processed
        tstamp = file_out.split('.')[0]
        print('finding bottles {}'.format(tstamp))

        pather = os.path.join("{}/raw".format(os.getenv("DATA_DIR")), file_out)
        out_pather = os.path.join("{}/processed".format(os.getenv("DATA_DIR")), file_out)
        num = find_bottles(pather, out_pather)

        # build inventory data/inventory
        print('updating inventory at {} with {} bottles'.format(tstamp, num))

        update_inventory("{}/inventory.txt".format(os.getenv("DATA_DIR")), tstamp, num)

    time.sleep(2)
