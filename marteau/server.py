from marteau import logger

from bottle import app, route, request

from marteau.queue import queue, get_job
from marteau.job import run_loadtest


@route('/', method='GET')
def index():
    return 'Welcome to Marteau'


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
