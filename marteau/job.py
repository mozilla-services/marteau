import time
import os
import subprocess
import sys
import fcntl
import argparse
import sys
import logging

from marteau import __version__, logger
from marteau.config import read_config
from marteau.redirector import Redirector

from funkload.BenchRunner import main as funkload
from funkload.ReportBuilder import main as build_report


workdir = '/tmp'

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG}

LOG_FMT = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
LOG_DATE_FMT = r"%Y-%m-%d %H:%M:%S"


def _stream(data):
    sys.stdout.write(data['data'])
    # XXX we'll push this in memory somewhere for
    # the web app to display it live


def streamredirect(func):
    def _streamredirect(repo, redirector=None):
        redirector = Redirector(_stream)
        redirector.start()
        func.redirector = redirector
        try:
            return func(repo, redirector=redirector)
        finally:
            redirector.kill()
    return _streamredirect


def run_func(cmd, redirector):
    logger.debug(cmd)
    process = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    if redirector:
        redirector.add_redirection('marteau', process, process.stdout)
        redirector.add_redirection('marteau', process, process.stderr)
    process.wait()
    return process.returncode


run_bench = "%s -c 'from funkload.BenchRunner import main; main()'"
run_bench = run_bench % sys.executable
run_report = "%s -c 'from funkload.ReportBuilder import main; main()'"
run_report = run_report % sys.executable
run_pip = "%s -c 'from pip import runner; runner.run()'"
run_pip = run_pip % sys.executable


@streamredirect
def run_loadtest(git_repo, redirector=None):
    if os.path.exists(git_repo):
        # just a local dir, lets work there
        os.chdir(git_repo)
    else:
        # checking out the repo
        os.chdir(workdir)
        name = git_repo.split('/')[-1].split('.')[0]
        run_func('git clone %s' % git_repo, redirector)
        os.chdir(os.path.join(workdir, name))

    # now looking for the marteau config file in there
    config = read_config(os.getcwd())

    wdir = config.get('wdir')
    if wdir is not None:
        os.chdir(wdir)

    # creating a virtualenv there
    run_func('virtualenv --no-site-packages .', redirector)

    python = os.path.join('bin', 'python')
    run_func(run_pip + ' install funkload', redirector)

    # install dependencies if any
    for dep in config.get('deps', []):
        run_func(run_pip + ' install %s' % dep, redirector)

    # is this a distributed test ?
    nodes = config.get('nodes', [])

    if nodes != []:
        workers = ','.join(nodes)
        workers = '--distribute-workers %s' % workers
        cmd = '%s --distribute ' % (run_bench, workers)
    else:
        cmd = run_bench

    run_func('%s %s %s' % (cmd, config['script'], config['test']),
                          redirector)

    run_func(run_report + ' --html -o html %s' %
            config['xml'], redirector)

    return 'OK'



def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)


def configure_logger(logger, level='INFO', output="-"):
    loglevel = LOG_LEVELS.get(level.lower(), logging.INFO)
    logger.setLevel(loglevel)
    if output == "-":
        h = logging.StreamHandler()
    else:
        h = logging.FileHandler(output)
        close_on_exec(h.stream.fileno())
    fmt = logging.Formatter(LOG_FMT, LOG_DATE_FMT)
    h.setFormatter(fmt)
    logger.addHandler(h)


def main():
    parser = argparse.ArgumentParser(description='Drives Funkload.')
    parser.add_argument('repo', help='Git repository or local directory',
                        nargs='?')
    parser.add_argument('--version', action='store_true',
                     default=False, help='Displays Circus version and exits.')
    parser.add_argument('--log-level', dest='loglevel', default='info',
            choices=LOG_LEVELS.keys() + [key.upper() for key in
                LOG_LEVELS.keys()],
            help="log level")
    parser.add_argument('--log-output', dest='logoutput', default='-',
            help="log output")

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.repo is None:
        parser.print_usage()
        sys.exit(0)

    # configure the logger
    configure_logger(logger, args.loglevel, args.logoutput)

    logger.info('Hammer ready. Where are the nails ?')
    try:
        return run_loadtest(args.repo)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Bye!')


if __name__ == '__main__':
    main()
