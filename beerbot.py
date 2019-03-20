import os
import time

from dotenv import load_dotenv

from image_processing.find_bottles import find_bottles
from image_processing.utils import take_picture, update_inventory
from image_processing.visuals import show_results
from util.image_utils import is_door_open
from slackclient import SlackClient

load_dotenv()

current_door_state = "closed"
prev_door_state = "open"

# instantiate Slack client
slack_client = SlackClient(os.environ.get("SLACK_BOT_OAUTH_TOKEN"))

CHANNEL = "beerbot-notifications"
COLD_IMAGE_PATH = "{}/cold.jpg".format(os.getenv("DATA_DIR"))



def __send_typing_event(channel):
    typing_event_json = {"id": 1, "type": "typing", "channel": channel}
    slack_client.server.send_to_websocket(typing_event_json)


def __generate_new_cold_image():
    show_results(COLD_IMAGE_PATH)
    return COLD_IMAGE_PATH


if slack_client.rtm_connect(with_team_state=False):
    print("Slackbot alerter connected and running!")

    # set template
    print("creating template")
    template_out = take_picture(
        filename="template",
        q="low",
        bw=True,
        out_fmt="jpeg",
        sleep_time=0,
        out_dir="{}".format(os.getenv("DATA_DIR")),
    )
    template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

    while True:
        file_out = take_picture(
            filename="temp",
            q="low",
            bw=True,
            out_fmt="jpeg",
            sleep_time=0,
            out_dir="{}/temp".format(os.getenv("DATA_DIR")),
        )
        file_path = os.path.join(os.getenv("DATA_DIR"), "temp", file_out)

        print("Checking template")

        prev_door_state = current_door_state
        current_door_state = (
            "open" if is_door_open(template_path, file_path) else "closed"
        )
        print("Current_door_state: {}".format(current_door_state))
        print("Prev_door_state: {}".format(prev_door_state))

        if current_door_state == "closed" and prev_door_state == "open":
            print("Taking photo for analysis")
            file_out = take_picture(
                q="high",
                out_fmt="png",
                sleep_time=1,
                out_dir="{}/raw".format(os.getenv("DATA_DIR")),
            )

            # set template
            print("Recreating template")
            template_out = take_picture(
                filename="template",
                q="low",
                bw=True,
                out_fmt="jpeg",
                sleep_time=0,
                out_dir="{}".format(os.getenv("DATA_DIR")),
            )
            template_path = os.path.join(os.getenv("DATA_DIR"), template_out)

            # find bottles save to data/processed
            tstamp = file_out.split(".")[0]
            print("finding bottles {}".format(tstamp))

            pather = os.path.join("{}/raw".format(os.getenv("DATA_DIR")), file_out)
            out_pather = os.path.join(
                "{}/processed".format(os.getenv("DATA_DIR")), file_out
            )
            centroids_out = os.path.join(
                "{}/inventory".format(os.getenv("DATA_DIR")), "{}.txt".format(tstamp)
            )
            num = find_bottles(pather, out_pather, centroids_out)

            # build inventory data/inventory
            print("updating inventory at {} with {} bottles".format(tstamp, num))

            update_inventory(
                "{}/inventory.txt".format(os.getenv("DATA_DIR")), tstamp, num
            )
            __send_typing_event(CHANNEL)
            latest_image = __generate_new_cold_image()
            with open(latest_image, "rb") as file_content:
                slack_client.api_call(
                    "files.upload",
                    channels=CHANNEL,
                    file=file_content,
                    title="Bottles: {}".format(num),
                )

        time.sleep(2)
