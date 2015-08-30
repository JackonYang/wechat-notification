# -*- Encoding: utf-8 -*-
import json
import time
from os.path import join, dirname, exists
from os import makedirs

import tornado.ioloop
import tornado.web
from tornado.options import define, options

from wechat_sdk import WechatBasic, WechatExt
from wechat_sdk.exceptions import NeedLoginError

from log4f import debug_logger

log = debug_logger(join(dirname(__file__), 'log'), 'root')

define("username", default='username', help="username of wechat", type=str)
define("password", default='password', help="password of wechat", type=str)
define("token", default='', help="token of wechat", type=str)
define("port", default=8000, help="run on the given port", type=int)
define("debug", default=False, help="run in Debug mode", type=bool)


today = lambda: time.strftime('%Y%m%d', time.localtime())
cookie_dir = join(dirname(__file__), 'cookie')


def login_http(username, password):
    wechat = WechatExt(username, password)
    wechat.login()

    if not exists(cookie_dir):
        makedirs(cookie_dir)
    fn = join(cookie_dir, 'cookie_{}.html'.format(today()))
    with open(fn, 'w') as f:
        json.dump(wechat.get_token_cookies(), f, indent=4)

    return wechat


def login_cookie(username, password):
    fn = join(cookie_dir, 'cookie_{}.html'.format(today()))
    if not exists(fn):
        raise NeedLoginError

    with open(fn, 'r') as f:
        kwargs = json.load(f)

    return WechatExt(username=username, password=password,
                     login=False, **kwargs)


def action(username, password, meth_name, *args, **kwargs):
    try:
        wechat = login_cookie(username, password)
        ret = getattr(wechat, meth_name)(*args, **kwargs)
    except NeedLoginError:
        wechat = login_http(username, password)
        ret = getattr(wechat, meth_name)(*args, **kwargs)

    return ret


user_fakeid = dict()


class CmdRobot:
    @classmethod
    def cmd_dy(self, fakeid, user):
        user_fakeid[user] = fakeid
        return 'subscribed. nickname={}, fakeid={}'.format(user, fakeid)

    @classmethod
    def cmd_td(self, fakeid, user):
        if user in user_fakeid:
            user_fakeid.pop(user)
        return 'unsubscribe successfully. nickname={}'.format(user)

    @classmethod
    def cmd_ls(self, fakeid, user):
        if user_fakeid:
            return 'user list:\n{}'.format('\n'.join(user_fakeid))
        else:
            return 'no user subscribed'

    @classmethod
    def cmd_help(self, fakeid, user):
        return u'回复: \ndy -- 订阅\ntd -- 退订\nls -- 已订阅用户列表\nhelp -- 帮助文档'


class WechatListener(tornado.web.RequestHandler):

    def auth(self):
        args = ['signature', 'timestamp', 'nonce']
        kwargs = {k: self.get_argument(k, '') for k in args}

        wechat = WechatBasic(token=options.token)
        if not wechat.check_signature(**kwargs):
            self.set_status(403)
            self.write('auth failed')
            self.finish()

    def get(self):
        """auth

        """
        self.auth()

        self.write(self.get_argument('echostr', 'echostr not found'))

    def post(self):
        log.debug('enter')
        self.auth()

        wechat_basic = WechatBasic(token=options.token)
        wechat_basic.parse_data(self.request.body)

        base_msg = wechat_basic.get_message()
        c, t = base_msg.content, base_msg.time

        log.info('recieve: {}, {}'.format(c.encode('utf8'), t))

        cmd = CmdRobot.cmd_help
        fakeid, user = None, None
        try:
            raw_msg = action(options.username, options.password,
                             'get_message_list')
            msgs = json.loads(raw_msg)['msg_item']
            for msg in msgs:
                if c == msg['content'] and t == msg['date_time']:
                    fakeid = msg['fakeid']
                    user = msg['nick_name'].encode('utf8')
                    log.info('found. {}, {}'.format(fakeid, user))
                    cmd = getattr(CmdRobot, 'cmd_{}'.format(c.encode('utf8')).lower(),
                                  CmdRobot.cmd_help)
                    break
            else:
                log.error('no match. {}'.format(msgs[0]['content']))
                self.write(wechat_basic.response_text(
                    'system error. please wait a second and send it again\n'))
        except Exception as e:
            log.error(e)
            pass

        self.write(wechat_basic.response_text(cmd(fakeid, user)))
        log.debug('exit')


class WechatSender(tornado.web.RequestHandler):

    def get(self):
        msg = self.get_argument('msg')

        for fakeid in user_fakeid.values():
            action(options.username, options.password,
                   'send_message', fakeid, msg)
        self.write('msg sent to {} users: {}'.format(len(user_fakeid),
                                                     ', '.join(user_fakeid)))


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/wechat-api/listen", WechatListener),
        (r"/wechat-api/send", WechatSender),
        ],
        debug=options.debug)
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
