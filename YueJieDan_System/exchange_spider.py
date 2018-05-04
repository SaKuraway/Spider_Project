#-*-coding:utf-8-*-
import requests,pymysql,re,datetime,json
from lxml import etree

mysql_client = pymysql.connect(host='148.66.60.194', port=17001, user='planner', password='plan1701',database='data_finance', charset='utf8')
cur = mysql_client.cursor()

def date_to_num(date):
    date = str(date).replace(',','') #
    month_num_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                      'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', 'January': '01',
                      'February': '02', 'March': '03', 'April': '04', 'June': '06', 'July': '07', 'August': '08',
                      'September': '09', 'October': '10', 'November': '11', 'December': '12'}
    try:
        date = date.strip().replace('\n', '').replace('\t', '')  # date = "28 Jan 2013"
        if ' ' in date:
            date_eng = date.split(' ')
        elif '/' in date:
            date_eng = date.split('/')
        elif '-' in date:
            date_eng = date.split('-')
        try:
            date_eng[1] = month_num_dict[date_eng[1]]
        except:
            try:
                date_eng[0] = month_num_dict[date_eng[0]]
            except:
                pass

        if len(date_eng[0]) < len(date_eng[-1]):
            date_eng[0], date_eng[1] = date_eng[1], date_eng[0] #
            date_eng[0], date_eng[-1] = date_eng[-1], date_eng[0] #
        date_number = '-'.join(date_eng)
        # print(date_number)
        return date_number
    except:
        return date

# USD 对外汇率
start_url = 'https://www.investing.com/currencies/streaming-forex-rates-majors'
headers = {
    "Accept":"text/plain, */*; q=0.01",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Connection":"keep-alive",
    # "Content-Length":"172",
    "Content-Type":"application/x-www-form-urlencoded",
    # "Cookie":"PHPSESSID=hklcml40iai2k7fl1hsessk587; geoC=HK; adBlockerNewUserDomains=1524217194; gtmFired=OK; StickySession=id.62467976145.766.www.investing.com; __gads=ID=dccb295e68cb60c3:T=1524217213:S=ALNI_MY1xolAGO5Pc3_fyRyx0Ajy73M7sg; editionPostpone=1524217225673; SideBlockUser=a%3A2%3A%7Bs%3A10%3A%22stack_size%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Bi%3A8%3B%7Ds%3A6%3A%22stacks%22%3Ba%3A1%3A%7Bs%3A11%3A%22last_quotes%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A3%3A%7Bs%3A7%3A%22pair_ID%22%3Bs%3A1%3A%221%22%3Bs%3A10%3A%22pair_title%22%3Bs%3A14%3A%22Euro+US+Dollar%22%3Bs%3A9%3A%22pair_link%22%3Bs%3A19%3A%22%2Fcurrencies%2Feur-usd%22%3B%7D%7D%7D%7D; optimizelySegments=%7B%224225444387%22%3A%22gc%22%2C%224226973206%22%3A%22direct%22%2C%224232593061%22%3A%22false%22%2C%225010352657%22%3A%22none%22%7D; optimizelyBuckets=%7B%2210555684981%22%3A%2210586870005%22%7D; optimizelyEndUserId=oeu1524217189920r0.266480008473186; billboardCounter_1=0; _ga=GA1.2.139730349.1524217243; _gid=GA1.2.1260749101.1524217247; nyxDorf=Y2dmNTVgMnBmMmllYTE3KzBkNm02L2FiNz4%3D; __qca=P0-2088123517-1524217403008; r_p_s_n=1",
    "Host":"www.investing.com",
    "Origin":"https://www.investing.com",
    "Referer":"https://www.investing.com/currencies/eur-usd-historical-data?optimizely_show_preview=false&optimizely_token=6712d697d95188777f29c3662e9f7ed1731788b91d34e5e154dfa90bda5714e1&optimizely_x10555684981=1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
}
ssion = requests.session()
start_html = ssion.get(url=start_url,headers=headers).text
start_response = etree.HTML(start_html)
print('汇率有%s个',len(start_response.xpath("//div[@id='cross_rates_container']//table[@id='cr1']//tr//td//a")))
for currencies in start_response.xpath("//div[@id='cross_rates_container']//table[@id='cr1']//tr//td//a//text()"):
    if currencies == 'USD/CNY':
        continue
    if 'USD' in currencies:
        try:
            # href = 'https://www.investing.com'+str(currencies.xpath(".//@href")[0])
            print(currencies)
            history_html_url = "https://www.investing.com/currencies/"+currencies.split('/')[0].lower()+"-"+currencies.split('/')[1].lower()+"-historical-data?"
            print(history_html_url)
            history_html = ssion.get(url=history_html_url,headers=headers).text
            pattern1 = re.compile('pairId:(.*?)[,}]',re.S)
            pattern2 = re.compile('smlId:(.*?)[,}]',re.S)
            curr_id = re.sub("\D", "", pattern1.findall(history_html)[0])
            smlID = re.sub("\D", "", pattern2.findall(history_html)[0])
            print('curr_id,smlID',curr_id,smlID)
            currency_formdata = {
                "curr_id":curr_id,
                "smlID":smlID,
                "header":currencies+" Historical Data",
                "st_date":"01/01/2010",
                "end_date":"01/01/2020",
                "interval_sec":"Daily",
                "sort_col":"date",
                "sort_ord":"DESC",
                "action":"historical_data",
            }
            history_data_url = 'https://www.investing.com/instruments/HistoricalDataAjax'
            # print(ssion.post(url=history_data_url,headers=headers,data=currency_formdata).text)
            history_data_response = etree.HTML(ssion.post(url=history_data_url,headers=headers,data=currency_formdata).text)
            date = history_data_response.xpath("//div[@id='results_box']//tr//td[1]//text()")
            price = history_data_response.xpath("//div[@id='results_box']//tr//td[2]//text()")
            open = history_data_response.xpath("//div[@id='results_box']//tr//td[3]//text()")
            high = history_data_response.xpath("//div[@id='results_box']//tr//td[4]//text()")
            low = history_data_response.xpath("//div[@id='results_box']//tr//td[5]//text()")
            change = history_data_response.xpath("//div[@id='results_box']//tr//td[6]//text()")
            # 去重
            cur.execute("select date from Exchange_Rate where exchange_currency='" + currencies + "';")
            existed_date = [date[0] for date in cur.fetchall()]
            print(currencies, 'existed_date:', existed_date)

            for date,price,open,high,low,change in zip(date,price,open,high,low,change):
                if date_to_num(date) not in existed_date:
                    print(currencies,date_to_num(date),price,open,high,low,change)
                    cur.execute("insert into Exchange_Rate (exchange_currency,date,price,open_price,high,low,change_percent) values (%s,%s,%s,%s,%s,%s,%s)", (currencies,date_to_num(date),price,open,high,low,change))
                else:
                    print('existed! pass..')
        except Exception as e:
            print('error!',e)
        else:
            mysql_client.commit()

# 人民币对外汇率
last_year_date = (datetime.datetime.now() + datetime.timedelta(days=-364)).strftime('%Y-%m-%d')
today = datetime.datetime.now().strftime('%Y-%m-%d')
chinamoney_headers = {
    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Connection":"keep-alive",
    "Content-Length":"0",
    # "Cookie":"JSESSIONID=4BrxNtFxjTRu3wE_Ukieap4pyd-ADAp-RP43sX9G2R5Qo4wey97k!944294888; _ulta_id.CM-Prod.e9dc=4371ab4d733ebcd6; ADMINCONSOLESESSION=h9PxPMqqQVfYTECiNWmOyAp_wRHJItmInWKtiYdd5JbLgcovT19m!944294888; _ulta_ses.CM-Prod.e9dc=d1f8286200b46c24; ZP_CAL=%27fdow%27%3Anull%2C%27history%27%3A%222017/04/24/14/43%2C2017/04/23/14/43%2C2017/04/03/14/43%2C2016/03/16/14/42%22%2C%27sortOrder%27%3A%22asc%22%2C%27hsize%27%3A9",
    "Host":"www.chinamoney.com.cn",
    "Origin":"http://www.chinamoney.com.cn",
    "Referer":"http://www.chinamoney.com.cn/r/cms/www/chinamoney/html/cn/historyParityCn.html",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
}
chinamoney_url= "http://www.chinamoney.com.cn/dqs/rest/dqs-u-fx-base/CcprHisNew?startDate="+last_year_date+"&endDate="+today
print(chinamoney_url)
chinamoney_formdata = {
    "startDate":last_year_date,
    "endDate":today
}
chinaforex_data_json = requests.post(url=chinamoney_url,headers=chinamoney_headers,data=chinamoney_formdata).text
chinaforex_data_dict = json.loads(chinaforex_data_json)
currency_list = chinaforex_data_dict['data']['head']
chinaforex_data_list= chinaforex_data_dict['records']

# 去重
cur.execute("select date from Exchange_Rate where exchange_currency='" + currency_list[-1] + "';")
existed_date = [date[0] for date in cur.fetchall()]
print(currency_list[-1], 'existed_date:', existed_date)
for chinaforex_data in chinaforex_data_list:
    date = chinaforex_data['date']  # '2018-04-23'
    value_list = chinaforex_data['values']   # [,,,]
    if date not in existed_date:
        for currency,value in zip(currency_list,value_list):
            print(date,currency,value)
            cur.execute("insert into Exchange_Rate(exchange_currency,date,price) values(%s,%s,%s)",(currency,date,value))
    else:
        print('existed! pass..')
mysql_client.commit()


cur.close()
mysql_client.close()