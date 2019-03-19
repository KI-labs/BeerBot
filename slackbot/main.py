import os
import time
import re
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get("SLACK_BOT_OAUTH_TOKEN"))
# starterbot's user ID in Slack: value is assigned after the bot starts up
beerbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == beerbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_inventory_command(command, channel):
    response = """
    We currently have the following items in stock:
    * 3 Franziskaner Alkoholfrei
    * 24 Paulaner Spezi
    """
    slack_client.api_call("chat.postMessage", channel=channel, text=response)


def handle_help_command(command, channel):
    response = "Try one of the following commands: inventory, photo"
    slack_client.api_call("chat.postMessage", channel=channel, text=response)


def handle_photo_command(command, channel):
    # slack_client.api_call(
    #     "chat.postMessage",
    #     channel=channel,
    #     text="Let me take a fresh picture for you...",
    # )
    slack_client.rtm_send_message(channel, "user_typing")
    with open(os.path.join(__location__, "1552989614.png"), "rb") as file_content:
        slack_client.api_call(
            "files.upload",
            channels=channel,
            file=file_content,
            title="Current contents",
        )

    # slack_client.api_call("chat.postMessage", channel=channel, text=response)


COMMAND_HANDLERS = {
    "inventory": handle_inventory_command,
    "help": handle_help_command,
    "photo": handle_photo_command,
}


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!

    handler_func = COMMAND_HANDLERS.get(command, handle_help_command)
    handler_func(command, channel)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        beerbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
