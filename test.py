from rq import Queue
from redis import Redis
import redis

import time
#from script.svrea_script import testfunc

from test1 import testfunc

#redis_conn = Redis(port=6379)
#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis_conn = redis.from_url('redis://localhost:6379')
q = Queue(connection = redis_conn)

res = q.enqueue(testfunc)

print (res.result)

time.sleep(5)

print(res.result)



