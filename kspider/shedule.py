from kspider.urls import norm_url,norm_index,get_host,check_host
from kspider.http import Request,Response
from kspider.settings import ScheduleSettings
from hashlib import md5
from ast import literal_eval
import redis

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

        request_str = self.redis_conn.spop(name=this_requesting_name)
        if not request_str:return None
        try:
            request = Request.build_request(request_str)
            self.redis_conn.sadd(
                this_requested_name, request.to_md5()
            )
            return request
        except Exception as e:
            # ****************
            print('e')
            # ****************
            return None


    def __put(self,kreq,way='right',rel='',dont_filter=False):
        '''
        :param kreq: 请求对象
        :param way: 'right'|'error'
        :param rel: str
        :param dont_filter: False|True
        :return: True|Flase
        成功True，失败False
        '''
        # 规范化url
        kreq.url = norm_url(kreq.url, index=self.index, rel=rel)
        # 得到url是否输入host
        check_host_ret = check_host(kreq.url, self.host)
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
        if dont_filter or (not self.redis_conn.sismember(this_requested_name,kreq.to_md5())):
            self.redis_conn.sadd(this_requesting_name,kreq.to_str())
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

    def put_error(self,kreq,rel='',dont_filter=False):
        return self.__put(
            kreq=kreq,
            way='error',
            rel=rel,
            dont_filter=dont_filter,
        )

    def put(self,kreq,rel='',dont_filter=False):
        return self.__put(
            kreq=kreq,
            way='right',
            rel=rel,
            dont_filter=dont_filter,
        )



if __name__ == '__main__':
    s = Schedule(index='https://www.baidu.com/')
    kreq = Kreq(url ='/abc/qwe/aaawww/345678')
    print(s.put(kreq))
    print(s.get_inner())
