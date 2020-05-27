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
        # 代理IP池的Redis链接
        self.redis_conn = redis.StrictRedis(**proxyPoolSettings.REDIS_CONN)
        # 代理IP地址
        self.proxy_url = proxy_url or proxyPoolSettings.PROXY_URL
        # 存放代理IP的键名
        self.key_name = proxyPoolSettings.REDIS_KEYNAME_NAME

        # 当代理IP更新后的延时请求时间
        self.__flush_delay_change = proxyPoolSettings.DELAY['flush_proxy_change']
        # 当代理IP未更新后的延时时间
        self.__flush_delay_nochange = proxyPoolSettings.DELAY['flush_proxy_nochange']
        # 当请求失败的延时时间
        self.__error_delay = proxyPoolSettings.DELAY['error']

        # 调用request.get_response()的最大尝试次数
        self.__request_max_retry_num = proxyPoolSettings.REQUEST_RETRY['request_max_retry_num']
        # 调用request.get_response()的失败重试延时时间
        self.__request_retry_delay = proxyPoolSettings.REQUEST_RETRY['request_retry_delay']
        # 调用request.get_response()的最大超时时间
        self.__timeout = proxyPoolSettings.REQUEST_RETRY['timeout']

        # 得到多个代理IP，使用的分隔符
        self.split_char = proxyPoolSettings.SPLIT_CHAR

        # 向Redis中所要代理IP，没有得到的重试延时
        self.get_delay = proxyPoolSettings.GET_DELAY

        # 代理IP池是否运行
        self.is_alive = False

        # 缓存代理IP
        self.__ips = []

    def __run(self):
        # 上一次得到的代理IP集合
        ips_last_set = {}
        # 循环更新self.__ips
        while True:
            # 发送请求，得到response，exception=None，如果异常，返回resp = None
            try:
                resp = get_response(
                    url=self.proxy_url,
                    max_retry_num=self.__request_max_retry_num,
                    retry_delay=self.__request_retry_delay,
                    timeout=self.__timeout,
                    exception=True
                )
            # 如果没有resp，报警告
            except Exception as e:
                warnings.warn(e)
                time.sleep(self.__error_delay)
                continue
            # 解析到resp中的代理ip，添加到Redis中
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

    # 开始更新代理ip线程
    def run(self):
        # 更新代理的线程对象
        self.thread_run_target = Thread(target=self.__run)
        # 启动线程
        self.thread_run_target.start()
        # 设置状态
        self.is_alive = True

    # 得到代理ip
    def get(self):
        # todo return {'http':'','https':''}
        # 如果缓存中有代理ip，则返回代理ip
        if self.__ips:
            return self.__ips.pop()
        # 从Redis中得到ip，更新self.__ips的缓存，并返回代理ip
        while True:
            # 得到Redis中代理ip的数目
            proxy_quantity = self.redis_conn.smembers(self.key_name)
            # 更新self.__ips
            self.__ips = self.redis_conn.srandmember(self.key_name, proxy_quantity)
            # 如果self.__ips有内容，则返回，否则延时重新更新
            if self.__ips:
                return self.__ips.pop()
            else:
                time.sleep(self.get_delay)

    # 关闭更新代理的线程
    def close(self):
        stop_thread(self.thread_run_target)
        self.is_alive = False
