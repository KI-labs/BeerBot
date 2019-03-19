import os
import shlex
from subprocess import Popen, PIPE

from slackbot.file_utils import get_latest_images


def run_cmd(cmd):
    """
    Basic function for running a subprocess call and returning response
    Args:
        cmd (str): shell command to execute
    Returns:
        exitcode (str): exit code from command
        out (str): response
        err (str): error (if any)
    """
    args = shlex.split(cmd)
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    err, out = proc.communicate()
    exitcode = proc.returncode

    return exitcode, err, out


def is_door_open(template, im):

    exitcode, err, out = run_cmd('compare -metric RMSE {} {} /dev/null'.format(template, im))
    pct = float(str(out).split(' ')[-1].replace('(', '').replace(')', '').replace('\'', ''))

    # # Get latest 5 images
    # images = get_latest_images("temp", 5)
    # if len(images) < 5:
    #     return False
    #
    # # Check if every image size falls within the "approved" window
    # for image in images:
    #     print(os.path.getsize(image))
    #     if not (130000 < os.path.getsize(image) < 155000):
    #         return False\

    print(pct)

    return pct > 0.05

