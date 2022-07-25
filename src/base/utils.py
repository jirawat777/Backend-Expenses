# IMPORT
import os
import redis
import json

redis_host = os.getenv("REDIS_PUBSUB_OPERATOR_HOST")
redis_port = os.getenv("REDIS_PUBSUB_OPERATOR_PORT")
r = redis.StrictRedis(host=redis_host, port=redis_port)
# UTILITY
def publicMsg(group,key,data):
    # PUBLIC
    r.publish(key,json.dumps(data))
    #r.close()
    
# def FCM ():
    # 