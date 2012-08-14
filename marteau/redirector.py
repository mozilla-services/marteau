# taken from circus
import fcntl
import errno
import os
import sys
import time
from threading import Thread
import select

from iowait import IOWait
try:
    from gevent import select
    GEVENT = True
except ImportError:
    GEVENT = False


class NamedPipe(object):
    def __init__(self, pipe, process, name):
        self.pipe = pipe
        self.process = process
        self.name = name
        self._fileno = pipe.fileno()
        fl = fcntl.fcntl(pipe, fcntl.F_GETFL)
        fcntl.fcntl(pipe, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def fileno(self):
        return self._fileno

    def read(self, buffer):
        if self.pipe.closed:
            return
        return self.pipe.read(buffer)


class BaseRedirector(object):
    def __init__(self, redirect, refresh_time=0.3, extra_info=None,
                 buffer=1024):
        self.pipes = []
        self._names = {}
        self.redirect = redirect
        self.extra_info = extra_info
        self.buffer = buffer
        self.running = False
        if extra_info is None:
            extra_info = {}
        self.extra_info = extra_info
        self.refresh_time = refresh_time
        if GEVENT:
            self.selector = select
        else:
            self.selector = IOWait()

    def add_redirection(self, name, process, pipe):
        npipe = NamedPipe(pipe, process, name)
        self.pipes.append(npipe)
        if not GEVENT:
            self.selector.watch(npipe, read=True)
        self._names[process.pid, name] = npipe

    def remove_redirection(self, name, process):
        key = process.pid, name
        if key not in self._names:
            return
        pipe = self._names[key]
        self.pipes.remove(pipe)
        if not GEVENT:
            self.selector.unwatch(pipe)
        del self._names[key]

    def _select(self):
        if len(self.pipes) == 0:
            time.sleep(.1)
            return
        try:
            try:
                if not GEVENT:
                    rlist = self.selector.wait(timeout=1.0)
                else:
                    rlist, __, __ = self.selector(self.pipes, [], [], 1.0)

            except select.error:     # need a non specific error
                return

            for elmt in rlist:
                if not GEVENT:
                    pipe, __, __ = elmt
                else:
                    pipe = elmt

                data = pipe.read(self.buffer)
                if data:
                    datamap = {'data': data, 'pid': pipe.process.pid,
                               'name': pipe.name}
                    datamap.update(self.extra_info)
                    self.redirect(datamap)
        except IOError, ex:
            if ex[0] != errno.EAGAIN:
                raise
            sys.exc_clear()


class Redirector(BaseRedirector, Thread):
    def __init__(self, redirect, refresh_time=0.3, extra_info=None,
            buffer=1024):
        Thread.__init__(self)
        BaseRedirector.__init__(self, redirect, refresh_time=refresh_time,
                extra_info=extra_info, buffer=buffer)
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self._select()
            time.sleep(self.refresh_time)

    def kill(self):
        if not self.running:
            return
        self.running = False
        try:
            self.join()
        except KeyboardInterrupt:
            pass
