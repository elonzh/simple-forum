# -*- coding: utf-8 -*-
__author__ = 'erliang'

from urlparse import urljoin
from datetime import datetime
from time import mktime

from BeautifulSoup import BeautifulSoup
from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from app.models import Post, Type
from hfutnews.items import XcHfutNewsItem


NEWS_TYPE = Type.query.filter_by(name="校区新闻").first()
NOTICE_TYPE = Type.query.filter_by(name="通知公告").first()
REPORT_TYPE = Type.query.filter_by(name="讲座报告").first()
DEFAULT_TYPE = Type.query.filter_by(name="其他").first()


class XcSpider(BaseSpider):
    name = "xc"
    allowed_domains = ["xc.hfut.edu.cn"]
    start_urls = ["http://xc.hfut.edu.cn/120/list.htm",
                  "http://xc.hfut.edu.cn/121/list.htm",
                  "http://xc.hfut.edu.cn/xsdt/list.htm"]

    def make_utc_time(self, time_str):
        struct_time = datetime.strptime(time_str, "%Y-%m-%d")
        timestamp = mktime(struct_time.timetuple())
        utc_time = datetime.utcfromtimestamp(timestamp)
        return utc_time

    def body_url_handler(self, base_url, body):
        bs = BeautifulSoup(body)
        has_src_tags = bs.findAll(src=True)
        for tag in has_src_tags:
            tag["src"] = urljoin(base_url, tag["src"])
        has_href_tags = bs.findAll(href=True)
        for tag in has_href_tags:
            tag["href"] = urljoin(base_url, tag["href"])
        return bs

    def parse(self, response):
        sel = Selector(response)
        page_num = sel.xpath("//tr/td[2]/text()[5]").extract()
        assert page_num != []
        page_num = int(page_num[0].split("/")[-1].strip())
        for i in range(1, page_num + 1):
            url = response.url.replace("list", "".join(["list", str(i)]))
            yield Request(url, callback=self.parse_list)

    def parse_list(self, response):
        sel = Selector(response)
        split_url = response.url.split("/")
        if "120" in split_url:
            post_type = NEWS_TYPE
        elif "121" in split_url:
            post_type = NOTICE_TYPE
        elif "xsdt" in split_url:
            post_type = REPORT_TYPE
        else:
            post_type = DEFAULT_TYPE
        post_titles = sel.xpath("//div[@class=\"listinfo\"]//table[1]//a/@title").extract()
        post_urls = sel.xpath("//div[@class=\"listinfo\"]//table[1]//a/@href").extract()
        post_times = sel.xpath("//div[@class=\"listinfo\"]//table[1]//tr/td[3]/text()").extract()
        for i in range(len(post_urls)):
            url = urljoin("http://xc.hfut.edu.cn", post_urls[i])
            if not Post.query.filter_by(link=url).first():
                item = XcHfutNewsItem()
                item["title"] = post_titles[i]
                item["link"] = url
                item["timestamp"] = self.make_utc_time(post_times[i].strip())
                item["type"] = post_type
                yield Request(item["link"],
                              callback=lambda response, item=item: self.get_post_body(response, item))  # 使用匿名函数封装参数

    def get_post_body(self, response, item):
        sel = Selector(response)
        article = sel.xpath("//div[@portletmode=\"articleAttri\"]")
        assert article.extract() != []
        body = article.xpath("//div[@class=\"entry\"]").extract()[0]
        handled_body = self.body_url_handler(base_url="http://xc.hfut.edu.cn", body=body)
        item["body"] = handled_body
        return item