import os
import time

from dotenv import load_dotenv

from image_processing.find_bottles import find_bottles
from image_processing.utils import take_picture, update_inventory
from util.image_utils import compare_images

load_dotenv()

was_door_open = False

# set template
print('creating template')
template_out = take_picture(filename="template", q="low", bw=True, out_fmt='jpeg', sleep_time=0,
                            out_dir="{}".format(os.getenv("DATA_DIR")))
template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

while True:
    file_out = take_picture(filename="temp", q="low", bw=True, out_fmt='jpeg', sleep_time=0,
                            out_dir="{}/temp".format(os.getenv("DATA_DIR")))
    file_path = os.path.join(os.getenv("DATA_DIR"), 'temp', file_out)

    print('Checking template…')
    template_diff = compare_images(template_out, file_out)
    print("Difference: {0:.2f}%".format(template_diff * 100))

    # prev_door_state = current_door_state
    # current_door_state = "open" if is_door_open(template_path, file_path) else "closed"
    # print("Current_door_state: {}".format(current_door_state))
    # print("Prev_door_state: {}".format(prev_door_state))

    if not was_door_open and template_diff > 0.05:
        print('Door opened')
        was_door_open = True

        print('Taking photo for analysis')
        file_out = take_picture(
            q="high", out_fmt="png", sleep_time=1, out_dir="{}/raw".format(os.getenv("DATA_DIR"))
        )

        # set template
        print('Recreating template')
        template_out = take_picture(filename="template", q="low", bw=True, out_fmt='jpeg', sleep_time=0,
                                    out_dir="{}".format(os.getenv("DATA_DIR")))
        template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

        # find bottles save to data/processed
        tstamp = file_out.split('.')[0]
        print('finding bottles {}'.format(tstamp))

        pather = os.path.join("{}/raw".format(os.getenv("DATA_DIR")), file_out)
        out_pather = os.path.join("{}/processed".format(os.getenv("DATA_DIR")), file_out)
        centroids_out = os.path.join("{}/inventory".format(os.getenv("DATA_DIR")), "{}.txt".format(tstamp))
        num = find_bottles(pather, out_pather, centroids_out)

        # build inventory data/inventory
        print('updating inventory at {} with {} bottles'.format(tstamp, num))

        update_inventory("{}/inventory.txt".format(os.getenv("DATA_DIR")), tstamp, num)

    if was_door_open and template_diff > 0.20:
        print('Door closed')
        was_door_open = False

    time.sleep(2)
