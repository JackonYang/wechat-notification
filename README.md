# wechat-notification

通过微信公众号, 将通知消息推送至个人微信. 无需认证公众号, 可群发.

v1.0 版本, 支持用户主动订阅 / 退订推送消息, 因稳定性低, 应用场景少, 不再继续维护.
代码和文档统一移至 listener-mode 目录下.

## DEMO

#### settings.py

配置 redis, 微信连接信息.

执行获取微信昵称对应的 ID

```python 
$ python wechat.py
```

将接受推送消息的帐号 ID 填写至 settings.py 的 `NOTIFY_IDS` 变量中.

```python
$ python demo.py
```

微信号会会收到推送消息.

这个版本更加适合程序调用.

## 开发环境

```shell
$ sudo pip install -r requirements.txt
```
