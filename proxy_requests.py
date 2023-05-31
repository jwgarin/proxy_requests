import requests
import os
import random
import re
from requests.auth import HTTPProxyAuth

get = lambda url, use_proxy=False, method="get", **kwargs: proxy_requests(url, use_proxy=use_proxy, method="get", **kwargs)
post = lambda url, use_proxy=False, method="post", **kwargs: proxy_requests(url, use_proxy=use_proxy, method="post", **kwargs)

def proxy_requests(url, use_proxy=False, method="get", **kwargs):
    # Proxy format http://{USERNAME}:{PASSWORD}@{IP}:{PORT}
    # Put proxies in proxies.txt
    if use_proxy and os.path.exists('proxies.txt'):
        with open('proxies.txt') as f:
            proxy_list = f.read().splitlines()
        proxies = {'http': random.choice(proxy_list)}
    else:
        proxies = None
    if method == 'get':
        for i in range(3):
            try:
                r = requests.get(url, proxies=proxies, **kwargs)
                break
            except Exception as exc:
                if i == 2:
                    raise Exception(exc)
                else:
                    pass
    elif method == 'post':
        r = requests.post(url, proxies=proxies, **kwargs)
    if r.status_code == 200:
        return r
    else:
        raise Exception('Error {} - {}'.format(r.status_code, url))

class Proxy:
    def __init__(self, proxy_input):
        self.proxy_input = proxy_input
        self.auth = HTTPProxyAuth(self.comp['user'], self.comp['pass'])
        self.proxies = {
            'http': '{}://{}:{}'.format(self.comp['schema'], self.comp['ip'], self.comp['port']),
            'https': '{}://{}:{}'.format(self.comp['schema'], self.comp['ip'], self.comp['port'])
        }

    @property
    def proxy_input(self):
        return self._proxy_input
    
    @proxy_input.setter
    def proxy_input(self, value):
        parts = value.replace('@', ':').split(':')
        comp = {}
        for part in parts:
            part = part.replace('//', '')
            if part.startswith('http'):
                comp['schema'] = part.replace('//', '')
            elif re.search(r'\d+.\d+.\d+.\d+|\w+\.\w+\.\w+', part):
                comp['ip'] = part
            elif part.isdecimal():
                comp['port'] = part
            elif 'user' not in comp \
                 and not re.search(r'\d+.\d+.\d+.\d+|\w+\.\w+\.\w+', part) \
                 and not part.startswith('http'):
                comp['user'] = part
            else:
                comp['pass'] = part
        self.comp = comp
        self._proxy_input = '{}://{}:{}@{}:{}'.format(comp['schema'], comp['user'], comp['pass'], comp['ip'], comp['port'])
