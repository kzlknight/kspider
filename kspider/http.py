from kspider.commen import retry_wrapper
from kspider.urls import norm_url
from hashlib import md5
from ast import literal_eval
import lxml.etree as le
import requests
import re


def get_response(url, data=None, headers={}, method='GET', proxies=False, params=None, timeout=5, max_retry_num=3,
                 retry_delay=1, exception=True, **kwargs) -> requests.get:
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
    url: str
    data: dict
    header: dict
    method: str
    callback: object
    errorback: object

    def __init__(
            self, url: str, data: dict = None, rel='',index='', headers: dict = None, method='GET', callback: object = None,
            errorback: object = None, meta={},
    ):
        self.url = url
        self.data = data
        self.headers = headers
        self.callback = callback
        self.errorback = errorback
        self.method = method
        self.meta = meta
        self.rel = rel
        self.index= index

    def to_dict(self):
        data = str(self.data) if self.data and type(self.data) == dict else ''
        headers = str(self.headers) if self.header and type(self.headers) == dict else ''
        callback = str(self.callback.__name__) if self.callback else ''
        errorback = str(self.errorback.__name__) if self.errorback else ''

        return dict(
            url=self.url,
            data=data,
            header=headers,
            method=self.method,
            callback=callback,
            errorback=errorback,
            meta=self.meta,
        )

    def to_str(self):
        return str(self.to_dict())

    def to_md5(self):
        dict_data = self.to_dict()
        return md5(
            '{url}-{data}-{method}'.format(
                url=dict_data['url'],
                data=dict_data['data'],
                method=dict_data['method'],
            ).encode('utf-8')
        ).hexdigest()

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

    @staticmethod
    def build_request(request_str):
        return Request(**literal_eval(request_str))

    def __str__(self):
        return self.to_str()


class Response():
    def __init__(self, request, response):
        self.request: Request = request
        self.body: bytes = response.content

    def xpath_one(self, path, content='', default=None):
        if not content:
            if not hasattr(self, '_body_x'):
                self._body_x = le.HTML(self.body)
            this_content_x = self._body_x
        else:
            this_content_x = le.HTML(content)

        rets = this_content_x.xpath(path)
        return rets[0] if rets else default

    def xpath_all(self, path, content=''):
        if not content:
            if not hasattr(self, '_body_x'):
                self._body_x = le.HTML(self.body)
            this_content_x = self._body_x
        else:
            this_content_x = le.HTML(content)
        return this_content_x.xpath(path)

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
