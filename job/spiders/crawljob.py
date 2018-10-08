# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
from job.items import JobItem
import json
from lxml import etree
from scrapy_redis.spiders import RedisCrawlSpider
import hashlib



class CrawljobSpider(RedisCrawlSpider):
    name = 'crawljob'
    allowed_domains = ['51job.com','search.51job.com']
    redis_key = "crawljob:start_urls"
    # start_urls = ['http://www.51job.com/']
    rules = (
        Rule(LinkExtractor(allow=r'http://search.51job.com/list/'),follow=True),
        Rule(LinkExtractor(allow=r'jobs'), callback='parse_detail', follow=True),

    )

    def parse_items(self, response):
        # print response.body.decode('gb2312')
        print '开始处理item'
        item = JobItem()
        url = response.url
        print url
        # lambda表达式，如果页面有数据，就获取，没有就赋值为空
        f = lambda x: x[0] if x else ''
        company = response.xpath('//p[@class="cname"]/a/@title').extract()  # 公司
        # 判断是否为职位页面，有company就是具体职位页面，否者是公司页面
        if company:
            company = company[0]
            # print company
            position = response.xpath('//h1/text()').extract()[0]  # 职位名称
            # print position
            salary = response.xpath('//div[@class="cn"]//strong/text()').extract()[0]  # 薪水
            location = response.xpath('//span[@class="lname"]/text()').extract()[0].strip()  # 地区
            work_address = location
            # print location
            work_years = f(response.xpath('//div[@class="t1"]//span[1]/text()').extract())  # 工作经验
            # print work_years
            # 判断是否有学历要求，没有标明的话赋值不限学历
            ie = response.xpath('//span/em[@class="i2"]').extract()
            if ie:
                degree = response.xpath('//div[@class="t1"]//span[2]/text()').extract()[0]  # 学历
                # print degree
            else:
                degree = '不限学历'
                # print degree
            position_type = response.xpath('//p[@class="msg ltype"]/text()').extract()[0].strip()  # 职位类别
            print response.xpath('//p[@class="msg ltype"]/text()').extract()[0]
            # 处理职位类别 去掉|和空格
            position_type = position_type.split('|')
            list_type = []
            for i in position_type:
                i = i.strip()
                list_type.append(i)
            position_type = list_type
            print position_type
            tags = f(response.xpath('//p[@class="t2"]/span/text()').extract())  # 标签
            print tags
            pub_date = response.xpath('//div[@class="t1"]//span/text()').extract()  # 发布日期
            # print str(pub_date)
            date = re.compile(r'\d{2}-\d{2}')
            datep = date.findall(str(pub_date))
            # print datep[0]
            desc = response.xpath('//div[@class="bmsg job_msg inbox"]//p/text()').extract()
            # 判断职位详情的html,有的是p标签，有的没有
            if desc:
                position_desc1 = desc
            else:
                position_desc1 = response.xpath('//div[@class="bmsg job_msg inbox"]/text()').extract()  # 职位简介
            position_desc = []
            # 处理职位详情
            for i in position_desc1:
                i = i.strip()
                print i
                if i != '':
                    position_desc.append(i.strip())
            print position_desc
            # work_address = ''.join(response.xpath('//div[@class="bmsg inbox"]/a/@onclick').extract()) # 工作地址
            # if len(work_address) > 1:
            #     adds = work_address.split(',')[1]
            #     work_address = adds.split(')')[0]
            #     print work_address
            # else:
            #     work_address = work_address[0]
            item['url'] = self.md5(url)
            item['company'] = company
            item['tags'] = tags
            item['position'] = position
            item['salary'] = salary
            item['degree'] = degree
            item['location'] = location
            item['work_years'] = work_years
            item['position_type'] = position_type
            item['pub_date'] = datep[0]
            item['position_desc'] = position_desc
            item['work_address'] = work_address
            print item
            yield item
        else:
            pass


    def md5(self, data):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()





