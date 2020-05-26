import time


def retry_wrapper(max_retry_num=3, retry_delay=1, exception=True):
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            this_for_num = max_retry_num - 1 if exception else max_retry_num
            for i in range(this_for_num):
                try:
                    return func(*args, **kwargs)
                except:
                    time.sleep(retry_delay)
            if exception:
                return func(*args, **kwargs)
            else:
                return None

        return wrapper2

    return wrapper1


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
        if res == 1: return True
        else: return False
    except:
        return None


def thread_wrapper(func):
    def wrapper(*args, **kwargs):
        thread_target = Thread(target=func,args=args,kwargs=kwargs)
        thread_target.start()
        return thread_target
    return wrapper


from multiprocessing import Process

def process_wrapper(func):
    def wrapper(*args,**kwargs):
        process_target = Process(target=func,args=args,kwargs=kwargs)
        process_target.start()
        return process_target
    return wrapper
