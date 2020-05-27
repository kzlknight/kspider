class ScheduleSettings():
    # Redis链接
    REDIS_CONN = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'encoding': 'utf-8',
        'decode_responses': True,
    }
    # Redis中的键的名字
    REDIS_KEYNAME = {
        'inner_requested_name': 'inner_requested',
        'inner_requesting_name': 'inner_requesting',
        'outer_requested_name': 'outer_requested',
        'outer_requesting_name': 'outer_requesting',
        'error_inner_requested_name': 'inner_error_requested',
        'error_outer_requested_name': 'outer_error_requested',
        'error_inner_requesting_name': 'inner_error_requesting',
        'error_outer_requesting_name': 'outer_error_requesting',
        'process_name': 'process',
    }
    SPOP_DELAY = 0.5

class ProcesserSettings():
    EXCUTE_THREAD = {
        # 'excute_request_thread_num': 8,
        # 'excute_response_thread_num': 2,
        'excute_request_thread_num': 1,
        'excute_response_thread_num': 1,
    }
    REQUEST_RETRY = {
        'request_max_retry_num': 3,
        'request_retry_delay': 1,
        'timeout': 5,
    }


class ProxyPoolSettings():
    # http/https接口地址
    PROXY_URL = ''
    # Redis链接
    REDIS_CONN = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'encoding': 'utf-8',
        'decode_responses': True,
    }
    # Redis中的键的名哦字
    REDIS_KEYNAME_NAME = 'proxy'
    DELAY = {
        'flush_proxy_change': 2,
        'flush_proxy_nochange': 1,
        'error': '1',
    }
    SPLIT_CHAR = ','
    REQUEST_RETRY = {
        'request_max_retry_num': 3,
        'request_retry_delay': 1,
        'timeout': 5,
    }
    GET_DELAY = 0.5

