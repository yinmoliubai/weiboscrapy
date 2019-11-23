# -*- coding: utf-8 -*-
import scrapy
import base64
import re
import rsa
from binascii import b2a_hex
import random
from urllib.parse import quote
import time
from ..items import WeiboscrapyItem
from lxml import etree

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    # allowed_domains = ['https://weibo.com']
    # start_urls = ['http://https://weibo.com/']
    # username = input('请输入你的微博账号：')  # 微博账号
    # password = input('请输入登录密码：')  # 微博密码
    # search = input('请输入查找的内容：')
    # page = input('请输入要爬取的页数：')
    
    
    username = 'xxxxxxxxxxx' # 微博账号
    password = 'xxxxxx' # 微博密码
    search = '微博签约作者'
    page = 51
    
    number = 0
    page_number = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    
    su = base64.b64encode(username.encode())  # 阅读js得知用户名进行base64转码
    
    def start_requests(self):
        prelogin_url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_={}'.format(int(time.time() * 1000))  # 注意su要进行quote转码
        yield scrapy.Request(url=prelogin_url,callback=self.get_formdata,headers=self.headers)

    # 预登录，获取一些必须的参数
    def get_formdata(self,response):
        self.nonce = re.findall(r'"nonce":"(.*?)"',response.text)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"',response.text)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"',response.text)[0]
        self.servertime = re.findall(r'"servertime":(.*?),',response.text)[0]
        # '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey, 16), int('10001', 16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = b2a_hex(rsa.encrypt(message.encode(), publickey))
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
        'entry': 'weibo',
        'gateway': '1',
        'from':'',
        'savestate': '7',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fpassport.weibo.com%2Fwbsso%2Flogout%3Fr%3Dhttps%253A%252F%252Fweibo.com%26returntype%3D1',
        'vsnf': '1',
        'su': self.su,
        'service': 'miniblog',
        'servertime': str(int(self.servertime)+random.randint(1,20)),
        'nonce': self.nonce,
        'pwencode': 'rsa2',
        'rsakv': self.rsakv,
        'sp': self.sp,
        'sr': '1366 * 768',
        'encoding': 'UTF - 8',
        'prelt': '275',
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        }
        # meta = {'dont_redirect': True}   不允许重定向
        yield scrapy.FormRequest(url=login_url,callback=self.login_middle,formdata=data,meta = {'dont_redirect': True})

    # 微博在提交数据后会跳转，此处获取跳转的url
    def login_middle(self,response):
        # with open('data.html','w',encoding='gbk')as f:
        #     f.write(response.text)
        data = response.text
        redirect_url = re.findall(r'location.replace\("(.*?)"\);',data)[0]
        yield scrapy.Request(url=redirect_url,callback=self.login_middle2,meta = {'dont_redirect': True})

    # 获取ticket和ssosavestate参数
    def login_middle2(self,response):
        ticket, ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"', response.text)[0]
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(ticket, ssosavestate, int(time.time() * 1000))
        yield scrapy.Request(url=uid_url,callback=self.get_uuid)

    # 请求获取uid
    def get_uuid(self,response):
        uid = re.findall(r'"uniqueid":"(.*?)"', response.text)[0]
        home_url = 'https://weibo.com/u/{}/home?wvr=5&lf=reg'.format(uid)
        # print(uid)
        self.headers['referer'] = 'https://weibo.com/'
        yield scrapy.Request(url=home_url,callback=self.go_homehtml,headers=self.headers)

    # 进入首页
    def go_homehtml(self,response):
        # print(response.text)
        url_decode = quote(quote(self.search))
        url = f'https://s.weibo.com/weibo/{url_decode}?topnav=1&wvr=6&b=1'
        yield scrapy.Request(url=url,callback=self.get_data,meta = {'dont_redirect': True})
        
    def get_data(self,response):
        s = quote(self.search)
        for i in range(1,self.page):
            url = f'https://s.weibo.com/user?q={s}&Refer=SUer_box&page={i}'
            print(url)
            time.sleep(3)
            # 向下一个执行函数传参 meta={'page':i}
            yield scrapy.Request(url= url,callback=self.parse)

    def parse(self, response):
        users_cards = response.xpath('//div[@id="pl_user_feedList"]/div[@class="card card-user-b s-pg16 s-brt1"]')
        self.page_number.append(len(users_cards))
        self.number += len(users_cards)
        print(self.number)
        print(self.page_number)
        for user_card in users_cards:
            item = WeiboscrapyItem()
            # 作家主页
            item['user_homepage_url'] = user_card.xpath('./div[@class="avator"]/a/@href').extract()[0]
            # 作者头像
            item['user_image_url'] = user_card.xpath('./div[@class="avator"]/a/img/@src').extract()[0]
            # 作者名
            item['user_name'] = user_card.xpath('./div[@class="info"]/div/a[1]/text()').extract()[0]
            # 微博个人认证 类型
            item['user_verify'] = user_card.xpath('./div[@class="info"]/div/a[2]/i/@class').extract()[0]
            # 作者工作地址
            item['user_address'] = ''.join(''.join(user_card.xpath('./div[@class="info"]/p[1]/text()').extract()).split())
            # 作者工作
            item['user_job'] = ' '.join(user_card.xpath('./div[@class="info"]/p[2]/text()').extract()[0].split())
            # 关注数
            item['user_follow_num'] = user_card.xpath('./div[@class="info"]/p[3]/span[1]/a/text()').extract()[0]
            # 粉丝数
            item['user_fans_num'] = user_card.xpath('./div[@class="info"]/p[3]/span[2]/a/text()').extract()[0]
            # 微博数
            item['user_profile_num'] = user_card.xpath('./div[@class="info"]/p[3]/span[3]/a/text()').extract()[0]
            
            item['user_detail'] = '',
            item['user_tags'] = '',
            item['user_school'] = '',
            item['user_work'] = ''
            
            # 除了上面的3个标签，还有几个p标签
            number = len(user_card.xpath('./div[@class="info"]/p')) - 3
            #  有4个p标签
            if number == 4:
                # 作者简介
                item['user_detail'] = user_card.xpath('./div[@class="info"]/p[4]/text()').extract()[0]
                # 作者标签
                item['user_tags'] = ''.join(user_card.xpath('./div[@class="info"]/p[5]/a/text()').extract())
                # 作者教育信息
                item['user_school'] = ' '.join(user_card.xpath('./div[@class="info"]/p[6]/a/text()').extract())
                # 作者职业信息
                item['user_work'] = ' '.join(user_card.xpath('./div[@class="info"]/p[7]/a/text()').extract())
            #  有3个p标签
            elif number == 3:
                # 作者简介
                item['user_detail'] = user_card.xpath('./div[@class="info"]/p[4]/text()').extract()[0]
                # 作者标签
                item['user_tags'] = ' '.join(user_card.xpath('./div[@class="info"]/p[5]/a/text()').extract())
                
                html_content = user_card.xpath('./div[@class="info"]/p[last()]/text()').extract()[0]
                xinxi = html_content.split('：')[0]
                if xinxi == '教育信息':
                    item['user_school'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
                # xinxi == '职业信息'
                else:
                    item['user_work'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
            #  有2个p标签
            elif number == 2:
                html_content = user_card.xpath('./div[@class="info"]/p[last()]/text()').extract()[0]
                xinxi = html_content.split('：')[0]
                if xinxi == '标签':
                    # 作者简介
                    item['user_detail'] = user_card.xpath('./div[@class="info"]/p[last()-1]/text()').extract()[0]
                    # 作者标签
                    item['user_tags'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
                # len(xinxi) == 4
                else:
                    if xinxi == '教育信息':
                        item['user_school'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
                    # xinxi == '职业信息'
                    else :
                        item['user_work'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
                    html_data = user_card.xpath('./div[@class="info"]/p[last()-1]/text()').extract()[0]
                    if html_data[:2] == '简介':
                        # 作者简介
                        item['user_detail'] = user_card.xpath('./div[@class="info"]/p[last()-1]/text()').extract()[0]
                    # html_data[:2] == '标签'
                    else :
                        # 作者标签
                        item['user_tags'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()-1]/a/text()').extract())
            # number == 1  只有一个p标签
            else:
                html_data = user_card.xpath('./div[@class="info"]/p[last()]/text()').extract()[0]
                if html_data[:2] == '简介':
                    # 作者简介
                    item['user_detail'] = user_card.xpath('./div[@class="info"]/p[last()]/text()').extract()[0]
                else:
                    # 作者标签
                    item['user_tags'] = ' '.join(user_card.xpath('./div[@class="info"]/p[last()]/a/text()').extract())
                    
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
            yield item
