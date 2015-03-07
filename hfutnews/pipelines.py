# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from app import db
from app.models import Post


class HfutnewsPipeline(object):
    def process_item(self, item, spider):
        news = Post(title=item["title"],
                    link=item["link"],
                    timestamp=item["timestamp"],
                    body=item["body"],
                    type=item["type"])
        try:
            db.session.add(news)
            db.session.commit()
        except:
            db.session.rollback()
        return item
