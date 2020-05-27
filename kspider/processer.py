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
            spider,
            proxyPool = None,
            scheduleSettings = ScheduleSettings,
            processerSettings = ProcesserSettings,
    ):
        self.spider = spider
        self.schedule = Schedule(index=self.spider.index,st=scheduleSettings)


        self.__request_max_retry_num = processerSettings.REQUEST_RETRY['request_max_retry_num']
        self.__request_retry_delay = processerSettings.REQUEST_RETRY['request_retry_delay']
        self.__request_timeout = processerSettings.REQUEST_RETRY['timeout']

        self.excute_request_thread_targets = []
        self.excute_response_thread_targets = []


        for i in range(processerSettings.EXCUTE_THREAD['excute_request_thread_num']):
            self.excute_request_thread_targets.append(
                Thread(target=self.excute_request)
            )

        for i in range(processerSettings.EXCUTE_THREAD['excute_response_thread_num']):
            self.excute_response_thread_targets.append(
                Thread(target=self.excute_response)
            )

        if proxyPool:
            if not proxyPool.is_alive:
                proxyPool.run()
            self.proxies = proxyPool
        else:
            self.proxies = None

        self.excute_response_queue = Queue()

    def excute_request(self):
        while True:
            request = self.schedule.get()
            print(request)
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

