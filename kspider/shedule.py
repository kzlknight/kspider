from kspider.urls import norm_url,norm_index,get_host,check_host
from kspider.http import Request,Response
from kspider.settings import ScheduleSettings
from hashlib import md5
from ast import literal_eval
import redis
import time

class Schedule():
    def __init__(self,index,st=ScheduleSettings):

        self.index = index
        self.host = get_host(self.index)

        self.redis_conn = redis.StrictRedis(**st.REDIS_CONN)

        self.inner_requested_name = '%s:%s' % (index,st.REDIS_KEYNAME['inner_requested_name'])
        self.inner_requesting_name = '%s:%s' % (index,st.REDIS_KEYNAME['inner_requesting_name'])
        self.outer_requested_name = '%s:%s' % (index,st.REDIS_KEYNAME['outer_requested_name'])
        self.outer_requesting_name = '%s:%s' % (index,st.REDIS_KEYNAME['outer_requesting_name'])

        self.error_inner_requested_name = '%s:%s' % (index,st.REDIS_KEYNAME['error_inner_requested_name'])
        self.error_inner_requesting_name = '%s:%s' % (index,st.REDIS_KEYNAME['error_inner_requesting_name'])
        self.error_outer_requested_name = '%s:%s' % (index,st.REDIS_KEYNAME['error_outer_requested_name'])
        self.error_outer_requesting_name = '%s:%s' % (index,st.REDIS_KEYNAME['error_outer_requesting_name'])

        self.process_name = '%s:%s' % (index,st.REDIS_KEYNAME['process_name'])
        self.spop_delay = st.SPOP_DELAY


    def __get(self,way,error=False):
        '''
        :param way: 'inner'|'outer'
        :param error: True|False
        :return: request|None
        没有数据，返回None
        有数组，转成字典，失败返回None，成功返回dict
        '''
        if error: # 如果异常
            if way == 'outer':
                this_requesting_name = self.error_outer_requesting_name
                this_requested_name = self.error_outer_requested_name
            else:
                this_requesting_name = self.error_inner_requesting_name
                this_requested_name = self.error_inner_requested_name
        else: # 如果非异常
            if way == 'outer':
                this_requesting_name = self.outer_requesting_name
                this_requested_name = self.outer_requested_name
            else:
                this_requesting_name = self.inner_requesting_name
                this_requested_name = self.inner_requested_name

        # 如果不能得到正确的request对象，程序则会一直循环
        while True:
            # 从Redis中的到request的字符串对象
            request_str = self.redis_conn.spop(name=this_requesting_name)
            # 如果没有request_str对象，延时，再次获取
            if not request_str:
                time.sleep(self.spop_delay)
                continue
            try:
                # 尝试通过request_str构造request类对象
                request = Request.build_request(request_str)
                # 标记已经请求
                self.redis_conn.sadd(
                    this_requested_name, request.to_md5()
                )
                # 返回request类对象
                return request
            except Exception as e:
                # ****************
                # 如果失败，一般是由于不能转成request，测试提示异常 【test】
                print(e)
                # ****************


    def __put(self,request,way='right',dont_filter=False):
        '''
        :param kreq: 请求对象
        :param way: 'right'|'error'
        :param rel: str
        :param dont_filter: False|True
        :return: True|Flase
        成功True，失败False
        '''
        # 规范化url
        request.url = norm_url(url=request.url,index=self.index,rel=request.rel)
        # 得到url是否输入host
        check_host_ret = check_host(request.url, self.host)
        # this_requesting_name 指向待请求
        # this_requested_name  指向已请求
        if way == 'error': # 如果异常
            if check_host_ret: # 如果属于本站
                this_requesting_name = self.error_inner_requesting_name
                this_requested_name =self.error_inner_requested_name
            else:
                this_requesting_name = self.error_outer_requesting_name
                this_requested_name = self.error_outer_requested_name
        else: # 如果非异常
            if check_host_ret: # 如果属于本站
                this_requesting_name = self.inner_requesting_name
                this_requested_name =self.inner_requested_name
            else:
                this_requesting_name = self.outer_requesting_name
                this_requested_name = self.outer_requested_name
        # 如果不拦截，或者未发送这个请求，返回True
        if dont_filter or (not self.redis_conn.sismember(this_requested_name,request.to_md5())):
            self.redis_conn.sadd(this_requesting_name,request.to_str())
            return True
        # 如果拦截，且已经发送了这个请求，返回False
        else:
            return False

    def get(self):
        return self.get_inner()

    def get_inner(self):
        return self.__get(way='inner',error=False)

    def get_outer(self):
        return self.__get(way='outer',error=False)

    def get_inner_error(self):
        return self.__get(way='inner',error=True)

    def get_outer_error(self):
        return self.__get(way='outer',error=True)

    def put_error(self,request,dont_filter=False):
        return self.__put(
            request=request,
            way='error',
            dont_filter=dont_filter,
        )

    def put(self,request,dont_filter=False):
        dont_filter = request.dont_filter or dont_filter
        return self.__put(
            request=request,
            way='right',
            dont_filter=dont_filter,
        )



if __name__ == '__main__':
    s = Schedule(index='https://www.baidu.com/')
    request= Request(url ='/abc/qwe/aaawww/345678')
    print(s.put(request))
    print(s.get_inner())
