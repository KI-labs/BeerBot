import os
import re
import time
from datetime import datetime as dt

from dateutil import tz

from analysis.file_utils import get_current_inventory
from analysis.visuals import cold_photo, debug_photo


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def parse_bot_commands(slack_client, bot_id):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    slack_events = slack_client.rtm_read()
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, command = parse_direct_mention(event["text"])
            if user_id == bot_id:
                handler_func = COMMAND_HANDLERS.get(command, handle_help_command)
                handler_func(command, event["channel"], slack_client)


def __handle_tz(timestamp):
    from_zone = tz.tzutc()
    to_zone = tz.gettz(os.environ.get("TZ"))
    return dt.utcfromtimestamp(timestamp).replace(tzinfo=from_zone).astimezone(to_zone)


def __message_for_inventory(inventory):
    if not inventory:
        return "I don't know yet what we have in stock"
    timestamp, count = inventory
    timestamp = __handle_tz(time.mktime(timestamp))
    return "As of {} there are {} bottles in the fridge".format(timestamp.strftime("%d.%m.%y %H:%M"), count)


def __send_typing_event(channel, slack_client):
    typing_event_json = {"id": 1, "type": "typing", "channel": channel}
    slack_client.server.send_to_websocket(typing_event_json)


def handle_inventory_command(command, channel, slack_client):
    print('Handling command "{}"'.format(command))
    response = __message_for_inventory(get_current_inventory())
    slack_client.api_call("chat.postMessage", channel=channel, text=response)


def handle_help_command(command, channel, slack_client):
    print('Handling command "{}"'.format(command))
    response = "Try one of the following commands: inventory, photo, debug"
    slack_client.api_call("chat.postMessage", channel=channel, text=response)


def handle_debug_command(command, channel, slack_client):
    print('Handling command "{}"'.format(command))
    __send_typing_event(channel, slack_client)

    # handle static IO
    debug_image = os.path.join(os.environ.get("DATA_DIR"), "debug.jpg")
    debug_photo(debug_image)
    with open(debug_image, "rb") as file_content:
        slack_client.api_call(
            "files.upload",
            channels=channel,
            file=file_content,
            title="DEBUG PREDICTION",
        )


def handle_cold_command(command, channel, slack_client):
    print('Handling command "{}"'.format(command))
    __send_typing_event(channel, slack_client)

    # handle static IO
    latest_image = os.path.join(os.environ.get("DATA_DIR"), "cold.jpg")

    cold_photo(latest_image)
    current_inventory = get_current_inventory()
    current_count = 0
    if current_inventory:
        _, current_count = current_inventory
    with open(latest_image, "rb") as file_content:
        slack_client.api_call(
            "files.upload",
            channels=channel,
            file=file_content,
            title="Bottles: {}".format(current_count),
        )


# available slack commands
COMMAND_HANDLERS = {
    "inventory": handle_inventory_command,
    "help": handle_help_command,
    "photo": handle_cold_command,
    "debug": handle_debug_command,
}
