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

    wdir = config.get('wdir')
    if wdir is not None:
        os.chdir(wdir)

    # creating a virtualenv there
    subprocess.check_call('virtualenv --no-site-packages .', shell=True)

    python = os.path.join('bin', 'python')
    subprocess.check_call('bin/pip install funkload', shell=True)

    # install dependencies if any
    for dep in config['deps']:
        subprocess.check_call('bin/pip install %s' % dep, shell=True)

    subprocess.check_call('bin/fl-run-bench %s %s' % (config['script'],
                                                      config['test']),
                          shell=True)

    subprocess.check_call('bin/fl-build-report --html -o html %s' %
            config['xml'], shell=True)

    return 'OK'


def main():
    run_loadtest(sys.argv[1])


if __name__ == '__main__':
    main()
