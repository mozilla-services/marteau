import signal
import time
import os
import json

from retools.queue import QueueManager, Worker, Job
from marteau.node import Node


_QM = None


def pid_to_jobid(pid):
    return _QM.redis.get('retools:jobpid:%s' % str(pid))


def get_console(job_id):
    return _QM.redis.get('retools:jobconsole:%s' % job_id)


def append_console(job_id, data):
    key = 'retools:jobconsole:%s' % job_id
    current = _QM.redis.get(key)
    if current is not None:
        data = current + data
    _QM.redis.set(key, data)


def get_node(name):
    data = _QM.redis.get('retools:node:%s' % name)
    return Node(**json.loads(data))


def delete_node(name):
    if not _QM.redis.sismember('retools:nodes', name):
        return
    _QM.redis.srem('retools:nodes', name)
    _QM.redis.delete('retools:node:%s' % name)


def get_nodes():
    names = _QM.redis.smembers('retools:nodes')
    for name in sorted(names):
        node = _QM.redis.get('retools:node:%s' % name)
        yield Node(**json.loads(node))


def save_job(job):
    job.redis.set('retools:job:%s' % job.job_id, job.to_json())


def save_node(node):
    names = _QM.redis.smembers('retools:nodes')
    if node.name not in names:
        _QM.redis.sadd('retools:nodes', node.name)
    _QM.redis.set('retools:node:%s' % node.name, node.to_json())


def purge_console(job_id):
    key = 'retools:jobconsole:%s' % job_id
    try:
        return _QM.redis.get(key)
    finally:
        _QM.redis.delete(key)


def get_result(job_id):
    res = _QM.redis.lindex('retools:result:%s' % job_id, 0)
    console = get_console(job_id)
    if res is None:
        return None, console
    return json.loads(res), console


def sorter(field):
    def _sort_jobs(job1, job2):
        return -cmp(job1.metadata[field], job2.metadata[field])
    return _sort_jobs


def get_failures():
    jobs = [get_job(job_id)
            for job_id in _QM.redis.smembers('retools:queue:failures')]
    jobs.sort(sorter('ended'))
    return jobs


def get_successes():
    jobs = [get_job(job_id)
            for job_id in _QM.redis.smembers('retools:queue:successes')]
    jobs.sort(sorter('ended'))
    return jobs


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
    #pl.delete('retools:job:%s' % job.job_id)
    pl.delete('retools:jobpid:%s' % str(os.getpid()))
    pl.sadd('retools:queue:successes', job.job_id)
    pl.lpush('retools:result:%s' % job.job_id, result)
    pl.expire('retools:result:%s', 3600)
    pl.sadd('retools:consoles', job.job_id)
    nodes = os.environ.get('MARTEAU_NODES')
    if nodes is not None:
        nodes = nodes.split(',')
        for name in nodes:
            node = get_node(name)
            node.status = 'idle'
            save_node(node)

    pl.execute()


def failure(job=None, exc=None):
    # depending on the failure we might requeue it with a
    # delay, using job.enqueue()
    # XXX
    pl = job.redis.pipeline()
    job.metadata['ended'] = time.time()
    save_job(job)
    exc = json.dumps({'msg': 'Error', 'data': str(exc)})
    pl.srem('retools:started', job.job_id)
    #pl.delete('retools:job:%s' % job.job_id)
    pl.delete('retools:jobpid:%s' % str(os.getpid()))
    pl.sadd('retools:queue:failures', job.job_id)
    pl.lpush('retools:result:%s' % job.job_id, exc)
    pl.sadd('retools:consoles', job.job_id)
    pl.expire('retools:result:%s', 3600)
    nodes = os.environ.get('MARTEAU_NODES')
    if nodes is not None:
        nodes = nodes.split(',')
        for name in nodes:
            node = get_node(name)
            node.status = 'idle'
            save_node(node)
    pl.execute()


def delete_job(job_id):
    _QM.redis.delete('retools:started', job_id)
    _QM.redis.delete('retools:job:%s' % job_id)
    _QM.redis.delete('retools:jobpid:%s' % job_id)
    _QM.redis.delete('retools:jobconsole:%s' % job_id)
    if _QM.redis.sismember('retools:consoles', job_id):
        _QM.redis.srem('retools:consoles', job_id)
    _QM.redis.srem('retools:queue:failures', job_id)
    _QM.redis.srem('retools:queue:successes', job_id)


def purge():
    for queue in _QM.redis.smembers('retools:queues'):
        _QM.redis.delete('retools:queue:%s' % queue)

    for job_id in _QM.redis.smembers('retools:queue:started'):
        _QM.redis.delete('retools:job:%s' % job_id)
        _QM.redis.delete('retools:jobpid:%s' % job_id)

    _QM.redis.delete('retools:queue:failures')
    _QM.redis.delete('retools:queue:successes')
    _QM.redis.delete('retools:queue:starting')

    for job_id in _QM.redis.smembers('retools:consoles'):
        _QM.redis.delete('retools:jobconsole:%s' % job_id)

    _QM.redis.delete('retools:consoles')
    _QM.redis.delete('retools:started')

    for node in get_nodes():
        node.status = 'idle'
        save_node(node)


def initialize():
    global _QM
    if _QM is not None:
        return
    _QM = QueueManager()
    _QM.subscriber('job_failure', handler='marteau.queue:failure')
    _QM.subscriber('job_postrun', handler='marteau.queue:success')
    _QM.subscriber('job_prerun', handler='marteau.queue:starting')


# XXX should be in the app init
initialize()


def cancel_job(job_id):
    redis = _QM.redis

    # first, find out which worker is working on this
    for worker_id in redis.smembers('retools:workers'):
        status_key = "retools:worker:%s" % worker_id
        status = redis.get(status_key)

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


def replay(job_id):
    job = get_job(job_id)
    data = job.to_dict()
    job_name = data['job']
    kwargs = data['kwargs']

    metadata = {'created': time.time(),
                'repo': data['metadata']['repo']}

    kwargs['metadata'] = metadata
    enqueue(job_name, **kwargs)


def enqueue(funcname, **kwargs):
    return _QM.enqueue(funcname, **kwargs)


def _get_job(job_id, queue_names, redis):
    for queue_name in queue_names:
        current_len = redis.llen(queue_name)

        # that's O(n), we should do better
        for i in range(current_len):
            # the list can change while doing this
            # so we need to catch any index error
            job = redis.lindex(queue_name, i)
            job_data = json.loads(job)

            if job_data['job_id'] == job_id:
                return Job(queue_name, job, redis)

    raise IndexError(job_id)


def get_job(job_id):
    try:
        return _QM.get_job(job_id)
    except IndexError:
        job = _QM.redis.get('retools:job:%s' % job_id)
        if job is None:
            raise
        return Job(_QM.default_queue_name, job, _QM.redis)


def get_jobs():
    return list(_QM.get_jobs())


def get_running_jobs():
    return [get_job(job_id)
            for job_id in _QM.redis.smembers('retools:started')]


def get_workers():
    ids = list(Worker.get_worker_ids(redis=_QM.redis))
    return [wid.split(':')[1] for wid in ids]


def delete_pids(job_id):
    _QM.redis.delete('retools:%s:pids' % job_id)


def add_pid(job_id, pid):
    _QM.redis.sadd('retools:%s:pids' % job_id, str(pid))


def remove_pid(job_id, pid):
    _QM.redis.srem('retools:%s:pids' % job_id, str(pid))


def get_pids(job_id):
    return [int(pid) for pid in _QM.redis.smembers('retools:%s:pids' % job_id)]
