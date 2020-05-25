import requests



def get_response(url,data=None,headers={},proxys=False,params=None,timeout=5,max_retry_num=3,retry_delay=1,**kwargs):
    for i in range(max_retry_num):
        try:
            pass



get_response.a = '123'





def retry_wrapper(max_retry_num=3,retry_delay=1):
    def wrapper1(func):
        def wrapper2(*args,**kwargs):
            for i in range(max_retry_num):
                try:
                    return func(*args,**kwargs),None
                except Exception as e:
                    time.sleep(retry_delay)
            return func(*args,**kwargs)
        return wrapper2
    return wrapper1




def get(url,data=None,headers={},proxys=False,params=None,timeout=5,max_retry_num=3,retry_delay=1,**kwargs):
    @retry_wrapper(max_retry_num=max_retry_num,retry_delay=retry_delay)
    def func(url, data=None, headers={},proxys=False, params=None,timeout=5,max_retry_num=3,**kwargs):
        return requests.get(
            url=url,
            params=params,
            data=data,
            headers=headers,
            proxies={'http': proxys, 'https': proxys} if proxys else None,
            timeout=timeout
        )

def get(url, data=None, headers={},proxys=False, params=None,timeout=5,max_retry_num=3,**kwargs):
    return requests.post(
        url=url,
        params=params,
        data=data,
        headers=headers,
        proxies={'http': proxys, 'https': proxys} if proxys else None,
        timeout=timeout
    )