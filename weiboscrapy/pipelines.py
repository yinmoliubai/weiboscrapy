# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pandas as pd

class WeiboscrapyPipeline(object):
    
    def open_spider(self,spider):
        # self.data_csv = pd.DataFrame(columns=('主页链接','头像','昵称','微博认证','地址','工作','关注','粉丝','微博','简介','标签','教育信息','职业信息'))
        self.data_csv = pd.DataFrame(columns=('user_homepage_url','user_name','user_image_url','user_verify','user_address','user_job',
                     'user_fans_num','user_follow_num','user_profile_num','user_detail','user_school','user_tags','user_work'))
        self.index = 0
    def process_item(self, item, spider):
        new_h = [item['user_homepage_url'],
                item['user_image_url'],
                item['user_name'],
                item['user_verify'],
                item['user_address'],
                item['user_job'],
                item['user_follow_num'],
                item['user_fans_num'],
                item['user_profile_num'],
                item['user_detail'],
                item['user_tags'],
                item['user_school'],
                item['user_work']]
        
        self.data_csv.loc[self.index] = new_h
        self.index += 1
        # print(self.data_csv)
        # print(
        #     '主页链接：{},\t头像：{},\t昵称：{},\n微博认证：{},\t地址：{},\t工作：{},\t关注：{},\t粉丝：{},\t微博：{},\n简介：{},\t标签：{},\t教育信息：{},\t职业信息：{},\n\n'.format(
        #         item['user_homepage_url'],
        #         item['user_image_url'],
        #         item['user_name'],
        #         item['user_verify'],
        #         item['user_address'],
        #         item['user_job'],
        #         item['user_follow_num'],
        #         item['user_fans_num'],
        #         item['user_profile_num'],
        #         item['user_detail'],
        #         item['user_tags'],
        #         item['user_school'],
        #         item['user_work']))
        return item

    def close_spider(self,spider):
        print('*'*10)
        # print(self.data_csv)
        self.data_csv.to_csv('user_data.csv',index=True)