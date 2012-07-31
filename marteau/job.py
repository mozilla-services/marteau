import time
import os
import subprocess
import sys

from marteau.config import read_config
from funkload.BenchRunner import main as funkload
from funkload.ReportBuilder import main as build_report

workdir = '/tmp'


def run_loadtest(git_repo):
    if os.path.exists(git_repo):
        # just a local dir, lets work there
        os.chdir(git_repo)
    else:
        # checking out the repo
        os.chdir(workdir)
        name = git_repo.split('/')[-1].split('.')[0]
        subprocess.check_call('git clone %s' % git_repo, shell=True)
        os.chdir(os.path.join(workdir, name))

    # now looking for the marteau config file in there
    config = read_config(os.getcwd())

    # running the tests  XXX will use lower-level code later
    saved = list(sys.argv)
    sys.argv[:] = [sys.executable, config['script'], config['test']]
    try:
        funkload()
    except SystemExit:
        pass
    finally:
        sys.argv[:] = saved

    # generating the reports
    saved = list(sys.argv)
    # xml can be found in the config file
    sys.argv[:] = [sys.executable, '--html', '-o', 'html', config['xml']]
    try:
        build_report()
    except SystemExit:
        pass
    finally:
        sys.argv[:] = saved

    return 'OK'


def main():
    run_loadtest(sys.argv[1])


if __name__ == '__main__':
    main()
