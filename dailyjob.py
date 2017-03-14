from rq import Queue
from worker import conn
from job import job

q = Queue(connection=conn)
q.enqueue(job, timeout=7200)