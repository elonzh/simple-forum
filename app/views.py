# -*- coding:utf-8 -*-
__author__ = "erliang"

import re
import qiniu
import requests
from urlparse import urljoin
from datetime import datetime
from os import path
from bs4 import BeautifulSoup, SoupStrainer
from markdown import markdown
from flask import render_template, flash, redirect, url_for, request, g, json, abort
from flask.ext.security import current_user, login_required
from flask.ext.sqlalchemy import get_debug_queries

from app import app, lm, db, cache, q, bucket
from models import User, Post, Type, PostFile
from forms import CetForm, EditorTitleForm, ProfileForm
from config import POSTS_PER_PAGE, DATABASE_QUERY_TIMEOUT, basedir


@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                query.statement, query.parameters, query.duration, query.context))
    return response


@app.teardown_request
def teardown_request(exception):
    if exception:
        print exception


@app.errorhandler(400)
def internal_error(error):
    flash(error, category="danger")


@app.errorhandler(404)
def internal_error(error):
    return render_template("404.html", title="页面没找到～"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return error


@app.route("/version")
@cache.cached(86400)
def version():
    with open(path.join(basedir, "README.md"), "rb") as md_file:
        text = markdown(md_file.read())
        return render_template("version.html", text=text)


# Flask-Security Views Start
# 使用url_for_security()定向至模块默认视图
# @app.route("/login", methods=["GET", "POST"])
# @cache.cached(86400)
# def login():
# login_form = LoginForm()
# if login_form.validate_on_submit():
# user = User.query.filter_by(email=login_form.email.data).first()
# assert isinstance(user, User)
#         if user:
#             if user.password == login_form.password.data:
#                 login_user(user, login_form.remember_me.data)
#                 return redirect(request.args.get("next") or url_for("index"))
#             else:
#                 flash("账号或密码不正确！")
#     return render_template("login.html", title="登陆", login_form=login_form)
#     login_user_form = LoginForm()
#     if login_user_form.validate_on_submit():
#         user = User.query.filter_by(email=login_user_form.email.data).first()
#         assert isinstance(user, User)
#         if user:
#             if user.password == login_user_form.password.data:
#                 login_user(user, login_user_form.remember.data)
#                 return redirect(request.args.get("next") or url_for("index"))
#             else:
#                 flash("账号或密码不正确！")
#     return render_template("security/login_user.html", login_user_form=login_user_form)
#
#
# @app.route("/logout")
# @login_required
# @cache.cached(86400)
# def logout():
#     logout_user()
#     return redirect(url_for("index"))
#
#
# @app.route("/register", methods=["GET", "POST"])
# @cache.cached(86400)
# def register():
#     register_form = RegisterForm()
#     if register_form.validate_on_submit():
#         if User.query.filter_by(email=register_form.email.data).first() is None:
#             news_type = Type.query.filter_by(name="校区新闻").first()
#             notice_type = Type.query.filter_by(name="通知公告").first()
#             user = User(email=register_form.email.data,
#                         password=register_form.password.data,
#                         last_seen=datetime.utcnow())
#             db.session.add(user)  # 用户添加后才能进行操作
#             user.follow(news_type)
#             user.follow(notice_type)
#             db.session.commit()
#             login_user(user)
#             return redirect(request.args.get("next") or url_for("index"))
#         else:
#             flash("账号已被注册")
#     return render_template("register.html", title="注册", register_form=register_form)
#     register_user_form = RegisterForm()
#     if register_user_form.validate_on_submit():
#         if User.query.filter_by(email=register_user_form.email.data).first() is None:
#             user = user_datastore.create_user(email=register_user_form.email.data, password=register_user_form.password.data)
#             login_user(user)
#             return redirect(request.args.get("next") or url_for("index"))
#         else:
#             flash("账号已被注册")
#     return render_template("security/register_user.html", register_user_form=register_user_form)
#
#
# @app.route("/reset")
# @cache.cached(86400)
# def reset():
#     pass
#
# @app.route("/change")
# @cache.cached(86400)
# def change():
#     pass
#
#
# @app.route("/confirm")
# @cache.cached(86400)
# def confirm():
#     pass
# Flask-Security Views End


@app.route("/welcome")
@cache.cached(86400)
def welcome():
    return render_template("welcome.html")


@app.route("/")
@app.route("/index")
@cache.cached(86400)
def index():
    try:
        page = int(request.args.get("p"))
    except (ValueError, TypeError):
        page = 1
    post_type = Type.query.filter_by(name=request.args.get("type")).first()
    if post_type:
        posts = Post.query.filter_by(type=post_type).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE,
                                                                                              False)
    else:
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template("index.html", title="工大包打听", posts=posts, type=post_type)


@app.route("/article/<int:post_id>")
@cache.cached(86400)
def article(post_id):
    """
    文章详情页
    :param post_id: 文章的数据库id
    :return: 文章详情页页面
    """
    post = Post.query.get(post_id)
    return render_template("article.html", title=post.title, post=post)


@app.route("/write", methods=["GET", "POST"])
@login_required
@cache.cached(86400)
def write():
    """
    新建文章与再编辑功能
    """
    # TODO:sae上新建文章会出现提交两次，待修复
    editor_title_form = EditorTitleForm()
    content = None
    # 获取要编辑的文章
    post_id = request.args.get("post_id")
    if post_id and request.method == "GET":
        post = Post.query.get(post_id)
        if post:
            if post.author == g.user:
                editor_title_form.title.data = post.title
                editor_title_form.type.data = post.type_id
                content = post.body
            else:
                flash("是你的就是你的，不是你的就不要乱动~", category="warning")
        else:
            flash("哪有这篇文章嘛~", category="info")
    # 处理提交的文章
    if editor_title_form.validate_on_submit():
        body = ""
        try:
            body = request.form["body"]
        except KeyError:
            flash("请输入至少15个字", category="info")
        text = BeautifulSoup(body).text.strip()
        if len(text) >= 15:  # Html标签存在时body也不为空
            if post_id:  # 不能使用post判断，因为请求方法为 POST，没有获取到文章对象
                post = Post.query.get(post_id)
                if post:
                    if post.author == g.user:
                        post.title = editor_title_form.title.data
                        post.body = body
                        post.type_id = editor_title_form.type.data
                        # post.link = url_for("article", post_id=post.id)
                        # post.author = g.user
                        post.timestamp = datetime.utcnow()
                    else:
                        flash("是你的就是你的，不是你的就不要乱动~", category="warning")
                else:
                    flash("哪有这篇文章嘛~", category="info")
            else:
                post = Post(title=editor_title_form.title.data,
                            body=body,
                            type_id=editor_title_form.type.data,
                            author=g.user,
                            timestamp=datetime.utcnow())
            new_files = PostFile.query.filter_by(post_id=None).all()
            # 数据库查询时新建的post会被自动提交，此时post.id已不为null
            post.link = url_for("article", post_id=post.id)
            if new_files:
                for post_file in new_files:
                    post_file.post_id = post.id
                    db.session.add(post_file)
            db.session.commit()
            return redirect(urljoin(url_for("index"), "?type=%s" % post.type.name))
        flash("请输入至少15个字", category="info")
    return render_template("write.html", title="write", editor_title_form=editor_title_form, content=content)


@app.route("/upload/editor", methods=["GET", "POST"])
@login_required
@cache.cached(86400)
def upload_editor():
    """
    处理编辑器的后端请求
    :return: 返回处理结果
    """
    # TODO:sae上传图片无法正常显示，待修正
    # TODO:公式插入有问题，重置按钮只能重置标题
    action = request.args.get("action")
    result = {}
    with open(path.join(app.static_folder, "js/ueditor/php/config.json")) as fp:
        try:
            config = json.loads(re.sub(r"\/\*.*\*\/", "", fp.read()))
        except:
            config = []
    if action == "config":
        result = config
    elif action in ("uploadimage", "uploadvideo", "uploadfile"):
        upfile = request.files["upfile"]
        bucket_name = "hfut-uploads"
        bucket_url = "http://7vzoi5.com1.z0.glb.clouddn.com"  # hfut-uploads 的URL
        token = q.upload_token(bucket_name, None, policy={"detectMime": 1})
        ret, info = qiniu.put_data(token, None, upfile)
        if info.exception:
            print info.status_code, info.exception["error"]
        else:
            exist_flag = PostFile.query.filter_by(key=ret["key"]).count()
            if exist_flag == 0:  # 相同文件处理
                post_file = PostFile(bucket=bucket_name, private=False, key=ret["key"])
                db.session.add(post_file)
                db.session.commit()
            result = {
                "state": "SUCCESS",
                "url": urljoin(bucket_url, ret["key"]),
                "title": "图片",
                "original": "图片"
            }
    return json.dumps(result)


@app.route("/profile_manage", methods=["GET", "POST"])
@login_required
@cache.cached(86400)
def profile_manage():
    """
    用户资料编辑功能
    :return: 返回修改后的资料页面
    """
    profile_form = ProfileForm()
    if profile_form.validate_on_submit():
        # 修改头像
        if profile_form.avatar.data:
            avatar = profile_form.avatar.data
            bucket_name = "hfut-avatar"
            # 删除原来储存的头像
            if g.user.avatar_key:
                ret, info = bucket.delete(bucket_name, g.user.avatar_key)
                print(info)
                if info.exception:
                    print info.status_code, info.exception
                    abort(500)
            # 上传新的头像
            token = q.upload_token(bucket_name, None, policy={"detectMime": 1})
            ret, info = qiniu.put_data(token, None, avatar)
            if info.exception:
                print info.status_code, info.exception
                abort(500)
            g.user.avatar_key = ret["key"]
        # 修改昵称
        if profile_form.nickname.data:
            if g.user.nickname == profile_form.nickname.data or \
                            User.query.filter_by(nickname=profile_form.nickname.data).first() is not None:
                flash("昵称已被占用", category="info")
            else:
                g.user.nickname = profile_form.nickname.data
                flash("修改成功", category="success")
        db.session.add(g.user)
        db.session.commit()
    else:
        profile_form.nickname.data = g.user.nickname
    return render_template("profile_manage.html", title=g.user.nickname, profile_form=profile_form)


@app.route("/post_manage")
@login_required
@cache.cached(86400)
def post_manage():
    """
    用户文章管理功能
    :return: 文章管理页面
    """
    post_id = request.args.get("delete")
    if post_id:
        post = Post.query.get(post_id)
        if post and post.author == g.user:
            # 批量删除文章关联的文件
            files = post.files
            for post_file in files:
                ret, info = bucket.delete("hfut-uploads", post_file.key)
                if info.exception:
                    print info.status_code, info.exception
                    abort(500)
                db.session.delete(post_file)
            # 删除文章
            db.session.delete(post)
            db.session.commit()
            flash("删除成功", category="success")
        else:
            flash("删除失败", category="danger")
    return render_template("post_manage.html", title="管理文章")


@app.route("/cet", methods=["GET", "POST"])
@cache.cached(86400)
def cet():
    """
    四六级查询功能
    :return: 返回查询结果
    """
    result = None
    cet_form = CetForm()
    if cet_form.validate_on_submit():
        zkzh = cet_form.zkzh.data
        xm = cet_form.xm.data
        url = "http://www.chsi.com.cn/cet/query"
        params = {"zkzh": zkzh, "xm": xm}
        # 必须伪造头信息
        headers = {
              'Host': 'www.chsi.com.cn',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
              'Referer': 'http://www.chsi.com.cn/cet/',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

        r = requests.get(url, headers=headers, params=params)
        ss = SoupStrainer("table", class_="cetTable")
        bs = BeautifulSoup(r.text, parse_only=ss)
        results_strings = list(bs.stripped_strings)
        ret = {}
        for i in xrange(0, len(results_strings), 2):
            ret[results_strings[i].rstrip("：")] = results_strings[i+1]
        # 如果没有查到结果将是空字典
        result = ret
    return render_template("cet.html", title="四六级查询", cet_form=cet_form, result=result)