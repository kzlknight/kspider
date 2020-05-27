from kspider.settings import ScheduleSettings
from kspider.settings import ProcesserSettings
from kspider.shedule import Schedule
from kspider.pool import ProxyPool
from kspider.http import Request,Response
from threading import Thread
from queue import Queue


class Processer():
    def __init__(
            self,
            spider, # 被实例化的爬虫
            proxyPool = None, # 被实例化的IP池
            scheduleSettings = ScheduleSettings, # 调度器的配置类
            processerSettings = ProcesserSettings, # 执行器的配置类
    ):
        # 爬虫类
        self.spider = spider
        # 调度器
        self.schedule = Schedule(index=self.spider.index,st=scheduleSettings)

        # 单词爬虫请求相关
        self.__request_max_retry_num = processerSettings.REQUEST_RETRY['request_max_retry_num'] # 最大的尝试次数
        self.__request_retry_delay = processerSettings.REQUEST_RETRY['request_retry_delay'] # 重试的延时
        self.__request_timeout = processerSettings.REQUEST_RETRY['timeout'] # 超时最大值

        # 解析request与response线程对象的地址列表
        self.excute_request_thread_targets = []
        self.excute_response_thread_targets = []

        # 生成解析request的线程对象
        for i in range(processerSettings.EXCUTE_THREAD['excute_request_thread_num']):
            self.excute_request_thread_targets.append(
                Thread(target=self.excute_request)
            )

        # 生成解析response的线程对象
        for i in range(processerSettings.EXCUTE_THREAD['excute_response_thread_num']):
            self.excute_response_thread_targets.append(
                Thread(target=self.excute_response)
            )

        # 代理IP池的管理
        # 如果使用了代理IP池
        if proxyPool:
            # 如果代理IP池没有开始更新，则自动开启
            if not proxyPool.is_alive:
                proxyPool.run()
            self.proxies = proxyPool
        else:
            self.proxies = None

        # 解析请求后交给处理响应的线程通信队列
        self.excute_response_queue = Queue()

    # 处理请求
    def excute_request(self):
        while True:
            # 得到request对象
            request = self.schedule.get() # 堵车状态
            try:
                request_response = request.get_response(
                    max_retry_num=self.__request_max_retry_num,
                    retry_delay=self.__request_retry_delay,
                    timeout=self.__request_timeout,
                    proxies=self.proxies,
                )
                response = Response(request=request,response=request_response)
                self.excute_response_queue.put(response)
            except Exception as e:
                print(e)
                # todo 拆分异常
                self.schedule.put_error(request=request)


    def excute_response(self):
        while True:
            response = self.excute_response_queue.get()
            try:
                callback_func = eval('self.spider.{callback}'.format(callback=response.request.callback))
                for request in callback_func(response):
                    self.schedule.put(request)
            except Exception as e:
                # ******************
                print(e)
                # ******************

    def run(self):
        for request in self.spider.start_request():
            self.schedule.put(request)

        for excute_request_thread_target in self.excute_request_thread_targets:
            excute_request_thread_target.start()

        for excute_response_thread_target in self.excute_response_thread_targets:
            excute_response_thread_target.start()

