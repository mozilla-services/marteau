# taken from circus
import fcntl
import errno
import os
import sys

from gevent import select as gselect
import gevent


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


class Redirector(object):
    def __init__(self, redirect, refresh_time=0.3, extra_info=None,
                 buffer=8096):
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
        self.running = False

    def add_redirection(self, name, process, pipe):
        npipe = NamedPipe(pipe, process, name)
        self.pipes.append(npipe)
        self._names[process.pid, name] = npipe

    def remove_redirection(self, name, process):
        key = process.pid, name
        if key not in self._names:
            return
        pipe = self._names[key]
        self.pipes.remove(pipe)
        del self._names[key]

    def dump(self, pipe, data):
        datamap = {'data': data, 'pid': pipe.process.pid,
                   'name': pipe.name}
        datamap.update(self.extra_info)
        self.redirect(datamap)

    def _select(self):
        if len(self.pipes) == 0:
            gevent.sleep(.1)
            return
        try:
            rlist = gselect.select(self.pipes, [], [], timeout=1.0)[0]

            while rlist != []:
                for pipe in rlist:
                    data = os.read(pipe.fileno(), self.buffer)
                    if data:
                        self.dump(pipe, data)

                rlist = gselect.select(self.pipes, [], [], timeout=1.0)[0]

        except IOError, ex:
            if ex[0] != errno.EAGAIN:
                raise
            sys.exc_clear()

        gevent.sleep(self.refresh_time)

    def start(self):
        self.running = True
        gevent.spawn(self.run)

    def run(self):
        while self.running:
            self._select()

    def kill(self):
        if not self.running:
            return
        self.running = False
