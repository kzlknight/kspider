class Settings():
    class Redis():
        conn = dict(
            host='localhost',
            port=6379,
            db=0,
            password=None,
            encoding='utf-8',
            decode_responses=True,
        )
        inner_requested_name = 'inner_requested'
        inner_requesting_name = 'inner_requesting'
        outer_requested_name = 'outer_requested'
        outer_requesting_name = 'outer_requesting'
        error_inner_requested_name = 'inner_error_requested'
        error_outer_requested_name = 'outer_error_requested'
        error_inner_requesting_name = 'inner_error_requesting'
        error_outer_requesting_name = 'outer_error_requesting'
        process_name = 'process'

    class Request():
        timeout = 5
        max_retry_num = 3
        default_headers = {}



