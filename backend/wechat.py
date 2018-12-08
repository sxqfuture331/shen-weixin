# -*- coding: utf-8 -*-
'''
封装微信调用逻辑
'''
import os
from datetime import datetime
import uuid

from flask import abort

from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy import WeChatClient

from .tuling import get_reply as tuling_reply
from .ticket_cache import TicketCache, get_ticket


# ticket缓存
cache_path = os.path.join(os.environ['PROJ_ROOT'], 'ticket.cache')
tc_obj = TicketCache(cache_path)

# 微信配置
APPID = 'wxac298b4a65250efb'
SECRET = 'a1a6c258f4b739e0db7df9ab3d8e9273'
TOKEN = '123456'
AES_KEY = '8O2AvUrZNmPncUHXfhxZ2cYWJCWScZvwlbIBHqD5gfu'
# 实例化微信(公众号)客户端
client = WeChatClient(APPID, SECRET)
# 获取微信公众平台-自动回复设置
autoreply_info = client.message.get_autoreply_info()
# 自动回复中，图片id（媒体id）
media_id = None
if 'message_default_autoreply_info' in autoreply_info:
    media_id = autoreply_info['message_default_autoreply_info']['content']


def print_msg_info(msg):
    '''
    公共属性: http://docs.wechatpy.org/zh_CN/master/messages.html#id2
    '''
    print('消息ID:', msg.id)
    print('来源用户:', msg.source)
    print('目标用户:', msg.target)
    print('发送时间:', msg.create_time)
    print('消息类型:', msg.type)

def verify_signature(signature, timestamp, nonce):
    '''
    验证签名
    '''
    try:
        check_signature(TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)

def get_img_replay(msg):
    '''
    得到图片回复
    '''
    global media_id
    from wechatpy.replies import ImageReply

    # 实例化 图片回复
    img_rpy = ImageReply()
    # 指定图片内容
    img_rpy.media_id = media_id
    # 创建回复
    if media_id is None:
        img_rpy = '这里需要一个图片'
    return create_reply(img_rpy, msg)

def raw_reply(data):
    '''
    明文消息回复
    '''
    # plaintext mode(明文模式)
    msg = parse_message(data) # 解析消息
    # 显示微信消息包含的信息
    print_msg_info(msg)
    # import ipdb as pdb; pdb.set_trace()
    # 判断消息类型
    if msg.type == 'text':
        # 文本消息
        if msg.content.lower() in ['2']:
            # 如果文本内容为 'img' 或 'image'
            # 得到图片回复
            reply = get_img_replay(msg)
        elif msg.content.lower() in ['1']:
            # 图文消息
            from wechatpy.replies import ArticlesReply
            # 对象字典
            from wechatpy.utils import ObjectDict
            # 实例化图文消息
            reply = ArticlesReply(message=msg)
            # 数据
            data = {
                'title': 'JS-SDK',
                'description': '尝试一下JS-SDK',
                'image': 'https://res.wx.qq.com/mpres/htmledition/images/bg/bg_login_banner_v53a7b38.jpg',
                'url': 'http://blog.gsw945.com/'
            }
            '''
            # 第一种方式
            # simply use dict as article
            reply.add_article(data)
            '''
            # 第二种方式
            # or you can use ObjectDict
            article = ObjectDict()
            article.title = data['title']
            article.description = data['description']
            article.image = data['image']
            article.url = data['url']
            reply.add_article(article)
        elif msg.content.lower() in ['3']:
            reply = create_reply('[Smirk][Smart]\nhttp://shenzhiwen.wx.gsw945.com/upload-image', msg)
            # 文本消息对象，content属性，即为消息内容(str类型)
        else:
            # reply = create_reply(msg.content, msg)
            reply = create_reply(tuling_reply(msg.content), msg)
    elif msg.type == 'link':
        txt = '\n'.join([
            '标题: {}'.format(msg.title),
            '描述: {}'.format(msg.description),
            '链接: {}'.format(msg.url)
        ])
        reply = create_reply(txt, msg)
    elif msg.type == 'image':
        txt = '\n'.join([
            '访问地址: {}'.format(msg.image),
            '媒体ID: {}'.format(msg.media_id)
        ])
        reply = create_reply(txt, msg)
    elif msg.type == 'voice':
        txt = '\n'.join([
            '格式: {}'.format(msg.format),
            '识别结果: {}'.format(msg.recognition),
            '媒体ID: {}'.format(msg.media_id)
        ])
        reply = create_reply(txt, msg)
    else:
        # import ipdb as pdb; pdb.set_trace()
        reply = create_reply('抱歉，暂时不能处理[{}]类型的消息'.format(msg.type), msg)
    return reply.render()

def encrypt_reply(data, msg_signature, timestamp, nonce):
    '''
    加密消息回复
    '''
    # encryption mode（加密模式）
    from wechatpy.crypto import WeChatCrypto

    # 实例化加密工具
    crypto = WeChatCrypto(TOKEN, AES_KEY, APPID)
    try:
        # 解密消息
        msg = crypto.decrypt_message(
            data,
            msg_signature,
            timestamp,
            nonce
        )
    except (InvalidSignatureException, InvalidAppIdException):
        abort(403)
    else:
        return crypto.encrypt_message(raw_reply(msg), nonce, timestamp)

def random_uuid():
    '''获取随机uuid'''
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return uuid.uuid5(uuid.NAMESPACE_DNS, ts).hex

def jsapi_response(url):
    '''jsapi签名请求响应'''
    global client, tc_obj
    # 随机字符串
    noncestr = random_uuid()
    # 时间戳
    timestamp = datetime.now().timestamp()
    # 获取 微信请求零时票据
    # ticket = client.jsapi.get_jsapi_ticket()
    ticket = get_ticket(tc_obj, client, timestamp)
    # 获取 jsapi签名
    signature = client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
    return {
        'appId': APPID,
        'nonceStr': noncestr,
        'timestamp': timestamp,
        'signature': signature
    }

def get_media_url(media_id):
    global client
    return client.media.get_url(media_id)












