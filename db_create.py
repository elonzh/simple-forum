#!flask/bin/python
# -*- coding:utf-8 -*-
from app import db

db.create_all(bind=None)

from datetime import datetime
from app.models import User, Type, Role

types = {"极客秀": "在这里尽情展现自己",
         "创意": "思想的火花",
         "技能交换": "合作愉快",
         "分享": "赠人玫瑰，手留余香",
         "活动": "大家一起来",
         "问与答": "答疑解惑",
         "交易": "废物利用",
         "兼职招聘": "赚点钱买卫龙",
         "失物招领": "姑娘你的益达！",
         "吐槽": "不吐不快！",
         "其他": "找不到啦~~"}
for key in types:
    db.session.add(Type(name=key, description=types[key]))

roles = {"user": "user",
         "moderator": "moderator",
         "admin": "admin",
         "superuser": "superuser"}
for key in roles:
    db.session.add(Role(name=key, description=roles[key]))

superuser = User(nickname="erliang",
                 email="eviler_liang@foxmail.com",
                 password="123456",
                 confirmed_at=datetime.utcnow(),
                 active=True,
                 roles=[Role.query.filter_by(name="superuser").first()])
db.session.add(superuser)
db.session.commit()