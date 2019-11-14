# weiboscrapy
scrapy登录微博并爬取签约作者信息

scrapy登录微博并爬取签约作者信息

第一步，创建项目

用scrapy命令创建一个weiboscrapy的项目，然后为了实现自动登录需要将settings.py中的COOKIES_ENABLED设置成True。

第二步，模拟登录

进行这一步的时候需要先了解微博的登录机制，然后才能实现scrapy的模拟登录。用start_requests()代替start_url。

这里仅贴出一部分代码

    def start_requests(self):
        # 微博登录跳转url
        prelogin_url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_={}'.format(int(time.time() * 1000))  
        yield scrapy.Request(url=prelogin_url,callback=self.get_formdata,headers=self.headers)

第三步，获取数据

在获取数据之前，需要先把items.py文件补充完整。

    class WeiboscrapyItem(scrapy.Item):
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

获取数据

    def parse(self, response):
        users_cards = response.xpath('//div[@id="pl_user_feedList"]/div[@class="card card-user-b s-pg16 s-brt1"]')
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
            yield item

看到这些代码你是不是想说为什么会这么多？，因为最后四条数据不一定存在，而且在HTML中这些数据都属于p标签的内容且p标签没有任何属性，这就要求你要根据内容来判断这个数据该存放到哪个item字段中。

第四步 数据存储

存储数据一般在pipelines.py文件中，别忘了在settings.py文件中将管道文件开启哦。

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
       
            return item
    
        def close_spider(self,spider):
            print('*'*10)
            self.data_csv.to_csv('user_data.csv',index=True)

结果展示：

一共爬取了50页的信息：



一共988条数据，为什么不是整数呢？因为有的页面的数据是不足20条的，有17/19条的页面。
