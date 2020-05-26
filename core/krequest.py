import requests
import time
import warnings

def retry_wrapper(max_retry_num=3,retry_delay=1,exception=True):
    def wrapper1(func):
        def wrapper2(*args,**kwargs):
            this_for_num  = max_retry_num-1 if exception else max_retry_num
            for i in range(this_for_num):
                try:
                    return func(*args,**kwargs)
                except Exception as e:
                    time.sleep(retry_delay)
            if exception: return func(*args,**kwargs)
            else: return None
        return wrapper2
    return wrapper1

def get_response(url,data=None,headers={},method='GET',proxies=False,params=None,timeout=5,max_retry_num=3,retry_delay=1,exception=True,**kwargs)->requests.get:
    if method == 'GET':
        this_func = requests.get
    elif method == 'POST':
        this_func = requests.post
    elif method == 'PUT':
        this_func = requests.put
    elif method == 'DELETE':
        this_func= requests.delete
    else:
        raise Exception('%s this method is not supported' % method)#~~~~


    @retry_wrapper(max_retry_num=max_retry_num,retry_delay=retry_delay,exception=exception)
    def send():
        if proxies:
            if type(proxies) == 'str':
                this_proxies = {'http':proxies,'https':proxies}
            else:
                this_proxies = proxies.get()
        else:
            this_proxies = None

        return this_func(url=url,data=data,headers=headers,proxies=this_proxies,params=params,timeout=timeout,**kwargs)
    return send()

import redis



class Settings():
    url = 'https://www.baidu.com'
    flush_deley_change = 2
    flush_delay_nochange = 1
    exception_delay = 1
    get_delay = 0.5
    split = ','
    charset = 'utf-8'

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
        self.flush_deley_change = ST.flush_deley_change
        self.flush_delay_nochange = ST.flush_delay_nochange
        self.exception_delay = ST.exception_delay
        self.split = ST.split
        self.charset = ST.charset
        self.get_delay = ST.get_delay

        self.__ips = []


    @thread_wrapper
    def __run(self):
        ips_last_set = {}
        while True:
            resp = get_response(url=self.url,exception=False)
            if not resp:
                warnings.warn('访问代理IP的url地址失败')
            try:
                ips = resp.content.decode('utf-8').split(self.split)
                if ips == ips_last_set:
                    ips_last_set = set(ips)
                    self.redis_conn.delete(self.key_name)
                    self.redis_conn.sadd(self.key_name,ips)
                    time.sleep(self.flush_deley_change)
                else:
                    time.sleep(self.flush_delay_nochange)
            except:
                warnings.warn('写入代理IP失败')
                time.sleep(self.exception_delay)


    def run(self):
        self.thread_run = Thread(target=self.__run)
        self.thread_run.start()

    def get(self):
        if self.__ips:
            return self.__ips.pop()
        while True:
            proxy_quantity = self.redis_conn.smembers(self.key_name)
            self.__ips = self.redis_conn.srandmember(self.key_name,proxy_quantity)
            if self.__ips:
                return self.__ips.pop()
            else:
                time.sleep(self.get_delay)


if __name__ == '__main__':
    p = ProxyPool()
    print(p.redis_conn.srandmember('123',2))








