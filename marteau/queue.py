from rq import Queue, use_connection
from rq.job import Job

use_connection()
queue = Queue()

def get_job(job_id):
    return Job.fetch(job_id, queue.connection)
