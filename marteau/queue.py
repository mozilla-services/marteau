import signal
import time
import os
import json

from retools.queue import QueueManager, Worker, Job
from marteau.node import Node


class Queue(object):

    def __init__(self):
        self._qm = QueueManager()
        self._qm.subscriber('job_failure', handler='marteau.queue:failure')
        self._qm.subscriber('job_postrun', handler='marteau.queue:success')
        self._qm.subscriber('job_prerun', handler='marteau.queue:starting')
        self._conn = self._qm.redis

    def pid_to_jobid(self, pid):
        return self._conn.get('retools:jobpid:%s' % str(pid))

    def get_console(self, job_id):
        return self._conn.get('retools:jobconsole:%s' % job_id)

    def append_console(self, job_id, data):
        key = 'retools:jobconsole:%s' % job_id
        current = self._conn.get(key)
        if current is not None:
            data = current + data
        self._conn.set(key, data)

    def get_node(self, name):
        data = self._conn.get('retools:node:%s' % name)
        return Node(**json.loads(data))

    def delete_node(self, name):
        if not self._conn.sismember('retools:nodes', name):
            return
        self._conn.srem('retools:nodes', name)
        self._conn.delete('retools:node:%s' % name)

    def get_nodes(self, check_available=False):
        names = self._conn.smembers('retools:nodes')
        nodes = []

        for name in sorted(names):
            node = self._conn.get('retools:node:%s' % name)
            node = Node(**json.loads(node))
            if check_available and (node.status != 'idle' or not node.enabled):
                continue
            nodes.append(node)

        return nodes

    def reset_nodes(self):
        for node in self.get_nodes():
            node.status = 'idle'
            self.save_node(node)

    def save_node(self, node):
        names = self._conn.smembers('retools:nodes')
        if node.name not in names:
            self._conn.sadd('retools:nodes', node.name)
        self._conn.set('retools:node:%s' % node.name, node.to_json())

    def purge_console(self, job_id):
        key = 'retools:jobconsole:%s' % job_id
        try:
            return self._conn.get(key)
        finally:
            self._conn.delete(key)

    def get_result(self, job_id):
        res = self._conn.lindex('retools:result:%s' % job_id, 0)
        console = self.get_console(job_id)
        if res is None:
            return None, console
        return json.loads(res), console

    def sorter(self, field):
        def _sort_jobs(job1, job2):
            return -cmp(job1.metadata[field], job2.metadata[field])
        return _sort_jobs

    def get_failures(self):
        jobs = [self.get_job(job_id)
                for job_id in self._conn.smembers('retools:queue:failures')]
        jobs.sort(self.sorter('ended'))
        return jobs

    def get_successes(self):
        jobs = [self.get_job(job_id)
                for job_id in self._conn.smembers('retools:queue:successes')]
        jobs.sort(self.sorter('ended'))
        return jobs

    def delete_job(self, job_id):
        self._conn.delete('retools:started', job_id)
        self._conn.delete('retools:job:%s' % job_id)
        self._conn.delete('retools:jobpid:%s' % job_id)
        self._conn.delete('retools:jobconsole:%s' % job_id)
        if self._conn.sismember('retools:consoles', job_id):
            self._conn.srem('retools:consoles', job_id)
        self._conn.srem('retools:queue:failures', job_id)
        self._conn.srem('retools:queue:successes', job_id)

    def purge(self):
        for queue in self._conn.smembers('retools:queues'):
            self._conn.delete('retools:queue:%s' % queue)

        for job_id in self._conn.smembers('retools:queue:started'):
            self._conn.delete('retools:job:%s' % job_id)
            self._conn.delete('retools:jobpid:%s' % job_id)

        self._conn.delete('retools:queue:failures')
        self._conn.delete('retools:queue:successes')
        self._conn.delete('retools:queue:starting')

        for job_id in self._conn.smembers('retools:consoles'):
            self._conn.delete('retools:jobconsole:%s' % job_id)

        self._conn.delete('retools:consoles')
        self._conn.delete('retools:started')

        for node in self.get_nodes():
            node.status = 'idle'
            self.save_node(node)

    def cancel_job(self, job_id):

        # first, find out which worker is working on this
        for worker_id in self._conn.smembers('retools:workers'):
            status_key = "retools:worker:%s" % worker_id
            status = self._conn.get(status_key)
            if status is None:
                continue

            status = json.loads(status)
            job_payload = status['payload']
            if job_payload['job_id'] != job_id:
                continue

            # that's the worker !
            # get its pid and ask it to stop
            pid = int(worker_id.split(':')[1])
            os.kill(pid, signal.SIGUSR1)
            break
        # XXX we make the assumption all went well...

    def replay(self, job_id):
        job = self.get_job(job_id)
        data = job.to_dict()
        job_name = data['job']
        kwargs = data['kwargs']

        metadata = {'created': time.time(),
                    'repo': data['metadata']['repo']}

        kwargs['metadata'] = metadata
        self.enqueue(job_name, **kwargs)

    def enqueue(self, funcname, **kwargs):
        return self._qm.enqueue(funcname, **kwargs)

    def _get_job(self, job_id, queue_names, redis):
        for queue_name in queue_names:
            current_len = self._conn.llen(queue_name)

            # that's O(n), we should do better
            for i in range(current_len):
                # the list can change while doing this
                # so we need to catch any index error
                job = self._conn.lindex(queue_name, i)
                job_data = json.loads(job)

                if job_data['job_id'] == job_id:
                    return Job(queue_name, job, redis)
        raise IndexError(job_id)

    def get_job(self, job_id):
        try:
            return self._qm.get_job(job_id)
        except IndexError:
            job = self._conn.get('retools:job:%s' % job_id)
            if job is None:
                raise
            return Job(self._qm.default_queue_name, job, self._conn)

    def get_jobs(self):
        return list(self._qm.get_jobs())

    def get_running_jobs(self):
        return [self.get_job(job_id)
                for job_id in self._conn.smembers('retools:started')]

    def get_workers(self):
        ids = list(Worker.get_worker_ids(redis=self._conn))
        return [wid.split(':')[1] for wid in ids]

    def delete_pids(self, job_id):
        self._conn.delete('retools:%s:pids' % job_id)

    def add_pid(self, job_id, pid):
        self._conn.sadd('retools:%s:pids' % job_id, str(pid))

    def remove_pid(self, job_id, pid):
        self._conn.srem('retools:%s:pids' % job_id, str(pid))

    def get_pids(self, job_id):
        return [int(pid) for pid in
                self._conn.smembers('retools:%s:pids' % job_id)]

    def cleanup_job(self, job_id):
        for pid in self.get_pids(job_id):
            os.kill(pid, signal.SIGTERM)

        self.delete_pids(job_id)

    def get_key(self, user):
        return self._conn.get('retools:apikey:%s' % user)

    def set_key(self, user, key):
        return self._conn.set('retools:apikey:%s' % user, key)


#
# Events
#
def starting(job=None):
    os.environ['MARTEAU_JOBID'] = job.job_id
    job.metadata['started'] = time.time()
    job.redis.sadd('retools:started', job.job_id)
    job.redis.set('retools:job:%s' % job.job_id, job.to_json())
    job.redis.set('retools:jobpid:%s' % str(os.getpid()), job.job_id)


def success(job=None, result=None):
    pl = job.redis.pipeline()
    job.metadata['ended'] = time.time()
    save_job(job)
    result = json.dumps({'data': result, 'msg': 'Success'})
    pl.srem('retools:started', job.job_id)
    pl.delete('retools:jobpid:%s' % str(os.getpid()))
    pl.sadd('retools:queue:successes', job.job_id)
    pl.lpush('retools:result:%s' % job.job_id, result)
    pl.expire('retools:result:%s', 3600)
    pl.sadd('retools:consoles', job.job_id)
    nodes = os.environ.get('MARTEAU_NODES')
    if nodes is not None:
        nodes = nodes.split(',')
        for name in nodes:
            data = job.redis.get('retools:node:%s' % name)
            node = Node(**json.loads(data))
            node.status = 'idle'
            names = job.redis.smembers('retools:nodes')
            if node.name not in names:
                job.redis.sadd('retools:nodes', node.name)
            job.redis.set('retools:node:%s' % node.name, node.to_json())

    pl.execute()


def save_job(job):
    job.redis.set('retools:job:%s' % job.job_id, job.to_json())


def failure(job=None, exc=None):
    # depending on the failure we might requeue it with a
    # delay, using job.enqueue()
    pl = job.redis.pipeline()
    job.metadata['ended'] = time.time()
    save_job(job)
    dump = json.dumps({'msg': 'Error', 'data': str(exc)})
    console_key = 'retools:jobconsole:%s' % job.job_id
    current = job.redis.get(console_key)
    if current is not None:
        data = current + str(exc) + '\n'

    else:
        data = str(exc) + '\n'
    pl.set(console_key, data)
    pl.srem('retools:started', job.job_id)
    pl.delete('retools:jobpid:%s' % str(os.getpid()))
    pl.sadd('retools:queue:failures', job.job_id)
    pl.lpush('retools:result:%s' % job.job_id, dump)
    pl.sadd('retools:consoles', job.job_id)
    pl.expire('retools:result:%s', 3600)
    nodes = os.environ.get('MARTEAU_NODES')
    if nodes is not None:
        nodes = nodes.split(',')
        for name in nodes:
            data = job.redis.get('retools:node:%s' % name)
            node = Node(**json.loads(data))
            node.status = 'idle'
            names = job.redis.smembers('retools:nodes')
            if node.name not in names:
                job.redis.sadd('retools:nodes', node.name)
            job.redis.set('retools:node:%s' % node.name, node.to_json())

    if 'enough free nodes' in str(exc):
        job.enqueue()

    pl.execute()
