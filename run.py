# -*- coding: utf-8 -*-
'''
启动文件
'''
import socket
import socks

socks.set_default_proxy(socks.SOCKS5, "47.104.104.132", 3080)
socket.socket = socks.socksocket


import os
os.environ['PROJ_ROOT'] = os.path.dirname(os.path.abspath(__file__))

from backend.main import app


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5656, debug=True)