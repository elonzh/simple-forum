# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import qiniu
import os
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail
from flask.ext.cache import Cache
from flask.ext.security import SQLAlchemyUserDatastore, Security
from flask.ext.admin import Admin
from flask.ext.babelex import Babel

from utilities import momentjs
from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, QINIU_ACCESS_KEY, QINIU_SECRET_KEY

# 初始化应用
app = Flask(__name__)
app.config.from_object("config")
# 初始化多语言工具(Flask-BabelEx)
babel = Babel(app)
# 初始化数据库管理工具(Flask-SQLAlchemy, Flask-Migrate, Flask-Script)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
# 初始化登陆接口(Flask-Login)
lm = LoginManager(app)
lm.login_view = "login"
lm.login_message = "您需要登录后访问本页面～"
# 初始化安全模块(Flask-Security)
# db 实例生成后才能导入
from models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
# 初始化后台管理模块(Flask-Admin)
admin = Admin(app, name="后台管理", base_template="admin/customized_base.html")
# 初始化邮件模块(Flask-Mail)
mail = Mail(app)
# 初始化缓存模块(Flask-Cache)
cache = Cache(app)

app.jinja_env.globals["momentjs"] = momentjs

# 初始化七牛服务
q = qiniu.Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
bucket = qiniu.BucketManager(q)

if "SERVER_SOFTWARE" in os.environ:
    import logging
    from logging.handlers import SMTPHandler

    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), "no-reply@" + MAIL_SERVER, ADMINS, "网站出现错误",
                               credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

else:
    import logging
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler("run.log", "a", 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("APP startup")

from app import views, models, admin_views