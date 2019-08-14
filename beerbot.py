import time

import os
from dotenv import load_dotenv
from slackclient import SlackClient

from analysis.file_utils import update_inventory
from analysis.find_bottles import find_bottles
from analysis.image_utils import is_door_open
from analysis.inventory import update_inventory as update_positions
from analysis.slack_utils import __send_typing_event
from analysis.utils import take_picture
from analysis.visuals import cold_photo

# load ENV from .env
load_dotenv()
DATA_DIR = os.environ.get("DATA_DIR")
CHANNEL = os.environ.get("CHANNEL")
SLACK_BOT_OATH_TOKEN = os.environ.get("SLACK_BOT_OAUTH_TOKEN")
ENDPOINT = os.environ.get("ENDPOINT")

# initialize inventory, state and slack client
update_positions()
current_door_state = "closed"
prev_door_state = "open"
slack_client = SlackClient(SLACK_BOT_OATH_TOKEN)

# handle static IO
RESPONSE_DIR = os.path.join(DATA_DIR, "response")
MASK_DIR = os.path.join(DATA_DIR, "mask")
RAW_DIR = os.path.join(DATA_DIR, "raw")
INVENTORY_DIR = os.path.join(DATA_DIR, "inventory")
for x in [RESPONSE_DIR, MASK_DIR, RAW_DIR, INVENTORY_DIR]:
    if not os.path.exists(x):
        os.makedirs(x)
COLD_IMAGE_PATH = os.path.join(DATA_DIR, "cold.jpg")
INVENTORY_PATH = os.path.join(DATA_DIR, "inventory.txt")

if __name__ == "__main__":

    if slack_client.rtm_connect(with_team_state=False):
        print("BeerBot (alert) connected and running!")

        # initialize by setting template
        print("creating template")
        template_out = take_picture(filename="template", q="low", bw=True, out_fmt="jpeg", sleep_time=0,
                                    out_dir="{}".format(DATA_DIR))
        template_path = os.path.join(DATA_DIR, template_out)

        while True:

            # take a low resolution image for comparison against the template
            file_out = take_picture(filename="temp", q="low", bw=True, out_fmt="jpeg", sleep_time=0,
                                    out_dir="{}/temp".format(DATA_DIR))
            file_path = os.path.join(DATA_DIR, "temp", file_out)

            # check state of door based on template
            print("Checking template")
            prev_door_state = current_door_state
            current_door_state = ("open" if is_door_open(template_path, file_path) else "closed")
            print("Current_door_state: {}".format(current_door_state))
            print("Prev_door_state: {}".format(prev_door_state))

            # process high resolution image
            if current_door_state == "closed" and prev_door_state == "open":
                print("Taking photo for analysis")
                file_out = take_picture(q="high", out_fmt="png", sleep_time=1,
                                        out_dir="{}/raw".format(DATA_DIR))
                tstamp, _ = os.path.splitext(file_out)

                # set NEW low resolution template image
                print("Recreating template")
                template_out = take_picture(filename="template", q="low", bw=True, out_fmt="jpeg", sleep_time=0,
                                            out_dir="{}".format(DATA_DIR))
                template_path = os.path.join(DATA_DIR, template_out)

                # find bottles save to data/processed
                print("finding bottles {}".format(tstamp))
                input_im = os.path.join(RAW_DIR, file_out)
                response_out = os.path.join(RESPONSE_DIR, "{}.json".format(tstamp))
                mask_out = os.path.join(MASK_DIR, "{}.png".format(tstamp))
                contours_out = os.path.join(INVENTORY_DIR, "{}.json".format(tstamp))
                num = find_bottles(ENDPOINT, input_im, response_out, mask_out, contours_out)

                # build inventory data/inventory
                print("updating inventory at {} with {} bottles".format(tstamp, num))
                update_inventory(INVENTORY_PATH, tstamp, num)
                __send_typing_event(CHANNEL, slack_client)

                # visualize NEW cold image
                cold_photo(COLD_IMAGE_PATH, simplify=False, logo_path=os.environ.get("LOGO_PATH"))
                with open(COLD_IMAGE_PATH, "rb") as file_content:
                    slack_client.api_call("files.upload", channels=CHANNEL, file=file_content,
                                          title="Bottles: {}".format(num), )

            time.sleep(2)
    else:
        print("Connection failed. Exception traceback printed above.")
