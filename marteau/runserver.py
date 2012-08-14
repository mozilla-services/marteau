import fcntl
import argparse
import sys
import logging
from ConfigParser import ConfigParser

from bottle import run

from marteau import __version__, logger
from marteau.server import app
from marteau.util import LOG_LEVELS, configure_logger


def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)


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
    #parser.add_argument('--server', help='web server to use',
    #                    default=SocketIOServer)
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
    app.config = config

    logger.info('Hammer ready. Where are the nails ?')
    try:
        run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Bye!')


if __name__ == '__main__':
    sys.exit(main())
