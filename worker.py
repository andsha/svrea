import os

import redis
from rq import Worker, Queue, Connection

from manage import DEFAULT_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)

#*****************************  USE WHEN RUN LOCAL  ******************************
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(BASE_DIR + '/svrea/.env'):
    f = open(BASE_DIR + '/svrea/.env', 'r')
    DATABASE_URL = f.readline().split('=')[1].strip().strip("'")
    os.environ.setdefault("DATABASE_URL", DATABASE_URL)

#**********************************************************************************

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    import django
    django.setup()
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()