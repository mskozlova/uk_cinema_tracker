import requests
import time
import json
import random

from functools import lru_cache
from functools import wraps

HEADERS = {
}

def retry(times=5):
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            sleep_time = 1.0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    print(
                        'Exception thrown when attempting to run %s, attempt '
                        '%d of %d. Sleeping for %f seconds' % (func, attempt, times, sleep_time)
                    )
                    attempt += 1
                    time.sleep(sleep_time + random.random())
                    sleep_time *= 2.0
            return func(*args, **kwargs)
        return newfn
    return decorator

def hash_dict(func):
    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HDict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped

@hash_dict
@lru_cache
@retry()
def get_json(revision: int, url: str, additional_headers: dict={}, use_proxy=False) -> dict:
    headers = {
        **HEADERS,
        **additional_headers,
    }
    if not use_proxy:
        r = requests.get(url, headers=headers)
    else:
        func_url = 'https://functions.yandexcloud.net/d4e5ltvrso9hp4qk0bg3'
        func_headers = {
            'Authorization': 'Api-Key AQVNyBGKQ8Y_VUQSQxYbrPxlfYdwWv08h3u6-yLa'
        }
        func_data = {
            "method": "GET",
            "url": url,
            "headers": headers,
        }
        r = requests.post(func_url, json=func_data, headers=func_headers)
        time.sleep(1.0 + random.random())
        return json.loads(r.json()['response']['text'])
    time.sleep(0.1)
    return r.json()

@hash_dict
@lru_cache
@retry()
def get_text(revision: int, url: str, additional_headers: dict={}) -> str:
    headers = {
        **HEADERS,
        **additional_headers,
    }
    r = requests.get(url, headers=headers)
    time.sleep(0.1)
    return r.text
    
@hash_dict
@lru_cache
@retry()
def post_with_json_response(revision: str, url: str, data: str, additional_headers: dict = {}) -> dict:
    headers = {
        **HEADERS,
        **additional_headers,
    }
    r = requests.post(url, data=data, headers=headers)
    time.sleep(0.1)
    return r.json()

@hash_dict
@lru_cache
@retry()
def post_with_text_response(revision: str, url: str, data: str, additional_headers: dict = {}) -> str:
    headers = {
        **HEADERS,
        **additional_headers,
    }
    r = requests.post(url, data=data, headers=headers)
    time.sleep(0.1)
    return r.text
