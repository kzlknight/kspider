from kspider.settings import ScheduleSettings
from kspider.settings import ProcesserSettings
from kspider.shedule import Schedule
from kspider.commen import stop_thread
from kspider.pool import ProxyPool
from kspider.http import Request,Response
from threading import Thread
from queue import Queue
import time


# todo
'''
1. 发送request失败，调用errorback
2. 解析response失败，调用某个中间件
3. download_middleware设置default header
4. yield request|data data可以交给管道文件
5. 关闭processer的条件，等待的时间
'''

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


        # 解析request与response线程对象的状态
        self.excute_request_thread_statements = []
        self.excute_response_thread_statements = []


        # 生成解析request的线程对象
        for i in range(processerSettings.EXCUTE_THREAD['excute_request_thread_num']):
            self.excute_request_thread_targets.append(
                Thread(target=self.excute_request,args=(i,))
            )
            self.excute_request_thread_statements.append(0)

        # 生成解析response的线程对象
        for i in range(processerSettings.EXCUTE_THREAD['excute_response_thread_num']):
            self.excute_response_thread_targets.append(
                Thread(target=self.excute_response,args=(i,))
            )
            self.excute_response_thread_statements.append(0)

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
    def excute_request(self,statement_index):
        while True:
            # 未获得request时，线程状态为0
            self.excute_request_thread_statements[statement_index] = 0
            # 得到request对象
            request = self.schedule.get() # 堵车状态
            # 获得request时，线程状态为1
            self.excute_request_thread_statements[statement_index] = 1
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

    # 处理异常
    def excute_response(self,statement_index):
        while True:
            # 未获得response，状态为0
            self.excute_response_thread_statements[statement_index] = 0
            # 得到response
            response = self.excute_response_queue.get()
            if not response:break
            # 获得response，状态为1
            self.excute_response_thread_statements[statement_index] = 1
            # # ***********
            # while True:
            #     print('response alive')
            #     time.sleep(1)
            # # ***********
            # 尝试执行回调函数
            try:
                callback_func = eval('self.spider.{callback}'.format(callback=response.request.callback))
                for request in callback_func(response):
                    self.schedule.put(request)
            except Exception as e:
                # ******************
                # todo spider error
                print(e)
                # ******************

    def __run(self):
        try:
            for request in self.spider.start_request():
                self.schedule.put(request)
        except Exception as e:
            # **********
            # todo spider error
            print(e)
            # *********

        for excute_request_thread_target in self.excute_request_thread_targets:
            excute_request_thread_target.start()


        for excute_response_thread_target in self.excute_response_thread_targets:
            excute_response_thread_target.start()

        # 检查是否执行完毕
        def check_excute():
            def check_excute_wrapper():
                for request_statement in self.excute_request_thread_statements:
                    if request_statement == 1:
                        return False
                for request_statement in self.excute_response_thread_statements:
                    if request_statement == 1:
                        return False
                return True

            for i in range(3):
                if not check_excute_wrapper():return False
                time.sleep(3)
            return True

        # 验证是否执行完毕，如果执行完毕，跳出循环
        while True:
            time.sleep(2)
            if check_excute():
                break

        self.close()


    # 开始
    def run(self):
        self.excute_run_thread_target = Thread(target=self.__run)
        self.excute_run_thread_target.start()



    def close(self):
        for thread_target in self.excute_request_thread_targets:
            stop_thread(thread_target)
        for thread_target in self.excute_response_thread_targets:
            self.excute_response_queue.put(None)
        try:
            stop_thread(self.excute_run_thread_target)
        except: pass



                
            
            
