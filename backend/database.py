# -*- coding: utf-8 -*-
'''数据库调用'''
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True, comment='主键ID')
    media_id = db.Column(db.String(255), nullable=False, comment='媒体ID') #　 unique=True,
    media_type = db.Column(db.String(32), nullable=False, comment='媒体类型')

    def __repr__(self):
        return '<Media [{!r}]>'.format(self.media_id)