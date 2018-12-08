# -*- coding: utf-8 -*-
'''
票据缓存管理
'''
import os
import json
from collections import OrderedDict
from datetime import datetime

import chardet


class TicketCache(object):
    """票据缓存"""
    def __init__(self, cache_path):
        super(TicketCache, self).__init__()
        self.cache_path = cache_path
        self.data = None

    def read(self):
        '''读取配置'''
        if os.path.exists(self.cache_path):
            bc = open(self.cache_path, 'rb').read()
            encoding = chardet.detect(bc).get('encoding', 'utf-8')
            self.data = json.loads(
                bc.decode(encoding, 'ignore'),
                object_pairs_hook=OrderedDict
            )
        return self.data

    def write(self, data):
        '''保存配置'''
        self.data = data
        with open(self.cache_path, 'w') as f:
            f.write(json.dumps(self.data, indent=4, ensure_ascii=False))

def get_ticket(tc_obj, client, timestamp=None):
    '''
    获取ticket
    '''
    # 过期时间（应小于但接近 微信要求的7200秒）
    expire = 3600 * 1.9
    # 当前时间戳
    ts_now = timestamp or datetime.now().timestamp()
    # 旧的缓存
    tc_old = tc_obj.read() or {}
    # 旧的时间戳
    ts_old = tc_old.get('timestamp', 0)
    # 旧的ticket
    ticket_old = tc_old.get('ticket', None)
    if not bool(ticket_old) or ts_now - ts_old > expire:
        # 旧的ticket无效
        # 或者，当前时间戳和配置相比，大于过期时间差，说明已过期
        # 过期了，则需要获取新的ticket
        # 获取 微信请求零时票据
        ticket = client.jsapi.get_jsapi_ticket()
        # 更新缓存
        tc_obj.write({
            'timestamp': ts_now,
            'ticket': ticket
        })
        # print('#new#' * 30)
        return ticket
    else:
        # print('=cache=' * 20)
        return ticket_old
