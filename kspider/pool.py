from kspider.settings import ProxyPoolSettings
from kspider.commen import stop_thread
from kspider.http import get_response
from threading import Thread
import redis
import warnings
import time


class ProxyPool():

    def __init__(
            self, proxy_url=None,
            proxyPoolSettings=ProxyPoolSettings,
    ):
        self.redis_conn = redis.StrictRedis(**proxyPoolSettings.REDIS_CONN)

        self.proxy_url = proxy_url or proxyPoolSettings.PROXY_URL
        self.key_name = proxyPoolSettings.REDIS_KEYNAME_NAME

        self.__flush_delay_change = proxyPoolSettings.DELAY['flush_proxy_change']
        self.__flush_delay_nochange = proxyPoolSettings.DELAY['flush_proxy_nochange']
        self.__error_delay = proxyPoolSettings.DELAY['error']

        self.__request_max_retry_num = proxyPoolSettings.REQUEST_RETRY['request_max_retry_num']
        self.__request_retry_delay = proxyPoolSettings.REQUEST_RETRY['request_retry_delay']
        self.__timeout = proxyPoolSettings.REQUEST_RETRY['timeout']

        self.split_char = proxyPoolSettings.SPLIT_CHAR

        self.get_delay = proxyPoolSettings.GET_DELAY

        self.is_alive = False
        self.__ips = []

    def __run(self):
        ips_last_set = {}
        while True:
            resp = get_response(
                url=self.proxy_url,
                max_retry_num=self.__request_max_retry_num,
                retry_delay=self.__request_retry_delay,
                timeout=self.__timeout,
                exception=False
            )
            if not resp:
                warnings.warn('访问代理IP的url地址失败')
            try:
                ips = resp.content.decode('utf-8').split(self.split_char)
                if ips == ips_last_set:
                    ips_last_set = set(ips)
                    self.redis_conn.delete(self.key_name)
                    self.redis_conn.sadd(self.key_name, ips)
                    time.sleep(self.__flush_delay_change)
                else:
                    time.sleep(self.__flush_delay_nochange)
            except:
                warnings.warn('写入代理IP失败')
                time.sleep(self.__error_delay)

    def run(self):
        self.thread_run_target = Thread(target=self.__run)
        self.thread_run_target.start()
        self.is_alive = True

    def get(self):
        if self.__ips:
            return self.__ips.pop()
        while True:
            proxy_quantity = self.redis_conn.smembers(self.key_name)
            self.__ips = self.redis_conn.srandmember(self.key_name, proxy_quantity)
            if self.__ips:
                return self.__ips.pop()
            else:
                time.sleep(self.get_delay)

    def close(self):
        stop_thread(self.thread_run_target)
        self.is_alive = False
