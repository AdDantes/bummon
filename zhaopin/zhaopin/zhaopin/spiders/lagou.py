# -*- coding: utf-8 -*-
import scrapy
import json
from uuid import uuid4
from copy import deepcopy
import re
import time

class LagouSpider(scrapy.Spider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.lagou.com/']
    pn = 1
    first = 'true'
    headers = {'Cookie': "JSESSIONID={}+user_trace_token={}".format(uuid4(), uuid4()),
               'Referer': "https://www.lagou.com/jobs/list_",
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
               }

    def parse(self, response):
        item = {}
        box_list = response.xpath('//div[@class="mainNavs"]/div[@class="menu_box"]')
        for box in box_list:
            item['total_category'] = box.xpath(
                './div[@class="menu_main job_hopping"]/div[@class="category-list"]/h2/text()').extract_first().strip()
            dl_list = box.xpath('./div[@class="menu_sub dn"]/dl')
            for dl in dl_list:
                item['mid_category'] = dl.xpath('./dt/span/text()').extract_first()
                detail_list = dl.xpath('./dd/a')
                for detail in detail_list:
                    item['detail_category'] = detail.xpath('./text()').extract_first()
                    item['detail_category_href'] = detail.xpath('./@href').extract_first()
                    yield scrapy.Request(item['detail_category_href'],
                                             cookies={'JSESSIONID': uuid4(), 'user_trace_token': uuid4()},
                                             callback=self.parse_item, meta={'item': deepcopy(item)},dont_filter=True
                                             )
                    # if self.pn < 30:
                    #     self.pn += 1
                    #     print('正在抓取第{}页'.format(self.pn))
                    #     self.first = 'false'
                    #     yield scrapy.FormRequest('https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false',
                    #                              formdata={'first': self.first, 'pn': str(self.pn), 'kd': item['detail_category']},
                    #                              cookies={'JSESSIONID': uuid4(), 'user_trace_token': uuid4()},)


    def parse_item(self, response):
        item = response.meta['item']
        a_list = response.xpath('//div[@class="position"]/div[@class="p_top"]/a[@class="position_link"]')
        for a in a_list:
            item['detail_position_url'] = a.xpath('./@href').extract_first()
            # print(item)
            yield scrapy.Request(item['detail_position_url'],cookies={'JSESSIONID': uuid4(), 'user_trace_token': uuid4()},
                                             callback=self.parse_detail, meta={'item': deepcopy(item)})
        next_url = response.xpath('//div[@class="pager_container"]/a[text()="下一页"]/@href').extract_first()
        print(next_url)
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse_item, cookies={'JSESSIONID': uuid4(), 'user_trace_token': uuid4()},meta={'item': deepcopy(item)},dont_filter=True)

    def parse_detail(self, response):
        item = response.meta['item']
        item['workYear'] = response.xpath('//dd[@class="job_request"]/p/span[3]/text()').extract_first().replace('/','').replace(' ','')
        item['workYear'] = re.findall('经验(.*?)$',item['workYear'])[0]
        item['city'] = response.xpath('//dd[@class="job_request"]/p/span[2]/text()').extract_first().replace('/','').replace(' ','')
        item['area'] = response.xpath('//div[@class="work_addr"]/a[2]/text()').extract_first()
        item['education'] = response.xpath('//dd[@class="job_request"]/p/span[4]/text()').extract_first().replace('/','').replace(' ','')
        item['salary'] = response.xpath('//dd[@class="job_request"]/p/span[@class="salary"]/text()').extract_first().replace('/','').replace(' ','')
        item['publish_time'] = response.xpath('//p[@class="publish_time"]/text()').extract_first()
        item['publish_time'] = re.findall('(.*?)\xa0',item['publish_time'])[0]
        if ':' in item['publish_time']:
            item['publish_time'] = time.strftime("%Y-%m-%d", time.localtime())
        desp = response.xpath('//dd[@class="job_bt"]/div/p/text()').extract()
        j = 0
        item['work_duty'] = ''
        global i
        for i in range(len(desp)):

            desp[i] = desp[i].replace('\xa0', ' ')
            if desp[i][0].isdigit():
                if j == 0:
                    desp[i] = desp[i][2:].replace('、', ' ')
                    desp[i] = re.sub('[；;.0-9。]', '', desp[i])
                    item['work_duty'] = item['work_duty'] + desp[i] + '/'
                    j += 1
                elif desp[i][0] == '1' and not desp[i][1].isdigit():
                    break
                else:
                    desp[i] = desp[i][2:].replace('、', ' ')
                    desp[i] = re.sub('[；;.0-9。]', '', desp[i])
                    item['work_duty'] = item['work_duty'] + desp[i] + '/'

        m = i
        j = 0
        item['work_requirement'] = ''
        for i in range(m, len(desp)):
            desp[i] = desp[i].replace('\xa0', ' ')
            if desp[i][0].isdigit():
                if j == 0:
                    desp[i] = desp[i][2:].replace('、', ' ')
                    desp[i] = re.sub('[；;.0-9。]', '', desp[i])
                    item['work_requirement'] = item['work_requirement'] + desp[i] + '/'
                    j += 1
                elif desp[i][0] == '1' and not desp[i][1].isdigit():
                    break
                else:
                    desp[i] = desp[i][2:].replace('、', ' ')
                    desp[i] = re.sub('[；;.0-9。]', '', desp[i])
                    item['work_requirement'] = item['work_requirement'] + desp[i] + '/'
        print(item)
        yield item
        print("-----------------------------")
