# -*-coding:utf-8-*-
import requests,time,pymysql
from lxml import etree

yield_curve_rates_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldAll'
bill_rates_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billratesAll'
long_termrate_rates_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=longtermrateAll'
real_yield_curve_rates_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=realyieldAll'
real_long_term_rates_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=reallongtermrateAll'
# history_url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=billratesAll'

mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
# 使用cursor()方法获取操作游标
cur = mysql_client.cursor()

for index,url in enumerate([yield_curve_rates_url,bill_rates_url,long_termrate_rates_url,real_yield_curve_rates_url,real_long_term_rates_url]):

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "__utmt=1; __utma=62311785.975372015.1517366644.1517366644.1517366644.1; __utmb=62311785.14.10.1517366644; __utmc=62311785; __utmz=62311785.1517366644.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.975372015.1517366644; _gid=GA1.2.1207123772.1517366644; fsr.s=%7B%22v2%22%3A1%2C%22v1%22%3A1%2C%22rid%22%3A%22d464cf4-82644728-c346-edac-7c270%22%2C%22to%22%3A4.1%2C%22mid%22%3A%22d464cf4-82645028-af41-1426-48178%22%2C%22rt%22%3Afalse%2C%22rc%22%3Atrue%2C%22c%22%3A%22https%3A%2F%2Fwww.treasury.gov%2Fresource-center%2Fdata-chart-center%2Finterest-rates%2FPages%2FTextView.aspx%22%2C%22pv%22%3A13%2C%22lc%22%3A%7B%22d1%22%3A%7B%22v%22%3A13%2C%22s%22%3Atrue%7D%7D%2C%22cd%22%3A1%2C%22f%22%3A1517370038739%2C%22meta%22%3A%7B%22rtp%22%3A%22c%22%2C%22rta%22%3A6%2C%22rts%22%3A2%7D%2C%22sd%22%3A1%2C%22l%22%3A%22en%22%2C%22i%22%3A-1%7D",
        "Host": "www.treasury.gov",
        "If-Modified-Since": "Tue, 30 Jan 2018 22:44:57 GMT",
        "Referer": "https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    html = requests.get(url=url,headers=headers).text
    # print(html)
    html_xpath_obj = etree.HTML(html)
    if index == 0:
        date = html_xpath_obj.xpath("//td[@class='text_view_data'][1]//text()")
        month_1 = html_xpath_obj.xpath("//td[@class='text_view_data'][2]//text()")
        month_3 = html_xpath_obj.xpath("//td[@class='text_view_data'][3]//text()")
        month_6 = html_xpath_obj.xpath("//td[@class='text_view_data'][4]//text()")
        year_1 = html_xpath_obj.xpath("//td[@class='text_view_data'][5]//text()")
        year_2 = html_xpath_obj.xpath("//td[@class='text_view_data'][6]//text()")
        year_3 = html_xpath_obj.xpath("//td[@class='text_view_data'][7]//text()")
        year_5 = html_xpath_obj.xpath("//td[@class='text_view_data'][8]//text()")
        year_7 = html_xpath_obj.xpath("//td[@class='text_view_data'][9]//text()")
        year_10 = html_xpath_obj.xpath("//td[@class='text_view_data'][10]//text()")
        year_20 = html_xpath_obj.xpath("//td[@class='text_view_data'][11]//text()")
        year_30 = html_xpath_obj.xpath("//td[@class='text_view_data'][12]//text()")

        cur.execute("select date from yield_curve_rates;")
        existed_date = [date[0] for date in cur.fetchall()]
        print('existed_date:', existed_date)
        for date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30 in zip(date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30):

            if date not in existed_date:
                cur.execute(
                    "insert into yield_curve_rates(date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30))
                print('inserting data to mysql...', date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30)
            else:
                print('existed!skiping...')

            print(date,month_1,month_3,month_6,year_1,year_2,year_3,year_5,year_7,year_10,year_20,year_30)
        print('----------------------------',index)
    elif index == 1:
        date = html_xpath_obj.xpath("//td[@class='text_view_data'][1]//text()")
        weeks_4_bank_discount= html_xpath_obj.xpath("//td[@class='text_view_data'][2]//text()")
        weeks_4_coupon_equivalent = html_xpath_obj.xpath("//td[@class='text_view_data'][3]//text()")
        weeks_13_bank_discount = html_xpath_obj.xpath("//td[@class='text_view_data'][4]//text()")
        weeks_13_coupon_equivalent = html_xpath_obj.xpath("//td[@class='text_view_data'][5]//text()")
        weeks_26_bank_discount = html_xpath_obj.xpath("//td[@class='text_view_data'][6]//text()")
        weeks_26_coupon_equivalent = html_xpath_obj.xpath("//td[@class='text_view_data'][7]//text()")
        weeks_52_bank_discount = html_xpath_obj.xpath("//td[@class='text_view_data'][8]//text()")
        weeks_52_coupon_equivalent = html_xpath_obj.xpath("//td[@class='text_view_data'][9]//text()")

        cur.execute("select date from bill_rates;")
        existed_date = [date[0] for date in cur.fetchall()]
        print('existed_date:', existed_date)

        for date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount, weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount, weeks_52_coupon_equivalent in zip(
                date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount,
                weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount,
                weeks_52_coupon_equivalent):

            if date not in existed_date:
                cur.execute(
                    "insert into bill_rates(date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount, weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount, weeks_52_coupon_equivalent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount, weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount, weeks_52_coupon_equivalent))
                print('inserting data to mysql...', date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount, weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount, weeks_52_coupon_equivalent)
            else:
                print('existed!skiping...')

            # print(date, weeks_4_bank_discount, weeks_4_coupon_equivalent, weeks_13_bank_discount, weeks_13_coupon_equivalent, weeks_26_bank_discount, weeks_26_coupon_equivalent, weeks_52_bank_discount, weeks_52_coupon_equivalent)
        print('----------------------------', index)
    elif index == 2:

        cur.execute("select date from long_termrate_rates;")
        existed_date = [date[0] for date in cur.fetchall()]
        print('existed_date:', existed_date)

        date = html_xpath_obj.xpath("//td[1]/table[@class='t-chart']/tbody/tr/td[1]//text()")
        lt_composite_10_yrs = html_xpath_obj.xpath("//td[1]/table[@class='t-chart']/tbody/tr/td[2]//text()")
        treasury_20_yr_cmt = html_xpath_obj.xpath("//td[2]/table[@class='t-chart']/tbody/tr/td[2]//text()")
        extrapolation_factor= html_xpath_obj.xpath("//td[2]/table[@class='t-chart']/tbody/tr/td[3]//text()")
        for date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor in zip(date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor):

            if date not in existed_date:
                cur.execute(
                    "insert into long_termrate_rates(date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor) VALUES(%s,%s,%s,%s)",
                    (date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor))
                print('inserting data to mysql...', date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor)
            else:
                print('existed!skiping...')

            # print(date,lt_composite_10_yrs,treasury_20_yr_cmt,extrapolation_factor)
        print('----------------------------', index)

    elif index == 3:

        cur.execute("select date from real_yield_curve_rates;")
        existed_date = [date[0] for date in cur.fetchall()]
        print('existed_date:', existed_date)

        date = html_xpath_obj.xpath("//td[@class='text_view_data'][1]//text()")
        year_5 = html_xpath_obj.xpath("//td[@class='text_view_data'][2]//text()")
        year_7 = html_xpath_obj.xpath("//td[@class='text_view_data'][3]//text()")
        year_10 = html_xpath_obj.xpath("//td[@class='text_view_data'][4]//text()")
        year_20 = html_xpath_obj.xpath("//td[@class='text_view_data'][5]//text()")
        year_30 = html_xpath_obj.xpath("//td[@class='text_view_data'][6]//text()")
        for date,year_5,year_7,year_10,year_20,year_30 in zip(date,year_5,year_7,year_10,year_20,year_30):

            if date not in existed_date:
                cur.execute(
                    "insert into real_yield_curve_rates(date,year_5,year_7,year_10,year_20,year_30) VALUES(%s,%s,%s,%s,%s,%s)",
                    (date,year_5,year_7,year_10,year_20,year_30))
                print('inserting data to mysql...', date,year_5,year_7,year_10,year_20,year_30)
            else:
                print('existed!skiping...')

            # print(date,year_5,year_7,year_10,year_20,year_30)
        print('----------------------------', index)

    else:

        cur.execute("select date from real_long_term_rates;")
        existed_date = [date[0] for date in cur.fetchall()]
        print('existed_date:', existed_date)

        date = html_xpath_obj.xpath("//td[@class='text_view_data'][1]//text()")
        lt_real_average_10_yrs = html_xpath_obj.xpath("//td[@class='text_view_data'][2]//text()")
        for date,lt_real_average_10_yrs in zip(date,lt_real_average_10_yrs):

            if date not in existed_date:
                cur.execute(
                    "insert into real_long_term_rates(date,lt_real_average_10_yrs) VALUES(%s,%s)",
                    (date,lt_real_average_10_yrs))
                print('inserting data to mysql...', date,lt_real_average_10_yrs)
            else:
                print('existed!skiping...')

            print(date,lt_real_average_10_yrs)

        print('----------------------------', index)
    mysql_client.commit()
    time.sleep(10)

print('正在排序数据表中的id列....')
tableNameList = ["yield_curve_rates","bill_rates","long_termrate_rates","real_yield_curve_rates","real_long_term_rates"]
for tableName in tableNameList:
    cur.execute("ALTER TABLE " + tableName + " DROP id;")
    cur.execute("ALTER  TABLE " + tableName + " ADD id MEDIUMINT( 8 ) NOT NULL  FIRST;")
    cur.execute("ALTER  TABLE " + tableName + " MODIFY COLUMN id MEDIUMINT( 8 ) NOT NULL  AUTO_INCREMENT,ADD PRIMARY  KEY(id);")
cur.close()
mysql_client.close()
print('Spider finish！',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))