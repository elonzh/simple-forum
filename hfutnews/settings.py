# -*- coding: utf-8 -*-

# Scrapy settings for hfutnews project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'hfutnews'

SPIDER_MODULES = ['hfutnews.spiders']
NEWSPIDER_MODULE = 'hfutnews.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hfutnews (+http://www.yourdomain.com)'

ITEM_PIPELINES = ['hfutnews.pipelines.HfutnewsPipeline']

