# -*- coding: utf-8 -*-
import scrapy
import re
from job.items import JobItem
import json
from lxml import etree
from scrapy_redis.spiders import RedisSpider
import hashlib


class Job51Spider(RedisSpider):
    name = 'job51'
    redis_key = 'job:start_urls'
    allowed_domains = ['51job.com']
    #用来拼接URL的字符串，因为%2B和%s冲突，识别错误
    s = '000000,0000,00,9,99,%2B'

    def parse(self,response):
        start_urls = 'http://js.51jobcdn.com/in/js/2016/layer/area_array_c.js?20170619'
        yield scrapy.Request(start_urls,callback=self.parse_city,dont_filter=True)

    def parse_city(self, response):
        # 爬出所有城市id
        print 'city函数开始运行'
        city = response.body.decode('gbk')
        city_num = re.compile(r'\d+')
        citynum = city_num.findall(city)
        list1 = []
        for i in citynum:
            i = str(i)
            list1.append(i)
        citynum_str = ','.join(citynum)
        # print citynum_str
        city_area = re.compile(r'\d{2}0000')
        cityarea = city_area.findall(citynum_str)
        list2 = []
        for i in cityarea:
            i = str(i)
            # 所有省份,需要排除掉
            list2.append(i)
        for i in list1:
            if i not in list2:
                # print i
                # 生成所有的列表页链接
                base_url = 'http://search.51job.com/list/%s,%s,2,%d.html?degreefrom=%d'
                cityurl = base_url % (i,self.s,1,99)
                # print cityurl
                #把城市ID传下去，用来构造列表页URL
                yield scrapy.Request(cityurl,callback=self.parse_list,meta={'id':i},dont_filter=True)
    def parse_list(self,response):
        print 'list函数开始运行'
        id = response.meta['id']
        page = response.xpath('//span[@class="td"]/text()').extract()
        if page:
            # print page[0]
            num1 = re.compile(r'\d+')
            #获取最大页数
            maxpage = int(num1.findall(page[0])[0])
            # print int(maxpage[0])
            for i in range(1,maxpage+1):
                base_url = 'http://search.51job.com/list/%s,%s,2,%d.html?degreefrom=%d'
                fullurl = base_url % (id,self.s,i,99)
                print 'fullurl:',fullurl
                # 循环发起请求,列表页,返回给详情页处理
                yield scrapy.Request(fullurl,callback=self.parse_detail)

    def parse_detail(self,response):
        # print response.body.decode('gbk')
        print 'detail 函数开始运行'
        detail = response.xpath('//p[@class="t1 "]//a/@href').extract()
        # print detail
        if detail:
            for i in detail:
                print 'detail:',i
                #priority  优先级，数字越大优先级越高，优先处理
                yield scrapy.Request(i,callback=self.parse_items,priority=1)

    def parse_items(self,response):
        # print response.body.decode('gb2312')
        print '开始处理item'
        item = JobItem()
        url = response.url
        print url
        #lambda表达式，如果页面有数据，就获取，没有就赋值为空
        f = lambda x : x[0] if x else ''
        company = response.xpath('//p[@class="cname"]/a/@title').extract()# 公司
        #判断是否为职位页面，有company就是具体职位页面，否者是公司页面
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
                degree = response.xpath('//div[@class="t1"]//span[2]/text()').extract()[0]# 学历
                # print degree
            else:
                degree = '不限学历'
                # print degree
            position_type = response.xpath('//p[@class="msg ltype"]/text()').extract()[0].strip() # 职位类别
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
            pub_date = response.xpath('//div[@class="t1"]//span/text()').extract()# 发布日期
            # print str(pub_date)
            date = re.compile(r'\d{2}-\d{2}')
            datep = date.findall(str(pub_date))
            # print datep[0]
            desc = response.xpath('//div[@class="bmsg job_msg inbox"]//p/text()').extract()
            #判断职位详情的html,有的是p标签，有的没有
            if desc:
                position_desc1 = desc
            else:
                position_desc1 = response.xpath('//div[@class="bmsg job_msg inbox"]/text()').extract()  # 职位简介
            position_desc = []
            #处理职位详情
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














