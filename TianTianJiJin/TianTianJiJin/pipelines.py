# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import pymysql

# 存到txt文本中
class TiantianjijinPipeline(object):
    def __init__(self):
        self.keyword = 'ACworth_TEST'
        self.file = open('Data/' + self.keyword + '.txt', 'a', encoding='utf-8')
        self.count = 1
        print('开始写入:')

    def process_item(self, item, spider):
        self.file.write(str(self.count) + '.\n' + str(item) + ',\r\n')
        self.count += 1
        return item

    def close_spider(self, spider):
        self.file.close()
        print('爬取完毕！共%s个基金。' % self.count)

# 存入MongoDB中
class TiantianjijinMongodbPipeline(object):
    def open_spider(self, spider):
        self.mongo_client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.db_name = self.mongo_client["TianTianJiJin"]
        self.sheet_name = self.db_name['TianTianJiJin_Alldata']

    def process_item(self, item, spider):
        self.sheet_name.insert(dict(item))
        return item

    def close_spider(self, spider):
        self.mongo_client.close()

# 存入MySQL中
class TiantianjijinMysqlPipeline(object):
    def open_spider(self, spider):
        # 指定mysql数据库
        self.mysql_client = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='shizairenwei', database = 'aqi', charset='utf8')

    def process_item(self, item, spider):
        # FIFO模式为 blpop，LIFO模式为 brpop，获取redis的键值
        # source, data = rediscli.blpop(["aqi:items"])
        # item = json.loads(data)
        try:
            # 使用cursor()方法获取操作游标
            cur = self.mysql_client.cursor()
            # 使用execute方法执行SQL INSERT语句
            cur.execute("insert into aqi_data(city, date, aqi, level, pm2_5, pm10, so2, co, no2, o3, rank, spider, crawled) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [item['city'], item['date'], item['aqi'], item['level'], item['pm2_5'], item['pm10'], item['so2'], item['co'], item['no2'], item['o3'], item['rank'], item['spider'], item['crawled']])
            # 提交sql事务
            self.mysql_client.commit()
            #关闭本次操作
            cur.close()
        except pymysql.Error as e:
            print(e)

    def close_spider(self, spider):
        self.mysql_client.close()
