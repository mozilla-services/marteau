import os
import json
import hashlib
import urllib
from base64 import urlsafe_b64decode as b64decode
import urllib2
import fcntl
import socket
from email.mime.text import MIMEText
from email.header import Header
from rfc822 import AddressList
import logging
import smtplib
import sys

import tokenlib
from circus import logger

DEFAULT_ROOT = 'http://localhost'
DEFAULT_SENDER = 'tarek@localhost'
DEFAULT_SMTP_HOST = 'localhost'
DEFAULT_SMTP_PORT = 25

TMPL = u"""\
Dear Marteau user.

We nailed it again, find the load test report at %s

Yours,

--
Marteau
"""


def send_report(rcpt, jobid=None, **options):
    subject = 'Your Marteau report'
    root = options.get('report.root', DEFAULT_ROOT)
    sender = options.get('report.sender', DEFAULT_SENDER)
    smtp_host = options.get('smtp.host', DEFAULT_SMTP_HOST)
    smtp_port = int(options.get('smtp.port', DEFAULT_SMTP_PORT))
    smtp_user = options.get('smtp.user')
    smtp_password = options.get('smtp.password')

    # preparing the message
    if jobid is None:
        url = root
    else:
        url = '%s/test/%s' % (root, jobid)

    body = TMPL % url

    msg = MIMEText(body.encode('utf-8'), 'plain', 'utf8')

    def _normalize_realname(field):
        address = AddressList(field).addresslist
        if len(address) == 1:
            realname, email = address[0]
            if realname != '':
                return '%s <%s>' % (str(Header(realname, 'utf-8')), str(email))
        return field

    msg['From'] = _normalize_realname(sender)
    msg['To'] = _normalize_realname(rcpt)
    msg['Subject'] = Header(subject, 'utf-8')

    logger.debug('Connecting to %s:%d' % (smtp_host, smtp_port))
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=5)
    except (smtplib.SMTPConnectError, socket.error), e:
        return False, str(e)

    # auth
    if smtp_user is not None and smtp_password is not None:
        logger.debug('Login with %r' % smtp_user)
        try:
            server.login(smtp_user, smtp_password)
        except (smtplib.SMTPHeloError,
                smtplib.SMTPAuthenticationError,
                smtplib.SMTPException), e:
            return False, str(e)

    # the actual sending
    logger.debug('Sending the mail')
    try:
        server.sendmail(sender, [rcpt], msg.as_string())
    finally:
        server.quit()

    return True, None


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


def send_form(url, params):
    params = urllib.urlencode(params)
    request = urllib2.Request(url, params)
    res = urllib2.urlopen(request).read()
    return res


def generate_key():
    return os.urandom(32).encode('hex')


def decode_mac_id(request, tokenid):
    queue = request.registry['queue']

    # extracting the user
    try:
        decoded_token = b64decode(tokenid)
    except TypeError, e:
        raise ValueError(str(e))
    payload = decoded_token[:-hashlib.sha1().digest_size]
    data = json.loads(payload)
    user = data['user']

    # getting the associated secret
    secret = queue.get_key(user)

    # now we can parse the token and make sure we're good
    tsecret = tokenlib.get_token_secret(tokenid, secret=secret)
    data = tokenlib.parse_token(tokenid, secret=secret)
    return user, tsecret


class ImportStringError(ImportError):
    """Provides information about a failed :func:`import_string` attempt."""

    #: String in dotted notation that failed to be imported.
    import_name = None
    #: Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception

        msg = (
            'import_string() failed for %r. Possible reasons are:\n\n'
            '- missing __init__.py in a package;\n'
            '- package or module path not included in sys.path;\n'
            '- duplicated package or module name taking precedence in '
            'sys.path;\n'
            '- missing module, class, function or variable;\n\n'
            'Debugged import:\n\n%s\n\n'
            'Original exception:\n\n%s: %s')

        name = ''
        tracked = []
        for part in import_name.replace(':', '.').split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, '__file__', None)))
            else:
                track = ['- %r found in %r.' % (n, i) for n, i in tracked]
                track.append('- %r not found.' % name)
                msg = msg % (import_name, '\n'.join(track),
                             exception.__class__.__name__, str(exception))
                break

        ImportError.__init__(self, msg)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.import_name,
                                 self.exception)


def import_string(import_name, silent=False):
    """Imports an object based on a string. This is useful if you want to
    use import paths as endpoints or something similar. An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    For better debugging we recommend the new :func:`import_module`
    function to be used instead.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
    `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    if isinstance(import_name, unicode):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
            # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError, e:
        if not silent:
            raise ImportStringError(import_name, e), None, sys.exc_info()[2]
