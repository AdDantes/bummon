# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class ZhaopinPipeline(object): # logo素材信息
    def __init__(self):
        # 连接本地数据库，测试专用！
        self.client = MongoClient('localhost', 27017)
        # 连接公司数据库，开发专用！
        # self.client = MongoClient(host="10.0.100.76", port=27017)
        self.db = self.client.zhaopin
        # self.db.authenticate('', '')
        self.lagou_category = self.db['lagou_category']
        self.lagou_new = self.db['lagou_new']
        self.liepin = self.db['liepin']


    def process_item(self, item, spider):
        if spider.name == 'lagou':
            self.lagou_new.insert_one(dict(item))
        elif spider.name == 'liepin':
            self.liepin.insert_one(dict(item))


        return item

