from marteau import queue
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings


def main(global_config, **settings):
    settings['mako.directories'] = 'marteau:templates'
    settings['pyramid.includes'] = ['pyramid_beaker']
    settings['session.type'] = 'file'
    settings['session.data_dir'] = '%(here)s/data/sessions/data'
    settings['session.lock_dir'] = '%(here)s/data/sessions/lock'
    settings['session.key'] = 'wqdIinsjb867'
    settings['session.secret'] = 'qwiqbUYbubsuygsUVvu'
    settings['session.cookie_on_exception'] = True
    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings, session_factory=session_factory)
    config.registry['queue'] = queue.Queue()

    config.add_route('index', '/')
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

    config.scan("marteau.web.views")
    return config.make_wsgi_app()
