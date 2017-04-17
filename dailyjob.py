from rq import Queue
from worker import conn
from job import job

from globalvars import workertimeout

q = Queue(connection=conn)
q.enqueue(job, timeout=workertimeout)

