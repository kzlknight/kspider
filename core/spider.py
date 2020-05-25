from threading import Thread
from queue import Queue
from .shedule import Kreq




class Spider():
    def __init__(
            self,
            index,
            thread_num=5,
    ):

        self.thread_num = thread_num
        pass

    def start_request(self):
        yield Kreq(
            url='http://www.baidu.com',
            callback=self.parse1
        )
    def parse1(self,response):
        pass

    def run(self):
        self.q_req = Queue()
        self.q_rep = Queue()

        for kreq in self.start_request():
            pass
        thread_targets = []
        for i in range(self.thread_num):
            thread_targets.append(Thread(target=self.excute_request))

        for thread_target in thread_targets:
            thread_target.start()

    def excute_request(self):
        pass

    def excute_response(self):
        pass


if __name__ == '__main__':
    a = A()
    print(a.test())



