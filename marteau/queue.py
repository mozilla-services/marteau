import json
from retools.queue import QueueManager, Worker, Job


_QM = None


def get_result(job_id):
    return json.loads(_QM.redis.lindex('retools:result:%s' % job_id, 0))


def get_failures():
    failures = list(_QM.get_jobs('failures'))
    return failures


def get_successes():
    return list(_QM.get_jobs('successes'))


def starting(job=None):
    job.redis.sadd('retools:started', job.job_id)
    job.redis.set('retools:job:%s' % job.job_id, job.to_json())


def success(job=None, result=None):
    pl = job.redis.pipeline()
    result = json.dumps({'data': result})
    pl.srem('retools:started', job.job_id)
    pl.delete('retools:job:%s' % job.job_id)
    pl.lpush('retools:queue:successes', job.to_json())
    pl.lpush('retools:result:%s' % job.job_id, result)
    pl.expire('retools:result:%s', 3600)
    pl.execute()


def failure(job=None, exc=None):
    pl = job.redis.pipeline()
    exc = json.dumps({'data': str(exc)})
    pl.srem('retools:started', job.job_id)
    pl.delete('retools:job:%s' % job.job_id)
    pl.lpush('retools:queue:failures', job.to_json())
    pl.lpush('retools:result:%s' % job.job_id, exc)
    pl.expire('retools:result:%s', 3600)
    pl.execute()


def initialize():
    global _QM
    if _QM is not None:
        return
    _QM = QueueManager()
    _QM.subscriber('job_failure', handler='marteau.queue:failure')
    _QM.subscriber('job_postrun', handler='marteau.queue:success')
    _QM.subscriber('job_prerun', handler='marteau.queue:starting')


def enqueue(funcname, **kwargs):
    return _QM.enqueue(funcname, **kwargs)


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
    return list(Worker.get_workers(redis=_QM.redis))
