import shlex
from subprocess import Popen, PIPE


def run_cmd(cmd):
    """
    Basic function for running a subprocess call and returning response
    Args:
        cmd (str): shell command to execute
    Returns:
        exitcode (str): exit code from command
        err (str): error (if any)
        out (str): response
    """
    args = shlex.split(cmd)
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    err, out = proc.communicate()
    exitcode = proc.returncode

    return exitcode, err, out


def compare_images(image1, image2):
    exitcode, err, out = run_cmd('compare -metric RMSE {} {} /dev/null'.format(image1, image2))
    return float(str(out).split(' ')[-1].replace('(', '').replace(')', '').replace('\'', ''))
