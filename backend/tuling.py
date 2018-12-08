# -*- coding: utf-8 -*-
'''
图灵机器人调用
'''
import requests

def get_reply(msg):
    #改成你自己的图灵机器人的api，上图红框中的内容，不过用我的也无所谓，只是每天自动回复的消息条数有限
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': '5d01acc49b1c4bde8ec14c157fba6926',  # Tuling Key
        'info': msg,  # 这是我们发出去的消息
        'userid': 'wechat-robot',  # 这里你想改什么都可以
    }
    # 我们通过如下命令发送一个post请求
    r = requests.post(apiUrl, data=data).json()
    return r.get('text')