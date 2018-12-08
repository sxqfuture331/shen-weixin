# -*- coding: utf-8 -*-
'''
初始化Flask应用
'''
import os

from flask import (
    Flask, request, abort, url_for, jsonify,
    render_template_string, render_template
)
from .wechat import verify_signature, raw_reply, encrypt_reply, jsapi_response, get_media_url
from .database import db, Media


app = Flask(
    __name__,
    template_folder=os.path.join(os.environ['PROJ_ROOT'], 'frontend', 'templates'),
    static_folder=os.path.join(os.environ['PROJ_ROOT'], 'frontend', 'static')
)
# url_for()函数生成外部地址(_external=True时)需要的配置
app.config.update({
    'SERVER_NAME': 'shenzhiwen.wx.gsw945.com',
    'PREFERRED_URL_SCHEME': 'http'
})
# 数据库配置
db_uri = 'sqlite:///{0}'.format(os.path.join(os.environ['PROJ_ROOT'], 'data.sqlite'))
app.config.update({
    'SQLALCHEMY_DATABASE_URI': db_uri,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
db.init_app(app)
with app.test_request_context():
    # 在模拟的上下文环境中，创建数据库
    db.create_all()

@app.route('/index')
def index():
    # return url_for('index', _external=True)
    return render_template('index2.html')

@app.route('/upload-image')
def upload_image():
    return render_template('upload-image.html')

@app.route('/kuaidi100')
def kuaidi100():
    return '<a href="https://m.kuaidi100.com/" target="_blank">快递查询</a>'

@app.route('/', methods=['GET', 'POST'])
def wechat():
    # 微信请求公共参数
    # 签名
    signature = request.args.get('signature', '')
    # 时间戳
    timestamp = request.args.get('timestamp', '')
    # 随机字符串
    nonce = request.args.get('nonce', '')

    # 检查签名
    verify_signature(signature, timestamp, nonce)

    if request.method == 'GET':
        # GET方式->验证签名
        echo_str = request.args.get('echostr', '')
        return echo_str

    # POST方式->自动回复
    # 加密类型
    encrypt_type = request.args.get('encrypt_type', 'raw')
    # 消息签名
    msg_signature = request.args.get('msg_signature', '')

    if encrypt_type == 'raw':
        # 明文模式
        return raw_reply(request.data)
    # 加密模式
    return encrypt_reply(request.data, msg_signature, timestamp, nonce)

@app.route('/jsapi', methods=['GET', 'POST'])
def jsapi():
    url = request.values.get('url')
    data = jsapi_response(url)
    return jsonify(data)

@app.route('/media', methods=['GET', 'POST'])
def media():
    # 获取参数
    media_id = request.values.get('media_id')
    media_type = request.values.get('media_type')
    # 记录保存到数据库
    obj = Media()
    obj.media_id = media_id
    obj.media_type = media_type
    db.session.add(obj)
    db.session.commit()
    data = {
        'error': 0,
        'desc': '保存成功',
        'url': get_media_url(media_id)
    }
    return jsonify(data)

@app.route('/image-list', methods=['GET', 'POST'])
def image_list():
    img_objs = Media.query.all()
    imgs = []
    for obj in img_objs:
        imgs.append(get_media_url(obj.media_id))
    data = {
        'error': 0,
        'desc': '获取数据成功',
        'imgs': imgs
    }
    return jsonify(data)