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

    def date_to_num(self,date):
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
                date_eng[0], date_eng[-1] = date_eng[-1], date_eng[0]
            date_number = '-'.join(date_eng)
            # print(date_number)
            return date_number
        except:
            return date

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

    def zurich_spider(self,zurich):
        """
                zurich调仓操作
                :param zurich: zurich data list
                :return: operating
                """
        # zurich = [(9861620, "nan", 'codysunmz', 'Ilovele$shi', 110947), (9860437, "nan", 'Zhuwenfang75', 'Zhuwenf0916', 1975), (8110328, "nan", 'Ljfeng11', 'Lejianf11', 1977), (9865684, "nan", 'Zhyong72', 'Zhangyong37', 1772), (9965607, "nan", 'codysunmz', 'Ilovele$shi', 110947), (8165955, "nan", 'Zhangli83', 'ZHLi1228', 1983), (8105512, "nan", 'Guoying0802', 'YingG0802', 1978), (9918958, "nan", 'kembleouyang', 'TianHao605', 1970060711), (9843770, "nan", 'Xiaoyantu', 'Melman228', 1993), (9865808, "nan", 'Liukejia1203', 'Liukejia0312', 1979), (9954377, "nan", 'Yingsun817', 'Sunying0718', 1078), (9966107, "nan", 'luofuflu8393', 'Zurich2010', 20100101), (8219179, "nan", 'lilijoe', 'Lili1211', 1211), (8222881, "nan", 'Tangdd0711', 'Tangdd1985', 1985), (8234561, "nan", 'liaxiaol9217', 'Jessie1023', 315217), (8243560, "nan", 'Wenpeihan0322', 'Wenpeihanha7803', '1830'), (8239800, "nan", 'Gaoyinlu7120', 'Gaoylu91702', 9712), (8258290, "nan", 'liubingl4475', 'Bingxin1963', 1363229179), (8261860, "nan", 'chenciqi3739', 'JKF12dyi', 86419042), (8275346, "nan", 'luo"nan"lu3102', 'Luo"nan"1214', 20041214), (8271953, "nan", 'hongliho1716', 'Hong23456', 123456), (8282865, "nan", 'kohonkoh5489', 'qweR1tyu', '001229'), (8286030, "nan", 'hanlecheng', '790097Hanlecheng', 7911), (8292356, "nan", 'linxiaol2780', 'Xiao23456', '031750'), (8294308, "nan", 'Fujun1218', 'FUjun9728', 1297), (8293940, "nan", 'Emei7811', 'Emei1978', 7811), (8297774, "nan", 'jingxinj8428', 'Jxin0810', '8010'), (8303439, "nan", 'denliden4327', 'SOHUcat368', 5549), (8303498, "nan", 'wangniwa6019', 'Wang1357', 19800110), (8309170, "nan", 'jenniferlu09', 'Climate0', 1975), (1603078, "nan", '05376142', 'XLM12345', '/'), (8335446, "nan", 'huashuih7675', 'Hsf198023Lhr', '5728632'), (8335128, "nan", 'Chuyjun2017', 'CHyinjun0127', 8217), (8337155, "nan", 'chenhuic2815', 'Huihua1973', '19730205'), (8337253, "nan", 'Pengxuan81', 'Pengx0709', 8179), (8328415, "nan", 'liuganli4250', 'Gang23456', 910516), (8352316, "nan", 'gaoweing6282', 'Vincent_tsh0017', 19830224), (8374085, "nan", 'liyiliyi2912', 'Hm1slv??', 26549215), (8377093, "nan", 'Tangzd6926', 'Tangzd0326', 9026), (8374932, "nan", 'Panhj7602', 'Panjuan0203', 7603), (8399878, "nan", 'kouhongk8073', 'Wangziming0322', 34474460), (8103619, "nan", 'penxiaop1994', 'Pengxiaor1976', 1976120188), (8104675, "nan", 'luoqinlu1078', 'LuoQinn03081', '080319'), (8380247, "nan", 'Hulijuan8116', 'Hulj8112', 8126), (8380353, "nan", 'luoyuanl0687', 'Yuan2345', 246321), (8103662, "nan", 'wuxiaowu5737', 'Xiao2345', 123456), (8103767, "nan", 'heshahes5446', 'Shan23456', 123456), (8178597, "nan", 'Liqian8023', 'Liqian9083', 1923), (8178228, "nan", 'weibinwe2308', 'Benfair_780531', '0417042807'), (8178236, "nan", 'Qjing8236', 'Qiujing8236', 8236), (8198369, "nan", 'cheyuxic7950', 'Yu234567', 123456), (8198475, "nan", 'Pangqping91', 'Pqiuping9401', 1418), (8207784, "nan", 'Hewei1130', 'Hewei11930', 1037), (8209884, "nan", 5001, '$florid413522', 201404), (8222227, "nan", 'renweire1365', 'RRww76110220', 78761420), (8219366, "nan", 'cheleich1774', 'Chen34567', '456789'), (8218009, "nan", 'wangkui', 'x49-kfY-BMH-ccn', 8218), (8222278, "nan", 'lixialix0920', 'Eva19810412', 19810412), (8227326, "nan", 'zhangning0512', 'Zhangni1850', 9015), (8231528, "nan", 'songjins5377', 'Tufe9705', 213213), (8224174, "nan", 'yangjian2699', 'YjianLiuj123', 19830626), (8224998, "nan", 'GaoYan8128', 'Huahua790228', 1981), (8225595, "nan", 'wanjiawa7305', 'WJY1973sz', 197312), (8222219, "nan", 'wangjiny3201', 'Jinyan2014', 123456), (8225083, "nan", 'liuguali4909', 'A1B2C3d4f5g6', 123456), (8227955, "nan", 4683, 'Dong23456', 19760821), (8231765, "nan", 'chezhuch6663', 'Xiao23456', 19740511), (8243022, "nan", 'niuconni5943', 'Niucongying1983', 19830313), (8242954, "nan", 'annaxyz', '1981-annaxyz', '0509'), (8243488, "nan", 'yujianyu3797', 'Jian23456', 8103), (8244124, "nan", 'Sunyhua2414', 'Syanhua0519', 8195), (8244115, "nan", 'zhaoxiao9794', 'Xiao23456', 19830328), (8244673, "nan", 'fanjiwfa2659', '13581910367YFzxf', 19811217), (8247157, "nan", 'Jinxin1979', 'JinXin0201', 1979), (8247425, "nan", 'oucanwou6569', 'Vids1516', 124124), (8247395, "nan", 'Guchqing0022', 'GUchangq0280', 1982), (8250345, "nan", 'Yuyan1217', 'YUyan1127', 9172), (8224192, "nan", 'liujingl3335', 'YjianLiuj123', 20051983), (8227946, "nan", 'Hua8227946', 'Shuang234', 1234), (8245554, "nan", 'wulinwul3390', 'Wuling1983', 19830908), (8219358, "nan", 'Liulihua17', 'Liulh8107', 9170), (8191615, "nan", 'Luotielu0141', 'Luotie0848', 246321), (8254146, "nan", 'Mgfang9011', 'Mg840911', 9011), (8278390, "nan", 'Xjnhua65', 'Xjianh56', 1983), (8282328, "nan", 'Wangyan', 'Wyan6605', 6605), (8292766, "nan", 'Tgrong1122', 'Tangr8312', 1812), (8292814, "nan", 'Chyang0781', 'Cheny0781', '0781'), (8324519, "nan", 'vaneyq', 'vaneyq198362V', 8362), (8363282, "nan", 'TongL1126', 'TLing8111', '1981'), (8363274, "nan", 'sunxiaosu', 'Sun19800720', '0720'), (8367490, "nan", 'Feiqm633', 'Fqmei751011', 1011), (8374551, "nan", 'Qwjuan51', 'Qiwj1018', 8710), (8380330, "nan", 'yver0929', 'Zhang0929yv', 929), (8383885, "nan", 'Zhna3885', 'Zhna1133', 8383), (8389395, "nan", 'Qhui8412', 'QiaoH1212', 8412), (8109581, "nan", 'Kaiyuan911202', 'Fnkayuan91', 9112), (8392086, "nan", 'Lixing', 'Lx123456', 1234), (8107295, "nan", 'Wagj7295', 'Wjin1102', 1102), (8108380, "nan", 'iloveamyfish', 'Jy00074827', 1314), (8109050, "nan", 'Gmb1972', 'Bomg1972', '0625'), (8115058, "nan", 'Qianc0507', 'Qcun1010', 8910), (8115067, "nan", 'Xdhu0125', 'Xiad5067', 1984), (8118236, "nan", 'Lyishan1987', 'Lyshan0303', 8703), (8118227, "nan", 'ZJLiang8227', 'ZhuoJL8207', '0709'), (8118254, "nan", 'Yyin1985', 'Ygyin8254', 8118), (8127024, "nan", 'linxiqian', '3354Him~', 1219), (8128241, "nan", 'Yexining', 'Zxn5201031', 1031), (8137151, "nan", 'Dengy1988', 'Dying1225', 8812), (8144050, "nan", 'jlp2016', 'u96f5JreqdQR', '0318'), (8148935, "nan", 'Jinh1889', 'Jhua1889', 1889), (8155982, "nan", 'Heri1808', 'Heru0216', '0216'), (8161777, "nan", 'Wenxj8989', 'WXjing2489', 3062), (8161974, "nan", 'laurieli2016', 'Password1', 1102), (8272304, "nan", 'Xiangli0322', 'Lixiang81', 1981), (8273478, "nan", 'Zhjr3478', 'Zjunr0918', 1980), (8275953, "nan", 'Chjmin83', 'Jiaminch38', 8381), (8286173, "nan", 'leizmax714', 'Zhlei0714', 1980), (8295304, "nan", 'TheaWang', 'ELaine0411', '0302'), (8295277, "nan", 'Xiuzhi', 'Iamzxz5613996', '0401'), (8299019, "nan", 'Shenchm0233', 'Shench0233miao', 1923), (8299868, "nan", 'BaiL0617', 'Lubai1706', 1986), (8300095, "nan", 'Zhcht502', 'Taocz0502', 1979), (8307178, "nan", 'zhouhao1985', 'Zhouhhuohz85', 8519), (8307812, "nan", 'Shenzh418', 'ZHsh0418', 1982), (8307855, "nan", 'Xuxm0725', 'XMxu0725', 1980), (8307828, "nan", 'LinQZ0702', 'Qiongzhu0207', 1992), (8319322, "nan", 'Cuij0512', 'Jingcui1279', 1979), (8319314, "nan", 'skyofhistory', '841024Free', 8996), (8326264, "nan", 'supertwh', 'Supertwh830928', '0928'), (8335131, "nan", 'Shixuefgzg3001', 'Shiguan8119', 1981), (8333357, "nan", 'Wang8765zheng', 'Wz139576ngeng', 3578), (8333366, "nan", 'Liangwq0822', 'Liangwq2208', 1981), (8332989, "nan", 'Zhaox1011', 'Zhao1979x', 1011), (8333039, "nan", 'lixixi0818', 'Azdlxx818', 527), (8339097, "nan", 'Huyap1014', 'Yaphu1410', 1982), (8347792, "nan", 'cheryze16', '0810zaqPP#.', '0813'), (8347784, "nan", 'zenosbaba', '0810zaqPP#', 813), (8348381, "nan", 'Yanli_Wang', 'Ad185wylzyn', '0215'), (8349637, "nan", 'wang_1983', 'Reuters2345', 8565), (8351994, "nan", 'hufenhuf0207', 'Fenhu2823', 2383), (8354241, "nan", 'hongmanlin', 'Hml258456', 2589), (8383517, "nan", 'dai451723844', '1800470036Dqy', 1993), (8399970, "nan", 'Motionway0812', 'Xinweimo0812', 7412), (8106328, "nan", 'Wang0702y', 'W0702yun', 1982), (8100666, "nan", 'Hgyxing119', 'Xgyaoh9137', 1973), (8106311, "nan", 'zhahailz1879', 'Lanhz914', 909471905), (8113758, "nan", 'Cheny1219x', 'Cy1912xiang', 1975), (8118786, "nan", 'Xiaoy1007', 'Xiao0710y', 1982), (8119766, "nan", 'Sandra88', 'YANGyang0724', 6202), (8121807, "nan", 'Zhoux18', 'Zhoux1118uan', 1982), (8124565, "nan", 'LIYANFEN', '239435feN', 3367), (8124581, "nan", 'Xiangy85', 'Xiang0908y', 1985), (8124547, "nan", 'zengqi19841226', 'cjlnFDS19841226', 3398), (8124735, "nan", ' jennyxk1975', 'Jenny_xk1975', '0618'), (8129502, "nan", 'Liu0807yy', 'Liuy0708yuan', 1972), (8288507, "nan", 'Wxiaog78', 'Wxgeng0112', 1978), (8336686, "nan", 'Liuyy0508', 'Yangyliu0508', 1984)]
        # zurich = [(8228098, "nan", 'Hxiaoting1213', 'Huangxt0526', 1213),(8283004 , "nan", 'yezhijye1190', 'Pang761019', 30114)]
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # driver = webdriver.Chrome(chrome_options=chrome_options)

        # PhamjomJs
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 1000
        cap["phantomjs.page.settings.loadImages"] = True
        cap["phantomjs.page.settings.disk-cache"] = True
        cap[
            "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        cap[
            "phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        driver = webdriver.PhantomJS(desired_capabilities=cap)

        for index, item in enumerate(zurich):
            self.cur = self.mysql_client.cursor()
            try:
                self.operation_counts += 1
                self.enum_index = index# 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                self.random_sleep()
                username = str(item[2]) # codysunmz
                password = str(item[3]) # Ilovele$shi
                # print('PIN:',str(item[4]))
                # 普通爬虫方式
                # zurich_login_url = 'https://online.zurichinternationalsolutions.com/login.aspx?ReturnUrl=%2fZIO%2fMyPolicies.mvc'
                # zurich_headers = {
                #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                #     "Accept-Encoding": "gzip, deflate, br",
                #     "Accept-Language": "zh-CN,zh;q=0.9",
                #     "Cache-Control": "max-age=0",
                #     "Connection": "keep-alive",
                #     "Content-Length": "2108",
                #     "Content-Type": "application/x-www-form-urlencoded",
                #     # "Cookie":"ASP.NET_SessionId=qzrmgc45czzb5h55tuclvt45; visid_incap_437653=cE9OR25GTS6Qmm1byrRsbYDDOFoAAAAAQUIPAAAAAABC7IzC4DotQBmwEh1HJ3t/; incap_ses_434_437653=8a0VW2bVCWec94AqB+EFBqaLl1oAAAAAgjqOT+B3hJMnZ0Vkre2giw==; RememberMe=Wang8765zheng",
                #     "Host": "online.zurichinternationalsolutions.com",
                #     "Origin": "https://online.zurichinternationalsolutions.com",
                #     "Referer": "https://online.zurichinternationalsolutions.com/login.aspx?ReturnUrl=%2fZIO%2fMyPolicies.mvc",
                #     "Upgrade-Insecure-Requests": "1",
                #     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                # }
                # zurich_data_login = {
                #     # "__LASTFOCUS": "",
                #     "ctl00_ToolkitScriptManager1_HiddenField": ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-GB:2a06c7e2-728e-4b15-83d6-9b269fb7261e:de1feab2:f2c8e708:720a52bf:f9cec9bc:7311d143",
                #     # "__EVENTTARGET": "",
                #     # "__EVENTARGUMENT": "",
                #     # "__VIEWSTATE": "/wEPDwUKMTI5NDk5NjQzNw8WAh4JUmV0dXJuVXJsBRMvWklPL015UG9saWNpZXMubXZjFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWBGYPZBYSAgEPDxYCHgRUZXh0BSRMb2dpbiB0byBadXJpY2ggSW50ZXJuYXRpb25hbCBvbmxpbmVkZAIHDw8WAh4MRXJyb3JNZXNzYWdlBR5Vc2VybmFtZSBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAILDw8WAh8CBR5QYXNzd29yZCBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAINDxAPFgIfAQUUUmVtZW1iZXIgbXkgVXNlcm5hbWVkZGRkAg8PDxYCHwEFCENvbnRpbnVlZGQCEQ8PFgIfAQU1PGEgaHJlZj0iL0xvc3RDcmVkZW50aWFscy9Vc2VyTmFtZS5hc3B4Ij51c2VybmFtZTwvYT5kZAITDw8WAh8BBTU8YSBocmVmPSIvTG9zdENyZWRlbnRpYWxzL1Bhc3N3b3JkLmFzcHgiPnBhc3N3b3JkPC9hPmRkAhUPDxYCHwEFmwFJIGZvcmdvdCBib3RoLiBJZiB5b3UgaGF2ZSBmb3Jnb3R0ZW4gbW9yZSB0aGFuIG9uZSBvZiB5b3VyIGxvZ2luIGRldGFpbHMsIHBsZWFzZSA8YSBocmVmPSIvSW5mb3JtYXRpb24vQ29udGFjdERldGFpbHMuYXNweCIgdGFyZ2V0PSJfYmxhbmsiPmNvbnRhY3QgdXM8L2E+LmRkAhcPZBYCAgEPZBYCZg8PFgQeCENzc0NsYXNzBRBhY2NvcmRpb24taGVhZGVyHgRfIVNCAgJkZAIBD2QWAgIBD2QWAmYPZBYCZg9kFgYCBQ9kFgYCCQ8QZGQWAGQCDw8QZGQWAGQCFQ8QZGQWAGQCBw8WAh4OUG9zdEJhY2tTY3JpcHQFQ19fZG9Qb3N0QmFjaygnY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSR1Y1BpblZhbGlkYXRvciRidG5RdWl0JywnJylkAgsPFgIfBQVMX19kb1Bvc3RCYWNrKCdjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHVjUGluVmFsaWRhdG9yJGJ0blJhbmRvbVBpblF1aXQnLCcnKWQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFJmN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkY2JSZW1lbWJlck1lBSRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJE11bHRpVmlldzEPD2RmZD0Dvsc87o3jOZ3ZPZVuZpVJ3Hfo",
                #     # "__VIEWSTATEGENERATOR": "C2EE9ABB",
                #     # "__SCROLLPOSITIONX": "0",
                #     # "__SCROLLPOSITIONY": "276",
                #     # "__EVENTVALIDATION": "/wEWBgLmnay0DQLJ4fq4BwL90KKTCAKipK3+BAKtnJ6XBQLrspm9A1uSQcy1zRVB9AVdXeBqyISrY6YA",
                #     "ctl00$ContentPlaceHolder1$txtUserName": username,
                #     "ctl00$ContentPlaceHolder1$txtPassword": password,
                #     "ctl00$ContentPlaceHolder1$cbRememberMe": "on",
                #     "ctl00$ContentPlaceHolder1$cmdLogin": "Continue",
                #     "ctl00$ContentPlaceHolder1$MyAccordion_AccordionExtender_ClientState": "-1",
                # }
                # zurich_data_pin = {
                #     "ctl00$ToolkitScriptManager1":"ctl00$ContentPlaceHolder1$ucPinValidator$UpdatePanel1 | ctl00$ContentPlaceHolder1$ucPinValidator$btnRandomPinContinue",
                #     "__LASTFOCUS":"",
                #     "ctl00_ToolkitScriptManager1_HiddenField":";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-GB:2a06c7e2-728e-4b15-83d6-9b269fb7261e:f9cec9bc:da1bcd61:de1feab2:f2c8e708:8613aea7:3202a5a2:a67c2700:720a52bf:589eaa30:ab09e3fe:87104b7c:be6fb298",
                #     "__EVENTTARGET":"",
                #     "__EVENTARGUMENT":"",
                #     "__VIEWSTATE":"/wEPDwUKMTI5NDk5NjQzNw9kFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWBGYPZBYUAgEPDxYCHgRUZXh0BSRMb2dpbiB0byBadXJpY2ggSW50ZXJuYXRpb25hbCBvbmxpbmVkZAIFDw8WAh8ABQljb2R5c3VubXpkZAIHDw8WAh4MRXJyb3JNZXNzYWdlBR5Vc2VybmFtZSBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAILDw8WAh8BBR5QYXNzd29yZCBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAINDxAPFgQfAAUUUmVtZW1iZXIgbXkgVXNlcm5hbWUeB0NoZWNrZWRnZGRkZAIPDw8WAh8ABQhDb250aW51ZWRkAhEPDxYCHwAFNTxhIGhyZWY9Ii9Mb3N0Q3JlZGVudGlhbHMvVXNlck5hbWUuYXNweCI+dXNlcm5hbWU8L2E+ZGQCEw8PFgIfAAU1PGEgaHJlZj0iL0xvc3RDcmVkZW50aWFscy9QYXNzd29yZC5hc3B4Ij5wYXNzd29yZDwvYT5kZAIVDw8WAh8ABZsBSSBmb3Jnb3QgYm90aC4gSWYgeW91IGhhdmUgZm9yZ290dGVuIG1vcmUgdGhhbiBvbmUgb2YgeW91ciBsb2dpbiBkZXRhaWxzLCBwbGVhc2UgPGEgaHJlZj0iL0luZm9ybWF0aW9uL0NvbnRhY3REZXRhaWxzLmFzcHgiIHRhcmdldD0iX2JsYW5rIj5jb250YWN0IHVzPC9hPi5kZAIXD2QWBGYPZBYCZg8WAh4FVmFsdWUFAi0xZAIBD2QWAmYPDxYEHghDc3NDbGFzcwUQYWNjb3JkaW9uLWhlYWRlch4EXyFTQgICZGQCAQ9kFgICAQ8PFgIeDlNlbGVjdGlvbkFycmF5FCsBAwIBAgMCBWQWAmYPZBYCZg9kFgwCAQ8PFgIeB1Zpc2libGVnZBYQAgMPFgIeBWNsYXNzBQ1zdGVwLTEtY2lyY2xlZAIFDxYCHwgFDXN0ZXAtMi1jaXJjbGVkAgcPDxYCHwAFJExvZ2luIHRvIFp1cmljaCBJbnRlcm5hdGlvbmFsIG9ubGluZWRkAgkPDxYCHwAFYUVudGVyIHRoZSAxPHN1cD5zdDwvc3VwPiwgMzxzdXA+cmQ8L3N1cD4gYW5kIDU8c3VwPnRoPC9zdXA+IGRpZ2l0cyBvZiB5b3VyIE1lbW9yYWJsZSBudW1iZXIgKFBJTilkZAILDw8WAh4KSGVhZGVyVGV4dAUmTWVtb3JhYmxlIG51bWJlciBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAIPD2QWDAIBDw8WBh4IUmVhZE9ubHloHgRNb2RlCyolU3lzdGVtLldlYi5VSS5XZWJDb250cm9scy5UZXh0Qm94TW9kZQIfB2dkZAIEDw8WBh8ABQEqHghUYWJJbmRleAH//x8HZ2RkAgcPDxYGHwpoHwsLKwQCHwdnZGQCCg8PFgYfAAUBKh8MAf//HwdnZGQCDQ8PFgYfCmgfCwsrBAIfB2dkZAIQDw8WBh8ABQEqHwwB//8fB2dkZAIRDw8WAh8ABQVMb2dpbmRkAhMPDxYCHwAFSjxhIGhyZWY9Ii9Mb3N0Q3JlZGVudGlhbHMvTWVtb3JhYmxlTnVtYmVyLmFzcHgiPkVtYWlsIG1lIGEgcmVzZXQgbGluay48L2E+ZGQCAw9kFg4CAQ8WAh8IBQ1zdGVwLTEtY2lyY2xlZAIDDxYCHwgFDXN0ZXAtMi1jaXJjbGVkAgUPDxYCHwAFFFNldCBNZW1vcmFibGUgbnVtYmVyZGQCDQ8PFgIfAQUsPGJyIC8+TWVtb3JhYmxlIG51bWJlciBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAITDw8WAh8BBTQ8YnIgLz5Db25maXJtIG1lbW9yYWJsZSBudW1iZXIgY2Fubm90IGJlIGxlZnQgYmxhbmsuZGQCFQ8PFgIfAQU0VGhlIE1lbW9yYWJsZSBudW1iZXJzIHlvdSBoYXZlIGVudGVyZWQgZG8gbm90IG1hdGNoLmRkAhsPDxYCHwAFlgFJZiB5b3Ugd291bGQgbGlrZSBhbnkgZnVydGhlciBpbmZvcm1hdGlvbiBvciBpZiB5b3UgbmVlZCBhc3Npc3RhbmNlLCBwbGVhc2UgPGEgaHJlZj0iL0luZm9ybWF0aW9uL0NvbnRhY3REZXRhaWxzLmFzcHgiIHRhcmdldD0iX2JsYW5rIj5jb250YWN0IHVzPC9hPi5kZAIFD2QWDgIBDw8WAh8ABT9QbGVhc2Ugc2VsZWN0IHRoZSBmb2xsb3dpbmcgbnVtYmVycyBmcm9tIHlvdXIgTWVtb3JhYmxlIG51bWJlci5kZAIDDw8WAh8JBRtQbGVhc2UgY29tcGxldGUgYWxsIGZpZWxkcy5kZAIJDxBkZBYAZAIPDxBkZBYAZAIVDxBkZBYAZAIXDw8WAh8ABQRRdWl0ZGQCGQ8PFgIfAAWWAUlmIHlvdSB3b3VsZCBsaWtlIGFueSBmdXJ0aGVyIGluZm9ybWF0aW9uIG9yIGlmIHlvdSBuZWVkIGFzc2lzdGFuY2UsIHBsZWFzZSA8YSBocmVmPSIvSW5mb3JtYXRpb24vQ29udGFjdERldGFpbHMuYXNweCIgdGFyZ2V0PSJfYmxhbmsiPmNvbnRhY3QgdXM8L2E+LmRkAgcPFgIeDlBvc3RCYWNrU2NyaXB0BUNfX2RvUG9zdEJhY2soJ2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkdWNQaW5WYWxpZGF0b3IkYnRuUXVpdCcsJycpZAILDxYCHw0FTF9fZG9Qb3N0QmFjaygnY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSR1Y1BpblZhbGlkYXRvciRidG5SYW5kb21QaW5RdWl0JywnJylkAg8PFgIfAAUeQXJlIHlvdSBzdXJlIHlvdSB3YW50IHRvIHF1aXQ/ZBgBBSRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJE11bHRpVmlldzEPD2QCAWSSGXyP8B4CdQyUN40kJsfdbMKNSw==",
                #     "__VIEWSTATEGENERATOR":"C2EE9ABB",
                #     "__SCROLLPOSITIONX":"0",
                #     "__SCROLLPOSITIONY":"129",
                #     "__EVENTVALIDATION":"/wEWCgLH95L/AwLq3vHlAgLq3q33DALq3pmcBALq3tWtDgLq3sHSBQLq3v3jDwKe9sGqAgLmp7nAAgKuzMWCC67dXydGn6z12OT+6I1cPlnibyuz",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin1":"1",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin2":"1",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin3":"0",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin4":"9",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin5":"4",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$TextBoxPin6":"7",
                #     "__ASYNCPOST":"true",
                #     "ctl00$ContentPlaceHolder1$ucPinValidator$btnRandomPinContinue":"Login"
                # }
                # # response = requests.post(url=zurich_login_url, headers=zurich_headers, data=zurich_data).text
                # ssion = requests.session()
                # ssion.post(url=zurich_login_url, headers=zurich_headers, data=zurich_data_login)
                # response0 = ssion.post(url='https://online.zurichinternationalsolutions.com/Login.aspx',headers=zurich_headers, data=zurich_data_pin)
                # response1 = ssion.get(url='https://online.zurichinternationalsolutions.com/default.aspx',headers=zurich_headers)
                # # response2 = ssion.
                # print('response0',response0.text)
                # print('response1',response1.text)
                # break

                # 模拟点击登录
                url = "https://online.zurichinternationalsolutions.com/Login.aspx"
                username_id = "ctl00_ContentPlaceHolder1_txtUserName"
                password_id = "ctl00_ContentPlaceHolder1_txtPassword"
                submit_id = "ctl00_ContentPlaceHolder1_cmdLogin"
                # 登录
                # self.browser_login(url, username, password, username_id, password_id, submit_id)
                driver.delete_all_cookies()
                driver.get(url)
                self.random_sleep()
                driver.find_element_by_id(username_id).send_keys(username)
                self.random_sleep()
                driver.find_element_by_id(password_id).send_keys(password)
                self.random_sleep()
                driver.find_element_by_id(submit_id).click()
                self.random_sleep()
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()
                # 判断PIN码的个数（因读excel时会忽略第一个数字0）
                response = etree.HTML(driver.page_source)
                PINCount = len(response.xpath("//tr/td[@class='PintextBox']//input"))
                print('PIN的位数为：', str(PINCount))
                PIN = str(item[4]) if len(str(item[4])) == len(str(PINCount)) else '0' * (PINCount - len(str(item[4]))) + str(item[4])
                # print(PINCount-1)
                # print(len(str(item[5])))
                print(self.policyNumber,'的PIN码为：', PIN)
                # 正在输入PIN码补充位
                # print(driver.page_source)
                for index, item in enumerate(str(PIN)):
                    if not driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").get_attribute("value"):
                        driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").send_keys(item)
                    self.random_sleep()
                # 点击登录
                self.wait_until(driver=driver, platform='zurich',selector_name="//input[@id='ctl00_ContentPlaceHolder1_ucPinValidator_btnRandomPinContinue']")
                self.random_sleep()
                # 输入PIN码后，部分账户会出现更改密码的提示
                try:
                    # 勾选
                    self.random_sleep(10, 12)
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_cbConfirmIgnore']").click()
                    # 点击continue
                    self.random_sleep()
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_btnConfirmIgnore']").click()
                except:
                    pass
                try:
                    # 勾选
                    self.random_sleep(10, 12)
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_rbAccept']").click()
                    # 点击continue
                    self.random_sleep()
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_btnAccept']").click()
                except:
                    pass
                # 输入PIN码后，部分账户会出现更改手机的提示
                try:
                    self.random_sleep(10, 12)
                    driver.find_element_by_xpath("//span[@class='view-policies']").click()
                except:
                    pass

                self.random_sleep()
                # 查询各保单号，符合则点击see more

                response = etree.HTML(driver.page_source)
                policy_no_list = response.xpath("//span[@id='spnPolNo']//text()")
                for index,policy_no in enumerate(policy_no_list):
                    if policy_no == self.policyNumber:
                        self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='polList']/div["+str(index+1)+"]//span[@class='seemore']")
                        break
                response = etree.HTML(driver.page_source)
                # 账户价值
                Spider_Date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                Date = response.xpath("//span[@class='fund-summary-date'][2]//text()")[0] if response.xpath("//span[@class='fund-summary-date'][2]") else ''
                Fund_Name = response.xpath("//div[@class='price-history-padding-inside']/div[@class='price-history-data-div']/div[1]//q//text()")
                Fund_Code = response.xpath("//div[@class='price-history-padding-inside']/div[@class='price-history-data-div']/div[4]//text()")
                Fund_Bid_Price_Currency = response.xpath("//div[@class='fundTblRow']/div[2]//q//text()")
                Unit = response.xpath("//div[@class='fundTblRow']/div[3]/q//text()")
                Fund_Bid_Price = response.xpath("//div[@class='fundTblRow']/div[4]/q//text()")
                Value_In_Fund_Currency = response.xpath("//div[@class='fundTblRow']/div[5]/q//text()")
                Value_In_Policy_Currency = response.xpath("//div[@class='fundTblRow']/div[6]/q//text()")
                print('Date,Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency:',Date,Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency)
                if not self.cur.execute("select * from Zurich_Account_Allocation where Policy_Num='" + self.policyNumber + "' and Spider_Date='"+Spider_Date+ "';"):
                    for Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency in zip(Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency):
                        self.try_except(self.cur.execute("insert into Zurich_Account_Allocation(Policy_Num,Spider_Date,Date,Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (self.policyNumber,Spider_Date, Date, Fund_Name,Fund_Code,Fund_Bid_Price_Currency.replace(',',''),Unit.replace(',',''),Fund_Bid_Price.replace(',',''),Value_In_Fund_Currency.replace(',',''),Value_In_Policy_Currency.replace(',',''))))
                # 未来供款
                self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='fundSumMob']/div[@class='uiTabs']/ul[@class='uitoggle']/li[2]") # Investment strategy
                response = etree.HTML(driver.page_source)
                Investment_Contribution_Fund_Name = response.xpath("//div[@class='tab-pane investmentStrategy sel']//div[@class='fund-portfolio-data']//text()")
                Investment_Contribution_Allocation = response.xpath("//div[@class='tab-pane investmentStrategy sel']//div[@class='fund-portfolio-data']//text()")
                print('Investment_Contribution_Fund_Name,Investment_Contribution_Allocation:',Investment_Contribution_Fund_Name,Investment_Contribution_Allocation)
                if not self.cur.execute("select * from Zurich_Investment_Contribution where Policy_Num='" + self.policyNumber + "' and Date='"+Date+ "';"):
                    for Fund_Name,Allocation in zip(Investment_Contribution_Fund_Name,Investment_Contribution_Allocation):
                        self.try_except(self.cur.execute("insert into Zurich_Investment_Contribution(Policy_Num,Date,Fund_Name,Allocation) VALUES(%s,%s,%s,%s)",(self.policyNumber,Date,Fund_Name,Allocation)))

                # 保费概况

                Total_Premium = ''.join(response.xpath("//div[@class='invsDataItm'][4]//h1//span//text()")).replace(',','')[:-3]
                Total_Premium_Currency = ''.join(response.xpath("//div[@class='invsDataItm'][4]//h1//span//text()")).replace(',','')[-3:]
                Total_withdrawal = ''.join(response.xpath("//div[@class='invsDataItm'][5]//h1//span//text()")).replace(',','')[:-3]
                Total_withdrawal_Currency = ''.join(response.xpath("//div[@class='invsDataItm'][5]//h1//span//text()")).replace(',','')[-3:]
                self.random_sleep()
                self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='page']/div[@class='tabs']/a[3]") # payment
                response = etree.HTML(driver.page_source)
                Payment_Frequency = ''.join(response.xpath("//section[@id='pay']//div[@class='regPrem sel']/div[1]/p//text()"))
                if not self.cur.execute("select * from Zurich_Premium_Info where Policy_Num='" + self.policyNumber + "' and Spider_Date='"+Spider_Date+"';"):
                    # self.try_except(self.cur.execute("delete from Zurich_Premium_Info where Policy_Num='" + self.policyNumber + "';"))
                    self.try_except(self.cur.execute("insert into Zurich_Premium_Info(Policy_Num,Spider_Date,Total_Premium,Total_withdrawal,Total_Premium_Currency,Total_withdrawal_Currency,Payment_Frequency) VALUES(%s,%s,%s,%s,%s,%s,%s)",(self.policyNumber,Spider_Date,Total_Premium,Total_withdrawal,Total_Premium_Currency,Total_withdrawal_Currency,Payment_Frequency)))

                print('Total_Premium,Total_withdrawal,Payment_Frequency:',Total_Premium,Total_withdrawal,Payment_Frequency)
                # 保费详细表
                Premium_due_Date = response.xpath("//div[@class='regPrem sel']//div/p[1]//q[@class='desktopOnly']//text()")
                Premium_Due = response.xpath("//div[@class='regPrem sel']//div/p[2]//q//text()")
                Payment_Date = response.xpath("//div[@class='regPrem sel']//div/p[3]//q//text()")
                Premium = response.xpath("//div[@class='regPrem sel']//div/p[4]//q//text()")
                Status = response.xpath("//div[@class='regPrem sel']//div/p[5]//q//text()")
                page_counts = len(response.xpath("//div[@class='regPrem sel']//div[@class='prmTblPg hidePrev']//p"))
                print('page_counts',page_counts)
                self.random_sleep()
                # 判断页数 读取
                for page in range(page_counts-2):
                    try:
                        driver.find_element_by_xpath("//div[@class='regPrem sel']/div/p["+str(page_counts)+"]").click() # div[@class='prmTblPg hidePrev']
                    except:
                        # print(driver.page_source)
                        print('总共有%s页：'%(page+1))
                        break
                    self.random_sleep()
                    response = etree.HTML(driver.page_source)
                    Premium_due_Date += response.xpath("//div[@class='regPrem sel']//div/p[1]//q[@class='desktopOnly']//text()")
                    Premium_Due += response.xpath("//div[@class='regPrem sel']//div/p[2]//q//text()")
                    Payment_Date += response.xpath("//div[@class='regPrem sel']//div/p[3]//q//text()")
                    Premium += response.xpath("//div[@class='regPrem sel']//div/p[4]//q//text()")
                    Status += response.xpath("//div[@class='regPrem sel']//div/p[5]//q//text()")
                    # if not response.xpath("//div[@class='prmTblPg hideNext']"):
                    #     self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='accordPanel']/div[@class='regPrem sel']/div/p["+str(page_counts)+"]")
                    # if page < page_counts:

                for Premium_due_Date,Premium_Due,Payment_Date,Premium,Status in zip(Premium_due_Date,Premium_Due,Payment_Date,Premium,Status):
                    print('Premium_due_Date,Premium_Due,Payment_Date,Premium,Status:',Premium_due_Date,Premium_Due,Payment_Date,Premium,Status)
                    if not self.cur.execute("select * from Zurich_Premium where Policy_Num='" + self.policyNumber + "' and Premium_due_Date='"+Premium_due_Date+ "';"):
                        self.try_except(self.cur.execute("insert into Zurich_Premium(Policy_Num,Spider_Date,Premium_due_Date,Premium_Due,Payment_Date,Premium,Premium_Due_Currency,Premium_Currency,Status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.policyNumber,Spider_Date,self.date_to_num(Premium_due_Date),Premium_Due.replace(',','')[:-4],self.date_to_num(Payment_Date),Premium.replace(',','')[:-4] if Premium.replace(',','')[:-4] else Premium.replace(',',''),Premium_Due.replace(',','')[-3:],Premium.replace(',','')[-3:],Status)))
                self.mysql_client.commit()
                print('commited.')
                self.successed += 1

                # 点击logout,登出
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                print(self.policyNumber,'Logout.')
                # driver.quit()

            except Exception as e:
                print(self.policyNumber,'error!',e)
                # 点击logout,登出
                # self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                # driver = webdriver.Chrome()
        self.cur.close()
        self.mysql_client.close()
        driver.quit()

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
            for policyNumber, platform, riskType, operationSituation, userName, passWord, PIN in zip(excel['保单号'],excel['Platform'],excel['风险属性'],excel['调仓情况'],excel['用户名'],excel['密码'],excel['PIN码']):
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
                if (platform == 'Zurich' or platform == 'Zurich new' or platform == 'zurich' and operationSituation != '登录失败'):
                    zurich.append((policyNumber,  riskType, userName, passWord,int(PIN)))
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
        # print('\n正在进行standard_life_spider调仓操作....')
        # self.standard_life_spider(data[3])
        print('\n正在进行zurich_spider调仓操作....')
        self.zurich_spider(data[2])
        # print('\n正在进行axa_spider调仓操作....')
        # self.axa_spider(data[4])

        print('\r\n调仓完毕！其中调仓成功 %s个/总数%s个。' % (self.successed, self.counts))
        # self.send_email()


if __name__ == '__main__':
    auto_operation = AutoOperation()
    auto_operation.start_work()
