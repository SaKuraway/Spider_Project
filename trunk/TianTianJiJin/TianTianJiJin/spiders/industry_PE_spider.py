import time
import json
import pymysql
import requests


class Industry_PE(object):
    def __init__(self, industry, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "Cookie": '__cfduid=d0c81848a2eebad51210d4c147cc190711511316905; __lc.visitor_id.8854324=S1511316915.8257f737d5; age=qualified; productHistory=8a357eae91d29c1d6e79314e7cecfc68dd8807d5829b90bc0b2966dedcaa37e0s%3A28%3A%2210631%2C10537%2C2255%2C11278%2C11347%22%3B; PHPSESSID=io98q9pmad6d6egpq2pc0lc7m6; _csrf=f8a85ccb84e56528020f391a65725311d98d52e9e2d191ce30108f6f479b070fs%3A32%3A%225UOKazj6fxFxkIN9k7Dgf_y_GLyYgOVt%22%3B; _ga=GA1.2.348931940.1511316919; _gid=GA1.2.981967218.1512005703; _gat=1; _identity=c31c979569920ccb44ace89d393b2badd0a7d030eac00091e7f9ff9d94c0aee6s%3A50%3A%22%5B26690%2C%22q6xVGtNRU3X6Qg5vY0kKg8zBN7Iopnwz%22%2C2592000%5D%22%3B; lc_window_state=minimized',
        }
        self.industry = industry
        html = requests.get(url=url, headers=self.headers).text
        # html = requests.get(url='http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code=000457&topline=10&year=2013&month=1,2,3,4,5,6,7,8,9,10,11,12').text
        # html = requests.get(url='http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code=000457&topline=10&year=2016&month=1,2,3,4,5,6,7,8,9,10,11,12').content.decode('utf-8')
        # print(html[-44:-2])
        # print(json.loads(html[44:-2]))
        # json1 = "['content:123,arryear:[2017,2016,2015,2014],curyear:2016']"
        # print(json.loads(json1))

        # pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        # pattern1 = re.compile(r',curyear:(.*?)};', re.S)
        # year_list = pattern.findall(html)[0]
        # print(item) [2017,2016,2015,2014]
        # last_yearlist = pattern.findall(html)[0][-1]
        # current_year = pattern1.findall(html)[0]
        data = html[12:]
        self.jingTai = json.loads(data)[0]
        self.dongTai = json.loads(data)[1]
        self.PE = []
        for index, item in enumerate(self.jingTai):
            item.append(self.dongTai[index][1])
            self.PE.append(item)
            # print(self.PE)

    def spide_to_mysql(self, flag=1):
        # mysql_client = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='jijin_data',charset='utf8')
        mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                       database='data_finance', charset='utf8')

        # 使用cursor()方法获取操作游标
        cur = mysql_client.cursor()
        for item in self.PE:
            try:
                # print('str(float(item[1]))=',str(float(item[1])))
                if cur.execute("select * from " + self.industry + " where date=" + str(
                        int((int(item[0]) / 1000))) + ";"):
                    message = '%s已存在第%s条数据，正在忽略...'
                    if not cur.execute("select * from " + self.industry + " where date=" + str(
                            int((int(item[0]) / 1000))) + " and dynamic_PE=" + str(float(item[2])) + ";"):
                        cur.execute("update " + self.industry + " set dynamic_PE=%s where date=%s and static_PE=%s",
                                    (float(item[2]), int((int(item[0]) / 1000)), float(item[1])))
                        message = '%s正在更新第%s条数据...'
                    print(message % (self.industry, flag))
                else:
                    cur.execute("insert into " + self.industry + "(date,static_PE,dynamic_PE) VALUES(%s,%s,%s)",
                                (int((int(item[0]) / 1000)), float(item[1]), float(item[2])))
                    # cur.execute("update 交通运输、仓储和邮政业行业市盈率 set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
                    # cur.execute("delete from 制造业行业市盈率 where id > 245")

                    print('%s正在插入第%s条数据...' % (self.industry, flag))
                flag += 1
            except pymysql.Error as e:
                print(e)
                # finally:
                # print(int((int(i) / 1000)))
                # 关闭本次操作
                # cur.close()

        # 保持id连续
        # cur.execute("update " + self.industry + " set id = id-" + str(id_plus) + " where id > " + str(id_plus))
        print('正在排序数据表中的id列....')
        cur.execute("ALTER TABLE " + self.industry + " DROP id;")
        cur.execute("ALTER  TABLE " + self.industry + " ADD id MEDIUMINT( 8 ) NOT NULL  FIRST;")
        cur.execute("ALTER  TABLE " + self.industry + " MODIFY COLUMN id MEDIUMINT( 8 ) NOT NULL  AUTO_INCREMENT,ADD PRIMARY  KEY(id);")
        cur.close()
        # flag = 1
        # for item in self.dongTai:
        #     try:
        #         # 使用cursor()方法获取操作游标
        #         cur = mysql_client.cursor()
        #         # cur.execute("insert into 交通运输、仓储和邮政业行业市盈率(id,date,static_PE) VALUES(%s,%s,%s)",(int(flag),int((int(item[0]) / 1000)), float(item[1])))
        #         cur.execute("update " + self.industry + " set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
        #         # cur.execute("delete from 制造业行业市盈率 where id > 245")
        #         print('正在更新%s的第%s条数据...' % (self.industry, flag))
        #     except pymysql.Error as e:
        #         print(e)
        #     finally:
        #         # print(int((int(i) / 1000)))
        #         flag += 1
        #         # 关闭本次操作
        #         cur.close()

        # 提交sql事务
        mysql_client.commit()
        mysql_client.close()
        print('%s操作完成！共操作%s条数据.' % (self.industry, flag - 1))
        time.sleep(5)


# to_mysql(jingTai,dongTai)

if __name__ == '__main__':
    # while True:
    industry_pe = Industry_PE('制造业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=C&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('电力、热力、燃气及水生产和供应业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=D&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('信息传输、软件和信息技术服务业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=I&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('批发和零售业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=F&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('文化、体育和娱乐业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=R&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('卫生和社会工作行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=Q&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('租赁和商务服务业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=L&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('水利、环境和公共设施管理业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=N&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('科学研究和技术服务业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=M&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('采矿业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=B&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()
    industry_pe = Industry_PE('交通运输、仓储和邮政业行业市盈率',
                              'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=G&Y=2017&Q=3&lastestYear=1')
    industry_pe.spide_to_mysql()

        # time.sleep(86400)  # 每隔一天运行一次 24*60*60=86400s

