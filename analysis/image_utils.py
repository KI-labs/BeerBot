import shlex
from subprocess import Popen, PIPE


def run_cmd(cmd):
    """
    Function for running a subprocess call and returning response
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


def is_door_open(template, im):
    exitcode, err, out = run_cmd('compare -metric RMSE {} {} /dev/null'.format(template, im))
    pct = float(str(out).split(' ')[-1].replace('(', '').replace(')', '').replace('\'', ''))

    print(pct)

    return pct > 0.05
