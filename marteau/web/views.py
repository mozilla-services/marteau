import socket
import urllib
import os
import time
import datetime
from ConfigParser import NoSectionError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import FileResponse
from pyramid_simpleform import Form
#from pyramid_simpleform.renderers import FormRenderer

from mako.lookup import TemplateLookup
import paramiko

from marteau.job import reportsdir
from marteau.node import Node
from marteau.web.schemas import JobSchema
import marteau


TOPDIR = os.path.dirname(marteau.__file__)
MEDIADIR = os.path.join(TOPDIR, 'media')
TMPLDIR = os.path.join(TOPDIR, 'templates')
TMPLS = TemplateLookup(directories=[TMPLDIR])
JOBTIMEOUT = 3600    # one hour
DOCDIR = os.path.join(TOPDIR, 'docs', 'build', 'html')


def time2str(data):
    if data is None:
        return 'Unknown date'
    return datetime.datetime.fromtimestamp(data).strftime('%Y-%m-%d %H:%M:%S')


@view_config(route_name='index', request_method='GET', renderer='index.mako')
def index(request):
    queue = request.registry['queue']

    return {'jobs': queue.get_jobs(),
            'workers': queue.get_workers(),
            'nodes': list(queue.get_nodes()),
            'failures': queue.get_failures(),
            'successes': queue.get_successes(),
            'get_result': queue.get_result,
            'running': queue.get_running_jobs(),
            'time2str': time2str}


@view_config(route_name='purge', request_method='GET')
def purge(request):
    """Adds a run into Marteau"""
    request.registry['queue'].purge()
    return 'purged'


@view_config(route_name='reset', request_method='GET')
def reset_nodes(request):
    """Adds a run into Marteau"""
    request.registry['queue'].reset_nodes()
    return 'reset'


@view_config(route_name='test', request_method='GET')
def get_all_jobs(request):
    """Adds a run into Marteau"""
    return request.registry['queue'].get_jobs()


@view_config(route_name='test', request_method='POST')
def add_run(request):
    """Adds a run into Marteau"""
    form = Form(request, schema=JobSchema)

    if not form.validate():
        #rendered = FormRenderer(form)
        items = form.errors.items()
        # should use a session here
        msg = '%s for %s' % (items[0][1], items[0][0])
        # render the index with the errors.
        #
        return HTTPFound('/?msg=%s' % msg)

    data = form.data
    repo = data.get('repo')
    redirect_url = data.get('redirect_url')
    cycles = data.get('cycles')
    duration = data.get('duration')
    nodes = data.get('nodes')
    email = data.get('email')

    metadata = {'created': time.time(),
                'repo': repo}

    queue = request.registry['queue']

    try:
        options = request.registry.settings
    except NoSectionError:
        options = {}

    job_id = queue.enqueue('marteau.job:run_loadtest', repo=repo,
                           cycles=cycles, nodes_count=nodes, duration=duration,
                           metadata=metadata, email=email,
                           options=options)

    if redirect_url is not None:
        return HTTPFound(location=redirect_url)

    return job_id


@view_config(route_name='cancel', request_method='GET')
def _cancel_job(request):
    jobid = request.matchdict['jobid']
    queue = request.registry['queue']
    queue.cancel_job(jobid)
    queue.cleanup_job(jobid)
    return HTTPFound(location='/')


@view_config(route_name='delete', request_method='GET')
def _delete_job(request):
    jobid = request.matchdict['jobid']
    queue = request.registry['queue']
    queue.delete_job(jobid)
    return HTTPFound(location='/')


@view_config(route_name='replay', request_method='GET')
def _requeue_job(request):
    jobid = request.matchdict['jobid']
    queue = request.registry['queue']
    queue.replay(jobid)
    return HTTPFound(location='/')


@view_config(route_name='job', request_method='GET', renderer='console.mako')
def _get_result(request):
    """Gets results from a run"""
    jobid = request.matchdict['jobid']
    queue = request.registry['queue']
    status, console = queue.get_result(jobid)
    if status is None:
        status = 'Running'
    else:
        status = status['msg']

    return {'status': status,
            'console': console,
            'job': queue.get_job(jobid),
            'time2str': time2str}


@view_config(route_name='nodes', request_method='GET',
             renderer='nodes.mako')
def _nodes(request):
    queue = request.registry['queue']
    return {'nodes': list(queue.get_nodes())}


@view_config(route_name='node_enable', request_method='GET')
def enable_node(request):
    # load existing
    queue = request.registry['queue']
    name = request.matchdict['node']
    node = queue.get_node(name)

    # update the flag
    node.enabled = not node.enabled

    queue.save_node(node)
    return HTTPFound(location='/nodes')


@view_config(route_name='node_test', request_method='GET')
def test_node(request):
    # trying an ssh connection
    connection = paramiko.client.SSHClient()
    connection.load_system_host_keys()
    connection.set_missing_host_key_policy(paramiko.WarningPolicy())
    name = request.matchdict['node']

    host, port = urllib.splitport(name)
    if port is None:
        port = 22

    username, host = urllib.splituser(host)
    credentials = {}

    if username is not None and ':' in username:
        username, password = username.split(':', 1)
        credentials = {"username": username, "password": password}
    elif username is not None:
        password = None
        credentials = {"username": username}

    try:
        connection.connect(host, port=port, timeout=5, **credentials)
        return 'Connection to %r : OK' % name
    except (socket.gaierror, socket.timeout), error:
        return str(error)


@view_config(route_name='node', request_method='GET')
def get_or_del_node(request):
    name = request.matchdict['name']
    queue = request.registry['queue']

    if 'delete' in request.query:
        queue.delete_node(name)
        return HTTPFound(location='/nodes')

    return queue.get_node(name)


@view_config(route_name='nodes', request_method='POST')
def add_node(request):
    """Adds a run into Marteau"""
    # xxx
    node_name = request.forms.get('name')
    if node_name is None:
        node_name = request.body.read()
        rest = True
    else:
        rest = False

    node = Node(name=node_name)
    queue = request.registry['queue']
    queue.save_node(node)

    if not rest:
        return HTTPFound(location='/nodes')

    return node_name


#@view_config('/media/<filename:path>')
#def media_dir(filename):
#    if filename == 'marteau.kar':
#        kw = {'mimetype': 'audio/midi'}
#    else:
##        kw = {}
#    return static_file(filename, root=MEDIADIR, **kw)


@view_config(route_name='report_file')
def report_dir(request):
    jobid = request.matchdict['jobid']
    filename = request.matchdict['filename']
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    path = os.path.join(reportsdir, jobid, filename)
    return FileResponse(path, request)


@view_config(route_name='report_index')
def report_index(request):
    jobid = request.matchdict['jobid']
    return HTTPFound(location='/report/%s/index.html' % jobid)


@view_config(route_name='docs_index')
def doc_index(request):
    return HTTPFound('/docs/index.html')


@view_config(route_name='docs_file')
def doc_dir(request):
    filename = request.matchdict['file']
    elmts = filename.split(os.sep)
    for unsecure in ('.', '..'):
        if unsecure in elmts:
            return HTTPNotFound()

    path = os.path.join(DOCDIR, filename)
    return FileResponse(path, request)
