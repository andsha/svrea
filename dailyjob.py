from rq import Queue
from worker import conn
from job import job

q = Queue(connection=conn,default_timeout=60)
q.enqueue(job, timeout=60)
