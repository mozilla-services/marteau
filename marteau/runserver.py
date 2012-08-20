import argparse
import sys
from ConfigParser import ConfigParser
from wsgiref.simple_server import make_server

from marteau import __version__, logger, queue
from marteau.web import main as webapp
from marteau.util import LOG_LEVELS, configure_logger


def main():
    parser = argparse.ArgumentParser(description='Funkload Server')
    parser.add_argument('--config', help='Config file, if any')
    parser.add_argument('--version', action='store_true',
                     default=False, help='Displays Marteau version and exits.')
    parser.add_argument('--log-level', dest='loglevel', default='info',
            choices=LOG_LEVELS.keys() + [key.upper() for key in
                LOG_LEVELS.keys()],
            help="log level")
    parser.add_argument('--log-output', dest='logoutput', default='-',
            help="log output")
    parser.add_argument('--host', help='Host', default='0.0.0.0')
    parser.add_argument('--port', help='port', default=8080)
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    # configure the logger
    configure_logger(logger, args.loglevel, args.logoutput)

    # loading the config file
    config = ConfigParser()
    if args.config is not None:
        logger.info('Loading %r' % args.config)
        config.read([args.config])


    # loading the app & the queue
    global_config = {}
    if config.has_section('marteau'):
        settings = dict(config.items('marteau'))
    else:
        settings = {}
    app = webapp(global_config, **settings)


    logger.info('Hammer ready. Where are the nails ?')
    try:
        httpd = make_server(args.host, args.port, app)
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Bye!')


if __name__ == '__main__':
    sys.exit(main())
