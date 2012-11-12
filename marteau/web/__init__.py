from marteau import queue

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid_beaker import session_factory_from_settings
from redis import Redis


def attach_redis_to_request(event):
    """Attach the redis object to the request, so that it's available under
    request.redis.
    """
    redis = event.request.registry['redis']
    setattr(event.request, 'redis', redis)


def main(global_config={}, **settings):
    # defaults
    if 'mako.directories' not in settings:
        settings['mako.directories'] = 'marteau:templates'

    session_factory = session_factory_from_settings(settings)

    # creating the config and the queue
    config = Configurator(settings=settings, session_factory=session_factory)
    redis = Redis()

    config.registry['redis'] = redis
    config.registry['queue'] = queue.Queue(redis=redis)

    # routing
    config.add_route('index', '/')
    config.add_route('sign', '/sign')
    config.add_route('logout', '/logout')
    config.add_route('purge', '/purge')
    config.add_route('reset', '/reset')
    config.add_route('test', '/test')
    config.add_route('cancel', '/test/{jobid}/cancel')
    config.add_route('delete', '/test/{jobid}/delete')
    config.add_route('replay', '/test/{jobid}/replay')
    config.add_route('job', '/test/{jobid}')
    config.add_route('nodes', '/nodes')
    config.add_route('node_enable', '/nodes/{name}/enable')
    config.add_route('node_test', '/nodes/{name}/test')
    config.add_route('node', '/nodes/{name}')
    config.add_route('report_index', '/report/{jobid}')
    config.add_route('report_file', '/report/{jobid}/{filename:.*}')
    config.add_route('docs_file', '/docs/{file:.*}')
    config.add_route('docs_index', '/docs')

    config.add_static_view('media', 'marteau:media/')
    config.add_route('karaoke', '/media/marteau.kar')

    config.scan("marteau.web.views")

    # plug-in the web-service.
    config.include("cornice")
    config.scan("marteau.web.api")

    # we want to attach redis to each new request
    config.add_subscriber(attach_redis_to_request, NewRequest)
    return config.make_wsgi_app()
