# -*- coding:utf-8 -*-
__author__ = "erliang"

from hashlib import md5

from flask.ext.security import UserMixin, RoleMixin

from app import db


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return "<Role %r>" % (self.name)

    def __unicode__(self):
        return self.name

class User(db.Model, UserMixin):
    # Flask-Security 的 UserMixin 继承自 Flask-Login 并额外添加了 is_active(), get_auth_token(), has_role() 三个方法
    id = db.Column(db.Integer, primary_key=True)
    avatar_key = db.Column(db.String(128))
    nickname = db.Column(db.String(10), index=True, unique=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    # Flask-Security 要求的字段
    email = db.Column(db.String(120), index=True, nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(39))
    current_login_ip = db.Column(db.String(39))
    login_count = db.Column(db.BigInteger())

    def avatar(self, size=50):
        if self.avatar_key:
            return "http://7vzpsx.com1.z0.glb.clouddn.com/%s?imageView2/1/w/%s/interlace/1" % (
            self.avatar_key, str(size))
        # 使用Gravatar多说国内镜像加速, d 为默认头像类型 http://en.gravatar.com/site/implement/images/
        return "".join(["http://gravatar.duoshuo.com/avatar/", md5(self.email).hexdigest(), "?d=identicon&s=", str(size)])

    def __repr__(self):
        return "<User %r>" % (self.nickname)

    def __unicode__(self):
        if self.nickname:
            return self.nickname
        return "无名氏：%s" % self.email


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(45), nullable=False, unique=True)
    description = db.Column(db.String(255))
    posts = db.relationship("Post", backref="type", lazy="dynamic")

    def __repr__(self):
        return "<Type %r>" % (self.name)

    def __unicode__(self):
        return self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    timestamp = db.Column(db.DateTime())
    link = db.Column(db.String(180))
    pined = db.Column(db.Boolean(), default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("type.id"))
    files = db.relationship("PostFile", backref="belongto", lazy="dynamic")

    def __repr__(self):
        return "<Post %r>" % (self.title)

    def __unicode__(self):
        return self.title


class PostFile(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    bucket = db.Column(db.String(64), nullable=False)
    private = db.Column(db.Boolean(), default=False)
    key = db.Column(db.String(128), nullable=False, unique=True)
    post_id = db.Column(db.Integer(), db.ForeignKey("post.id"))

    def __repr__(self):
        return "<PostFile %r belong to %r>" % (self.key, self.post_id)

    def __unicode__(self):
        return self.key