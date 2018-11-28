# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy

class LiepinSpider(scrapy.Spider):
    name = 'liepin'
    allowed_domains = ['liepin.com']
    start_urls = ['https://www.liepin.com']


    def parse(self,response):
        item = {}
        a_list = response.xpath('//div[@class="wrap"]/p/a')
        for a in a_list:
            item['total_title'] =  a.xpath('./b/text()').extract_first()
            url = a.xpath('./@href').extract_first()
            yield scrapy.Request(url,callback=self.parse_mid,meta={'item':deepcopy(item)})

    def parse_mid(self, response):
        item = response.meta['item']
        li_list = response.xpath('//ul[@class="sidebar float-left"]/li')
        for li in li_list:
            item['sidebar_title'] = li.xpath('./div[@class="sidebar-title"]/h2/text()').extract_first()
            a_list = li.xpath('./dl/dd/a')
            for a in a_list:
                item['mid_title'] = a.xpath('./text()').extract_first()
                mid_url = a.xpath('./@href').extract_first()
                mid_url = 'https://www.liepin.com'+ mid_url
                yield scrapy.Request(mid_url,callback=self.parse_item,meta={'item':deepcopy(item)})

    def parse_item(self,response):
        item = response.meta['item']
        div_list = response.xpath('//div[@class="job-info"]')
        for div in div_list:
            detail_url = div.xpath('./h3/a/@href').extract_first()
            item['detail_url'] = 'https://www.liepin.com'+detail_url
            item['title'] = div.xpath('./h3/a/text()').extract_first().strip()
            item['salary'] = div.xpath('./p/span[@class="text-warning"]/text()').extract_first()
            item['city'] = div.xpath('./p/a[@class="area"]/text()').extract_first()
            item['education'] = div.xpath('./p/span[@class="edu"]/text()').extract_first()
            item['workYear'] = div.xpath('./p/span[@class="edu"]/following-sibling::span[1]/text()').extract_first()
            item['createTime'] = div.xpath('./p[@class="time-info clearfix"]/time/@title').extract_first()
            print(item)
            yield item
        next_url = response.xpath('//div[@class="pagerbar"]/a[text()="下一页"]/@href').extract_first()
        next_url = 'https://www.liepin.com'+ str(next_url)
        print(next_url)
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse_item, meta={'item': deepcopy(item)})
