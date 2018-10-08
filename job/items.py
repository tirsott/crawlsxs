# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()#链接
    company = scrapy.Field()#公司
    position = scrapy.Field()#职位名称
    salary = scrapy.Field()#薪水
    location = scrapy.Field()#地区
    work_years = scrapy.Field()#工作经验
    degree = scrapy.Field()#学历
    position_type = scrapy.Field()#职位类别
    tags = scrapy.Field()#标签
    pub_date = scrapy.Field()#发布日期
    position_desc = scrapy.Field()#职位简介
    work_address = scrapy.Field()#工作地址
    crawled = scrapy.Field()
    spider = scrapy.Field()


