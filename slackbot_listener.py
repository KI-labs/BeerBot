import time

import os
from dotenv import load_dotenv
from slackclient import SlackClient

from analysis.slack_utils import parse_bot_commands

# load ENV from .env
load_dotenv()
LISTEN_DELAY = int(os.environ.get("LISTEN_DELAY"))
SLACK_BOT_OATH_TOKEN = os.environ.get("SLACK_BOT_OAUTH_TOKEN")

# initialize slack client and bot
slack_client = SlackClient(SLACK_BOT_OATH_TOKEN)
beerbot_id = None

if __name__ == "__main__":

    if slack_client.rtm_connect(with_team_state=False):
        print("BeerBot (listen) connected and running!")

        # read bot user ID (call Web API method `auth.test`)
        beerbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            # handle slack command
            parse_bot_commands(slack_client, beerbot_id)
            time.sleep(LISTEN_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
