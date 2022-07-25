from datetime import datetime
from django.conf import settings
import redis
import json
import dotenv
from pathlib import Path  # Python 3.6+ only
import os
import django_rq

# global
worker_list = {
    'worker_0': None,
    'worker_1': None,
    'worker_2': None,
    'worker_3': None,
    'worker_4': None,
    'worker_5': None,
    'worker_6': None,
    'worker_7': None,
    'worker_8': None,
    'worker_9': None,
    'worker_10': None,
    'worker_11': None,
    'worker_12': None,
    'worker_13': None,
    'worker_14': None,
}

if not settings.TESTING:
    dotenv.read_dotenv(settings.ROOT_DIR)

modulo = int(os.getenv("MODULO"))

def queue_waiting_response(qid,kind):
    r = redis.StrictRedis(host=settings.RQ_QUEUES[kind]['HOST'], port=6379)  
    p = r.pubsub()
    datetime_second = datetime.now().second
    datetime_timeout = 10 
    msg = {}

    p.subscribe('on_message')
    PAUSE = True
    while PAUSE:
        message = p.get_message()
        if message:
            if  message['type'] == 'message':
                d = json.loads(message['data'])
                if int(d['qid']) == int(qid):
                    PAUSE = False
                    msg['data'] = d
                    msg['error'] = ''
        if (datetime.now().second - datetime_second) > datetime_timeout:
            PAUSE = False
            msg['error'] = 'error request timeout'
    close_redis_connection(r)
    return msg

def getQueue(member_id):
    queue_index = member_id % modulo
    queue_list = list(settings.RQ_QUEUES)[queue_index]

    queue = worker_list.get(queue_list)

    if queue is None:
        import sys
        print('Get queue {}'.format(queue_list),file=sys.stderr)
        queue = django_rq.get_queue(queue_list, autocommit=True, is_async=True, default_timeout=360)
        worker_list[queue_list] = queue
    
    return queue

def close_redis_connection(r):
    r.close()
    # time.sleep(5)