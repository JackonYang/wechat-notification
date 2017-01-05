# -*- coding:utf-8 -*-
import os


REDIS_CONN = {
    'host': os.getenv('REDIS_HOST', '127.0.0.1'),
    'port': 6379,
    'db': 8,
}

WECHAT_CONN = {
    'username': '',
    'password': '',
}

NOTIFY_IDS = [
    '2271762240',  # k
]

MSG_SIGNATURE = 'AutoSend by Python'


try:
    from local_settings import *  # noqa
except Exception as e:
    pass
