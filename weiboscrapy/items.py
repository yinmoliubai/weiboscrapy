# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_homepage_url = scrapy.Field()
    user_name = scrapy.Field()
    user_image_url = scrapy.Field()
    user_verify = scrapy.Field()
    user_address = scrapy.Field()
    user_job = scrapy.Field()
    user_follow_num = scrapy.Field()
    user_fans_num = scrapy.Field()
    user_profile_num = scrapy.Field()
    user_detail = scrapy.Field()
    user_tags = scrapy.Field()
    user_school = scrapy.Field()
    user_work = scrapy.Field()

