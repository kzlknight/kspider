from queue import Queue as TQueue
from threading import Thread
from .settings import Settings as ST
import requests
import time





class Processer():
    def send_request(
            self, url, data=None, proxys=False, headers={}, params=None, method='GET', timeout=None, max_retry_num=None, **kwargs,
    ):
        timeout = timeout or self.ST.Request.timeout
        max_retry_num = max_retry_num or self.ST.Request.max_retry_num
        headers = headers or self.ST.Request.default_headers

        try:
            for i in range(max_retry_num - 1):
                if method == 'GET':
                    return requests.get(
                        url=url,
                        params=params,
                        data=data,
                        headers=headers,
                        proxies={'http': proxys,'https': proxys} if proxys else None,
                        timeout=timeout
                    )
                else:


    def __init__(
            self,
            spider,
            ST=ST,
            req_t_num=8,
            rep_t_num=2,
    ):
        self.ST = ST
        self.spider = spider

        self.q_req = TQueue()
        self.q_rep = TQueue()

        self.excute_request_t_targets = []
        self.excute_response_t_targets = []
        for i in range(req_t_num):
            self.excute_request_t_targets.append(
                Thread(target=self.excute_request)
            )
        for i in range(rep_t_num):
            self.excute_response_t_targets.append(
                Thread(target=self.excute_response)
            )

    def run(self):
        for excute_request_t in self.excute_request_t_targets:
            excute_request_t.start()

        for excute_response_t in self.excute_response_t_targets:
            excute_response_t.start()

        for data in self.spider.start_request():
            # todo 区分req与item
            self.q_req.put(data)

    def excute_request(self):
        while True:
            kreq = self.q_req.get()
            if not kreq: break

    def excute_response(self):
        pass
