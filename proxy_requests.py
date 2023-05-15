import requests
import os
import random


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
