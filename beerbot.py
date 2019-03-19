import os
import time
from os import getenv

from dotenv import load_dotenv
from util.image_utils import is_door_closed
from image_processing.utils import take_picture

load_dotenv()

current_door_state = "closed"
prev_door_state = "open"

while True:
    take_picture(q="low", out_dir="{}/temp".format(os.getenv("DATA_DIR")))

    prev_door_state = current_door_state
    current_door_state = "closed" if is_door_closed() else "open"

    if current_door_state == "closed" and prev_door_state == "open":
        take_picture(
            q="high", out_fmt="png", out_dir="{}/raw".format(os.getenv("DATA_DIR"))
        )

        # TODO -> find bottles save to data/processed

        # TODO -> build inventory data/inventory

    time.sleep(5)
