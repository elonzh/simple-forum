# -*- coding: utf-8 -*-
__author__ = "erliang"

from flask import request, session, g
from flask.ext.admin import AdminIndexView, expose
from flask.ext.admin.form import rules
from flask.ext.admin.contrib.sqla import ModelView, filters

from app import admin, db, babel
from models import User, Post


@babel.localeselector
def get_locale():
    override = request.args.get("lang")
    if override:
        session["lang"] = override
    return session.get("lang", "zh")

class MyView(AdminIndexView):
    def is_accessible(self):
        if g.user.has_role("superuser"):
            return True
        return False

    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class UserModelView(ModelView):
    def is_accessible(self):
        if g.user.has_role("superuser"):
            return True
        return False

    column_labels = {"nickname":"昵称",
                     "email":"邮箱",
                     "active":"可用",
                     "confirmed_at":"邮箱验证时间",
                     "last_login_at":"上次登录时间",
                     "current_login_at":"当前登录时间",
                     "last_login_ip":"上次登录IP",
                     "current_login_ip":"当前登录IP",
                     "login_count":"登录次数"}

    column_list = ("id",
                   "nickname",
                   "email",
                   "active",
                   "confirmed_at",
                   "last_login_at",
                   "current_login_at",
                   "last_login_ip",
                   "current_login_ip",
                   "login_count")

    form_create_rules = ("nickname", "email", "active")
    form_edit_rules = form_create_rules

    def __init__(self, **kwargs):
        super(UserModelView, self).__init__(User, db.session, **kwargs)

class PostModelView(ModelView):
    def is_accessible(self):
        if g.user.has_role("superuser"):
            return True
        return False

    column_labels = {"title":"标题",
                     "author":"作者",
                     "timestamp":"修改时间",
                     "pined":"置顶",
                     "link":"链接",
                     "body":"正文",
                     "type":"类型"}

    column_list = ("id",
                   "title",
                   "author",
                   "timestamp",
                   "pined")

    column_searchable_list = ("title", User.nickname)

    column_sortable_list = ("title",
                            ("author", User.nickname),
                           "timestamp",
                           "pined")

    column_filters = ("title", "body")

    form_edit_rules = ("type", "title", "body", "author", "timestamp", "pined", "link")

    form_create_rules = form_edit_rules

    def __init__(self, **kwargs):
        super(PostModelView, self).__init__(Post, db.session, **kwargs)


admin.add_view(UserModelView(name="用户管理"))
admin.add_view(PostModelView(name="文章管理"))