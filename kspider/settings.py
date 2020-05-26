class ScheduleSettings():
    # redis链接
    REDIS_CONN = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'encoding': 'utf-8',
        'decode_responses': True,
    }
    # redis中的键的名字
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
