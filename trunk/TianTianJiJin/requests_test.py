import json
import pymysql
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    "Cookie": '__cfduid=d0c81848a2eebad51210d4c147cc190711511316905; __lc.visitor_id.8854324=S1511316915.8257f737d5; age=qualified; productHistory=8a357eae91d29c1d6e79314e7cecfc68dd8807d5829b90bc0b2966dedcaa37e0s%3A28%3A%2210631%2C10537%2C2255%2C11278%2C11347%22%3B; PHPSESSID=io98q9pmad6d6egpq2pc0lc7m6; _csrf=f8a85ccb84e56528020f391a65725311d98d52e9e2d191ce30108f6f479b070fs%3A32%3A%225UOKazj6fxFxkIN9k7Dgf_y_GLyYgOVt%22%3B; _ga=GA1.2.348931940.1511316919; _gid=GA1.2.981967218.1512005703; _gat=1; _identity=c31c979569920ccb44ace89d393b2badd0a7d030eac00091e7f9ff9d94c0aee6s%3A50%3A%22%5B26690%2C%22q6xVGtNRU3X6Qg5vY0kKg8zBN7Iopnwz%22%2C2592000%5D%22%3B; lc_window_state=minimized',
}
html = requests.get(
    url='http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=G&Y=2017&Q=3&lastestYear=1',headers=headers).text
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
jingTai = json.loads(data)[0]
dongTai = json.loads(data)[1]


def to_mysql(jingtai,dongtai, flag=1):
    # mysql_client = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='jijin_data',charset='utf8')
    mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105', database='data_finance',charset='utf8')
    for item in jingtai:

            try:
                # 使用cursor()方法获取操作游标
                cur = mysql_client.cursor()
                cur.execute("insert into 交通运输、仓储和邮政业行业市盈率(id,date,static_PE) VALUES(%s,%s,%s)",(int(flag),int((int(item[0]) / 1000)), float(item[1])))
                # cur.execute("update 交通运输、仓储和邮政业行业市盈率 set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
                # cur.execute("delete from 制造业行业市盈率 where id > 245")
                print('正在插入第%s条数据...'%flag)
            except pymysql.Error as e:
                print(e)
            finally:
            # print(int((int(i) / 1000)))
                flag += 1
                # 关闭本次操作
                cur.close()
    flag = 1
    for item in dongtai:

        try:
            # 使用cursor()方法获取操作游标
            cur = mysql_client.cursor()
            # cur.execute("insert into 交通运输、仓储和邮政业行业市盈率(id,date,static_PE) VALUES(%s,%s,%s)",(int(flag),int((int(item[0]) / 1000)), float(item[1])))
            cur.execute("update 交通运输、仓储和邮政业行业市盈率 set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
            # cur.execute("delete from 制造业行业市盈率 where id > 245")
            print('正在更新第%s条数据...' % flag)
        except pymysql.Error as e:
            print(e)
        finally:
            # print(int((int(i) / 1000)))
            flag += 1
            # 关闭本次操作
            cur.close()
    # 提交sql事务
    mysql_client.commit()
    mysql_client.close()
    print('操作完成！共%s条数据.'%(flag-1))

# to_mysql(jingTai)
to_mysql(jingTai,dongTai)

