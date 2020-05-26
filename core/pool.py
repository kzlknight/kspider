import redis
from threading import Thread
import inspect
import ctypes

def stop_thread(thread):
    try:
        exctype = SystemExit
        tid = ctypes.c_long(thread.ident)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res ==1:
            return True
        else:return False
    except:
        return None


def thread_wrapper(func):
    def wrapper1(*args,**kwargs):
        func(*args,**kwargs).start()
    return wrapper1


class Settings():
    url = 'https://www.baidu.com'
    flush_deley = 2
    split = ','

    class Redis():
        redis = True
        conn = dict(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            encoding='utf-8',
            decode_responses=True
        )
        key_name = 'proxy'




class ProxyPool():

    def __init__(
            self,ST=Settings
    ):
        self.redis_conn = redis.StrictRedis(**ST.Redis.conn)
        self.key_name = ST.Redis.key_name
        self.url = ST.url
        self.flush_delay = ST.flush_deley
        self.split = ST.split


    def __run(self):
        pass

    def run(self):
        self.thread_run = Thread(target=self.__run)
        self.thread_run.start()







