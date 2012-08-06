import json
from retools.queue import QueueManager, Worker


_QM = None


def get_result(job_id):
    return _QM.redis.lindex('retools:result:%s' % job_id, 0)


def get_failures():
    failures = list(_QM.get_jobs('failures'))
    return failures


def get_successes():
    return list(_QM.get_jobs('successes'))


def success(job=None, result=None):
    pl = job.redis.pipeline()
    result = json.dumps({'data': result})
    pl.lpush('retools:queue:successes', job.to_json())
    pl.lpush('retools:result:%s' % job.job_id, result)
    pl.expire('retools:result:%s', 3600)
    pl.execute()


def failure(job=None, exc=None):
    pl = job.redis.pipeline()
    exc = json.dumps({'data': str(exc)})
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


def enqueue(funcname, **kwargs):
    return _QM.enqueue(funcname, **kwargs)


def get_job(job_id):
    return _QM.get_job(job_id)


def get_jobs():
    return list(_QM.get_jobs())


def get_workers():
    return list(Worker.get_workers(redis=_QM.redis))
