import os

from bottle import app, route, request
from mako.template import Template

from marteau.queue import queue, get_job, get_jobs
from marteau.job import run_loadtest
from marteau import logger


CURDIR = os.path.dirname(__file__)


@route('/', method='GET')
def index():
    index = Template(filename=os.path.join(CURDIR, 'templates', 'index.mako'))
    return index.render(jobs=get_jobs())


@route('/test', method='GET')
def get_all_jobs():
    """Adds a run into Marteau"""
    return get_jobs()


@route('/test', method='POST')
def add_run():
    """Adds a run into Marteau"""
    # a run is a github repo...
    repo = request.body.read()
    job = queue.enqueue(run_loadtest, repo)
    return job.get_id()


@route('/test/<jobid>', method='GET')
def _get_result(jobid):
    """Gets results from a run"""
    res = get_job(jobid).return_value
    if res is None:
        return 'not ready'
    return res


app = app()
