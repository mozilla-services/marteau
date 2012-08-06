import os

from bottle import app, route, request
from mako.template import Template

from marteau import queue


CURDIR = os.path.dirname(__file__)
JOBTIMEOUT = 3600    # one hour
queue.initialize()


@route('/', method='GET')
def index():
    index = Template(filename=os.path.join(CURDIR, 'templates', 'index.mako'))
    return index.render(jobs=queue.get_jobs(),
                        workers=queue.get_workers(),
                        failures=queue.get_failures(),
                        successes=queue.get_successes(),
                        get_result=queue.get_result,
                        running=queue.get_running_jobs())


@route('/purge', method='GET')
def purge():
    """Adds a run into Marteau"""
    queue.purge()
    return 'purged'


@route('/test', method='GET')
def get_all_jobs():
    """Adds a run into Marteau"""
    return queue.get_jobs()


@route('/test', method='POST')
def add_run():
    """Adds a run into Marteau"""
    # a run is a github repo...
    repo = request.body.read()
    job_id = queue.enqueue('marteau.job:run_loadtest', repo=repo)
    return job_id


@route('/test/<jobid>', method='GET')
def _get_result(jobid):
    """Gets results from a run"""
    res = Template(filename=os.path.join(CURDIR, 'templates', 'console.mako'))

    status, console = queue.get_result(jobid)
    if status is None:
        status = 'Running'

    return res.render(status=status, console=console)


app = app()
