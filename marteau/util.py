import fcntl
import socket
from email.mime.text import MIMEText
from email.header import Header
from rfc822 import AddressList
import logging
import smtplib

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
    root = options.get('root', DEFAULT_ROOT)
    sender = options.get('smtp.sender', DEFAULT_SENDER)
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
