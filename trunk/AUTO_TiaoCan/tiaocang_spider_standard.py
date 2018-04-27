import re
import os
import sys
import time
import random
import pandas
import pymysql
import requests
from lxml import etree
from copy import deepcopy
# smtp服务器模块
import smtplib
# 构造邮件模块
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
# 有序字典模块
import collections
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf
# 导入 webdriver
from selenium import webdriver
# 右键操作
from selenium.webdriver import ActionChains
# 引入keys包调用多个键盘按键配合操作
from selenium.webdriver.common.keys import Keys
# WebDriverWait 库，负责循环等待
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# 导入 Select 类 处理下拉框
from selenium.webdriver.support.ui import Select
# expected_conditions 类，负责条件出发
from selenium.webdriver.support import expected_conditions as EC
# 导入selenium的报头对象
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class AutoOperation(object):
    """
    Hansard、ITA、zurich三个平台的基金自动化调仓程序。——SaKuraPan__2017.12__Trussan .
    """

    def __init__(self):
        """
        初始化参数
        """
        # excel文件名
        # self.excel_name = 'Excel/ClientSwitch ' + str(input("请输入需要调仓的Excel表格年月，如 201712：")) + '.xls'
        self.excel_name = 'Excel/ClientSwitch login_test.xls'
        # excel中保单号的行数
        self.policy_index = 0
        # excel表格的行索引
        # 错误标志
        self.error = 0
        # 成功次数
        self.successed = 0
        # 失败次数
        self.failed = 0
        # 调仓个数
        self.operation_counts = 0
        # 链接数据库
        # self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
        self.mysql_client = pymysql.connect(host='148.66.60.194', port=17001, user='planner', password='plan1701',database='data_finance_oversea', charset='utf8')
        # 使用cursor()方法获取操作游标
        self.cur = self.mysql_client.cursor()
        self.Hansard_index = []
        self.ITA_index = []
        self.zurich_index = []
        self.standard_life_index = []
        self.axa_index = []

    def _format_addr(self, address):
        """
        规范邮件地址
        :param address: 邮箱用户名及地址
        :return: MIME规范化的用户名及地址
        """
        name, addr = parseaddr(address)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def browser_login(self, url, username, password, username_id, password_id, submit_id):
        """
        调用并操作浏览器对象
        :param url: 网址
        :param username: 用户名
        :param password: 密码
        :param username_id: 用户名输入框ID
        :param password_id: 密码输入框ID
        :param submit_id: 点击确认的ID
        :return: driver对象
        """
        # 调用环境变量指定的Chrome浏览器创建浏览器对象
        driver = webdriver.Chrome()
        # driver = webdriver.Chrome(executable_path="./chromedriver_linux64/chromedriver")

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(chrome_options=chrome_options)

        # 先随机获取一个user-agent
        # agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        # 将PhantomJS浏览器报头 转为字典对象，可以修改键对应的值
        # cap = dict(DesiredCapabilities.PHANTOMJS)
        # 修改PhantomJS的user-agent
        # dcap["phantomjs.page.settings.userAgent"] = agent
        # 如果没有在环境变量指定PhantomJS位置
        # driver = webdriver.PhantomJS()
        # driver = webdriver.PhantomJS(executable_path="./phantomjs-2.1.1-linux-x86_64/bin/phantomjs")

        # ②第二种方法：
        # cap = webdriver.DesiredCapabilities.PHANTOMJS
        # cap["phantomjs.page.settings.resourceTimeout"] = 1000
        # cap["phantomjs.page.settings.loadImages"] = True
        # cap["phantomjs.page.settings.disk-cache"] = True
        # cap[
        #     "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        # cap[
        #     "phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        # driver = webdriver.PhantomJS(desired_capabilities=cap)

        # 1.登录操作
        # get方法会一直等到页面被完全加载，然后才会继续程序，通常测试会在这里选择 self.random_sleep()
        driver.get(url)
        self.random_sleep()
        driver.find_element_by_id(username_id).send_keys(username)
        self.random_sleep()
        driver.find_element_by_id(password_id).send_keys(password)
        self.random_sleep()
        driver.find_element_by_id(submit_id).click()
        self.random_sleep()
        return driver

    def standard_life_spider(self, standard_life):
        """
        standard_life_spider调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        # standard_life = [(39970, "nan", 'albertzhou', 'zhoulu2011'), (47220, "nan", 'QueenieLuo', '12345678'), (45319, "nan", 'liuql', '789654'), (49168, "nan", 'Xiesi130', '840130abc'), (41063, "nan", 'sunna', '123456'), (46070, "nan", 'polin82082', 'tan3708026'), (38849, "nan", 'joles', '123123'), (42322, "nan", 'PANPEI', 'IPSOS1234'), (50829, "nan", 'gskmwj', '87390635'), (39429, "nan", 'tagichan', 'rika1217'), (46837, "nan", '2423569', '123qwe'), (44111, "nan", 'luohuiou', '080160'), (45381, "nan", 'zhoujy', 'gzrbzjy'), (44805, "nan", 'hwbinboy', '23290778Hzy'), (48663, "nan", 'AJIAO', 'HK6q8080'), (48440, "nan", 'yuanna1981', 'Gd87787439'), (28958, "nan", 'zhang28958', 'qwr0935'), (48396, "nan", 'fanchen94', 'fanchen94'), (50560, "nan", 'bubuzcp', '006136lsm'), (50010, "nan", 'zhouzhihui', '731230'), (39976, "nan", 'yin39976', '19870519'), (33435, "nan", 'chen33435', 'jian1234'), (40228, "nan", 'liang40228', '19870807'), (42224, "nan", 'yangyang66', '28784458'), (48588, "nan", 'hongrong', 'chr2012'), (36523, "nan", 'lege0322', '460725'), (50556, "nan", 'longkai77', '404767116'), (50557, "nan", 'xiaojie77', '404767116'), (45448, "nan", 'Janney', '1343033294'), (44537, "nan", 'longlele', '19850516'), (44893, "nan", 'lixiuwen', '19840229'), (42046, "nan", 'joyce008', 'wu831422'), (44544, "nan", 'zhangwl', '19841012'), (39879, "nan", 'juntim', 'juntim123'), (46654, "nan", 'chenguobo', '04170619'), (41933, "nan", 'szetohl', 'szetohl137'), (39424, "nan", 'tanhuizhi', '52tanhzsl'), (38933, "nan", 'clzsu', 'czz816'), (49256, "nan", 'hrchao18', 'Tutu18'), (42047, "nan", 'azhuzhu', 'echo1022'), (43072, "nan", 'jingjing', 'hq800513'), (31361, "nan", 'xu31361', '123514meng'), (42279, "nan", 'teresaH', 'Aimi0410'), (41655, "nan", 'xu41655', 'ting1234'), (30256, "nan", 'liang30256', '630913'), (31362, "nan", 'wang31362', 'wqy660912'), (52270, "nan", 'lujunfeng', '19831109'), (42039, "nan", 'azhuzhu', 'echo1022'), (46978, "nan", 'moringsing', 'lw771219'), (47846, "nan", 'sophy', 'sophy123'), (44545, "nan", 'heqina', 'qinahe'), (44536, "nan", 'wuqiyun', 'zoewuqiyun'), (42114, "nan", 'vixen_xu', '147852'), (49135, "nan", 'qiuqu', '19740820'), (48414, "nan", 'yao198001', 'xilin2011'), (47692, "nan", 'yuekui', '770805chen'), (47847, "nan", 'yayapay', 'taodan2523'), (48485, "nan", 'guo197909', 'yuguo197909'), (47693, "nan", 'timye2012', 'yihk0611'), (48094, "nan", 'yang198009', 'Ylpy2010'), (47655, "nan", 'ccpig_0504', '820504'), (47665, "nan", 510121, '510121'), (50447, "nan", 'mandymd', 'Mp3210'), (49655, "nan", 'Mws1124', 'Welsa1124'), (52569, "nan", 'hanhoumei', 'ly975331'), (52664, "nan", 'doublel', 'liangliang'), (52668, "nan", '00052668', '22op00'), (53007, "nan", 'HUANGHAO', 'HUANGHAO62'), (53010, "nan", '34118590', '11082011'), (53246, "nan", 'beansmile', 'han783xiao'), (53009, "nan", 'zlij123', 'zlij1225'), (54426, "nan", '00054426', '0054426'), (55228, "nan", 'lixc1112', '19790718'), (55229, "nan", '14739427', 'wangjing'), (55445, "nan", 'zhangshx', 'W0i7s2x4h'), (55878, "nan", 'yuanziming', '19730312'), (55954, "nan", 'aimee5127', 'Bear0526'), (56615, "nan", 'pengliushe', 'Sl19770424'), (56379, "nan", 'CHENLJ0313', 'jing7lc9'), (56378, "nan", '00056378', '19850928'), (56663, "nan", 'zeng1982', 'szy2011'), (57116, "nan", 'wlqiong', '980324wlq'), (57030, "nan", 'zhuyin1977', '20081210'), (56565, "nan", 'lilili2013', 'lilili2013'), (57148, "nan", 'purplestar', 'xiyan1981'), (57431, "nan", 'fangwei8', 'fangwei88'), (58342, "nan", 'leoyou2003', '290612'), (58445, "nan", 'tt0528', '87588599'), (58446, "nan", 'f19770321', '731218'), (58669, "nan", 'lynibm111', 'lyn7536'), (59008, "nan", 'chenying22', '19780202'), (59196, "nan", 'james＿guan', 'Guan2345'), (59197, "nan", 'zhoujy', 'gzrbzjy'), (59198, "nan", 'SEChen', 'aws7890'), (59443, "nan", 'XY645639', 'PASS6456'), (59199, "nan", 'michael22', 'yolanda26'), (59627, "nan", 'grapefunny', 'fgf510290'), (30792, "nan", 'LHY1975', 'liu0121'), (60050, "nan", 'ada0564', 'ada1101'), (59765, "nan", 'bobbychen', 520102), (59858, "nan", 'yukinben', 'uASl201309'), (59766, "nan", 'zjhlang', '99sped6'), (61253, "nan", 'aileen0302', 'aileen0302'), (60897, "nan", 'wangjin', 'haoyu0314'), (62625, "nan", 'chuntian', '2008007007'), (63041, "nan", 'edison2014', 'Edison2016'), (62977, "nan", 'chenjingwe', 'Gaojing106'), (63137, "nan", 'xgbb', 'xgbb197076'), (63138, "nan", 'czc', '51766gd'), (62851, "nan", 'cjianming', 'cjm1984'), (63393, "nan", 'mandy901', 'mandy901'), (63548, "nan", 'xianyuhui', 'Xianyuhui5'), (63563, "nan", 'zhangli920', '0704zlzzq'), (63576, "nan", 'HUANGHAO', 'HUANGHAO62'), (63597, "nan", 'xuhuixian', 'xu775532'), (63598, "nan", 'Rachel1985', 'Rachel1234'), (63596, "nan", 'candyxuqin', 'XUHU880728'), (63638, "nan", 'moonyfox', 'Wanghui28'), (56031, "nan", 'jadewang', 'Hkfs0601')]
        # standard_life = [(53011, "nan", 'jaffyhu', 'Jaffyhu121')]
        standard_life_login_url = 'https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch'

        if not standard_life:
            print('standard_life无需spider的保单！')
            return
        print('------------')
        standard_life_login_url = 'https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch'
        standard_life_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            # "Content-Length":"849",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.standardlife.hk",
            "Origin": "https://www.standardlife.hk",
            "Referer": "https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }


        for index, item in enumerate(standard_life):
            # 链接数据库
            # self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
            self.error = 0
            self.operation_counts += 1
            self.enum_index = index
            ssion = requests.session()
            try:
                # 保单号,如 T25W017027
                Policy_Num = str(item[0])[-5:]
                # 风险类型
                self.riskType = str(item[1])
                # 卖出基金

                self.random_sleep()
                username = str(item[2])
                password = str(item[3])[:10]
                standard_life_login_data = {
                    # 隐藏项
                    # "__EVENTTARGET":"",
                    # "__EVENTARGUMENT":"",
                    # "__VIEWSTATE":"/wEPDwUKMTI4OTM0MDc3Nw9kFgYCAg9kFgRmDw8WAh4EVGV4dAUJSG9uZyBLb25nZGQCAQ8PFgIfAAUyPGEgaHJlZj0ibG9naW5fYm5jLmFzcHg/bG9naW5fZnJvbT1jJmxhbmc9Y2giPjwvYT5kZAIDD2QWCAIDDxYCHgV2YWx1ZQUG55m75YWlZAIEDxYCHwEFBuWPlua2iGQCBg8PFgQeDEVycm9yTWVzc2FnZQUW6KuL6Ly45YWl55So5oi25ZCN56ixIR4HVmlzaWJsZWhkZAIHDw8WBB8CBRDoq4vovLjlhaXlr4bnorwhHwNoZGQCBA8WBB8BBQbnmbvoqJgeB29uY2xpY2sFQWphdmFzY3JpcHQ6IHNlbGYubG9jYXRpb24uaHJlZj0nc2lnbnVwL3NpZ251cF9vcmkxLmFzcHg/bGFuZz1jaCc7ZGRoLf0sHYaMuosyNYwLu33f6QZcN5+ST4l88V1V5Cc2/A==",
                    # "__VIEWSTATEGENERATOR":"8AA00206",
                    # "__EVENTVALIDATION":"/wEdAAUeH57yDkX4HY5qJ7J0J5vmwTsQWw6y6U5GrbZKe7xDC5F8FshjtXqo3Hg5+xfiAwIv8m/1VahZrxjv/SWm8XxLcNVahIS9ELOYiVfSrKeler2R8SNJd9+8/HyayjlUcGmwY1xoPi3ckN+XQDQ11Otx",
                    # "login_from":"c",
                    # 固定项
                    "txt_name": username,
                    "txt_password": password,
                    "btn_Login": "登入"
                }

                # standard_life的登录操作
                login_response = requests.get(url=standard_life_login_url, headers=standard_life_headers)
                # 获取登录的hidden参数
                login_response = etree.HTML(login_response.text)
                hidden_names = login_response.xpath("//div//input[@type='hidden']/@name")
                hidden_values = [login_response.xpath("//div//input[@name='" + hidden_name + "']/@value")[0] if login_response.xpath("//div//input[@name='" + hidden_name + "']/@value") else '' for hidden_name in hidden_names]
                # print(hidden_names, hidden_values)
                for hidden_name, hidden_value in zip(hidden_names, hidden_values):
                    # print(hidden_name, ':', hidden_value)
                    standard_life_login_data[hidden_name] = hidden_value
                # print(standard_life_login_data)
                # 登录
                after_login_response = ssion.post(url=standard_life_login_url, headers=standard_life_headers,
                                                  data=standard_life_login_data)
                print('---------------')
                print(after_login_response.text)
                print(username,'~~~~~~~~~~~~~~~~~',Policy_Num)
                pattern = re.compile(r"href='(.*?)';}toFull", re.S)
                try:
                    standard_list_url = "https://www.standardlife.hk/login/" + pattern.findall(after_login_response.text)[0]
                except Exception as e:
                    print('------------------登录失败')
                    print('error，未能匹配到此保单号:', Policy_Num, e, '可能是账户正在登录中！')
                    continue
                print('------------------登录成功')
                standard_list_response = ssion.get(url=standard_list_url, headers=standard_life_headers)
                # print(standard_list_response.text) # <SCRIPT language='JavaScript'>function toFull(){self.location.href='policy/cust_pol_sum_main.aspx?module_id=MO12&sub_module_id=SUB1201&func_id=FN120101&lang=ch';}toFull();</SCRIPT><script language='JavaScript'>		window.close();</script>
                standard_detail_response = etree.HTML(standard_list_response.text)
                standard_detail_url = "https://www.standardlife.hk/login/policy/" + standard_detail_response.xpath("//a[text()='000" + Policy_Num + "']/@href")[0]
                standard_detail_response = ssion.get(url=standard_detail_url, headers=standard_life_headers)
                # print(standard_detail_response.text)
                standard_detail_response = etree.HTML(standard_detail_response.text)
                print('~~~~~~~~~~~~~~~~~')
                # 账户保费
                Spider_Date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                Currency = ''.join(standard_detail_response.xpath("//span[@id='pol_details_lbPolCur']//text()"))
                Total_Premium = ''.join(standard_detail_response.xpath(
                    "//span[@id='lbPVSContribution']//text()")).replace(',','') if standard_detail_response.xpath(
                    "//span[@id='lbPVSContribution']") else ''
                Total_withdrawal = ''.join(standard_detail_response.xpath(
                    "//span[@id='lbPVSWithdrawals']//text()")).replace(',','') if standard_detail_response.xpath(
                    "//span[@id='lbPVSWithdrawals']") else ''
                Payment_Frequency = ''.join(standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIPayFeq']//text()")) if standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIPayFeq']") else ''
                Regular_Premium = ''.join(standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIContribution']//text()")).replace(',','') if standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIContribution']") else ''
                print('Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium:',Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)
                if not self.cur.execute("select * from Standardlife_Premium_Info where Policy_Num='" + Policy_Num + "' and Spider_Date='"+Spider_Date+"';"):
                    # self.try_except(self.cur.execute("delete from standardlife_premium_info where Policy_Num='" + Policy_Num + "';"))
                    self.try_except(self.cur.execute("insert into Standardlife_Premium_Info(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium) VALUES(%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)))

                # 未来供款
                titles = standard_detail_response.xpath(
                    "//div[@class='largeSizeHolder1000']/div/span[@class='h2']//text()")
                print(titles)
                Date = ''
                for index, title in enumerate(titles):
                    if '戶口' in title:
                        length = len(standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@id='Table_Alloc']//tr/td[3]"))
                        Investment_Account0 = str(re.sub("\D", "", title))
                        Investment_Account = [Investment_Account0[:2]] * length
                        Date = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[5]//text()")[
                            0] if standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[5]") else Date
                        Account_Type = ['01'] * length if '最初' in title else ['02'] * length
                        account_type = '01' if '最初' in title else '02'
                        Allocation_In_Policy_Currency = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@id='Table_Alloc']//tr/td[3]//text()")
                        Allocation = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@id='Table_Alloc']//tr/td[2]//text()")
                        Allocation_Fund_Name = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@id='Table_Alloc']//tr/td[1]//text()")[1:-1]
                        print(index,
                              'Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name',
                              Investment_Account, Account_Type, Allocation_In_Policy_Currency, Allocation,
                              Allocation_Fund_Name)
                        if not self.cur.execute("select * from Standardlife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "' and Spider_Date='" + Spider_Date + "';"):
                            # self.try_except(self.cur.execute("delete from StandardLife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "';"))
                            for Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name in zip(Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name):
                                print(Policy_Num,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency.replace(',',''),Allocation,Allocation_Fund_Name)
                                self.try_except(self.cur.execute("insert into Standardlife_Future_Investment_Contribution(Policy_Num,Spider_Date,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (Policy_Num,Spider_Date,self.date_to_num(Date),Investment_Account,Account_Type,Allocation_In_Policy_Currency.replace(',',''),Allocation,Allocation_Fund_Name)))

                        Fund_Name = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[1]//text()")
                        Reference_Code = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[2]//text()")
                        Currency = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[3]//text()")
                        Unit = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[4]//text()")
                        Price = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[6]//text()")
                        Weight = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[7]//text()")
                        Value_In_Fund_Currency = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[8]//text()")
                        Value_In_Policy_Currency = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[9]//text()")

                        print('Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency:',Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                        if not self.cur.execute("select * from Standardlife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date +  "';"):
                            # self.try_except(self.cur.execute("delete from StandardLife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date + "';"))
                            for Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency in zip(Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency):
                                print(Policy_Num,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                                self.try_except(self.cur.execute("insert into Standardlife_Account_Allocation(Policy_Num,Spider_Date,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (Policy_Num,Spider_Date,self.date_to_num(Date),Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit.replace(',',''),Price.replace(',',''),Weight,Value_In_Fund_Currency.replace(',',''),Value_In_Policy_Currency.replace(',',''))))

                # 点击交易日志
                daily_url = "https://www.standardlife.hk/login/" + standard_detail_response.xpath(
                    "//table[@id='pol_sum_menu_tableLink']//tr//td//a[2]/@href")[0][3:]
                standard_daily_response = ssion.get(url=daily_url, headers=standard_life_headers)
                # print(standard_daily_response.text) # <SCRIPT language='JavaScript'>function toFull(){self.location.href='policy/cust_pol_sum_main.aspx?module_id=MO12&sub_module_id=SUB1201&func_id=FN120101&lang=ch';}toFull();</SCRIPT><script language='JavaScript'>		window.close();</script>
                response = etree.HTML(standard_daily_response.text)
                Payment_date = response.xpath("//table[@id='tblPH']//tr/td[1]//text()")
                Premium_due_Date = response.xpath("//table[@id='tblPH']//tr/td[2]//text()")
                Payment_Method = response.xpath("//table[@id='tblPH']//tr/td[3]//text()")
                Policy_Currency = response.xpath("//table[@id='tblPH']//tr/td[4]//text()")
                Premium = response.xpath("//table[@id='tblPH']//tr/td[5]//text()")
                Status = response.xpath("//table[@id='tblPH']//tr/td[6]//text()")
                Remark = response.xpath("//table[@id='tblPH']//tr/td[7]//text()")
                print('Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark:',Payment_date, Premium_due_Date, Payment_Method, Policy_Currency, Premium, Status, Remark)
                for Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark in zip(Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark):
                    if not self.cur.execute("select * from Standardlife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + self.date_to_num(Payment_date) + "';"):
                        print(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
                        # self.try_except(self.cur.execute("delete from StandardLife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + Payment_date + "';"))
                        self.try_except(self.cur.execute("insert into Standardlife_Premium(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,self.date_to_num(Payment_date),self.date_to_num(Premium_due_Date),Payment_Method,Policy_Currency,Premium.replace(',',''),Status,Remark)))
                # 搞定其中一个保单号
                # driver.close()
                # driver.switch_to.window(driver.window_handles[0])
                self.mysql_client.commit()
                print('commited.')

                # self.cur.close()
                # 登出
                # logout
                ssion.get(url='https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&logoff=Y&lang=ch',
                          headers=standard_life_headers)
                print(username,Policy_Num,':Logout')
                self.successed += 1

            except Exception as e:
                print(str(Policy_Num) + str(self.riskType), e,'：error!调仓失败！')
                # 登出
                ssion.get(url='https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&logoff=Y&lang=ch',
                          headers=standard_life_headers)
                print(username, Policy_Num, ':Logout')
                # self.wait_until(driver=driver, platform='standard_life',selector_name="//li[@class='globalCustomerLogin']/a/img")
                # print(Policy_Num, ':Logout')
                # self.random_sleep(60,61)
                # continue
                # self.error = 1
                # driver.save_screenshot('调仓失败截图文件夹/standard_life/' + str(Policy_Num) + str(self.riskType) + ".png")
                # print(Policy_Num, '失败调仓截图中')
                # self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
                # if len(driver.window_handles) >= 2:
                #     driver.switch_to.window(driver.window_handles[1])
                #     driver.close()
                # driver.switch_to.window(driver.window_handles[0])
                # driver.quit()
            finally:
                self.random_sleep(3,5)
        self.cur.close()
        self.mysql_client.close()

    def date_to_num(self, date):
        month_num_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12','January': '01', 'February': '02', 'March': '03', 'April': '04', 'June': '06', 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}
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
                date_eng[0], date_eng[-1] = date_eng[-1], date_eng[0]
            date_number = '-'.join(date_eng)
            # print(date_number)
            return date_number
        except:
            return date

    def wait_until(self, driver, selector_name, platform='Hansard', selector_way='XPATH', action='click',
                   send_keys=None):
        """
            显式等待延迟 + 元素操作事件
        :param driver: 浏览器对象
        :param selector_name: 操作节点名称
        :param selector_way: 操作节点方式
        :param action: 操作节点的事件
        :param send_keys: 模拟键盘输入keys
        :return:
        """
        if self.error == 1:
            return
        selector = By.XPATH
        find_element = driver.find_element_by_xpath(selector_name)
        if selector_way == 'ID':
            selector = By.ID
            find_element = driver.find_element_by_id(selector_name)
        elif selector_way == 'CLASS_NAME':
            selector = By.CLASS_NAME
            find_element = driver.find_element_by_class_name(selector_name)
        elif selector_way == 'LINK_TEXT':
            selector = By.LINK_TEXT
            find_element = driver.find_element_by_link_text(selector_name)
        try:
            # 页面一直循环，直到 id="myDynamicElement" 出现
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((selector, selector_name)))
        except:
            self.error = 1
            print(driver.page_source)
            driver.save_screenshot('调仓失败截图文件夹/WAIT_UNTIL/' + str(self.policyNumber) + str(self.riskType) + ".png")
            if platform == 'Hansard':
                self.write_excel(policy_index=self.Hansard_index[self.enum_index], message='调仓失败')
            elif platform == 'ITA':
                self.write_excel(policy_index=self.ITA_index[self.enum_index], message='调仓失败')
            elif platform == 'zurich':
                self.write_excel(policy_index=self.zurich_index[self.enum_index], message='调仓失败')
            elif platform == 'standard_life':
                self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
            elif platform == 'axa':
                self.write_excel(policy_index=self.axa_index[self.enum_index], message='调仓失败')

            print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！', action + ':' + selector_name)
            # driver.close()
        else:
            if action == 'click':
                find_element.click()
            elif action == 'clear':
                find_element.clear()
            elif action == 'send_keys':
                find_element.send_keys(str(send_keys))
            elif action == 'text':
                return find_element.text
        finally:

            self.random_sleep()

    def random_sleep(self, least=1, most=2):
        """
        随机休眠一段时间
        :return: No
        """
        time.sleep(random.randint(least, most))

    def read_excel(self):
        """
        读取excel里的数据
        :return: data_list
        """
        index = 0
        excel = pandas.read_excel(self.excel_name)
        # print(excel)
        value = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
        # 数据列表
        data_list = []
        Hansard = []
        ITA = []
        zurich = []
        standard_life = []
        axa = []
        # print(excel['保单号'], excel['Platform'], excel['风险属性'], excel['调仓情况'], excel['用户名'], excel['密码'], excel['PIN码'])
        try:
            # 正常调仓
            # for policyNumber, sellingPercent, riskType, operationSituation, userName, passWord, PIN in zip(excel['保单号'],excel['卖出比例'],excel['风险属性'],excel['调仓情况'],excel['用户名'],excel['密码'],excel['PIN码']):
            # login_test
            # for policyNumber, platform, riskType, operationSituation, userName, passWord, PIN in zip(excel['保单号'],excel['Platform'],excel['风险属性'],excel['调仓情况'],excel['用户名'],excel['密码'],excel['PIN码']):
                # if str(policyNumber).startswith("5") and value.match(
                #         str(sellingPercent)) and operationSituation != '调仓成功':
                #     Hansard.append((policyNumber, sellingPercent, riskType))
                #     self.Hansard_index.append(index)
                # elif str(policyNumber).startswith("T") and value.match(
                #         str(sellingPercent)) and operationSituation != '调仓成功':
                #     ITA.append((policyNumber, sellingPercent, riskType))
                #     self.ITA_index.append(index)
                # elif str(policyNumber).startswith("8") and value.match(str(sellingPercent)) and operationSituation != '调仓成功':
                #     zurich.append((policyNumber, sellingPercent, riskType, userName, passWord, str(int(PIN))))
                # login_test
                if (platform == 'Zurich' or platform == 'Zurich new' or platform == 'zurich'):
                    zurich.append((policyNumber,  riskType, userName, passWord,PIN))
                    self.zurich_index.append(index)
                index += 1
        except:
            # for policyNumber, riskType, operationSituation, userName, passWord in zip(excel['保单号'], excel['风险属性'],excel['调仓情况'], excel['用户名'],excel['密码']):
            for policyNumber, platform, riskType, operationSituation, userName, passWord in zip(excel['保单号'],excel['Platform'], excel['风险属性'],excel['调仓情况'], excel['用户名'],excel['密码']):
                # if '-' not in str(policyNumber) and operationSituation != '调仓成功':
                if '-' not in str(policyNumber) and operationSituation == '登录成功' and platform == 'Standard':
                    standard_life.append((policyNumber, riskType, userName, passWord))
                    self.standard_life_index.append(index)
                # elif str(policyNumber).startswith("5") and '-' in str(policyNumber) and operationSituation != '调仓成功':
                elif str(policyNumber).startswith("5") and '-' in str(policyNumber):
                    axa.append((policyNumber, riskType, userName, passWord))
                    self.axa_index.append(index)
                index += 1

        print('Hansard_dataList：',Hansard)
        print('ITA_dataList：',ITA)
        print('zurich_dataList：',zurich)
        print('standard_life_dataList：',standard_life)
        print('axa_dataList：',axa)
        data_list.append(Hansard)
        data_list.append(ITA)
        data_list.append(zurich)
        data_list.append(standard_life)
        data_list.append(axa)
        # 需要调仓数
        self.counts = len(Hansard) + len(ITA) + len(zurich) + len(standard_life) + len(axa)
        print('\n需要调仓的保单个数为：%s' % self.counts)
        return data_list

    def write_excel(self, policy_index, policy_col=4,message='调仓成功'):
        """
        写入调仓情况信息
        :param message:
        :return: No
        """
        policy_row = policy_index + 1
        excel_name = self.excel_name
        excel_content = open_workbook(excel_name, formatting_info=False)
        new_xls_file = copy(excel_content)
        sheet = new_xls_file.get_sheet(0)
        sheet.write(policy_row, policy_col, message)
        os.remove(excel_name)
        new_xls_file.save(excel_name)

    def check_workoff(self, off_time=2300):
        """
        定时停止程序：到了18:30分，完成当前手头上的调仓任务后便停止调仓操作。
        :param off_time:
        :return: No
        """
        # if int(time.strftime("%H%M")) >= off_time:
        #     # while order_time>0:
        #     #     time.sleep(1)
        #     #     order = input('够钟落班收工，如需加班请输入SaKura靓仔('+str(order_time)+'):')
        #     #     if order == 'SaKura靓仔':
        #     #         return
        #     print('好，够钟收工！正在发送战绩邮件....', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        #           '\n今日战绩：调仓成功 %s个/失败%s个。' % (self.successed, (self.operation_counts - self.successed)))
        #     # 发送邮件给资管部人员
        #     self.send_email()
        #     # 停止程序
        #     sys.exit(0)

    def send_email(self):
        """
        下班时发送邮件到资管部人员.
        :return: No
        """
        # 不带SSL安全套层
        from_addr = 'sakurapan@trussan.com'  # input('From: ')
        password = 'Cbc_123'  # input('Password: ')
        to_addr = [
            'sakurapan@trussan.com', 'yuwinliang@trussan.com', 'sarahguo@trussan.com', 'zainxue@trussan.com',
            '544538297@qq.com', 'iqpmw@126.com']  # input('To: ')
        # to_addr = ['sakurapan@trussan.com', '544538297@qq.com']  # input('To: ')
        smtp_server = 'smtp.exmail.qq.com'  # input('SMTP server: ')
        server = smtplib.SMTP(smtp_server, 25)

        # SMTP服务器：smtp.exmail.qq.com(使用SSL，端口号465)
        # smtp_server = 'smtp.exmail.qq.com'
        # smtp_port = 465
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.connect(smtp_server, smtp_port)
        # server.starttls()

        # 邮件对象:
        msg = MIMEMultipart()
        # msg = MIMEText('hello，收到请回复~', 'plain', 'utf-8')
        msg['From'] = self._format_addr('SaKura_AutoEmail<%s>' % from_addr)
        msg['To'] = self._format_addr('资管部人员<%s>' % to_addr)
        msg['Subject'] = Header('Trussan自动调仓情况反馈', 'utf-8').encode()

        # 邮件正文是MIMEText:
        msg.attach(MIMEText(
            '今日调仓情况：今日战绩：调仓成功 %s个 / 失败 %s个。（附件为调仓总表）' % (self.successed, (self.operation_counts - self.successed)),
            'plain', 'utf-8'))

        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(self.excel_name, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('excel', 'xls',
                            filename='ClientSwitch ' + time.strftime('%Y%m%d', time.localtime(
                                time.time())) + ' adjustment_situation.xls', )
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename='ClientSwitch ' + time.strftime('%Y%m%d',
                                                                                                          time.localtime(
                                                                                                              time.time())) + ' adjustment_situation.xls')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)

        # 查看网络交互信息
        server.set_debuglevel(1)
        # 登录账户
        server.login(from_addr, password)
        # 发送邮件
        server.sendmail(from_addr, to_addr, msg.as_string())
        # 退出
        server.quit()

    def try_except(self,sth):

        # 使用cursor()方法获取操作游标
        # self.cur = self.mysql_client.cursor()
        print('inserting data to mysql ...')
        try:
            sth
        except pymysql.Error as e:
            with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
                print('Writing Error info...',e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'：'+str(e) + '\r\n')
            f.close()
        # finally:
        #     self.cur.close()
            # self.mysql_client.commit()
            # return sth

    def start_work(self):
        """
        开始任务调度
        :return: opearting
        """
        # 1.读取Excel表格数据
        data = self.read_excel()
        # 2.进行自动调仓操作
        print('\n正在进行standard_life_spider调仓操作....')
        self.standard_life_spider(data[3])
        # print('\n正在进行zurich_spider调仓操作....')
        # self.zurich_spider(data[2])
        # print('\n正在进行axa_spider调仓操作....')
        # self.axa_spider(data[4])

        print('\r\n调仓完毕！其中调仓成功 %s个/总数%s个。' % (self.successed, self.counts))
        # self.send_email()


if __name__ == '__main__':
    auto_operation = AutoOperation()
    auto_operation.start_work()

