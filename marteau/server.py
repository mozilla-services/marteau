import os
import time
import datetime

from bottle import app, route, request, redirect, static_file
from mako.lookup import TemplateLookup

from marteau import queue
from marteau.job import reportsdir
from marteau.node import Node


CURDIR = os.path.dirname(__file__)
MEDIADIR = os.path.join(CURDIR, 'media')
TMPLDIR = os.path.join(CURDIR, 'templates')
TMPLS = TemplateLookup(directories=[TMPLDIR])
JOBTIMEOUT = 3600    # one hour
DOCDIR = os.path.join(CURDIR, 'docs', 'build', 'html')


queue.initialize()


def time2str(data):
    if data is None:
        return 'Unknown date'
    return datetime.datetime.fromtimestamp(data).strftime('%Y-%m-%d %H:%M:%S')


@route('/', method='GET')
def index():
    index = TMPLS.get_template('index.mako')
    return index.render(jobs=queue.get_jobs(),
                        workers=queue.get_workers(),
                        nodes=list(queue.get_nodes()),
                        failures=queue.get_failures(),
                        successes=queue.get_successes(),
                        get_result=queue.get_result,
                        running=queue.get_running_jobs(),
                        time2str=time2str)


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
    # XXX should use colander here
    repo = request.forms.get('repo')
    redirect_url = request.forms.get('redirect_url')
    cycles = request.forms.get('cycles')
    duration = request.forms.get('duration')
    if duration is not None:
        duration = int(duration)

    nodes = request.forms.get('nodes')
    if nodes is not None:
        nodes = int(nodes)

    metadata = {'created': time.time(),
                'repo': repo}

    job_id = queue.enqueue('marteau.job:run_loadtest', repo=repo,
                           cycles=cycles, nodes_count=nodes, duration=duration,
                           metadata=metadata)
    if redirect_url is not None:
        return redirect(redirect_url)

    return job_id


@route('/test/<jobid>', method='GET')
def _get_result(jobid):
    """Gets results from a run"""
    res = TMPLS.get_template('console.mako')
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


@route('/nodes', method='GET')
def _nodes():
    res = TMPLS.get_template('nodes.mako')
    return res.render(nodes=list(queue.get_nodes()))


@route('/nodes/<name>/enable', method='GET')
def enable_node(name):
    # load existing
    node = queue.get_node(name)

    # update the flag
    node.enabled = not node.enabled

    queue.save_node(node)
    redirect('/nodes')


@route('/nodes/<name>', method='GET')
def del_node(name):
    if 'delete' in request.query:
        queue.delete_node(name)
        redirect('/nodes')

    return queue.get_node(name)


@route('/nodes', method='POST')
def add_node():
    """Adds a run into Marteau"""
    node_name = request.forms.get('name')
    if node_name is None:
        node_name = request.body.read()
        rest = True
    else:
        rest = False

    node = Node(name=node_name)
    queue.save_node(node)
    if not rest:
        return redirect('/nodes')

    return node_name



@route('/media/<filename:path>')
def media_dir(filename):
    return static_file(filename, root=MEDIADIR)


@route('/report/<jobid>/<filename:path>')
def report_dir(jobid, filename):
    path = os.path.join(reportsdir, jobid)
    return static_file(filename, root=path)


@route('/report/<jobid>')
def report_index(jobid):
    return redirect('/report/%s/index.html' % jobid)


@route('/docs/<filename:path>')
def doc_dir(filename):
    return static_file(filename, root=DOCDIR)


@route('/docs')
def doc_index():
    return redirect('/docs/index.html')


app = app()
