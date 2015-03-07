# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XcHfutNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field()
    title = scrapy.Field()
    timestamp = scrapy.Field()
    body = scrapy.Field()
    type = scrapy.Field()

