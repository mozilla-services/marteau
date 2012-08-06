import fcntl
import argparse
import sys
import logging

from bottle import run

from marteau import __version__, logger
from marteau.server import app


LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG}

LOG_FMT = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
LOG_DATE_FMT = r"%Y-%m-%d %H:%M:%S"


def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)


def configure_logger(logger, level='INFO', output="-"):
    loglevel = LOG_LEVELS.get(level.lower(), logging.INFO)
    logger.setLevel(loglevel)
    if output == "-":
        h = logging.StreamHandler()
    else:
        h = logging.FileHandler(output)
        close_on_exec(h.stream.fileno())
    fmt = logging.Formatter(LOG_FMT, LOG_DATE_FMT)
    h.setFormatter(fmt)
    logger.addHandler(h)


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

    logger.info('Hammer ready. Where are the nails ?')
    try:
        run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Bye!')


if __name__ == '__main__':
    sys.exit(main())
