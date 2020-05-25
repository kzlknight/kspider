from multiprocessing import Process,Queue
from threading import Thread




# class EnginePool():
#     def __init__(
#             self,
#             pool_num=10,
#     ):
#         self.spider_q = Queue()
#         for i in range(pool_num):
#             p = Process(target=self.process_spider,args=(self.spider_q,))
#             p.start()
#         pass
#
#     def put_spider(self,spider):
#         self.spider_q.put(spider)
#
#     def thread_spider(self,spider):
#         for req in spider.
#
#
#     def process_spider(self,q):
#         spider:Spider = q.get()
#         thread_targets = []
#         for i in range(spider.thread_num):
#             thread_targets.append(Thread(target=spider.thread_spider))
#         for thread_target in thread_targets:
#             thread_target.start()
#
#
#
#     def process_request(self):
#         pass
#
#     def process_response(self):
#         pass
#
#
# class Spider():
#     def __init__(self,index):
#         self.index = index

# if __name__ == '__main__':
#     e = EnginePool()
#     s = Spider(index=123)
#     s2 = Spider(index=454646454545)
#     e.put_spider(s)
#     e.put_spider(s2)




