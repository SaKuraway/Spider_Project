# -*-coding:utf-8-*-
import requests, pymysql, time
from lxml import etree

mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                               database='data_finance', charset='utf8')
# 使用cursor()方法获取操作游标
cur = mysql_client.cursor()

Fund_codes = ['050002','001061','002393','539001','486002','000834','096001','000509','002847','070008','482002','340005','217004','005008','213009','001887','001882','001661']  # '001061','002393','539001','486002','000834','096001','000509'
# 净值日期</th><th>单位净值</th><th>累计净值</th><th>日增长率</th><th>申购状态</th><th>赎回状态</th><th class='tor last'>分红送配
# 净值日期</th><th>每万份收益</th><th>7日年化收益率（%）</th><th>申购状态</th><th>赎回状态</th><th class='tor last'>分红送配
for Fund_code in Fund_codes:
    try:
        history_NAV_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10&sdate=&edate='.format(
            Fund_code)
        DEFAULT_REQUEST_HEADERS = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Host": "fund.eastmoney.com",
            "Referer": "http://fund.eastmoney.com/data/fundranking.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        }

        response0 = requests.get(url=history_NAV_url, headers=DEFAULT_REQUEST_HEADERS).text
        # print(response0)
        response = etree.HTML(response0)

        td7 = response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]")

        History_NAV_Date = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                            for i in response.xpath("//table[@class='w782 comm lsjz']//tr/td[1]")]  # 净值日期
        NAV = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
               response.xpath("//table[@class='w782 comm lsjz']//tr/td[2]")]  # 单位净值
        ANAV = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//table[@class='w782 comm lsjz']//tr/td[3]")]  # 累计净值
        Day_change = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i
                      in response.xpath("//table[@class='w782 comm lsjz']//tr/td[4]")] if td7 else ['货币基金' for i in
                                                                                                    response.xpath(
                                                                                                        "//table[@class='w782 comm lsjz']//tr/td[1]")]  # 收益率
        Purchase_status = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                           for i in response.xpath("//table[@class='w782 comm lsjz']//tr/td[5]")] if td7 else [
            i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
            response.xpath("//table[@class='w782 comm lsjz']//tr/td[4]")]  # 申购状态
        Redeem_status = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                         response.xpath("//table[@class='w782 comm lsjz']//tr/td[6]")] if td7 else [
            i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
            response.xpath("//table[@class='w782 comm lsjz']//tr/td[5]")]  # 赎回状态
        Dividends_distribution = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in td7] if td7 else [
            i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
            response.xpath("//table[@class='w782 comm lsjz']//tr/td[6]")]  # 分红配送
        # print('````````')
        # print(History_NAV_Date)
        # print(NAV)
        # print(ANAV)
        # print(Day_change)
        # print(Purchase_status)
        # print(Redeem_status)
        # print(Dividends_distribution)

        cur.execute("select History_NAV_Date from History_NAV where Fund_code=" + "'" + Fund_code + "'" + ";")
        existed_date = [date[0] for date in cur.fetchall()]
        print(Fund_code, 'existed_date:', existed_date)
        print(History_NAV_Date, NAV, ANAV, Day_change, Purchase_status, Redeem_status, Dividends_distribution)
        for History_NAV_Date, NAV, ANAV, Day_change, Purchase_status, Redeem_status, Dividends_distribution in zip(
                History_NAV_Date, NAV, ANAV, Day_change, Purchase_status, Redeem_status, Dividends_distribution):
            # 判断是否已存在于数据库中
            if History_NAV_Date not in existed_date:
                cur.execute(
                    "insert into History_NAV(Fund_code,History_NAV_Date,NAV,ANAV,Unit_yield,7days_annualised_return,Day_change,Purchase_status,Redeem_status,Dividends_distribution) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (Fund_code, History_NAV_Date, NAV, ANAV if td7 else None, None if td7 else NAV,
                     None if td7 else ANAV, Day_change, Purchase_status, Redeem_status, Dividends_distribution))
                print('inserting data to mysql...', Fund_code, History_NAV_Date, NAV, ANAV if td7 else None,
                      None if td7 else NAV, None if td7 else ANAV, Day_change, Purchase_status, Redeem_status,
                      Dividends_distribution)
            else:
                pass
                # print('existed!skiping...')

        mysql_client.commit()
        time.sleep(5)
    except pymysql.Error as e:
        print('error!', e)
        time.sleep(30)


# 调整货币基金净值

# cur.execute("SELECT Fund_code from History_NAV WHERE Day_change='货币基金' GROUP BY Fund_code;")
# Fund_codes = [fund_code[0] for fund_code in cur.fetchall()]

Fund_codes = ['000509','002847','070008','482002','340005','217004','213009']   # 货币基金
for Fund_code in Fund_codes:
    # 待完善逻辑
    cur.execute("select History_NAV_Date,NAV,ANAV from History_NAV where Fund_code=" + "'" + Fund_code + "'" + "ORDER BY History_NAV_Date;")
    # if not cur.execute("select 7days_annualised_return from History_NAV where Fund_code=" + "'" + Fund_code + "' and 7days_annualised_return = 1" + "ORDER BY History_NAV_Date;"):
    #     cur.execute("INSERT INTO history_nav(Fund_code,History_NAV_Date,NAV,ANAV,Day_change,Purchase_status,Redeem_status,Dividends_distribution) VALUE(Fund_code,'2014-01-09','','1','货币基金','封闭期','封闭期','');")

    results = cur.fetchall()
    # print(results)
    before_ANAV = 1 # float(result[2][:-1])
    for index, result in enumerate(results):
        if index < len(results) - 1:
            try:
                behind_NAV = float(results[index + 1][1])
                behind_date = results[index + 1][0]
                ANAV = before_ANAV * (1 + (behind_NAV / 10000))  # update history_nav set annualised_return_7_days = annualised_return_7_days where fund_code ='000509' and history_date = behind_date;
                before_ANAV = ANAV
                before_7days_annualised_return = str(results[index][2])
                annualised_return = str(results[index + 1][2])
                print(behind_date,ANAV)
                print('此时before_7days_annualised_return和annualised_return分别为：',before_7days_annualised_return,annualised_return)
                if 'None' in annualised_return :
                    print("UPDATE History_NAV SET ANAV='"+str(ANAV)+"' WHERE Fund_code='"+Fund_code+"' and History_NAV_Date='"+behind_date+"';")
                    cur.execute("UPDATE History_NAV SET ANAV='"+str(ANAV)+"' WHERE Fund_code='"+Fund_code+"' and History_NAV_Date='"+behind_date+"';")
            except:
                print('error')
                mysql_client.commit()
    mysql_client.commit()

cur.close()
mysql_client.close()
print('Spider finish！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
