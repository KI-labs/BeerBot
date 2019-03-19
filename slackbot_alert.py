import os
import re
import time
from datetime import datetime as dt

from dotenv import load_dotenv
from slackclient import SlackClient

from util.file_utils import get_latest_image, get_current_inventory

load_dotenv()

# instantiate Slack client
slack_client = SlackClient(os.environ.get("SLACK_BOT_OAUTH_TOKEN"))
# starterbot's user ID in Slack: value is assigned after the bot starts up
beerbot_id = None

# constants
RTM_READ_DELAY = 10  # 1 second delay between reading from RTM
THRESHOLD = 3
CHANNEL = "UCL1VMX6D"
# CHANNEL = "beerbot-notifications"

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Slackbot alerter connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        beerbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            current_inventory = get_current_inventory()
            if current_inventory:
                _timestamp, count = current_inventory
                if count < THRESHOLD:
                    slack_client.api_call(
                        "chat.postMessage",
                        channel=CHANNEL,
                        text="@channel We're running out of beer! There are less than {} bottles left".format(
                            THRESHOLD
                        ),
                        link_names=1,
                    )

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
