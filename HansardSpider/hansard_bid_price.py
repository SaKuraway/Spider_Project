#-*-coding:utf-8-*-
import requests,re,pymysql,time,sys,datetime
from lxml import etree

hansard_passwd = str(input("请输入6位hansard动态密码："))
# hansard_passwd = str(sys.argv[1])

# mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
mysql_client = pymysql.connect(host="112.74.93.48",port=3306,user="root",password="962ced336f",database="statement",charset="utf8")
cur = mysql_client.cursor()

def get_all_date(start='2015-12-31',end='2018-07-11'):

    datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end, '%Y-%m-%d')

    month_num_dict = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul',
                      '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
    format_date_list = []
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        format_date = str(datestart)[:10]
        format_date = '-'.join(
            [format_date.split('-')[-1], month_num_dict[format_date.split('-')[1]], format_date.split('-')[0]])
        # print(format_date)
        format_date_list.append(format_date)
    return format_date_list

def date_to_num(input_date):
    month_num_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                      'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12', 'January': '01',
                      'February': '02', 'March': '03', 'April': '04', 'June': '06', 'July': '07', 'August': '08',
                      'September': '09', 'October': '10', 'November': '11', 'December': '12'}
    try:
        date = input_date.strip().replace('\n', '').replace('\t', '')  # date = "28 Jan 2013"
        if ' ' in date:
            date_eng = date.split(' ')
        elif '/' in date:
            date_eng = date.split('/')
        elif '-' in date:
            date_eng = date.split('-')

        try:
            month = month_num_dict[date_eng[0]]
            date_eng[0], date_eng[1] = date_eng[1], month
        except:
            try:
                month = month_num_dict[date_eng[1]]
                date_eng[1] = month
            except:
                month = month_num_dict[date_eng[-1]]
                date_eng[1], date_eng[-1] = month, date_eng[1]

        if len(date_eng[0]) < len(date_eng[-1]):
            date_eng[0], date_eng[-1] = date_eng[-1], date_eng[0]

        date_number = '-'.join(date_eng)
        # print(date_number)
        return date_number

    except:
        return input_date


def bonusget(input_x):
    x = input_x.strip().lower()
    if x == 'monthly':
        return 20
    if x == 'quarterly':
        return 8
    if x == 'half-yearly' or x == 'semi-annual':
        return 4
    if x == 'annually' or x == 'annual':
        return 2
    if x == 'initial':
        return '1'
    if x == 'accumulator':
        return '2'
    else:
        print('bonus or type error',input_x)


def frequency_to_num(input_x):
    x = input_x.strip().lower()
    if x == 'monthly':
        return 1
    if x == 'quarterly' :
        return 3
    if x == 'half-yearly' or x == 'semi-annual':
        return 6
    if x == 'annually' or x == 'annual':
        return 12
    else:
        print('frequency_error:',input_x)
        return input_x

def try_except(sth):

    # 使用cursor()方法获取操作游标
    # self.cur = self.mysql_client.cursor()
    print('inserting data to mysql ...')
    try:
        sth
    except pymysql.Error as e:
        with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
            print('Writing Error info...', e)
            f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
        f.close()
        # finally:
        #     self.cur.close()
        # self.mysql_client.commit()
        # return sth

start_url = 'https://ho.hftrust.com/CookieAuth.dll?GetLogon?curl=Z2F&reason=0&formdir=9'
login_url = 'https://ho.hftrust.com/CookieAuth.dll?Logon'
search_url = 'https://ho.hftrust.com/hansard/hansard/servlet/pds/Pds'
history_url = 'https://ho.hftrust.com/hansard/hansard/servlet/pds/Pds?RequestedPage=SearchResultsHeader'

login_headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Cache-Control":"max-age=0",
    "Connection":"keep-alive",
    # "Content-Length":"114",
    "Content-Type":"application/x-www-form-urlencoded",
    # "Cookie":"rsa-local=ernc15035Z00Z002Z005ACAA8D2Z005ACAA8D2Z00Z00Z00ZA5+Z27Z9CZDE2Z7EZ95Z2FZ09Z17ZD41ZCBZE5cZ90ZAAZ1EZE2ZB2ZFEZ93ZC4jZ5DZBCZ9CZ99Z8BZ12",
    "Host":"ho.hftrust.com",
    "Origin":"https://ho.hftrust.com",
    "Referer":"https://ho.hftrust.com/CookieAuth.dll?GetLogon?curl=Z2F&reason=0&formdir=9",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
}
login_data = {
    # "userid":"ntnd15035",
    # "userid":"ernc15035",
    "userid":"cess15035",

    # "passcode":"sarah33"+str(hansard_passwd),
    # "passcode":"fizz"+str(hansard_passwd),
    "passcode":"yuwin"+str(hansard_passwd),
    "SubmitCreds":""

    # hidden token数据如下：
    # stage:useridandpasscode
    # curl:Z2F
    # sessionid:0
    # formdir:9
    # trusted:4
}

search_data = {
    "eou":"",
    "Advanced":"false",
    "RequestedPage":"SearchResultsFrame",
    "SavedSearch":"",
    "Action":"TempStoreCriteria",
    "PolicyNumber":"",
    "Surname":"",
    "Forename":"",
    "Sort":"None",
    "PolicyStatusCheck":"on",
    "PolicyStatus":"Active",
    "Company":"",
    "PolicyRole":"",
    "ProductGroup":"All",
}
# allocation_data = {
#     "Report":"UnitAllocation",
#     "policyNumber":"562371",
#     "checkDigit":"T",
#     "company":"HIL",
#     "Locale":"GB,en",
#     "type":"HTML",
# }

# 获取登录参数
ssion = requests.session()
print('start_url---------------------')
login_html = ssion.get(url=start_url, headers=login_headers).text # ,verify=False
# print(login_html)
login_html_xpathobj = etree.HTML(login_html)
hidden_names = login_html_xpathobj.xpath("//input[@type='hidden']//@name")
# print(hidden_names)
hidden_values = [login_html_xpathobj.xpath("//input[@name='"+hidden_name+"']/@value") for hidden_name in hidden_names]
# print(hidden_values)
for hidden_name,hidden_value in zip(hidden_names,hidden_values):
    login_data[hidden_name] = hidden_value[0] if hidden_value else ''
print(login_data)

time.sleep(1)
# login
after_login_html = ssion.post(url=login_url,headers=login_headers,data=login_data)
# print(after_login_html.text)
print('login~~~~~~~~~')
# print(after_login_html.request.headers)
print(after_login_html.cookies)
time.sleep(1)
# 首页
home_page = ssion.get(url='https://ho.hftrust.com/hansard/hansard/servlet/frontpage/FrontPage',headers=login_headers)
time.sleep(1)
# 反爬幌子
search_html1 = ssion.post(url=search_url,headers=login_headers,data=search_data)
search_html2 = ssion.get(url=history_url,headers=login_headers)
# print(search_html2.text)
print('spider_beginning********************')
time.sleep(1)
# 真正获取数据
search_html3 = ssion.post(url=search_url,headers=login_headers,data={"RequestedPage":"SearchResults"})
# print(search_html3.text)
# print(etree.HTML(search_html3.text).xpath("table[@class='search_result ']//tr//td//a//text()"))
print('/////////'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'//////////')
time.sleep(2)
list_page = ssion.get(url='https://ho.hftrust.com/hansard/hansard/servlet/pds/Pds?PaginationSize=1000&Start=0&RequestedPage=SearchResults&POLICYSTATUSCHECK=on&POLICYSTATUS=Active&SORT=None&PRO',headers=login_headers) # 默认是50和50
# print(list_page.text)

# policy_no_list=['562713','562250','562710','564106','564101','563689','563896','563851','563448','563466','564642','564663','563616','563754','563174','564597','564246','563654','563324','566945','565390','565412','565424','565428','565479','566859','565669','566405','566423','566436','565905','565924','566557','565759','567286','566258','567210','562716','562690','562696','563070','562368','562715','562277','564089','564142','562819','563925','563824','564771','564547','563290','563636','563638','564587','567017','565126','565169','565203','566953','566046','566123','566204','565299','565331','565461','565474','565499','566898','566879','566936','567167','566331','566519','565732','567325','565477','562369','562487','562821','562825','562830','562836','562808','563032','562805','562168','562346','562365','562371','562711','562483','562699','562704','563699','564534','564540','564545','564653','563748','563772','563828','563835','565018','565129','565214','566968','566218','565374','565485','566857','566457','566403','566412','566782','566488','566504','566270','566304','565977','566016','562598','563016','563029','562275','563153','562390','562677','562247','562695','563721','564474','564108','564155','563753','564983','563576','563225','564222','564323','564681','562779','565065','566994','566101','565363','565447','565799','566907','565592','565817','566460','566620','566490','565700','565783','566015','562820','567329','562717','562729','562732','562573','562656','562775','562776','562335','562366','562723','562454','563684','563683','564494','564501','564114','564109','564119','564541','564636','563606','563621','563776','563797','564210','564271','563651','564574','564595','566969','565475','566882','566377','566509','565763','565714','563610','563842','562357','562413','562503','562650','563175','563157','563092','562724','562436','562292','564086','564111','564149','564150','564531','563617','563618','563563','563193','564226','564598','564298','564667','563278','563652','564592','565207','566980','566180','566735','565257','565336','565437','566873','566900','565820','566414','566473','566362','566550','567264','565531','566245','565979','563464','562727','562433','562515','562823','562831','562781','563099','562202','562338','562614','564778','564782','564169','563815','564418','563207','564596','563286','563166','566234','565476','566912','567172','565596','566575','566787','566342','565734','565736','565756','567346','566279','562372','562645','562508','562544','562647','562257','562350','562251','563713','564130','564646','564189','563817','564673','564551','564273','564565','563655','563661','564575','565123','566955','567041','566121','565245','565449','565452','566914','565664','566344','565768','565770','565958','565032','562499','562571','562602','562643','562415','563159','562772']
pattern = re.compile(r"polNumArray = new Array\((.*?)\);", re.S)
pattern_policy = re.compile("\d", re.S)
policy_no_list = pattern.findall(list_page.text)[0].replace("'",'').replace('"','').replace(' ','').split(',')
# policy_no_list.reverse()
print('policy_no_list的数量',len(policy_no_list)-1)
Spider_Date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
for policy_no in policy_no_list[1:]:
    print('-----------')
    print(policy_no)
    if policy_no != '562508':
        print('continue')
        continue
    try:
        allocation_data = {
            "Report":"UnitAllocation",
            "policyNumber":int(policy_no),
            "checkDigit":"T",
            "company":"HIL",
            "Locale":"GB,en",
            "type":"HTML"
        }
        history_page_data = {
            "Report":"HistoricUAS",
            "policyNumber":policy_no,
            "checkDigit":"H",
            "company":"HIL",
            "Locale":"GB,en",
            "type":"HTML"
        }
        # 选择日期页面
        ssion.post(url=history_url, headers=login_headers, data=history_page_data)
        for date in get_all_date():
            print(date)
            history_allocation_data = {
                "HistoricUAS_StartDate":date,
                "HistoricUAS_EndDate":"",
                "RequestedPage":"SearchResultsHeader",
                "Report":"HistoricUAS",
                "policyNumber":policy_no,
                "checkDigit":"H",
                "company":"HIL",
                "Locale":"GB,en",
                "type":"HTML"
            }

            time.sleep(1)
            # 获取allcation
            time.sleep(1)
            allocation_html = ssion.post(url=history_url, headers=login_headers, data=history_allocation_data)
            # print(allocation_html.text)

            allocation_response = etree.HTML(allocation_html.text)
            Fund_code = []
            Fund_name = []
            unit = []
            type = []
            price_date = []
            bid_price = []
            fund_value = []
            rate = []
            uks = []
            accumulator_flag = 0
            full_policy_no = ''.join(allocation_response.xpath("//div[@class='full list_2_col']//ul/li[2]/text()")).strip().replace(' ','')
            product = ''.join(allocation_response.xpath("//div[@class='full list_2_col']//ul/li[1]/text()")).strip().replace(' ','')
            policy_currency = ''.join(allocation_response.xpath("//div[@class='full list_2_col']/ul/li[last()]/text()")).strip().replace(' ','')
            total_value = float(''.join(allocation_response.xpath("//tr[@class='bottom']/td[@class='number']//text()")).strip().replace(',','').replace(' ','')) if allocation_response.xpath("//tr[@class='bottom']/td[@class='number']") else 1
            print('full_policy_no',full_policy_no)
            for length in range(2,len(allocation_response.xpath("//div[@class='results']//table//tr"))):
                if allocation_response.xpath("//div[@class='results']//table//tr[" + str(length) + "]/td[1]//text()")[0] == u'\xa0':
                    accumulator_flag = 1
                else:
                    accumulator_flag = 0
                Fund_code.append(allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[1]//text()")[0] if accumulator_flag == 0 else fund_code)
                Fund_name.append(allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[2]//text()")[0] if accumulator_flag == 0 else fund_name)
                price_date.append(allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[5]//text()")[0] if accumulator_flag == 0 else allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[4]//text()")[0])
                bid_price.append(allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[6]//text()")[0] if accumulator_flag == 0 else allocation_response.xpath("//div[@class='results']//table//tr["+str(length)+"]/td[5]//text()")[0])
                fund_code = allocation_response.xpath(
                    "//div[@class='results']//table//tr[" + str(length) + "]/td[1]//text()")[0]
                fund_name = allocation_response.xpath(
                    "//div[@class='results']//table//tr[" + str(length) + "]/td[2]//text()")[0]
                time.sleep(1)
            if not cur.execute("select * from tb_allocation_initial where policy_no='" + full_policy_no + "' and price_date='" + price_date + "';"):
                for Fund_code,Fund_name,price_date,bid_price in zip(Fund_code,Fund_name,price_date,bid_price):
                    # print(Fund_code,Fund_name,unit.replace(',',''),type,date_to_num(price_date),bid_price.replace(',',''),fund_value[:3],fund_value[3:].replace(',',''),rate,uks.replace(',',''))
                    print(full_policy_no, Fund_name, Fund_code,bid_price.replace(',',''),date_to_num(price_date))
                    cur.execute("insert into tb_allocation_initial(policy_no,fund,fund_code,price,price_date) VALUES(%s,%s,%s,%s,%s)",(full_policy_no, Fund_name, Fund_code,bid_price.replace(',',''),date_to_num(price_date)))

            time.sleep(2)

    except Exception as e:
        print(policy_no,':error!', e)
    else:
        mysql_client.commit()
        print('committed.')
        break

print('Spider_finish!',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
# Logout
ssion.get(url='https://ho.hftrust.com/hansard/hansard/servlet/frontpage/FrontPage?RequestedPage=LoggedOut&Action=LogOut',headers=login_headers)
print('logout.')

cur.close()
mysql_client.close()

