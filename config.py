# -*- coding:utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = "KsawqWWASK212sauyt4"

QINIU_ACCESS_KEY = "OyPuCLYfJExWEB0V0_lTXA4i7Ic2SI8I2NOwq7Jf"
QINIU_SECRET_KEY = "zFae7U03gwm4PBFSHb1dvwT6cQMXL3VQ2-k6CIdN"

if "SERVER_SOFTWARE" in os.environ:
    from sae.const import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB

    SQLALCHEMY_DATABASE_URI = "mysql://{0:s}:{1:s}@{2:s}:{3:s}/{4:s}".format(MYSQL_USER, MYSQL_PASS, MYSQL_HOST,
                                                                             MYSQL_PORT, MYSQL_DB)
else:
    SQLALCHEMY_DATABASE_URI = "mysql://{0:s}:{1:s}@{2:s}:{3:s}/{4:s}".format("root", "mysqladmin", "localhost", "3306",
                                                                             "test")
SQLALCHEMY_POOL_RECYCLE = 5  # 修复SAE MySQL gone away
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 0.5
# 分页设置
POSTS_PER_PAGE = 10
# 全文搜索设置
# MAX_SEARCH_RESULTS = 20

# email server
MAIL_SERVER = "smtpcloud.sohu.com"
MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = "*******"
MAIL_USERNAME = "*******"
MAIL_PASSWORD = "*******"

# administrator list
ADMINS = ["*******"]

CACHE_TYPE = "memcached"
CACHE_KEY = 'view/%s'
CACHE_DEFAULT_TIMEOUT = 86400

# Flask-Security Configuration
# http://pythonhosted.org/Flask-Security/configuration.html
# Core
SECURITY_PASSWORD_HASH = "sha512_crypt"  # bcrypt(依赖pybcrypt), sha512_crypt, or pbkdf2_sha512.
SECURITY_PASSWORD_SALT = "82qyg2#$Wd}"
SECURITY_EMAIL_SENDER = "*******"
# URLs and Views
# SECURITY_POST_REGISTER_VIEW = "/register"
SECURITY_POST_CONFIRM_VIEW = "/profile_manage"
# SECURITY_POST_RESET_VIEW = "/reset"
SECURITY_POST_CHANGE_VIEW = "/profile_manage"
SECURITY_UNAUTHORIZED_VIEW = "/login"
# Feature Flags
SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_TRACKABLE = True
SECURITY_CHANGEABLE = True
# Email
SECURITY_EMAIL_SUBJECT_REGISTER = "欢迎注册"
SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = "密码重置成功"
SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = "重置您的密码"
SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = "密码修改成功"
SECURITY_EMAIL_SUBJECT_CONFIRM = "确认您的邮箱"
