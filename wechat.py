# -*- Encoding: utf-8 -*-
import json
import redis
from os.path import join, dirname
from wechat_sdk import WechatExt
# from wechat_sdk.exceptions import NeedLoginError

from log4f import debug_logger
import settings


LOGIN_TIMEOUT = 4 * 3600  # 4 hours
r = redis.StrictRedis(**settings.REDIS_CONN)
log = debug_logger(join(dirname(__file__), 'log/notify'), 'root.notify')


def login(username, password):
    d = r.get(username)
    if d:
        log.info('lazy login. use cookie, username={}'.format(username))
        return WechatExt(username, password, login=False, **json.loads(d))
    else:
        print username, password
        wechat = WechatExt(username, password, login=False)
        wechat.login()
        log.info('login to wechat server. username={}'.format(username))
        r.setex(username, LOGIN_TIMEOUT,
                json.dumps(wechat.get_token_cookies(), indent=4))
        return wechat


def init_info():
    rsp_str = login(**settings.WECHAT_CONN).get_user_list()
    for u in json.loads(rsp_str)['contacts']:
        name = u['nick_name'].encode('utf8')
        fakeid = u['id']
        r.set(fakeid, name)
        print '{:12} -- {}'.format(fakeid, name)


def send(msg_text):
    msg = u'{}. {}'.format(msg_text, settings.MSG_SIGNATURE)
    for fakeid in settings.NOTIFY_IDS:
        name = r.get(fakeid) or fakeid
        log.info(u'msg sent. user={}. msg={}'.format(name, msg))
        login(**settings.WECHAT_CONN).send_message(fakeid, msg)


if __name__ == "__main__":
    init_info()
    # send(u'亲爱的')
