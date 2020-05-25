from core.url import norm_index,norm_url,get_host,check_host
from hashlib import md5
from .settings import Settings as ST
from ast import literal_eval
import redis



def build_kreq(req_data_str):
    '''
    :param req_data_str:
    :return: kreq|None
    '''
    try:
        return Kreq(**literal_eval(req_data_str))
    except:
        return None
class Kreq():
    url:str
    data:dict
    header:dict
    method:str
    callback:object
    errorback:object

    def __init__(
            self,url:str,data:dict=None,header:dict=None,method='GET',callback:object=None,errorback:object=None,
    ):
        self.url = url
        self.data = data
        self.header = header
        self.callback = callback
        self.errorback = errorback
        self.method = method

    def to_dict(self):
        data = str(self.data) if self.data and type(self.data) == dict else ''
        header = str(self.header) if self.header and type(self.header) == dict else ''
        callback = str(self.callback.__name__) if self.callback else ''
        errorback = str(self.errorback.__name__) if self.errorback else ''

        return dict(
            url=self.url,
            data=data,
            header=header,
            method=self.method,
            callback=callback,
            errorback=errorback,
        )

    def to_str(self):
        return str(self.to_dict())

    def to_md5(self):
        dict_data = self.to_dict()
        return md5(
            '{url}-{data}-{method}'.format(
                url = dict_data['url'],
                data = dict_data['data'],
                method = dict_data['method'],
            ).encode('utf-8')
        ).hexdigest()

    def __str__(self):
        return self.to_str()

def req_data_str_to_md5(url,data,method):
    return md5(
        '{url}{data}{method}'.format(
            url = url,data=data,method=method,
        ).encode('utf-8')
    ).hexdigest()


class Schedule():
    def __init__(self,index,st=ST):

        self.index = index
        self.host = get_host(self.index)

        self.redis_conn = redis.StrictRedis(**st.Redis.conn)

        self.inner_requested_name = '%s:%s' % (index,st.Redis.inner_requested_name)
        self.inner_requesting_name = '%s:%s' % (index,st.Redis.inner_requesting_name)
        self.outer_requested_name = '%s:%s' % (index,st.Redis.outer_requested_name)
        self.outer_requesting_name = '%s:%s' % (index,st.Redis.outer_requesting_name)

        self.error_inner_requested_name = '%s:%s' % (index,st.Redis.error_inner_requested_name)
        self.error_inner_requesting_name = '%s:%s' % (index,st.Redis.error_inner_requesting_name)
        self.error_outer_requested_name = '%s:%s' % (index,st.Redis.error_outer_requested_name)
        self.error_outer_requesting_name = '%s:%s' % (index,st.Redis.error_outer_requesting_name)

        self.process_name = '%s:%s' % (index,st.Redis.process_name)


    def __get(self,way,error=False):
        '''
        :param way: 'inner'|'outer'
        :param error: True|False
        :return: dict|None
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

        req_data_str = self.redis_conn.spop(name=this_requesting_name)
        if not req_data_str:return None
        try:
            kreq = build_kreq(req_data_str)
            self.redis_conn.sadd(
                this_requested_name, kreq.to_md5()
            )
            return kreq
        except: return None


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
