import re

# __all__ = ['norm_url','norm_index','get_host','check_host']

url_pattern_https = re.compile(
    '^https://www\.\w{1,50}\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu).*$'
)
url_pattern_http = re.compile(
    '^http://www\.\w{1,50}\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu).*$'
)
url_pattern_slash2_www = re.compile(
    '^//www\.\w{1,50}\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu).*$'
)
url_pattern_www = re.compile(
    '^www\.\w{1,50}\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu).*$'
)

index_pattern_https = re.compile(
    '^https://www\.\w{1,50}\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu)/{0,1}$'
)
pattern_host = re.compile(
    '^https://www\.(.*?)\.(com|cn|top|ltd|net|xin|vip|store|shop|wang|cloud|xyz|ren|tech|online|site|ink|link|love|art|fun|club|cc|website|press|space|beer|luxe|video|group|fit|yoga|com.cn|net.cn|org.cn|pro|biz|info|design|work|mobi|kim|pub|org|name|tv|co|asia|red|live|wiki|gov.cn|life|world|run|show|city|gold|today|plus|cool|icu).*'
)


def norm_index(index: str):
    # 为index添加https://
    if index.startswith('https://'):
        pass
    elif index.startswith('http://'):
        index = re.sub('http://', 'https://', index, count=1)
    elif index.startswith('//'):
        index = re.sub('//', 'https://', index, count=1)
    elif index.startswith('www'):
        index = 'https://' + index
    else:
        # 如果没有满足前几个条件，返回None
        return None
    if re.match(index_pattern_https, index):
        if not index.endswith('/'):
            index += '/'
        # 返回index，结尾有/
        return index
    else:
        # 规范化index后，不符合正则表达式，返回None
        return None


def norm_url(url: str, index='', rel='', ):
    # 规范化url
    if re.match(url_pattern_https, url):  # https://
        pass
    elif re.match(url_pattern_http, url):  # http:// --> https://
        url = re.sub('http://', 'https://', url, count=1)
    elif re.match(url_pattern_slash2_www, index):  # // --> https:?/
        url = re.sub('//', 'https://', url, count=1)
    elif re.match(url_pattern_www, url):  # www --> https://www
        url = 'https://' + url
    else:  # rel或者/host
        if url.startswith('/'):
            url = index + url[1:]
        else:
            if rel.endswith('/'):
                rel = rel[0:-1]
            url = rel + '/' + url

    return url


def get_host(url):
    '''
    :param url:
    :return: host:str|None
    '''
    try:
        return re.findall(
            pattern_host, 'https://www.baidu.com'
        )[0][0]
    except:
        return None


def check_host(url, host):
    url_host = get_host(url)
    if url_host == host:
        return True
    else:
        return False


if __name__ == '__main__':
    def test():
        url_suffixs = ['com', 'cn', 'top', 'ltd', 'net', 'xin', 'vip', 'store', 'shop', 'wang', 'cloud', 'xyz', 'ren',
                       'tech', 'online', 'site', 'ink', 'link', 'love', 'art', 'fun', 'club', 'cc', 'website',
                       'press', 'space', 'beer', 'luxe', 'video', 'group', 'fit', 'yoga', 'com.cn', 'net.cn', 'org.cn',
                       'pro',
                       'biz', 'info', 'design', 'work', 'mobi', 'kim', 'pub', 'org', 'name', 'tv', 'co', 'asia', 'red',
                       'live', 'wiki', 'gov.cn', 'life', 'world', 'run', 'show', 'city', 'gold', 'today', 'plus',
                       'cool',
                       'icu', ]
        test_urls = {
            'https_urls': [
                'https://www.baidu.com',
                'https://www.baidu.com/',
                'https://www.baidu.com/abc/edf',
                'https://www.baidu.com/abc/edf/',
                'https://www.baidu.com/abc/edf/#',
                'https://www.baidu.com/abc/edf?a=1',
            ],
            'http_urls': [
                'http://www.baidu.com',
                'http://www.baidu.com/',
                'http://www.baidu.com/abc/edf',
                'http://www.baidu.com/abc/edf/',
                'http://www.baidu.com/abc/edf/#',
                'http://www.baidu.com/abc/edf?a=1',
            ],
            'slash_urls': [
                '//www.baidu.com',
                '//www.baidu.com/',
                '//www.baidu.com/abc/edf',
                '//www.baidu.com/abc/edf/',
                '//www.baidu.com/abc/edf/#',
                '//www.baidu.com/abc/edf?a=1',
            ],
            'www_urls': [
                'www.baidu.com',
                'www.baidu.com/',
                'www.baidu.com/abc/edf',
                'www.baidu.com/abc/edf/',
                'www.baidu.com/abc/edf/#',
                'www.baidu.com/abc/edf?a=1',
            ],
            'follow_indexs': [
                '/abc/edf',
                '/abc/edf/',
                '/abc/edf/#',
                '/abc/edf?a=1',
            ],
            'rel_urls': [
                'edf',
                'edf/',
                'edf/#',
                'edf?a=1',
            ]
        }

        pattern_dict = {
            'https_urls': url_pattern_https,
            'http_urls': url_pattern_http,
            'slash_urls': url_pattern_slash2_www,
            'www_urls': url_pattern_www,
        }

        for pattern_key in pattern_dict.keys():
            pattern_value = pattern_dict[pattern_key]
            for url_key in test_urls.keys():
                for url in test_urls[url_key]:
                    ret = re.match(pattern_value, url)
                    if pattern_key == url_key and not ret:
                        print('对的没有匹配成功', url, pattern_key)
                    if pattern_key != url_key and ret:
                        print('把错的匹配成功了', url, pattern_key)
