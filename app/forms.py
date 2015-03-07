# -*- coding:utf-8 -*-
__author__ = "erliang"

from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, Optional

from app import db
from models import Type


# 使用Flask-Security form.py 默认表单
# class RegisterForm(Form):
# # nickname = StringField("Nickname", validators=[DataRequired(message="请输入昵称"),
#     # Length(min=4, max=64, message="昵称长度为4到32位")])
#     # email = StringField("Email", validators=[DataRequired(),
#     # Email(message="邮箱格式不正确")])
#     account = StringField("Account", validators=[DataRequired(message="请输入账号"),
#                                                  Regexp("[A-Za-z0-9_]", message="密码由数字,字母或下划线组成"),
#                                                  Length(min=4, max=32, message="账号长度为4到32位")])
#     password = PasswordField("Password", validators=[DataRequired(message="请输入密码"),
#                                                      Regexp("[A-Za-z0-9~!@#$%^&*_.]", message="密码由数字,字母或~!@#$%^&*_.组成"),
#                                                      Length(min=6, max=32, message="密码长度为6到32位"),
#                                                      EqualTo("confirm", message="密码不一致")])
#     confirm = PasswordField("Repeat Password")
#
#
# class LoginForm(Form):
#     account = StringField("Account", validators=[DataRequired(message="请输入账号"),
#                                                  Regexp("[A-Za-z0-9_]", message="密码由数字,字母或下划线组成")])
#     password = PasswordField("password", validators=[DataRequired(message="请输入密码")])
#     remember_me = BooleanField("remember_me", default=False)


class EditorTitleForm(Form):
    try:
        from sqlalchemy.exc import ProgrammingError
        _chroices = db.session.query(Type.id, Type.name).all()
    except ProgrammingError as e:
        _chroices = []
    type = SelectField("Types", validators=[DataRequired()], choices=_chroices,
                       coerce=int)  # 选择表单默认value值类型为字符串,"coerce=int"选项
    title = StringField("Title", validators=[DataRequired(message="请输入标题"), Length(max=32, message="标题最多为32字")])


class ProfileForm(Form):
    avatar = FileField("头像", validators=[Optional(),
                                         FileAllowed(["jpeg", "png", "gif", "jpg"], message="文件格式不正确")])
    nickname = StringField("昵称", validators=[Optional(),
                                             Length(min=4, max=10, message="昵称为4到10个字符"),
                                             # TODO:正则表达式中文匹配存在问题
                                             Regexp("[0-9a-zA-Z\u4e00-\u9fa5\-_]{4,10}", message="昵称仅包含中文，字母，数字或\"-\"\"_\"")])


class CetForm(Form):
    zkzh = StringField("zkzh", validators=[Length(max=15, message="哎哎哎，多了，多了~"),
                                           Regexp("[0-9]{15}", message="15位数字啊，同志！")])
    xm = StringField("xm", validators=[Length(max=6, message="哪有这么长的名字啊")])