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

    def zurich_spider(self,zurich):
        """
                zurich调仓操作
                :param zurich: zurich data list
                :return: operating
                """
        # zurich = [(9861620, "nan", 'codysunmz', 'Ilovele$shi', 110947), (9860437, "nan", 'Zhuwenfang75', 'Zhuwenf0916', 1975), (8110328, "nan", 'Ljfeng11', 'Lejianf11', 1977), (9865684, "nan", 'Zhyong72', 'Zhangyong37', 1772), (9965607, "nan", 'codysunmz', 'Ilovele$shi', 110947), (8165955, "nan", 'Zhangli83', 'ZHLi1228', 1983), (8105512, "nan", 'Guoying0802', 'YingG0802', 1978), (9918958, "nan", 'kembleouyang', 'TianHao605', 1970060711), (9843770, "nan", 'Xiaoyantu', 'Melman228', 1993), (9865808, "nan", 'Liukejia1203', 'Liukejia0312', 1979), (9954377, "nan", 'Yingsun817', 'Sunying0718', 1078), (9966107, "nan", 'luofuflu8393', 'Zurich2010', 20100101), (8219179, "nan", 'lilijoe', 'Lili1211', 1211), (8222881, "nan", 'Tangdd0711', 'Tangdd1985', 1985), (8234561, "nan", 'liaxiaol9217', 'Jessie1023', 315217), (8243560, "nan", 'Wenpeihan0322', 'Wenpeihanha7803', '1830'), (8239800, "nan", 'Gaoyinlu7120', 'Gaoylu91702', 9712), (8258290, "nan", 'liubingl4475', 'Bingxin1963', 1363229179), (8261860, "nan", 'chenciqi3739', 'JKF12dyi', 86419042), (8275346, "nan", 'luo"nan"lu3102', 'Luo"nan"1214', 20041214), (8271953, "nan", 'hongliho1716', 'Hong23456', 123456), (8282865, "nan", 'kohonkoh5489', 'qweR1tyu', '001229'), (8286030, "nan", 'hanlecheng', '790097Hanlecheng', 7911), (8292356, "nan", 'linxiaol2780', 'Xiao23456', '031750'), (8294308, "nan", 'Fujun1218', 'FUjun9728', 1297), (8293940, "nan", 'Emei7811', 'Emei1978', 7811), (8297774, "nan", 'jingxinj8428', 'Jxin0810', '8010'), (8303439, "nan", 'denliden4327', 'SOHUcat368', 5549), (8303498, "nan", 'wangniwa6019', 'Wang1357', 19800110), (8309170, "nan", 'jenniferlu09', 'Climate0', 1975), (1603078, "nan", '05376142', 'XLM12345', '/'), (8335446, "nan", 'huashuih7675', 'Hsf198023Lhr', '5728632'), (8335128, "nan", 'Chuyjun2017', 'CHyinjun0127', 8217), (8337155, "nan", 'chenhuic2815', 'Huihua1973', '19730205'), (8337253, "nan", 'Pengxuan81', 'Pengx0709', 8179), (8328415, "nan", 'liuganli4250', 'Gang23456', 910516), (8352316, "nan", 'gaoweing6282', 'Vincent_tsh0017', 19830224), (8374085, "nan", 'liyiliyi2912', 'Hm1slv??', 26549215), (8377093, "nan", 'Tangzd6926', 'Tangzd0326', 9026), (8374932, "nan", 'Panhj7602', 'Panjuan0203', 7603), (8399878, "nan", 'kouhongk8073', 'Wangziming0322', 34474460), (8103619, "nan", 'penxiaop1994', 'Pengxiaor1976', 1976120188), (8104675, "nan", 'luoqinlu1078', 'LuoQinn03081', '080319'), (8380247, "nan", 'Hulijuan8116', 'Hulj8112', 8126), (8380353, "nan", 'luoyuanl0687', 'Yuan2345', 246321), (8103662, "nan", 'wuxiaowu5737', 'Xiao2345', 123456), (8103767, "nan", 'heshahes5446', 'Shan23456', 123456), (8178597, "nan", 'Liqian8023', 'Liqian9083', 1923), (8178228, "nan", 'weibinwe2308', 'Benfair_780531', '0417042807'), (8178236, "nan", 'Qjing8236', 'Qiujing8236', 8236), (8198369, "nan", 'cheyuxic7950', 'Yu234567', 123456), (8198475, "nan", 'Pangqping91', 'Pqiuping9401', 1418), (8207784, "nan", 'Hewei1130', 'Hewei11930', 1037), (8209884, "nan", 5001, '$florid413522', 201404), (8222227, "nan", 'renweire1365', 'RRww76110220', 78761420), (8219366, "nan", 'cheleich1774', 'Chen34567', '456789'), (8218009, "nan", 'wangkui', 'x49-kfY-BMH-ccn', 8218), (8222278, "nan", 'lixialix0920', 'Eva19810412', 19810412), (8227326, "nan", 'zhangning0512', 'Zhangni1850', 9015), (8231528, "nan", 'songjins5377', 'Tufe9705', 213213), (8224174, "nan", 'yangjian2699', 'YjianLiuj123', 19830626), (8224998, "nan", 'GaoYan8128', 'Huahua790228', 1981), (8225595, "nan", 'wanjiawa7305', 'WJY1973sz', 197312), (8222219, "nan", 'wangjiny3201', 'Jinyan2014', 123456), (8225083, "nan", 'liuguali4909', 'A1B2C3d4f5g6', 123456), (8227955, "nan", 4683, 'Dong23456', 19760821), (8231765, "nan", 'chezhuch6663', 'Xiao23456', 19740511), (8243022, "nan", 'niuconni5943', 'Niucongying1983', 19830313), (8242954, "nan", 'annaxyz', '1981-annaxyz', '0509'), (8243488, "nan", 'yujianyu3797', 'Jian23456', 8103), (8244124, "nan", 'Sunyhua2414', 'Syanhua0519', 8195), (8244115, "nan", 'zhaoxiao9794', 'Xiao23456', 19830328), (8244673, "nan", 'fanjiwfa2659', '13581910367YFzxf', 19811217), (8247157, "nan", 'Jinxin1979', 'JinXin0201', 1979), (8247425, "nan", 'oucanwou6569', 'Vids1516', 124124), (8247395, "nan", 'Guchqing0022', 'GUchangq0280', 1982), (8250345, "nan", 'Yuyan1217', 'YUyan1127', 9172), (8224192, "nan", 'liujingl3335', 'YjianLiuj123', 20051983), (8227946, "nan", 'Hua8227946', 'Shuang234', 1234), (8245554, "nan", 'wulinwul3390', 'Wuling1983', 19830908), (8219358, "nan", 'Liulihua17', 'Liulh8107', 9170), (8191615, "nan", 'Luotielu0141', 'Luotie0848', 246321), (8254146, "nan", 'Mgfang9011', 'Mg840911', 9011), (8278390, "nan", 'Xjnhua65', 'Xjianh56', 1983), (8282328, "nan", 'Wangyan', 'Wyan6605', 6605), (8292766, "nan", 'Tgrong1122', 'Tangr8312', 1812), (8292814, "nan", 'Chyang0781', 'Cheny0781', '0781'), (8324519, "nan", 'vaneyq', 'vaneyq198362V', 8362), (8363282, "nan", 'TongL1126', 'TLing8111', '1981'), (8363274, "nan", 'sunxiaosu', 'Sun19800720', '0720'), (8367490, "nan", 'Feiqm633', 'Fqmei751011', 1011), (8374551, "nan", 'Qwjuan51', 'Qiwj1018', 8710), (8380330, "nan", 'yver0929', 'Zhang0929yv', 929), (8383885, "nan", 'Zhna3885', 'Zhna1133', 8383), (8389395, "nan", 'Qhui8412', 'QiaoH1212', 8412), (8109581, "nan", 'Kaiyuan911202', 'Fnkayuan91', 9112), (8392086, "nan", 'Lixing', 'Lx123456', 1234), (8107295, "nan", 'Wagj7295', 'Wjin1102', 1102), (8108380, "nan", 'iloveamyfish', 'Jy00074827', 1314), (8109050, "nan", 'Gmb1972', 'Bomg1972', '0625'), (8115058, "nan", 'Qianc0507', 'Qcun1010', 8910), (8115067, "nan", 'Xdhu0125', 'Xiad5067', 1984), (8118236, "nan", 'Lyishan1987', 'Lyshan0303', 8703), (8118227, "nan", 'ZJLiang8227', 'ZhuoJL8207', '0709'), (8118254, "nan", 'Yyin1985', 'Ygyin8254', 8118), (8127024, "nan", 'linxiqian', '3354Him~', 1219), (8128241, "nan", 'Yexining', 'Zxn5201031', 1031), (8137151, "nan", 'Dengy1988', 'Dying1225', 8812), (8144050, "nan", 'jlp2016', 'u96f5JreqdQR', '0318'), (8148935, "nan", 'Jinh1889', 'Jhua1889', 1889), (8155982, "nan", 'Heri1808', 'Heru0216', '0216'), (8161777, "nan", 'Wenxj8989', 'WXjing2489', 3062), (8161974, "nan", 'laurieli2016', 'Password1', 1102), (8272304, "nan", 'Xiangli0322', 'Lixiang81', 1981), (8273478, "nan", 'Zhjr3478', 'Zjunr0918', 1980), (8275953, "nan", 'Chjmin83', 'Jiaminch38', 8381), (8286173, "nan", 'leizmax714', 'Zhlei0714', 1980), (8295304, "nan", 'TheaWang', 'ELaine0411', '0302'), (8295277, "nan", 'Xiuzhi', 'Iamzxz5613996', '0401'), (8299019, "nan", 'Shenchm0233', 'Shench0233miao', 1923), (8299868, "nan", 'BaiL0617', 'Lubai1706', 1986), (8300095, "nan", 'Zhcht502', 'Taocz0502', 1979), (8307178, "nan", 'zhouhao1985', 'Zhouhhuohz85', 8519), (8307812, "nan", 'Shenzh418', 'ZHsh0418', 1982), (8307855, "nan", 'Xuxm0725', 'XMxu0725', 1980), (8307828, "nan", 'LinQZ0702', 'Qiongzhu0207', 1992), (8319322, "nan", 'Cuij0512', 'Jingcui1279', 1979), (8319314, "nan", 'skyofhistory', '841024Free', 8996), (8326264, "nan", 'supertwh', 'Supertwh830928', '0928'), (8335131, "nan", 'Shixuefgzg3001', 'Shiguan8119', 1981), (8333357, "nan", 'Wang8765zheng', 'Wz139576ngeng', 3578), (8333366, "nan", 'Liangwq0822', 'Liangwq2208', 1981), (8332989, "nan", 'Zhaox1011', 'Zhao1979x', 1011), (8333039, "nan", 'lixixi0818', 'Azdlxx818', 527), (8339097, "nan", 'Huyap1014', 'Yaphu1410', 1982), (8347792, "nan", 'cheryze16', '0810zaqPP#.', '0813'), (8347784, "nan", 'zenosbaba', '0810zaqPP#', 813), (8348381, "nan", 'Yanli_Wang', 'Ad185wylzyn', '0215'), (8349637, "nan", 'wang_1983', 'Reuters2345', 8565), (8351994, "nan", 'hufenhuf0207', 'Fenhu2823', 2383), (8354241, "nan", 'hongmanlin', 'Hml258456', 2589), (8383517, "nan", 'dai451723844', '1800470036Dqy', 1993), (8399970, "nan", 'Motionway0812', 'Xinweimo0812', 7412), (8106328, "nan", 'Wang0702y', 'W0702yun', 1982), (8100666, "nan", 'Hgyxing119', 'Xgyaoh9137', 1973), (8106311, "nan", 'zhahailz1879', 'Lanhz914', 909471905), (8113758, "nan", 'Cheny1219x', 'Cy1912xiang', 1975), (8118786, "nan", 'Xiaoy1007', 'Xiao0710y', 1982), (8119766, "nan", 'Sandra88', 'YANGyang0724', 6202), (8121807, "nan", 'Zhoux18', 'Zhoux1118uan', 1982), (8124565, "nan", 'LIYANFEN', '239435feN', 3367), (8124581, "nan", 'Xiangy85', 'Xiang0908y', 1985), (8124547, "nan", 'zengqi19841226', 'cjlnFDS19841226', 3398), (8124735, "nan", ' jennyxk1975', 'Jenny_xk1975', '0618'), (8129502, "nan", 'Liu0807yy', 'Liuy0708yuan', 1972), (8288507, "nan", 'Wxiaog78', 'Wxgeng0112', 1978), (8336686, "nan", 'Liuyy0508', 'Yangyliu0508', 1984)]
        # zurich = [(9861620, "nan", 'codysunmz', 'Ilovele$shi', 110947), (9843770, "nan", 'Xiaoyantu', 'Melman228', 1993), (8335128, "nan", 'Chuyjun2017', 'CHyinjun0127', 8217)]
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver = webdriver.Chrome()
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
                #     # 隐藏的，tpye='hidden'
                #     # "__LASTFOCUS": "",
                #     "ctl00_ToolkitScriptManager1_HiddenField": ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-GB:2a06c7e2-728e-4b15-83d6-9b269fb7261e:de1feab2:f2c8e708:720a52bf:f9cec9bc:7311d143",
                #     # "__EVENTTARGET": "",
                #     # "__EVENTARGUMENT": "",
                #     # "__VIEWSTATE": "/wEPDwUKMTI5NDk5NjQzNw8WAh4JUmV0dXJuVXJsBRMvWklPL015UG9saWNpZXMubXZjFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWBGYPZBYSAgEPDxYCHgRUZXh0BSRMb2dpbiB0byBadXJpY2ggSW50ZXJuYXRpb25hbCBvbmxpbmVkZAIHDw8WAh4MRXJyb3JNZXNzYWdlBR5Vc2VybmFtZSBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAILDw8WAh8CBR5QYXNzd29yZCBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAINDxAPFgIfAQUUUmVtZW1iZXIgbXkgVXNlcm5hbWVkZGRkAg8PDxYCHwEFCENvbnRpbnVlZGQCEQ8PFgIfAQU1PGEgaHJlZj0iL0xvc3RDcmVkZW50aWFscy9Vc2VyTmFtZS5hc3B4Ij51c2VybmFtZTwvYT5kZAITDw8WAh8BBTU8YSBocmVmPSIvTG9zdENyZWRlbnRpYWxzL1Bhc3N3b3JkLmFzcHgiPnBhc3N3b3JkPC9hPmRkAhUPDxYCHwEFmwFJIGZvcmdvdCBib3RoLiBJZiB5b3UgaGF2ZSBmb3Jnb3R0ZW4gbW9yZSB0aGFuIG9uZSBvZiB5b3VyIGxvZ2luIGRldGFpbHMsIHBsZWFzZSA8YSBocmVmPSIvSW5mb3JtYXRpb24vQ29udGFjdERldGFpbHMuYXNweCIgdGFyZ2V0PSJfYmxhbmsiPmNvbnRhY3QgdXM8L2E+LmRkAhcPZBYCAgEPZBYCZg8PFgQeCENzc0NsYXNzBRBhY2NvcmRpb24taGVhZGVyHgRfIVNCAgJkZAIBD2QWAgIBD2QWAmYPZBYCZg9kFgYCBQ9kFgYCCQ8QZGQWAGQCDw8QZGQWAGQCFQ8QZGQWAGQCBw8WAh4OUG9zdEJhY2tTY3JpcHQFQ19fZG9Qb3N0QmFjaygnY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSR1Y1BpblZhbGlkYXRvciRidG5RdWl0JywnJylkAgsPFgIfBQVMX19kb1Bvc3RCYWNrKCdjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHVjUGluVmFsaWRhdG9yJGJ0blJhbmRvbVBpblF1aXQnLCcnKWQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFJmN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkY2JSZW1lbWJlck1lBSRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJE11bHRpVmlldzEPD2RmZD0Dvsc87o3jOZ3ZPZVuZpVJ3Hfo",
                #     # "__VIEWSTATEGENERATOR": "C2EE9ABB",
                #     # "__SCROLLPOSITIONX": "0",
                #     # "__SCROLLPOSITIONY": "276",
                #     # "__EVENTVALIDATION": "/wEWBgLmnay0DQLJ4fq4BwL90KKTCAKipK3+BAKtnJ6XBQLrspm9A1uSQcy1zRVB9AVdXeBqyISrY6YA",
                #     "ctl00$ContentPlaceHolder1$MyAccordion_AccordionExtender_ClientState": "-1",
                #     # 固定的，tpye='text'
                #     "ctl00$ContentPlaceHolder1$cbRememberMe": "on",
                #     "ctl00$ContentPlaceHolder1$cmdLogin": "Continue",
                #     "ctl00$ContentPlaceHolder1$txtUserName": username,
                #     "ctl00$ContentPlaceHolder1$txtPassword": password,
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
                Date = self.date_to_num(response.xpath("//span[@class='fund-summary-date'][2]//text()")[0]) if response.xpath("//span[@class='fund-summary-date'][2]") else ''
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
                            (self.policyNumber,Spider_Date, Date, Fund_Name,Fund_Code,Fund_Bid_Price_Currency,Unit,Fund_Bid_Price,Value_In_Fund_Currency,Value_In_Policy_Currency)))
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

                Total_Premium = ''.join(response.xpath("//div[@class='invsDataItm'][4]//h1//span//text()"))
                Total_withdrawal = ''.join(response.xpath("//div[@class='invsDataItm'][5]//h1//span//text()"))
                self.random_sleep()
                self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='page']/div[@class='tabs']/a[3]") # payment
                response = etree.HTML(driver.page_source)
                Payment_Frequency = ''.join(response.xpath("//section[@id='pay']//div[@class='regPrem sel']/div[1]/p//text()"))
                if not self.cur.execute("select * from Zurich_Premium_Info where Policy_Num='" + self.policyNumber + "' and Spider_Date='"+Spider_Date+"';"):
                    # self.try_except(self.cur.execute("delete from Zurich_Premium_Info where Policy_Num='" + self.policyNumber + "';"))
                    self.try_except(self.cur.execute("insert into Zurich_Premium_Info(Policy_Num,Spider_Date,Total_Premium,Total_withdrawal,Payment_Frequency) VALUES(%s,%s,%s,%s,%s)",(self.policyNumber,Spider_Date,Total_Premium,Total_withdrawal,Payment_Frequency)))

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
                    if not self.cur.execute("select * from Zurich_Premium where Policy_Num='" + self.policyNumber + "' and Spider_Date='"+Spider_Date+ "';"):
                        self.try_except(self.cur.execute("insert into Zurich_Premium(Policy_Num,Spider_Date,Premium_due_Date,Premium_Due,Payment_Date,Premium,Status) VALUES(%s,%s,%s,%s,%s,%s,%s)",(self.policyNumber,Spider_Date,self.date_to_num(Premium_due_Date),Premium_Due,self.date_to_num(Payment_Date),Premium,Status)))
                self.mysql_client.commit()
                print('commited.')
                # self.cur.close()
                # 点击logout,登出
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                # driver.quit()

            except Exception as e:
                print(self.policyNumber,'error!',e)
                # 点击logout,登出
                # self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                # driver = webdriver.Chrome()
        self.mysql_client.close()
        driver.quit()

    # def standard_life_spider(self, standard_life):
    #     """
    #     zurich调仓操作
    #     :param zurich: zurich data list
    #     :return: operating
    #     """
    #     # standard_life = [(39970, "nan", 'albertzhou', 'zhoulu2011'), (47220, "nan", 'QueenieLuo', '12345678'), (45319, "nan", 'liuql', '789654'), (49168, "nan", 'Xiesi130', '840130abc'), (41063, "nan", 'sunna', '123456'), (46070, "nan", 'polin82082', 'tan3708026'), (38849, "nan", 'joles', '123123'), (42322, "nan", 'PANPEI', 'IPSOS1234'), (50829, "nan", 'gskmwj', '87390635'), (39429, "nan", 'tagichan', 'rika1217'), (46837, "nan", '2423569', '123qwe'), (44111, "nan", 'luohuiou', '080160'), (45381, "nan", 'zhoujy', 'gzrbzjy'), (44805, "nan", 'hwbinboy', '23290778Hzy'), (48663, "nan", 'AJIAO', 'HK6q8080'), (48440, "nan", 'yuanna1981', 'Gd87787439'), (28958, "nan", 'zhang28958', 'qwr0935'), (48396, "nan", 'fanchen94', 'fanchen94'), (50560, "nan", 'bubuzcp', '006136lsm'), (50010, "nan", 'zhouzhihui', '731230'), (39976, "nan", 'yin39976', '19870519'), (33435, "nan", 'chen33435', 'jian1234'), (40228, "nan", 'liang40228', '19870807'), (42224, "nan", 'yangyang66', '28784458'), (48588, "nan", 'hongrong', 'chr2012'), (36523, "nan", 'lege0322', '460725'), (50556, "nan", 'longkai77', '404767116'), (50557, "nan", 'xiaojie77', '404767116'), (45448, "nan", 'Janney', '1343033294'), (44537, "nan", 'longlele', '19850516'), (44893, "nan", 'lixiuwen', '19840229'), (42046, "nan", 'joyce008', 'wu831422'), (44544, "nan", 'zhangwl', '19841012'), (39879, "nan", 'juntim', 'juntim123'), (46654, "nan", 'chenguobo', '04170619'), (41933, "nan", 'szetohl', 'szetohl137'), (39424, "nan", 'tanhuizhi', '52tanhzsl'), (38933, "nan", 'clzsu', 'czz816'), (49256, "nan", 'hrchao18', 'Tutu18'), (42047, "nan", 'azhuzhu', 'echo1022'), (43072, "nan", 'jingjing', 'hq800513'), (31361, "nan", 'xu31361', '123514meng'), (42279, "nan", 'teresaH', 'Aimi0410'), (41655, "nan", 'xu41655', 'ting1234'), (30256, "nan", 'liang30256', '630913'), (31362, "nan", 'wang31362', 'wqy660912'), (52270, "nan", 'lujunfeng', '19831109'), (42039, "nan", 'azhuzhu', 'echo1022'), (46978, "nan", 'moringsing', 'lw771219'), (47846, "nan", 'sophy', 'sophy123'), (44545, "nan", 'heqina', 'qinahe'), (44536, "nan", 'wuqiyun', 'zoewuqiyun'), (42114, "nan", 'vixen_xu', '147852'), (49135, "nan", 'qiuqu', '19740820'), (48414, "nan", 'yao198001', 'xilin2011'), (47692, "nan", 'yuekui', '770805chen'), (47847, "nan", 'yayapay', 'taodan2523'), (48485, "nan", 'guo197909', 'yuguo197909'), (47693, "nan", 'timye2012', 'yihk0611'), (48094, "nan", 'yang198009', 'Ylpy2010'), (47655, "nan", 'ccpig_0504', '820504'), (47665, "nan", 510121, '510121'), (50447, "nan", 'mandymd', 'Mp3210'), (49655, "nan", 'Mws1124', 'Welsa1124'), (52569, "nan", 'hanhoumei', 'ly975331'), (52664, "nan", 'doublel', 'liangliang'), (52668, "nan", '00052668', '22op00'), (53007, "nan", 'HUANGHAO', 'HUANGHAO62'), (53010, "nan", '34118590', '11082011'), (53246, "nan", 'beansmile', 'han783xiao'), (53009, "nan", 'zlij123', 'zlij1225'), (54426, "nan", '00054426', '0054426'), (55228, "nan", 'lixc1112', '19790718'), (55229, "nan", '14739427', 'wangjing'), (55445, "nan", 'zhangshx', 'W0i7s2x4h'), (55878, "nan", 'yuanziming', '19730312'), (55954, "nan", 'aimee5127', 'Bear0526'), (56615, "nan", 'pengliushe', 'Sl19770424'), (56379, "nan", 'CHENLJ0313', 'jing7lc9'), (56378, "nan", '00056378', '19850928'), (56663, "nan", 'zeng1982', 'szy2011'), (57116, "nan", 'wlqiong', '980324wlq'), (57030, "nan", 'zhuyin1977', '20081210'), (56565, "nan", 'lilili2013', 'lilili2013'), (57148, "nan", 'purplestar', 'xiyan1981'), (57431, "nan", 'fangwei8', 'fangwei88'), (58342, "nan", 'leoyou2003', '290612'), (58445, "nan", 'tt0528', '87588599'), (58446, "nan", 'f19770321', '731218'), (58669, "nan", 'lynibm111', 'lyn7536'), (59008, "nan", 'chenying22', '19780202'), (59196, "nan", 'james＿guan', 'Guan2345'), (59197, "nan", 'zhoujy', 'gzrbzjy'), (59198, "nan", 'SEChen', 'aws7890'), (59443, "nan", 'XY645639', 'PASS6456'), (59199, "nan", 'michael22', 'yolanda26'), (59627, "nan", 'grapefunny', 'fgf510290'), (30792, "nan", 'LHY1975', 'liu0121'), (60050, "nan", 'ada0564', 'ada1101'), (59765, "nan", 'bobbychen', 520102), (59858, "nan", 'yukinben', 'uASl201309'), (59766, "nan", 'zjhlang', '99sped6'), (61253, "nan", 'aileen0302', 'aileen0302'), (60897, "nan", 'wangjin', 'haoyu0314'), (62625, "nan", 'chuntian', '2008007007'), (63041, "nan", 'edison2014', 'Edison2016'), (62977, "nan", 'chenjingwe', 'Gaojing106'), (63137, "nan", 'xgbb', 'xgbb197076'), (63138, "nan", 'czc', '51766gd'), (62851, "nan", 'cjianming', 'cjm1984'), (63393, "nan", 'mandy901', 'mandy901'), (63548, "nan", 'xianyuhui', 'Xianyuhui5'), (63563, "nan", 'zhangli920', '0704zlzzq'), (63576, "nan", 'HUANGHAO', 'HUANGHAO62'), (63597, "nan", 'xuhuixian', 'xu775532'), (63598, "nan", 'Rachel1985', 'Rachel1234'), (63596, "nan", 'candyxuqin', 'XUHU880728'), (63638, "nan", 'moonyfox', 'Wanghui28'), (56031, "nan", 'jadewang', 'Hkfs0601')]
    #     # standard_life = [(48663, "nan", 'AJIAO', 'HK6q8080'), (47692, "nan", 'yuekui', '770805chen')]
    #     if not standard_life:
    #         print('standard_life无需spider的保单！')
    #         return
    #     print('------------')
    #     # 调出浏览器
    #     chrome_options = webdriver.ChromeOptions()
    #     chrome_options.add_argument('--headless')
    #     chrome_options.add_argument('--disable-gpu')
    #     driver = webdriver.Chrome(chrome_options=chrome_options) # , executable_path="./chromedriver_linux64/chromedriver"
    #
    #     # cap = webdriver.DesiredCapabilities.PHANTOMJS
    #     # cap["phantomjs.page.settings.resourceTimeout"] = 1000
    #     # cap["phantomjs.page.settings.loadImages"] = True
    #     # cap["phantomjs.page.settings.disk-cache"] = True
    #     # cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    #     # cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    #     # driver = webdriver.PhantomJS(desired_capabilities=cap)
    #
    #     # 打开浏览器登录
    #     url = "https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch"
    #     for index, item in enumerate(standard_life):
    #         # 链接数据库
    #         # self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
    #         self.error = 0
    #         self.operation_counts += 1
    #         self.enum_index = index
    #         try:
    #             # 保单号,如 T25W017027
    #             Policy_Num = str(item[0])
    #             # 风险类型
    #             self.riskType = str(item[1])
    #             # 卖出基金
    #
    #             self.random_sleep()
    #             username = str(item[2])
    #             password = str(item[3])
    #
    #             # 发送链接
    #             driver.get(url)
    #             # driver.set_page_load_timeout(100)
    #             # 窗口最大化
    #             # driver.maximize_window()
    #             self.random_sleep()
    #             # 点击特别安排的OK
    #             try:
    #                 driver.find_element_by_xpath("//div[@class='ui-dialog-buttonset']/button/span").click()
    #             except:
    #                 pass
    #             # 登录
    #             self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
    #                             action='clear')
    #             self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
    #                             action='send_keys', send_keys=username)
    #             self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
    #                             action='clear')
    #             self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
    #                             action='send_keys', send_keys=password)
    #             # self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='btn_Login']")
    #             driver.find_element_by_xpath("//input[@id='btn_Login']").click()
    #             self.random_sleep()
    #             try:
    #                 response = driver.page_source
    #                 responses = etree.HTML(response).xpath("//table[@id='tblPolInfoSum']//tr//td[@class='LightGrey']/a")
    #             except Exception as e:
    #                 print(e,'error,可能账户正在被登陆中',Policy_Num)
    #                 driver.quit()
    #                 # 调出浏览器
    #                 chrome_options = webdriver.ChromeOptions()
    #                 chrome_options.add_argument('--headless')
    #                 chrome_options.add_argument('--disable-gpu')
    #                 driver = webdriver.Chrome(chrome_options=chrome_options)  # , executable_path="./chromedriver_linux64/chromedriver"
    #                 # cap = webdriver.DesiredCapabilities.PHANTOMJS
    #                 # cap["phantomjs.page.settings.resourceTimeout"] = 1000
    #                 # cap["phantomjs.page.settings.loadImages"] = True
    #                 # cap["phantomjs.page.settings.disk-cache"] = True
    #                 # cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    #                 # cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    #                 # driver = webdriver.PhantomJS(desired_capabilities=cap)
    #                 continue
    #             print(username, ':Login')
    #             for index,response in enumerate(responses):
    #                 try:
    #                     print(response.text)
    #                     print(Policy_Num)
    #                     if Policy_Num.strip() not in response.text:
    #                         continue
    #                     self.random_sleep()
    #                     # self.wait_until(driver=driver, platform='standard_life', selector_name="//table[@id='tblPolInfoSum']//tr["+str(index+2)+"]/td[@class='LightGrey']/a")
    #                     self.wait_until(driver=driver, platform='standard_life',
    #                                     selector_name="//table[@id='tblPolInfoSum']//tr["+str(index+2)+"]/td[@class='LightGrey']/a")
    #                     # 切换至新窗口
    #                     # policyLink = str(driver.find_element_by_xpath("//table[@id='tblPolInfoSum']//tr["+str(index+2)+"]/td[@class='LightGrey']/a").get_attribute("href"))
    #                     # js = 'window.open("' + policyLink + '");'
    #                     # driver.execute_script(js)
    #                     # print(driver.window_handles)
    #                     # 其中一个保单号
    #                     # driver.switch_to.window(driver.window_handles[1])
    #                     self.random_sleep(5,10)
    #                     response = etree.HTML(driver.page_source)
    #                     # response = response.xpath("//table[@id='pol_sum_menu_tableLink']//tr//td/span[@class='blue']/a")
    #                     Spider_Date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #                     Currency = ''.join(response.xpath("//span[@id='pol_details_lbPolCur']//text()"))
    #                     Total_Premium = ''.join(response.xpath("//span[@id='lbPVSContribution']//text()")) if response.xpath("//span[@id='lbPVSContribution']") else ''
    #                     Total_withdrawal = ''.join(response.xpath("//span[@id='lbPVSWithdrawals']//text()")) if response.xpath("//span[@id='lbPVSWithdrawals']") else ''
    #                     Payment_Frequency = ''.join(response.xpath("//span[@id='pay_info_lbPIPayFeq']//text()")) if response.xpath("//span[@id='pay_info_lbPIPayFeq']") else ''
    #                     Regular_Premium = ''.join(response.xpath("//span[@id='pay_info_lbPIContribution']//text()")) if response.xpath("//span[@id='pay_info_lbPIContribution']") else ''
    #                     print('Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium:',Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)
    #                     if not self.cur.execute("select * from Standardlife_Premium_Info where Policy_Num='" + Policy_Num + "' and Spider_Date='"+Spider_Date+"';"):
    #                         # self.try_except(self.cur.execute("delete from standardlife_premium_info where Policy_Num='" + Policy_Num + "';"))
    #                         self.try_except(self.cur.execute("insert into Standardlife_Premium_Info(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium) VALUES(%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)))
    #
    #                     # 未来供款
    #                     titles = response.xpath("//div[@class='largeSizeHolder1000']/div/span[@class='h2']//text()")
    #                     print(titles)
    #                     for index,title in enumerate(titles):
    #                         if '戶口' in title:
    #                             length = len(response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[3]"))
    #                             Investment_Account0 = str(re.sub("\D", "", title))
    #                             Investment_Account = [Investment_Account0[:2]]*length
    #                             Date = self.date_to_num(response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][5]//text()")[0]) if response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][5]") else ''
    #                             Account_Type = ['01']*length if '最初' in title else ['02']*length
    #                             account_type = '01' if '最初' in title else '02'
    #                             Allocation_In_Policy_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[3]//text()")
    #                             Allocation = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[2]//text()")
    #                             Allocation_Fund_Name = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[1]//text()")[1:-1]
    #                             print(index,'Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name',Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)
    #                             if not self.cur.execute("select * from Standardlife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "' and Spider_Date='" + Spider_Date + "';"):
    #                                 # self.try_except(self.cur.execute("delete from StandardLife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "';"))
    #                                 for Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name in zip(Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name):
    #                                     print(Policy_Num,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)
    #                                     self.try_except(self.cur.execute("insert into Standardlife_Future_Investment_Contribution(Policy_Num,Spider_Date,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
    #                                         (Policy_Num,Spider_Date,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)))
    #                             Fund_Name = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][1]//text()")
    #                             Reference_Code = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][2]//text()")
    #                             Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][3]//text()")
    #                             Unit = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][4]//text()")
    #                             Price = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][6]//text()")
    #                             Weight = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][7]//text()")
    #                             Value_In_Fund_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][8]//text()")
    #                             Value_In_Policy_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][9]//text()")
    #                             print('Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency:',Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
    #                             if not self.cur.execute("select * from Standardlife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date +  "';"):
    #                                 # self.try_except(self.cur.execute("delete from StandardLife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date + "';"))
    #                                 for Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency in zip(Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency):
    #                                     print(Policy_Num,Date,Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
    #                                     self.try_except(self.cur.execute("insert into Standardlife_Account_Allocation(Policy_Num,Spider_Date,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
    #                                         (Policy_Num,Spider_Date,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)))
    #
    #                     # 点击交易日志
    #                     self.wait_until(driver=driver, platform='standard_life', selector_name="//table[@id='pol_sum_menu_tableLink']//tr//td//a[2]")
    #                     self.random_sleep()
    #                     response = etree.HTML(driver.page_source)
    #                     Payment_date = response.xpath("//table[@id='tblPH']/tbody//tr/td[1]//text()")
    #                     Premium_due_Date = response.xpath("//table[@id='tblPH']/tbody//tr/td[2]//text()")
    #                     Payment_Method = response.xpath("//table[@id='tblPH']/tbody//tr/td[3]//text()")
    #                     Policy_Currency = response.xpath("//table[@id='tblPH']/tbody//tr/td[4]//text()")
    #                     Premium = response.xpath("//table[@id='tblPH']/tbody//tr/td[5]//text()")
    #                     Status = response.xpath("//table[@id='tblPH']/tbody//tr/td[6]//text()")
    #                     Remark = response.xpath("//table[@id='tblPH']/tbody//tr/td[7]//text()")
    #                     print('Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark:',Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
    #                     if not self.cur.execute("select * from Standardlife_Premium where Policy_Num='" + Policy_Num + "' and Spider_Date='" + Spider_Date + "';"):
    #                         for Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark in zip(Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark):
    #                             print(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
    #                             # self.try_except(self.cur.execute("delete from StandardLife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + Payment_date + "';"))
    #                             self.try_except(self.cur.execute("insert into Standardlife_Premium(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,Payment_date,self.date_to_num(Premium_due_Date),Payment_Method,Policy_Currency,Premium,Status,Remark)))
    #                     # 搞定其中一个保单号
    #                     # driver.close()
    #                     # driver.switch_to.window(driver.window_handles[0])
    #                     self.mysql_client.commit()
    #                     print('commited.')
    #                 except Exception as e:
    #                     print('error!:',e)
    #             # self.cur.close()
    #             # 登出
    #             self.wait_until(driver=driver, platform='standard_life', selector_name="//li[@class='globalCustomerLogin']/a/img")
    #             print(username,Policy_Num,':Logout')
    #             # 删除所有cookies，以便下个用户登录
    #             driver.delete_all_cookies()
    #             # 单击登出
    #
    #         except Exception as e:
    #             print(str(Policy_Num) + str(self.riskType), e,'：error!调仓失败！')
    #             # 登出
    #             # self.wait_until(driver=driver, platform='standard_life',selector_name="//li[@class='globalCustomerLogin']/a/img")
    #             # print(Policy_Num, ':Logout')
    #             # self.random_sleep(60,61)
    #             # continue
    #             # self.error = 1
    #             # driver.save_screenshot('调仓失败截图文件夹/standard_life/' + str(Policy_Num) + str(self.riskType) + ".png")
    #             # print(Policy_Num, '失败调仓截图中')
    #             # self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
    #             # if len(driver.window_handles) >= 2:
    #             #     driver.switch_to.window(driver.window_handles[1])
    #             #     driver.close()
    #             # driver.switch_to.window(driver.window_handles[0])
    #             # driver.quit()
    #     driver.quit()
    #     self.mysql_client.close()

    def standard_life_spider(self, standard_life):
        """
        standard_life_spider调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        # standard_life = [(39970, "nan", 'albertzhou', 'zhoulu2011'), (47220, "nan", 'QueenieLuo', '12345678'), (45319, "nan", 'liuql', '789654'), (49168, "nan", 'Xiesi130', '840130abc'), (41063, "nan", 'sunna', '123456'), (46070, "nan", 'polin82082', 'tan3708026'), (38849, "nan", 'joles', '123123'), (42322, "nan", 'PANPEI', 'IPSOS1234'), (50829, "nan", 'gskmwj', '87390635'), (39429, "nan", 'tagichan', 'rika1217'), (46837, "nan", '2423569', '123qwe'), (44111, "nan", 'luohuiou', '080160'), (45381, "nan", 'zhoujy', 'gzrbzjy'), (44805, "nan", 'hwbinboy', '23290778Hzy'), (48663, "nan", 'AJIAO', 'HK6q8080'), (48440, "nan", 'yuanna1981', 'Gd87787439'), (28958, "nan", 'zhang28958', 'qwr0935'), (48396, "nan", 'fanchen94', 'fanchen94'), (50560, "nan", 'bubuzcp', '006136lsm'), (50010, "nan", 'zhouzhihui', '731230'), (39976, "nan", 'yin39976', '19870519'), (33435, "nan", 'chen33435', 'jian1234'), (40228, "nan", 'liang40228', '19870807'), (42224, "nan", 'yangyang66', '28784458'), (48588, "nan", 'hongrong', 'chr2012'), (36523, "nan", 'lege0322', '460725'), (50556, "nan", 'longkai77', '404767116'), (50557, "nan", 'xiaojie77', '404767116'), (45448, "nan", 'Janney', '1343033294'), (44537, "nan", 'longlele', '19850516'), (44893, "nan", 'lixiuwen', '19840229'), (42046, "nan", 'joyce008', 'wu831422'), (44544, "nan", 'zhangwl', '19841012'), (39879, "nan", 'juntim', 'juntim123'), (46654, "nan", 'chenguobo', '04170619'), (41933, "nan", 'szetohl', 'szetohl137'), (39424, "nan", 'tanhuizhi', '52tanhzsl'), (38933, "nan", 'clzsu', 'czz816'), (49256, "nan", 'hrchao18', 'Tutu18'), (42047, "nan", 'azhuzhu', 'echo1022'), (43072, "nan", 'jingjing', 'hq800513'), (31361, "nan", 'xu31361', '123514meng'), (42279, "nan", 'teresaH', 'Aimi0410'), (41655, "nan", 'xu41655', 'ting1234'), (30256, "nan", 'liang30256', '630913'), (31362, "nan", 'wang31362', 'wqy660912'), (52270, "nan", 'lujunfeng', '19831109'), (42039, "nan", 'azhuzhu', 'echo1022'), (46978, "nan", 'moringsing', 'lw771219'), (47846, "nan", 'sophy', 'sophy123'), (44545, "nan", 'heqina', 'qinahe'), (44536, "nan", 'wuqiyun', 'zoewuqiyun'), (42114, "nan", 'vixen_xu', '147852'), (49135, "nan", 'qiuqu', '19740820'), (48414, "nan", 'yao198001', 'xilin2011'), (47692, "nan", 'yuekui', '770805chen'), (47847, "nan", 'yayapay', 'taodan2523'), (48485, "nan", 'guo197909', 'yuguo197909'), (47693, "nan", 'timye2012', 'yihk0611'), (48094, "nan", 'yang198009', 'Ylpy2010'), (47655, "nan", 'ccpig_0504', '820504'), (47665, "nan", 510121, '510121'), (50447, "nan", 'mandymd', 'Mp3210'), (49655, "nan", 'Mws1124', 'Welsa1124'), (52569, "nan", 'hanhoumei', 'ly975331'), (52664, "nan", 'doublel', 'liangliang'), (52668, "nan", '00052668', '22op00'), (53007, "nan", 'HUANGHAO', 'HUANGHAO62'), (53010, "nan", '34118590', '11082011'), (53246, "nan", 'beansmile', 'han783xiao'), (53009, "nan", 'zlij123', 'zlij1225'), (54426, "nan", '00054426', '0054426'), (55228, "nan", 'lixc1112', '19790718'), (55229, "nan", '14739427', 'wangjing'), (55445, "nan", 'zhangshx', 'W0i7s2x4h'), (55878, "nan", 'yuanziming', '19730312'), (55954, "nan", 'aimee5127', 'Bear0526'), (56615, "nan", 'pengliushe', 'Sl19770424'), (56379, "nan", 'CHENLJ0313', 'jing7lc9'), (56378, "nan", '00056378', '19850928'), (56663, "nan", 'zeng1982', 'szy2011'), (57116, "nan", 'wlqiong', '980324wlq'), (57030, "nan", 'zhuyin1977', '20081210'), (56565, "nan", 'lilili2013', 'lilili2013'), (57148, "nan", 'purplestar', 'xiyan1981'), (57431, "nan", 'fangwei8', 'fangwei88'), (58342, "nan", 'leoyou2003', '290612'), (58445, "nan", 'tt0528', '87588599'), (58446, "nan", 'f19770321', '731218'), (58669, "nan", 'lynibm111', 'lyn7536'), (59008, "nan", 'chenying22', '19780202'), (59196, "nan", 'james＿guan', 'Guan2345'), (59197, "nan", 'zhoujy', 'gzrbzjy'), (59198, "nan", 'SEChen', 'aws7890'), (59443, "nan", 'XY645639', 'PASS6456'), (59199, "nan", 'michael22', 'yolanda26'), (59627, "nan", 'grapefunny', 'fgf510290'), (30792, "nan", 'LHY1975', 'liu0121'), (60050, "nan", 'ada0564', 'ada1101'), (59765, "nan", 'bobbychen', 520102), (59858, "nan", 'yukinben', 'uASl201309'), (59766, "nan", 'zjhlang', '99sped6'), (61253, "nan", 'aileen0302', 'aileen0302'), (60897, "nan", 'wangjin', 'haoyu0314'), (62625, "nan", 'chuntian', '2008007007'), (63041, "nan", 'edison2014', 'Edison2016'), (62977, "nan", 'chenjingwe', 'Gaojing106'), (63137, "nan", 'xgbb', 'xgbb197076'), (63138, "nan", 'czc', '51766gd'), (62851, "nan", 'cjianming', 'cjm1984'), (63393, "nan", 'mandy901', 'mandy901'), (63548, "nan", 'xianyuhui', 'Xianyuhui5'), (63563, "nan", 'zhangli920', '0704zlzzq'), (63576, "nan", 'HUANGHAO', 'HUANGHAO62'), (63597, "nan", 'xuhuixian', 'xu775532'), (63598, "nan", 'Rachel1985', 'Rachel1234'), (63596, "nan", 'candyxuqin', 'XUHU880728'), (63638, "nan", 'moonyfox', 'Wanghui28'), (56031, "nan", 'jadewang', 'Hkfs0601')]
        # standard_life = [(48663, "nan", 'AJIAO', 'HK6q8080'), (47692, "nan", 'yuekui', '770805chen')]
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
                    "//span[@id='lbPVSContribution']//text()")) if standard_detail_response.xpath(
                    "//span[@id='lbPVSContribution']") else ''
                Total_withdrawal = ''.join(standard_detail_response.xpath(
                    "//span[@id='lbPVSWithdrawals']//text()")) if standard_detail_response.xpath(
                    "//span[@id='lbPVSWithdrawals']") else ''
                Payment_Frequency = ''.join(standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIPayFeq']//text()")) if standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIPayFeq']") else ''
                Regular_Premium = ''.join(standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIContribution']//text()")) if standard_detail_response.xpath(
                    "//span[@id='pay_info_lbPIContribution']") else ''
                print('Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium:',Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)
                if not self.cur.execute("select * from Standardlife_Premium_Info where Policy_Num='" + Policy_Num + "' and Spider_Date='"+Spider_Date+"';"):
                    # self.try_except(self.cur.execute("delete from standardlife_premium_info where Policy_Num='" + Policy_Num + "';"))
                    self.try_except(self.cur.execute("insert into Standardlife_Premium_Info(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium) VALUES(%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)))

                # 未来供款
                titles = standard_detail_response.xpath(
                    "//div[@class='largeSizeHolder1000']/div/span[@class='h2']//text()")
                print(titles)
                for index, title in enumerate(titles):
                    if '戶口' in title:
                        length = len(standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@id='Table_Alloc']//tr/td[3]"))
                        Investment_Account0 = str(re.sub("\D", "", title))
                        Investment_Account = [Investment_Account0[:2]] * length
                        Date = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][5]//text()")[
                            0] if standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][5]") else ''
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

                        Fund_Name = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][1]//text()")
                        Reference_Code = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][2]//text()")
                        Currency = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][3]//text()")
                        Unit = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][4]//text()")
                        Price = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][6]//text()")
                        Weight = standard_detail_response.xpath("//div[@class='largeSizeHolder1000'][" + str(
                            index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][7]//text()")
                        Value_In_Fund_Currency = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][8]//text()")
                        Value_In_Policy_Currency = standard_detail_response.xpath(
                            "//div[@class='largeSizeHolder1000'][" + str(
                                index) + "]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][9]//text()")

                        print('Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency:',Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                        if not self.cur.execute("select * from Standardlife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date +  "';"):
                            # self.try_except(self.cur.execute("delete from StandardLife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "' and Spider_Date='" + Spider_Date + "';"))
                            for Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency in zip(Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency):
                                print(Policy_Num,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                                self.try_except(self.cur.execute("insert into Standardlife_Account_Allocation(Policy_Num,Spider_Date,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (Policy_Num,Spider_Date,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)))

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
                if not self.cur.execute("select * from Standardlife_Premium where Policy_Num='" + Policy_Num + "' and Spider_Date='" + Spider_Date + "';"):
                    for Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark in zip(Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark):
                        print(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
                        # self.try_except(self.cur.execute("delete from StandardLife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + Payment_date + "';"))
                        self.try_except(self.cur.execute("insert into Standardlife_Premium(Policy_Num,Spider_Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Spider_Date,Payment_date,self.date_to_num(Premium_due_Date),Payment_Method,Policy_Currency,Premium,Status,Remark)))
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

    def axa_spider(self, axa):
        """
        axa调仓操作
        :param axa: axa data list
        :return: operating
        """
        # axa = [('503-8634308', "nan", 1227237, 'Chenxy11'), ('503-8697354', "nan", 1228279, 'Ajiao808'), ('503-8776281', "nan", '1233918', 'Abcd1234'), ('503-8787833', "nan", '1261535', 'Cody1234'), ('504-6213954', "nan", '1241719', 'Xp198307'), ('504-6248463', "nan", 1242981, 'ZHsh8109'), ('504-6327358', "nan", '1246636', 'Liml1986'), ('504-6365804', "nan", '1249198', 'YangZJ12'), ('504-6682075', "nan", '1268584', 'Zhuhong8'), ('504-6901178', "nan", 1282023, 'QinFF123'), ('504-6952494', "nan", 1283511, 'Hong0312'), ('504-6963806', "nan", '1283544', 'Huihui20'), ('504-6971056', "nan", '1285092', 'We4in1az'), ('504-7000996', "nan", 1284717, 'Shilin87'), ('504-6952460', "nan", 1284609, 'Sting112'), ('504-7022156', "nan", 1290402, 'ZhTing20'), ('504-7046460', "nan", 1286961, 'Zhanll83'), ('504-7054290', "nan", 1287006, 'Quxinn76'), ('504-7054209', "nan", 1287002, 'Ny198006'), ('504-7079131', "nan", 1294719, 'Zhengb29'), ('504-7089643', "nan", 1289952, 'Hzelin18'), ('504-7103733', "nan", 1290571, 'Luoyuu25'), ('504-7119697', "nan", 1290707, 'Zyanzi92'), ('504-7136857', "nan", 1291966, 'yhWb8532'), ('504-7139281', "nan", 1291564, 'Lang2015'), ('504-7138549', "nan", 1291562, 'Zyfang38'), ('504-7151187', "nan", 1291986, 'Welcome1'), ('504-7160931', "nan", 1293512, 'Zhezhe20'), ('504-7168710', "nan", 1293582, 'Ru234567'), ('504-7189732', "nan", 1293774, 'Zhaow732'), ('504-7203129', "nan", 1294308, 'Geliuu16'), ('504-7202840', "nan", 1297669, 'Jj840308'), ('504-7223465', "nan", 1295855, 'QiangL08'), ('504-7222723', "nan", 1295967, '611310Ma'), ('504-7222673', "nan", 1295850, 'Zhixin50'), ('504-7235303', "nan", 1296401, 'Myao1104'), ('504-7235212', "nan", 1296399, 'Cuihua83'), ('504-7242721', "nan", 1296829, 'Zcongy24'), ('504-7247803', "nan", 1298455, 'Ruo"nan"24'), ('504-7248694', "nan", 1297197, 'Liulie23'), ('504-7266795', "nan", 1298523, 'MIer9220'), ('504-7271548', "nan", 1298128, 'Mm123123'), ('504-7235139', "nan", 1298740, 'He070503'), ('504-7247704', "nan", 1302145, 'Lye1027r'), ('504-7248652', "nan", 1298456, 'Xingzh21'), ('504-7248546', "nan", 1299940, 'Weibing0'), ('504-7260764', "nan", 1298035, 'Xinliu26'), ('504-7264626', "nan", 1298073, 'Xiacui73'), ('504-7266720', "nan", 1301853, 'Yueyue38'), ('504-7270656', "nan", 1298543, 'Wang2345'), ('504-7296503', "nan", 1299607, 'Hzq25125'), ('504-7298699', "nan", 1326723, 'Wgyien23'), ('504-7354567', "nan", 1302448, 'Feng2345'), ('504-7354617', "nan", 1302449, 'Yingyi81'), ('504-7351019', "nan", 1302434, 'Luo23456'), ('504-7350698', "nan", 1302430, 'Fangxu26'), ('504-7350672', "nan", 1302429, 'Jieyan29'), ('504-7350649', "nan", 1302428, 'Yanding8'), ('504-7334536', "nan", 1301759, 'Nc392766'), ('504-7350573', "nan", 1304257, 'Qinqin67'), ('504-7343388', "nan", 1304024, 'Linye720'), ('504-7369185', "nan", 1303882, 'Kehuih08'), ('504-7381503', "nan", 1305241, 'Meimei24'), ('504-7381529', "nan", 1304783, 'Xz130221'), ('504-7417042', "nan", 1306485, 'Yingiu48'), ('504-7416952', "nan", 1307504, 'Panpan04'), ('504-7372064', "nan", 1303892, 'Yanyyu17'), ('504-7443857', "nan", 1307715, 'Yeting15'), ('504-7398762', "nan", 1305297, 'Wang2345'), ('504-7381370', "nan", 1305383, 'Chen2345'), ('504-7391106', "nan", 1305106, 'Jingr513'), ('504-7416002', "nan", 1306230, 'Li234567'), ('504-7427058', "nan", 1310490, 'Qingyu90'), ('504-7438154', "nan", 1307587, 'Jingl758'), ('504-7443345', "nan", 1307699, 'Zhchi699'), ('504-7442347', "nan", 1308603, 'Zchunj03'), ('504-7447312', "nan", 1307779, 'Deyiyi79'), ('504-7478705', "nan", 1308844, 'Yingyy44'), ('504-7478820', "nan", 1309064, 'Guyue088'), ('504-7478630', "nan", 1308843, 'Renhui43'), ('504-7478861', "nan", 1308847, 'MGlym369'), ('504-7477541', "nan", 1309992, 'Tongxz92'), ('504-7493365', "nan", 1310018, 'Wengxi18'), ('504-7486252', "nan", 1312471, 'Mzqing71'), ('504-7493407', "nan", 1309438, 'Meizhi43'), ('504-7500839', "nan", 1309608, 'Yongni39'), ('504-7500813', "nan", 1309607, 'Sanyou88'), ('504-7525257', "nan", 1310525, 'LuoYx525'), ('504-7525539', "nan", 1310531, 'Xiaomei5'), ('504-7525349', "nan", 1310527, 'Xiaxia27'), ('504-7571913', "nan", 1311150, 'Jingli50'), ('504-7577506', "nan", 1310681, 'Butrat76'), ('504-7577357', "nan", 1310678, 'Lulu0130'), ('504-7597629', "nan", 1311422, 'Limin422'), ('504-7632376', "nan", 1312642, 'Haochen2'), ('504-7630230', "nan", 1312610, 'Xinxin26'), ('504-7641427', "nan", 1313052, 'Zhmiao24'), ('504-7645402', "nan", 1313393, 'Fang0926'), ('504-7653737', "nan", 1314338, 'Xueqin33'), ('504-7653562', "nan", 1315105, 'Xieff105'), ('504-7653422', "nan", 1314626, 'Zhymeg56'), ('504-7653976', "nan", 1313492, 'Axa12345'), ('504-7653893', "nan", 1313488, 'Xiaofu59'), ('504-7675656', "nan", 1314143, 'Leilei43'), ('504-7676647', "nan", 1315602, 'Wlimei47'), ('504-7676829', "nan", 1314653, 'Tglili53'), ('504-7692156', "nan", 1315616, 'Wruyin16'), ('504-7707921', "nan", 1316223, 'Wxjg0722'), ('504-7707897', "nan", 1316222, 'Lcyao330'), ('504-7724520', "nan", 1315988, 'ZLwen988'), ('504-7724504', "nan", 1315984, 'Chent984'), ('504-7724454', "nan", 1315985, 'Chent985'), ('504-7724561', "nan", 1316587, 'Lj810123'), ('504-7739007', "nan", 1317776, 'Zhjyu815'), ('504-7748552', "nan", 1317454, 'Hxjing16'), ('504-7748750', "nan", 1317458, 'Lliyuan8'), ('504-7748719', "nan", 1317457, 'Cxumin17'), ('504-7748511', "nan", 1317452, 'Lntgfu52'), ('504-7754014', "nan", 1318217, '54022Wjt'), ('504-7761464', "nan", 1318359, 'Wweii412'), ('504-7797393', "nan", 1319949, 'LYLin112'), ('504-7812895', "nan", 1320573, 'Kesc1964'), ('504-7825194', "nan", 1321537, 'Zctao537'), ('504-7897722', "nan", 1325531, 'Belle616'), ('504-7905095', "nan", 1325102, 'Xyun5095'), ('504-7917884', "nan", 1325890, 'Lishn884'), ('504-7941389', "nan", 1326928, 'Zjping28'), ('504-7945117', "nan", 1326957, 'Ysyuan57'), ('504-7963813', "nan", 1327403, 'MJ520lyg'), ('504-7963961', "nan", 1328096, 'Chenxl61'), ('504-7985170', "nan", 1327990, 'Wjing990'), ('504-7985162', "nan", 1327989, 'Kjfeng62'), ('504-8009483', "nan", 1328709, 'Ying1226'), ('504-8009533', "nan", 1328710, '156801Zh'), ('504-8035355', "nan", 1329861, 'Lin00610'), ('504-8035900', "nan", 1333208, 'Zyf85127'), ('504-8049281', "nan", 1330935, 'Gujj0935'), ('504-8076524', "nan", 1331297, 'Zhch1297'), ('504-8239171', "nan", 1335231, 'Hmxg9171'), ('504-8303498', "nan", 1339176, 'Wangh176'), ('504-8314172', "nan", 1337690, 'Zhhh7690'), ('504-8372204', "nan", 1340768, 'Xhjuan68'), ('504-8372196', "nan", 1340767, 'Xujj0126'), ('504-8431679', "nan", 1349553, 'DEyy1103'), ('504-8431737', "nan", 1342377, '870914Zh'), ('504-8440183', "nan", 1349554, 'Qiminw83'), ('504-8480700', "nan", 1349889, 'Yanghy10'), ('504-6365671', "nan", 1253922, 'Etihad12')]
        if not axa:
            print('axa无需调仓的保单！')
            return
        # 打开Chrome浏览器登录
        axa_login_url = 'https://www1.e-axa.com.hk/Life/login.do;jsessionid=YXdVhXxcCY9pdFNPlYVyzwpTv9Jkr9pg0BSZ7b39nG6v0n868yCj!31778653?methodName=login'
        axa_policy_url = 'https://www1.e-axa.com.hk/Life/policyLinkage.do?methodName=getPolicyLinkage'
        axa_payment_url = 'https://www1.e-axa.com.hk/Life/displayPaymentDetails.do?methodName=displayPaymentDetails'
        axa_acount_url = 'https://www1.e-axa.com.hk/Life/displayAccountValue.do?methodName=displayAccountValue'
        axa_logout_url = 'https://www1.e-axa.com.hk/Life/logout.do?methodName=logout'


        for index, item in enumerate(axa):
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                username = str(item[2])
                password = str(item[3])
                # headers、formdata
                axa_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Content-Length": "33",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Cookie": "JSESSIONID=YXdVhXxcCY9pdFNPlYVyzwpTv9Jkr9pg0BSZ7b39nG6v0n868yCj!31778653; AACOKIAQ=!411Ft5lqNsNTrL76ck1ujqT7OOpxHs17nckt+oxUAtg1Wo09gKk9UxM7wvpNMZsGwNP/x5XvTgQuQY6rd+z67Kpog7UemzmQ+t7MDaPC2rbKZqZlfeU6c7a9n5f/eY2PoXKPw/eqZwiHL5CwPaZ7NPFRmrMojzOgjm0o+d/N6sh7HiUM1rSHo204HDUwgQr0fL2x",
                    "Host": "www1.e-axa.com.hk",
                    "Origin": "https://www1.e-axa.com.hk",
                    "Referer": "https://www1.e-axa.com.hk/Life/changeLocale.do?methodName=changeLocale&language=zh&country=HK",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
                }
                axa_data = {
                    "loginID": username,
                    "password": password,
                }
                ssion_policy_data = {
                    "pagination_mode": "FIRST",
                    "isFirstPage": "true",
                    "isLastPage": "true",
                    "pageIndex": "1",
                    "policyRequest.lang": "zh_HK",
                    "policyRequest.appCode": "CSSC",
                    "policyRequest.page": "/jsp/policy/displayContactInfo.jsp",
                    "policyRequest.webItemID": "2",
                    "policyRequest.needBasicInfo": "true",
                    "policyRequest.policyNo": self.policyNumber,
                    "policyListRequest.sortColumnInAsc": "false",
                    "policyListRequest.sortByColumnName": "policyNo"
                }
                ssion_payment_data = {
                    "policyRequest.policyNo": self.policyNumber,
                    "policyRequest.appCode": "CSSC",
                    "policyRequest.page": "/jsp/policy/displayPaymentDetails.jsp",
                    "policyRequest.webItemID": "7",
                    "policyRequest.needBasicInfo": "false"
                }
                ssion_acount_data = {
                    "policyRequest.policyNo": self.policyNumber,
                    "policyRequest.appCode": "CSSC",
                    "policyRequest.page": "/jsp/policy/displayAccountValue.jsp",
                    "policyRequest.webItemID": "6",
                    "policyRequest.needBasicInfo": "false"
                }
                ssion_logout_data = {
                    "methodName":"logout"
                }
                print('-----------------')
                ssion = requests.session()
                response = ssion.post(url=axa_login_url, headers=axa_headers, data=axa_data)
                # print(response.text)
                if 'Welcome,' in response.text:
                    print(username,'登录成功')
                else:
                    print(self.policyNumber,'登录失败')
                    continue
                # 点击保单号
                response1 = ssion.post(axa_policy_url,data=ssion_policy_data)
                print('policyNumber:',self.policyNumber)
                time.sleep(2)
                # 点击Payment
                payment_html = ssion.post(url=axa_payment_url,data=ssion_payment_data)
                # print(payment_html.text)
                response = etree.HTML(payment_html.text)
                Spider_Date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                Payment_Frequency = ''.join(response.xpath("//table[3]//tr[1]/td/b//text()"))  # 2
                Regular_Premium = ''.join(response.xpath("//table[3]//tr[3]/td/b//text()")).strip().replace(' ', '').replace('\t','').replace('\n','')  # 2
                Last_Premium = ''.join(response.xpath("//table[6]//tr[2]/td/b//text()")).strip().replace(' ', '').replace('\t','').replace('\n','')  # 5
                Last_Premium_Date = self.date_to_num(''.join(response.xpath("//table[6]//tr[3]/td/b//text()")))  # 5
                Information_Date = self.date_to_num(''.join(response.xpath("//table[9]//font[@class='txtNote']//text()"))[-10:])  # 9
                print('Spider_Date,Payment_Frequency,Regular_Premium,Last_Premium,Last_Premium_Date,Information_Date:',
                      Spider_Date, Payment_Frequency, Regular_Premium, Last_Premium, Last_Premium_Date,
                      Information_Date)
                if not self.cur.execute("select * from AXA_Premium where Policy_Num='" + self.policyNumber + "' and Spider_Date='" + Spider_Date + "';"):
                    # self.try_except(self.cur.execute("delete from AXA_Premium where Policy_Num='" + self.policyNumber + "';"))
                    self.try_except(self.cur.execute("insert into AXA_Premium(Policy_Num,Spider_Date,Payment_Frequency,Regular_Premium,Last_Premium,Last_Premium_Date,Information_Date) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (self.policyNumber,Spider_Date,Payment_Frequency,Regular_Premium,Last_Premium,Last_Premium_Date,Information_Date)))

                time.sleep(2)
                # 点击Acount
                acount_html = ssion.post(url=axa_acount_url,data=ssion_acount_data)
                # print(acount_html.text)
                response = etree.HTML(acount_html.text)
                # print(response.text)
                # 时间
                response.xpath("//table[3]//span/b//text()")
                # 最初账户基金名   # 5
                Account_Type = '01'
                Date = self.date_to_num(''.join(response.xpath("//table[2]//tr[3]/td/span/b//text()"))[-10:])
                Fund_Name_01 = response.xpath("//table[4]//td[@class='cellGrey'][1]//text()")
                Allocation_01 = response.xpath("//table[4]//td[@class='cellGrey'][2]//text()")
                Fund_Bid_Price_Currency_01 = response.xpath("//table[4]//td[@class='cellGrey'][3]//text()")
                Fund_Bid_Price_01 = response.xpath("//table[4]//td[@class='cellGrey'][4]//text()")
                Unit_01 = response.xpath("//table[4]//td[@class='cellGrey'][5]//text()")
                Fund_Currency_01 = response.xpath("//table[4]//td[@class='cellGrey'][6]//text()")
                Value_In_Fund_Currency_01 = response.xpath("//table[4]//td[@class='cellGrey'][7]//text()")
                Policy_Currency_01 = response.xpath("//table[4]//td[@class='cellGrey'][8]//text()")
                Value_In_Policy_Currency_01 = response.xpath("//table[4]//td[@class='cellGrey'][9]//text()")
                print(Account_Type, Date, Fund_Name_01, Allocation_01, Fund_Bid_Price_Currency_01, Fund_Bid_Price_01,
                      Unit_01, Fund_Currency_01, Value_In_Fund_Currency_01, Policy_Currency_01,
                      Value_In_Policy_Currency_01)
                if not self.cur.execute("select * from AXA_Account_Allocation where Policy_Num='" + self.policyNumber + "' and Spider_Date='" + Spider_Date + "' and Account_Type='01';"):
                    for Fund_Name_01, Allocation_01, Fund_Bid_Price_Currency_01, Fund_Bid_Price_01,Unit_01, Fund_Currency_01, Value_In_Fund_Currency_01, Policy_Currency_01,Value_In_Policy_Currency_01 in zip(Fund_Name_01, Allocation_01, Fund_Bid_Price_Currency_01, Fund_Bid_Price_01,Unit_01, Fund_Currency_01, Value_In_Fund_Currency_01, Policy_Currency_01,Value_In_Policy_Currency_01):
                        self.try_except(self.cur.execute("insert into AXA_Account_Allocation(Policy_Num,Spider_Date, Date, Account_Type, Fund_Name, Allocation, Fund_Bid_Price_Currency, Fund_Bid_Price,Unit, Fund_Currency, Value_In_Fund_Currency, Policy_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (self.policyNumber,Spider_Date, Date, Account_Type, Fund_Name_01, Allocation_01, Fund_Bid_Price_Currency_01, Fund_Bid_Price_01,Unit_01, Fund_Currency_01, Value_In_Fund_Currency_01, Policy_Currency_01,Value_In_Policy_Currency_01)))

                # 累计账户基金名   # 7
                Account_Type = '02'
                Fund_Name_02 = response.xpath("//table[6]//td[@class='cellGrey'][1]//text()")
                Allocation_02 = response.xpath("//table[6]//td[@class='cellGrey'][2]//text()")
                Fund_Bid_Price_Currency_02 = response.xpath("//table[6]//td[@class='cellGrey'][3]//text()")
                Fund_Bid_Price_02 = response.xpath("//table[6]//td[@class='cellGrey'][4]//text()")
                Unit_02 = response.xpath("//table[6]//td[@class='cellGrey'][5]//text()")
                Fund_Currency_02 = response.xpath("//table[6]//td[@class='cellGrey'][6]//text()")
                Value_In_Fund_Currency_02 = response.xpath("//table[6]//td[@class='cellGrey'][7]//text()")
                Policy_Currency_02 = response.xpath("//table[6]//td[@class='cellGrey'][8]//text()")
                Value_In_Policy_Currency_02 = response.xpath("//table[6]//td[@class='cellGrey'][9]//text()")

                print(Account_Type, Date, Fund_Name_02, Allocation_02, Fund_Bid_Price_Currency_02, Fund_Bid_Price_02,
                      Unit_02, Fund_Currency_02, Value_In_Fund_Currency_02, Policy_Currency_02,
                      Value_In_Policy_Currency_02)
                if not self.cur.execute("select * from AXA_Account_Allocation where Policy_Num='" + self.policyNumber + "' and Date='" + Date + "' and Account_Type='02';"):
                    for Fund_Name_02, Allocation_02, Fund_Bid_Price_Currency_02, Fund_Bid_Price_02,Unit_02, Fund_Currency_02, Value_In_Fund_Currency_02, Policy_Currency_02,Value_In_Policy_Currency_02 in zip(Fund_Name_02, Allocation_02, Fund_Bid_Price_Currency_02, Fund_Bid_Price_02,Unit_02, Fund_Currency_02, Value_In_Fund_Currency_02, Policy_Currency_02,Value_In_Policy_Currency_02):
                        self.try_except(self.cur.execute("insert into AXA_Account_Allocation(Policy_Num,Spider_Date,Date,Account_Type,Fund_Name, Allocation, Fund_Bid_Price_Currency, Fund_Bid_Price,Unit, Fund_Currency, Value_In_Fund_Currency, Policy_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                            (self.policyNumber,Spider_Date, Date, Account_Type, Fund_Name_02, Allocation_02, Fund_Bid_Price_Currency_02, Fund_Bid_Price_02,Unit_02, Fund_Currency_02, Value_In_Fund_Currency_02, Policy_Currency_02,Value_In_Policy_Currency_02)))
                self.mysql_client.commit()
                print('commited.')
                # 点击登出
                logout_html = ssion.post(url=axa_logout_url, data=ssion_logout_data)
                time.sleep(2)

            except Exception as e:
                print(str(self.policyNumber), '：error!调仓失败！',e)

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

