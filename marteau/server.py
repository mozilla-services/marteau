import os
from bottle import app, route, request, redirect, static_file
from mako.template import Template

from marteau import queue
from marteau.job import reportsdir


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
    repo = request.forms.get('repo')
    if repo is None:
        repo = request.body.read()
        rest = True
    else:
        rest = False

    job_id = queue.enqueue('marteau.job:run_loadtest', repo=repo)
    if not rest:
        return redirect('/')

    return job_id


@route('/test/<jobid>', method='GET')
def _get_result(jobid):
    """Gets results from a run"""
    res = Template(filename=os.path.join(CURDIR, 'templates', 'console.mako'))
    report = None
    status, console = queue.get_result(jobid)

    if status is None:
        status = 'Running'
    else:
        status = status['data']
        if os.path.exists(status):
            # we have a report
            status = 'Finished.'
            report = '/report/%s' % jobid

    return res.render(status=status, console=console, report=report)


@route('/report/<jobid>/<filename:path>')
def report_dir(jobid, filename):
    path = os.path.join(reportsdir, jobid)
    return static_file(filename, root=path)


@route('/report/<jobid>')
def report_index(jobid):
    return redirect('/report/%s/index.html' % jobid)


app = app()
