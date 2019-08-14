import time

import os
from dotenv import load_dotenv
from slackclient import SlackClient

from analysis.file_utils import get_current_inventory
from analysis.slack_utils import __handle_tz

# load ENV from .env
load_dotenv()
CHANNEL = os.environ.get("CHANNEL")
ALERT_DELAY = int(os.environ.get("ALERT_DELAY"))
MIN_BEER_THRESHOLD = int(os.environ.get("MIN_BEER_THRESHOLD"))
SLACK_BOT_OATH_TOKEN = os.environ.get("SLACK_BOT_OAUTH_TOKEN")

# initialize slack client and bot
slack_client = SlackClient(SLACK_BOT_OATH_TOKEN)
beerbot_id = None

if __name__ == "__main__":

    if slack_client.rtm_connect(with_team_state=False):
        print("BeerBot (alert) connected and running!")

        # read bot user ID (call Web API method `auth.test`)
        beerbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:

            # check current inventory
            current_inventory = get_current_inventory()
            if current_inventory:
                timestamp, count = current_inventory
                timestamp = __handle_tz(timestamp)
                print("[{}] Current inventory - {}".format(timestamp.strftime("%d.%m.%y %H:%M %Z"), count))
                if count < MIN_BEER_THRESHOLD:
                    slack_client.api_call(
                        "chat.postMessage",
                        channel=CHANNEL,
                        text="@channel We're running out of beer! There are less than {} bottles left".format(
                            MIN_BEER_THRESHOLD
                        ),
                        link_names=1,
                    )

            time.sleep(ALERT_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
