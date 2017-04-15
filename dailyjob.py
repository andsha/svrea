from rq import Queue
from worker import conn
from job import job

from svrea_script.views import workertimeout

q = Queue(connection=conn)
q.enqueue(func=job, timeout=workertimeout)

