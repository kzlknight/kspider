from kspider.settings import ScheduleSettings
from kspider.settings import ProcesserSettings
from kspider.shedule import Schedule
from kspider.http import Request,Response
from threading import Thread
from queue import Queue


class Processer():
    def __init__(
            self,
            spider,
            scheduleSettings = ScheduleSettings,
            processerSettings = ProcesserSettings,
    ):
        self.spider = spider
        self.schedule = Schedule(index=self.spider.index,st=scheduleSettings)


        self.__request_max_retry_num = processerSettings.REQUEST_RETRY['request_max_retry_num']
        self.__request_retry_delay = processerSettings.REQUEST_RETRY['request_retry_delay']
        self.__request_timeout = processerSettings.REQUEST_RETRY['timeou']

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


    def excute_request(self):
        while True:
            request = self.schedule.get()
            request_response = request.get_response(
                max_retry_num=self.__request_max_retry_num,
                retry_delay=self.__request_retry_delay,
                timeout=self.__request_timeout,
            )
            response = Response(request=request,response=request_response)
            
        pass

    def excute_response(self):
        pass



    def run(self):
        for request in self.spider.start_request:
            self.schedule.put(request)

        for excute_request_thread_target in self.excute_request_thread_targets:
            excute_request_thread_target.start()

        for excute_response_thread_target in self.excute_response_thread_targets:
            excute_response_thread_target.start()

