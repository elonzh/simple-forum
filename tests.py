# -*- coding: utf8 -*-
from coverage import coverage

cov = coverage(branch=True, omit=["flask/*", "tests.py"])
cov.start()

import os
import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app, db
from app.models import User, Post, Type


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:mysqladmin@localhost/test?charset=utf8"
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        # make valid nicknames
        # n = User.make_valid_nickname("John_123")
        # assert n == "John_123"
        # n = User.make_valid_nickname("John_[123]\n")
        # assert n == "John_123"
        # create a user
        u = User(nickname="john", account="john@example.com", password="123")
        db.session.add(u)
        db.session.commit()
        assert u.is_authenticated() == True
        assert u.is_active() == True
        assert u.is_anonymous() == False
        assert u.id == int(u.get_id())

    def test_avatar(self):
        # create a user
        u = User(nickname="john", account="john@example.com", password="123")
        avatar = u.avatar(128)
        expected = "http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6"
        assert avatar[0:len(expected)] == expected

    def test_follow(self):
        u1 = User(nickname="john", account="john@example.com", password="123")
        u2 = User(nickname="susan", account="susan@example.com", password="123")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert u1.unfollow(u2) == None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) == None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().nickname == "susan"
        assert u2.followers.count() == 1
        assert u2.followers.first().nickname == "john"
        u = u1.unfollow(u2)
        assert u != None
        db.session.add(u)
        db.session.commit()
        assert u1.is_following(u2) == False
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(account="john@example.com", password="123")
        u2 = User(account="susan@example.com", password="123")
        u3 = User(account="mary@example.com", password="123")
        u4 = User(account="david@example.com", password="123")
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        type1 = Type(name="1")
        type2 = Type(name="2")
        type3 = Type(name="3")
        type4 = Type(name="4")
        p1 = Post(title="1", body="post from john", author=u1, timestamp=utcnow + timedelta(seconds=1), type=type1)
        p2 = Post(title="1", body="post from susan", author=u2, timestamp=utcnow + timedelta(seconds=2), type=type2)
        p3 = Post(title="1", body="post from mary", author=u3, timestamp=utcnow + timedelta(seconds=3), type=type3)
        p4 = Post(title="1", body="post from david", author=u4, timestamp=utcnow + timedelta(seconds=4), type=type4)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        u1.follow(type1)
        u1.follow(type2)
        u1.follow(type4)
        u2.follow(type2)
        u2.follow(type3)
        u3.follow(type3)
        u3.follow(type4)
        u4.follow(type4)
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1[0].id == p4.id
        assert f1[1].id == p2.id
        assert f1[2].id == p1.id
        assert f2[0].id == p3.id
        assert f2[1].id == p2.id
        assert f3[0].id == p4.id
        assert f3[1].id == p3.id
        assert f4[0].id == p4.id

    def test_delete_post(self):
        # create a user and a post
        u = User(nickname="john", account="john@example.com", password="123")
        type = Type(name="1")
        p = Post(title="1", body="test post", author=u, timestamp=datetime.utcnow(), type=type)
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        # query the post and destroy the session
        p = Post.query.get(1)
        db.session.remove()
        # delete the post using a new session
        db.session = db.create_scoped_session()
        db.session.delete(p)
        db.session.commit()


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "\nHTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()
