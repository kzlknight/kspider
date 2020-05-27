from kspider.commen import retry_wrapper
from kspider.urls import norm_url
from hashlib import md5
from ast import literal_eval
import lxml.etree as le
import requests
import re


# 发送get或post请求，返回response对象
def get_response(
        url, data=None, headers={}, method='GET', proxies=False, params=None, timeout=5, max_retry_num=3,
        retry_delay=1, exception=True, **kwargs
) -> requests.get:
    if method == 'GET':
        this_func = requests.get
    elif method == 'POST':
        this_func = requests.post
    elif method == 'PUT':
        this_func = requests.put
    elif method == 'DELETE':
        this_func = requests.delete
    else:
        raise Exception('%s this method is not supported' % method)  # ~~~~

    @retry_wrapper(max_retry_num=max_retry_num, retry_delay=retry_delay, exception=exception)
    def send():
        if proxies:
            if type(proxies) == 'str':
                this_proxies = {'http': proxies, 'https': proxies}
            else:
                this_proxies = proxies.get()
        else:
            this_proxies = None

        return this_func(
            url=url, data=data, headers=headers, proxies=this_proxies, params=params, timeout=timeout,
            **kwargs
        )

    return send()


class Request():
    def __init__(
            self, url: str, data: dict = None, headers: dict = None, method='GET', index='', rel='',
            callback: object = None, errorback: object = None, meta={},
    ):
        self.url = url
        self.data = data
        self.headers = headers
        self.callback = callback
        self.errorback = errorback
        self.method = method
        self.meta = meta
        self.rel = rel
        self.index = index

    # 转为字典
    def to_dict(self):
        # 处理callback会掉函数
        if not self.callback:  # 如果没有callback
            callback = ''
        elif type(self.callback) == str:  # 如果callback是函数名
            callback = self.callback
        else:  # 如果callback是函数地址
            callback = self.callback.__name__

        # 处理errorback
        if not self.errorback:  # 如果没有errorback
            errorback = ''
        elif type(self.errorback) == str:  # 如果errorback是函数名
            errorback = self.errorback
        else:  # 如果errorback是函数地址
            errorback = self.errorback.__name__

        return dict(
            url=self.url,
            data=self.data,
            headers=self.headers,
            method=self.method,
            callback=callback,
            errorback=errorback,
            meta=self.meta,
        )

    # 转为字符串
    def to_str(self):
        return str(self.to_dict())

    # 对url，data，method进行md5加密
    def to_md5(self):
        dict_data = self.to_dict()
        return md5(
            '{url}-{data}-{method}'.format(
                url=dict_data['url'],
                data=dict_data['data'],
                method=dict_data['method'],
            ).encode('utf-8')
        ).hexdigest()

    #  发送请求
    def get_response(self, proxies=None, max_retry_num=3, retry_delay=1, timeout=5, exception=False):
        return get_response(
            url=self.url,
            data=self.data,
            headers=self.headers,
            method=self.method,
            proxies=proxies,
            timeout=timeout,
            max_retry_num=max_retry_num,
            retry_delay=retry_delay,
            exception=exception,
        )

    # 通过to_str的返回值，创建request对象
    @staticmethod
    def build_request(request_str):
        return Request(**literal_eval(request_str))

    def __str__(self):
        return self.to_str()


class Response():
    def __init__(self, request, response):
        self.request: Request = request # 上一次请求的对象
        self.body: bytes = response.content # 返回response的字节

    # 返回唯一的xpath结果
    def xpath_one(self, path, content='', default=None):
        if not content:
            if not hasattr(self, '_body_x'):
                self._body_x = le.HTML(self.body)
            this_content_x = self._body_x
        else:
            this_content_x = le.HTML(content)

        rets = this_content_x.xpath(path)
        return rets[0] if rets else default

    # 返回多个xpath的结果
    def xpath_all(self, path, content=''):
        if not content:
            if not hasattr(self, '_body_x'):
                self._body_x = le.HTML(self.body)
            this_content_x = self._body_x
        else:
            this_content_x = le.HTML(content)
        return this_content_x.xpath(path)

    # 返回request
    def follow(
            self, url: str, data: dict = None, headers: dict = None, method='GET', callback: object = None,
            errorback: object = None, meta={}, rel='',
    ):
        return Request(
            url=url,
            data=data,
            headers=headers,
            method=method,
            callback=callback,
            errorback=errorback,
            meta=meta,
            rel=rel if rel else self.request.rel
        )
