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
        self.excel_name = 'Excel/ClientSwitch ' + str(input("请输入需要调仓的Excel表格年月，如 201712：")) + '.xls'
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
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                            database='data_finance_oversea', charset='utf8')
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

    def hansard_operation(self, Hansard):
        """
        Hansard调仓操作
        :param Hansard: Hansard data list
        :return: Operating
        """
        if not Hansard:
            print('Hansard无需调仓的保单！')
            return
        # 检查是否够钟落班
        self.check_workoff()
        # 打开Chrome浏览器登录
        url = "https://ho.hftrust.com/CookieAuth.dll?GetLogon?curl=Z2F&reason=0&formdir=9"
        # username = 'cess15035'  # 领导的
        username = 'ernc15035'  # 老细的
        # 登录，输入6位动态数字密码：
        # password = 'yuwin' + str(input("请输入Hansard的6位登录动态数字密码："))     # 领导的
        password = 'fizz' + str(input("请输入Hansard的6位登录动态数字密码："))  # 老细的
        username_id = "username"
        password_id = "passcode"
        submit_id = "SubmitCreds"
        driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
        # 0.进入调仓页面：
        self.random_sleep()
        driver.maximize_window()
        self.wait_until(driver=driver, selector_name="//div[@id='container']//div[@class='section']/ul[1]/li/a")
        # driver.find_element_by_xpath("//div[@id='container']//div[@class='section']/ul[1]/li/a").click()
        # 1.取出excel的数据进行输入Hansard调仓：
        for index, item in enumerate(Hansard):
            # 检查是否够钟落班
            self.check_workoff()
            self.enum_index = index
            self.error = 0
            self.operation_counts += 1
            try:
                # 保单号
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = int(round(float(item[1]) * 100))
                # 风险类型
                self.riskType = str(item[2])
                # 输入保单号
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//div[@class='col'][1]/input", action='clear')
                self.wait_until(driver=driver, selector_name="//div[@class='col'][1]/input", action='send_keys',
                                send_keys=self.policyNumber)
                self.random_sleep()
                # 点击Search
                driver.find_element_by_class_name("submit").click()
                # # print(driver.current_url)
                self.random_sleep()
                # 切换到后台渲染源码页面
                try:
                    driver.switch_to.frame('Display')
                except:
                    print('switch_to.frame==error!')

                self.random_sleep()
                # 鼠标移动到保单号处
                self.wait_until(driver=driver,
                                selector_name="//tr[@id='resultsRow0']/td[1]/a[@id='resultsRow0Enabled']")

                driver.implicitly_wait(1)
                self.random_sleep()
                # 进入到调仓界面
                self.wait_until(driver=driver, selector_name="//div[@id='cluetip-inner']//p[@id='ofs0']")
                # print(driver.window_handles)
                # 切换到新窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[1])
                self.random_sleep()
                driver.maximize_window()
                # 选择需要卖出的基金
                self.wait_until(driver=driver,
                                selector_name="//div[@class='container'][1]//div[@class='col switch middle'][1]//div[@class='vertcenter']//div[@id='uniform-C04S2']")

                self.random_sleep()

                # 点击switchSelection
                self.wait_until(driver=driver, selector_name="//span[@class='switchSelection link']/a")

                self.random_sleep()

                # 输入卖出比例
                self.wait_until(driver=driver, selector_name="//thead//input[@id='changePercentage']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//thead//input[@id='changePercentage']",
                                action='send_keys', send_keys=self.sellingPercent)

                self.random_sleep()
                # 风险属性对应的卖出比例判断：
                MC173S2 = 47 if self.riskType == '增长型' else 41
                MC186S2 = 18 if self.riskType == '增长型' else 12
                MC217S2 = 12 if self.riskType == '增长型' else 12
                MC178S2 = 23 if self.riskType == '增长型' else 35
                # 先填比例，后选基金。如此重复四遍①：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']",
                                action='send_keys', send_keys=MC173S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']",
                                action='send_keys', send_keys='MC173S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[1]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)
                # 先填比例，后选基金。如此重复四遍②：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']",
                                action='send_keys', send_keys=MC186S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']",
                                action='send_keys', send_keys='MC186S2')
                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[2]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍③：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']",
                                action='send_keys', send_keys=MC217S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']",
                                action='send_keys', send_keys='MC217S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[3]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍④：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']",
                                action='send_keys', send_keys=MC178S2)

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']",
                                action='send_keys', send_keys='MC178S2')

                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[4]/li[@class='ui-menu-item']/a[1]")
                # driver.find_element_by_xpath("//ul[4]/li[@class='ui-menu-item']/a[1]").click()
                self.random_sleep()
                driver.implicitly_wait(2)
                # 点击Agree：
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")

                # 点击Continue：
                self.random_sleep()
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")
                self.random_sleep()

                # 点击Comfirm：
                self.random_sleep()
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")
                self.random_sleep()
                driver.implicitly_wait(2)

                # 获取调仓完成的页面截图：
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot(
                        '成功调仓截图文件夹/Hansard/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    # self.policy_index = self.Hansard_index[index]
                    self.write_excel(policy_index=self.Hansard_index[index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                self.random_sleep()
                # 关闭当前窗口
                driver.close()
                self.random_sleep()
                # 切换到原窗口，继续调下一个保单号
                driver.switch_to.window(driver.window_handles[0])
                self.random_sleep()
                # 后退
                driver.back()
                # 循环调仓。
            except:
                print('hansard---')
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/Hansard/' + str(self.policyNumber) + str(self.riskType) + ".png")
                self.write_excel(policy_index=self.Hansard_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) < 2:
                    # 刷新
                    driver.refresh()
                    self.random_sleep()
                else:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    # 切换到原窗口，继续调下一个保单号
                    driver.switch_to.window(driver.window_handles[0])
                    self.random_sleep()
                    # 后退
                    driver.back()
                self.random_sleep()

        print('Hansard调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # 关闭浏览器
        driver.quit()

    def hansard_operation_emergency(self, Hansard):
        """
        Hansard调仓操作
        :param Hansard: Hansard data list
        :return: Operating
        """
        if not Hansard:
            print('Hansard无需调仓的保单！')
            return
        # 检查是否够钟落班
        self.check_workoff()
        # 打开Chrome浏览器登录
        url = "https://ho.hftrust.com/CookieAuth.dll?GetLogon?curl=Z2F&reason=0&formdir=9"
        # username = 'cess15035'  # 领导的
        username = 'ernc15035'  # 老细的
        # 登录，输入6位动态数字密码：
        # password = 'yuwin' + str(input("请输入Hansard的6位登录动态数字密码："))     # 领导的
        password = 'fizz' + str(input("请输入Hansard的6位登录动态数字密码："))  # 老细的
        username_id = "username"
        password_id = "passcode"
        submit_id = "SubmitCreds"
        driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
        # 0.进入调仓页面：
        self.random_sleep()
        driver.maximize_window()
        self.wait_until(driver=driver, selector_name="//div[@id='container']//div[@class='section']/ul[1]/li/a")
        # driver.find_element_by_xpath("//div[@id='container']//div[@class='section']/ul[1]/li/a").click()
        # 1.取出excel的数据进行输入Hansard调仓：
        for index, item in enumerate(Hansard):
            # 检查是否够钟落班
            self.check_workoff()
            self.enum_index = index
            self.error = 0
            self.operation_counts += 1
            try:
                # 保单号
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = int(round(float(item[1]) * 100))
                # 风险类型
                self.riskType = str(item[2])
                # 输入保单号
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//div[@class='col'][1]/input", action='clear')
                self.wait_until(driver=driver, selector_name="//div[@class='col'][1]/input", action='send_keys',
                                send_keys=self.policyNumber)
                self.random_sleep()
                # 点击Search
                driver.find_element_by_class_name("submit").click()
                # # print(driver.current_url)
                self.random_sleep()
                # 切换到后台渲染源码页面
                try:
                    driver.switch_to.frame('Display')
                except:
                    print('switch_to.frame==error!')

                self.random_sleep()
                # 鼠标移动到保单号处
                self.wait_until(driver=driver,
                                selector_name="//tr[@id='resultsRow0']/td[1]/a[@id='resultsRow0Enabled']")

                driver.implicitly_wait(1)
                self.random_sleep()
                # 进入到调仓界面
                self.wait_until(driver=driver, selector_name="//div[@id='cluetip-inner']//p[@id='ofs0']")
                # print(driver.window_handles)
                # 切换到新窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[1])
                self.random_sleep()
                driver.maximize_window()
                # 把当前持有的所有基金卖出，点击“Switch all”
                self.wait_until(driver=driver,selector_name="//a[@id='switchAll']")
                self.random_sleep()

                self.random_sleep()
                # self.wait_until(driver=driver, selector_name="//thead//input[@id='changePercentage']",
                #                 action='send_keys', send_keys=self.sellingPercent)

                self.random_sleep()
                # 风险属性对应的卖出比例判断：
                MC173S2 = 40 if self.riskType == '增长型' else 35
                MC186S2 = 15 if self.riskType == '增长型' else 10
                MC217S2 = 10 if self.riskType == '增长型' else 10
                MC178S2 = 20 if self.riskType == '增长型' else 30
                C04S2 = 15 if self.riskType == '增长型' else 15
                # 先填比例，后选基金。如此重复四遍①：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']",
                                action='send_keys', send_keys=MC173S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']",
                                action='send_keys', send_keys='MC173S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[1]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)
                # 先填比例，后选基金。如此重复四遍②：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']",
                                action='send_keys', send_keys=MC186S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']",
                                action='send_keys', send_keys='MC186S2')
                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[2]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍③：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']",
                                action='send_keys', send_keys=MC217S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']",
                                action='send_keys', send_keys='MC217S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[3]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍④：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']",
                                action='send_keys', send_keys=MC178S2)

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']",
                                action='send_keys', send_keys='MC178S2')

                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[4]/li[@class='ui-menu-item']/a[1]")
                # driver.find_element_by_xpath("//ul[4]/li[@class='ui-menu-item']/a[1]").click()
                self.random_sleep()
                driver.implicitly_wait(2)
                # 先填比例，后选基金。如此重复五遍⑤：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage5']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage5']",
                                action='send_keys', send_keys=C04S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName5']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName5']",
                                action='send_keys', send_keys='C04S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[5]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)
                # 点击Agree：
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")



                # 未来配置，点击“redirectAll”
                self.wait_until(driver=driver,selector_name="//a[@id='redirectAll']")

                self.random_sleep()
                self.random_sleep()

                # 先填比例，后选基金。如此重复四遍①：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage1']",
                                action='send_keys', send_keys=MC173S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName1']",
                                action='send_keys', send_keys='MC173S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[1]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)
                # 先填比例，后选基金。如此重复四遍②：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage2']",
                                action='send_keys', send_keys=MC186S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName2']",
                                action='send_keys', send_keys='MC186S2')
                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[2]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍③：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage3']",
                                action='send_keys', send_keys=MC217S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName3']",
                                action='send_keys', send_keys='MC217S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[3]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复四遍④：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage4']",
                                action='send_keys', send_keys=MC178S2)

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName4']",
                                action='send_keys', send_keys='MC178S2')

                self.random_sleep()

                self.wait_until(driver=driver, selector_name="//ul[4]/li[@class='ui-menu-item']/a[1]")
                # driver.find_element_by_xpath("//ul[4]/li[@class='ui-menu-item']/a[1]").click()
                self.random_sleep()
                driver.implicitly_wait(2)

                # 先填比例，后选基金。如此重复五遍⑤：
                self.wait_until(driver=driver, selector_name="//input[@id='percentage5']", action='clear')

                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='percentage5']",
                                action='send_keys', send_keys=C04S2)
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName5']", action='clear')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//input[@id='fundName5']",
                                action='send_keys', send_keys='C04S2')
                self.random_sleep()
                self.wait_until(driver=driver, selector_name="//ul[5]/li[@class='ui-menu-item']/a[1]")
                driver.implicitly_wait(2)
                # 点击Agree：
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")

                # 点击Continue：
                self.random_sleep()
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")
                self.random_sleep()

                # 点击Comfirm：
                self.random_sleep()
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")
                self.random_sleep()
                driver.implicitly_wait(2)

                # 获取调仓完成的页面截图：
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot(
                        '成功调仓截图文件夹/Hansard/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    # self.policy_index = self.Hansard_index[index]
                    self.write_excel(policy_index=self.Hansard_index[index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                self.random_sleep()
                # 关闭当前窗口
                driver.close()
                self.random_sleep()
                # 切换到原窗口，继续调下一个保单号
                driver.switch_to.window(driver.window_handles[0])
                self.random_sleep()
                # 后退
                driver.back()
                # 循环调仓。
            except:
                print('hansard---')
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/Hansard/' + str(self.policyNumber) + str(self.riskType) + ".png")
                self.write_excel(policy_index=self.Hansard_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) < 2:
                    # 刷新
                    driver.refresh()
                    self.random_sleep()
                else:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    # 切换到原窗口，继续调下一个保单号
                    driver.switch_to.window(driver.window_handles[0])
                    self.random_sleep()
                    # 后退
                    driver.back()
                self.random_sleep()

        print('Hansard调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # 关闭浏览器
        driver.quit()

    def ita_operation(self, ITA):
        """
        ITA调仓操作
        :param ITA: ITA data list
        :return: opearting
        """
        if not ITA:
            print('ITA无需调仓的保单！')
            return
        # 检查是否够钟落班
        self.check_workoff()
        # 打开Chrome浏览器登录
        url = "https://ita.secureaccountaccess.com/Account/Login?ReturnUrl=%2f"
        username = 'sarah'
        password = 'Trussan1105'
        username_id = "UserName"
        password_id = "Password"
        submit_id = "submit-login"
        driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
        driver.maximize_window()
        self.random_sleep()
        self.random_sleep()
        self.random_sleep()
        print('login')
        # 点击前往主页
        self.wait_until(driver=driver, platform='ITA', selector_name="//div[@id='column-1']//div[@class='portlet-body']/a[1]")
        # driver.find_element_by_link_text("前往主页").click()
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, "//div[@class='portlet-body']//a")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath("//div[@class='portlet-body']//a").click()
        print('前往主页')
        self.random_sleep()
        driver.maximize_window()

        # 点击查询
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH,
        #                                         '''//ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a''')))
        # except Exception as e:
        #     print('==============error6================')
        self.random_sleep()
        driver.save_screenshot('test.png')
        print('准备点击查询')
        self.wait_until(driver=driver, platform='ITA',
                        selector_name='''//div[@class='page-container']/div[@id='sideBar']/div[@class='page-sidebar navbar-collapse collapse']/ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a[@id='menu_0']''')
        print('已点击查询')
        # driver.find_element_by_xpath(
        #     '''//div[@class='page-container']/div[@id='sideBar']/div[@class='page-sidebar navbar-collapse collapse']/ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a[@id='menu_0']''').click()
        self.random_sleep()
        # 点击标准查询
        self.wait_until(driver=driver, platform='ITA',
                        selector_name="""//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""")
        # try:
        #     element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH,
        #                                                                                """//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath(
        #     """//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""").click()
        self.random_sleep()
        # 点击计划
        self.wait_until(driver=driver, platform='ITA',
                        selector_name="//div[@class='radio-list']/label[@id='Label_Option2']")
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, "//div[@class='radio-list']/label[@id='Label_Option2']")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath("//div[@class='radio-list']/label[@id='Label_Option2']").click()

        for index, item in enumerate(ITA):
            # 检查是否够钟落班
            self.check_workoff()
            self.operation_counts += 1
            self.error = 0
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = round(float(item[1]) * 100, 2)
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                # 点击输入保单号
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='clear')
                print(self.policyNumber, '点击输入保单号')
                # 输入保单号
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").clear()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='send_keys', send_keys=self.policyNumber)
                print(self.policyNumber, '输入保单号')
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").send_keys(self.policyNumber)
                self.random_sleep()
                # 点击搜寻
                self.wait_until(driver=driver, platform='ITA', selector_name="//button[@id='SearchButton']")
                print(self.policyNumber, '点击搜寻')
                # driver.find_element_by_xpath("//button[@id='SearchButton']").click()
                self.random_sleep()
                # 点击计划号码
                try:
                    element = WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//table[@id='TableReport']//tr[@class='odd']/td[1]/a")))
                except Exception as e:
                    print('==============error6================')
                # self.wait_until(driver=driver,platform='ITA', selector_name="//table[@id='TableReport']//tr[@class='odd']/td[1]/a")
                print(self.policyNumber, '点击计划号码')
                # 切换至新窗口
                policyLink = str(
                    driver.find_element_by_xpath("//table[@id='TableReport']//tr[@class='odd']/td[1]/a").get_attribute(
                        "href"))
                js = 'window.open("' + policyLink + '");'
                driver.execute_script(js)
                # print(driver.window_handles)
                driver.switch_to.window(driver.window_handles[1])
                print(self.policyNumber, '切换至新窗口')
                self.random_sleep()
                driver.maximize_window()
                self.random_sleep(15, 20)
                # 点击主计划
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''')
                print(self.policyNumber, '点击主计划')
                # driver.find_element_by_xpath(
                #     '''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''').click()
                # 点击基金转换&平衡
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='sub-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][3]/a[@id='menu_0']/div[@class='title']''')
                print(self.policyNumber, '点击基金转换&平衡')
                # 勾选基金转换
                self.random_sleep()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//form[@id='Step1']/div[@class='form-body select-option']/div[@class='form-group']/div[@class='radio-list']/label[1]/label")
                print(self.policyNumber, '勾选基金转换')
                # 点击下一个
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='Step1panel']//div[@id='stepsTransferRebalance_1']//div[@class='panel-body form']//form[@id='Step1']//div[@class='form-actions']/input[@type='submit']")
                print(self.policyNumber, '点击下一个')
                self.random_sleep()
                self.random_sleep()
                self.random_sleep()
                # 点击选择基金
                FIDC_index = 100
                try:
                    for i in range(5):
                        text = str(self.wait_until(driver=driver, platform='ITA',
                                                   selector_name="//div[@id='Step2panel']//form[@id='formStep2']/div[@id='searchResult1']/div[@class='table-scroll']//tr[@class='rowSearch'][" + str(
                                                       i + 1) + "]/td[@class='thCol1']/label", action='text'))
                        if text == 'FIDC':
                            FIDC_index = i + 1
                            break
                            # print(FIDC_index)
                except:
                    print('error!!')
                    self.error = 1
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//tr[@class='rowSearch'][" + str(
                                    FIDC_index) + "]/td[@class='thCol12']/a")
                print(self.policyNumber, '点击选择基金')
                # 清除买入比例
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']/div[@class='table-scroll']//tr/td/input",
                                action='clear')
                print(self.policyNumber, '清除买入比例')
                # 填入买入比例
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']/div[@class='table-scroll']//tr/td/input",
                                action='send_keys', send_keys=self.sellingPercent)
                print(self.policyNumber, '填入买入比例')
                self.random_sleep(10, 15)
                # 点击下一个
                self.wait_until(driver=driver, platform='ITA', selector_name="//div[@class='form-actions']/button")
                print(self.policyNumber, '点击下一个')
                # 点击选择
                # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@id='s2id_fundCode']/a[@class='select2-choice select2-default']/span[@id='select2-chosen-37']")
                buyingPercentList = collections.OrderedDict()  # 有序字典
                buyingPercentList['ACAI'] = 23.53 if self.riskType == '增长型' else 41.18
                buyingPercentList['FTCF'] = 17.65 if self.riskType == '增长型' else 11.76
                buyingPercentList['MFVF'] = 29.41 if self.riskType == '增长型' else 23.53
                buyingPercentList['MSGB'] = 29.41 if self.riskType == '增长型' else 23.53
                row_index = 1
                for name, value in buyingPercentList.items():
                    self.random_sleep()
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='Step2']/div[@class='table-container']/table[@id='datatableFilter']//tr[@class='bg-grey-cararra']/td[1]/div[@id='s2id_fundCode']/a")
                    # # selector_name="//table[@id='datatableFilter']//tr[@class='bg-grey-cararra']/td[1]/div[@id='s2id_fundCode']/a")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清除输入框并输入基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='clear')
                    print(self.policyNumber, '清除输入框并输入基金代码')
                    self.random_sleep()
                    # print(name, value)
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='send_keys', send_keys=name)
                    # 点击基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/ul/li[@class='select2-results-dept-0 select2-result select2-result-selectable custom-panel-select2-option select2-highlighted']/div//span[1]")
                    print(self.policyNumber, '点击基金代码')
                    self.random_sleep()
                    # 点击搜寻
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='Step2']/div[@class='table-container']//tr[@class='bg-grey-cararra']/td/button[@class='btn btn-sm filter-submit green-seagreen']")
                    print(self.policyNumber, '点击搜寻')
                    self.random_sleep(10,15)
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//table[@class='table table-condensed table-hover']//tr[@class='rowTransferRebalance']/td/a[@class='btn btn-xs grey-steel']")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清空买入比例输入框
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='clear')
                    print(self.policyNumber, '清空买入比例输入框')
                    self.random_sleep()
                    # 填入买入比例
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='send_keys', send_keys=value)
                    print(self.policyNumber, '填入买入比例')
                    row_index += 1
                # 四个选择完了
                # 点击下一步
                self.random_sleep()
                # 点击空白处
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='MainBody']")
                self.random_sleep(3, 5)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']//button")
                print(self.policyNumber, '四个选择完了，点击下一步')
                self.random_sleep()
                print('准备点确认了！~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # time.sleep(500000)
                # 点击确认
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='divStep4']/div[@class='form-actions']/button[@class='btn bg-blue pull-right']")
                print(self.policyNumber, '点击确认')
                try:
                    # 点击完成
                    self.random_sleep()
                    driver.find_element_by_xpath(
                        "//div[@id='Step5panel']/div[@id='stepsTransferRebalance_5']//div[@class='form-actions']/a").click()
                    # self.wait_until(driver=driver,platform='ITA',
                    #                 selector_name="//div[@id='Step5panel']/div[@id='stepsTransferRebalance_5']/div[@class='panel-body form']/div[@class='form-actions']/a")
                    print(self.policyNumber, '点击完成')
                    self.random_sleep()
                    self.random_sleep()
                    # 点击两个缩进箭头
                    driver.find_element_by_xpath(
                        "//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a").click()
                    print(self.policyNumber, '点击第一个缩进箭头')
                    # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a")
                    self.random_sleep()
                    driver.find_element_by_xpath(
                        "//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a").click()
                    print(self.policyNumber, '点击第二个缩进箭头')
                    # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a")
                except:
                    if self.error == 0:
                        print(self.policyNumber, '购买ITA保单后报错了,可能截图有问题')
                    else:
                        print(self.policyNumber, 'error!!')
                    # # 点击两个缩进箭头
                    # driver.find_element_by_xpath(
                    #     "//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a").click()
                    # print(self.policyNumber, '点击第一个缩进箭头')
                    # # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a")
                    # self.random_sleep()
                    # driver.find_element_by_xpath(
                    #     "//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a").click()
                    # print(self.policyNumber, '点击第二个缩进箭头')
                self.random_sleep()
                # 调仓完毕，截图保存。
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot('成功调仓截图文件夹/ITA/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    print(self.policyNumber, '成功调仓截图中')
                    # self.policy_index = self.ITA_index[index]
                    self.write_excel(policy_index=self.ITA_index[index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/ITA/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.ITA_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])

        print('ITA调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # 关闭浏览器
        driver.quit()

    def ita_operation_emergency(self, ITA):
        """
        ITA调仓操作
        :param ITA: ITA data list
        :return: opearting
        """
        if not ITA:
            print('ITA无需调仓的保单！')
            return
        # 检查是否够钟落班
        self.check_workoff()
        # 打开Chrome浏览器登录
        url = "https://ita.secureaccountaccess.com/Account/Login?ReturnUrl=%2f"
        username = 'sarah'
        password = 'Trussan1105'
        username_id = "UserName"
        password_id = "Password"
        submit_id = "submit-login"
        driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
        driver.maximize_window()
        self.random_sleep()
        print('login')
        # 点击前往主页
        self.wait_until(driver=driver, platform='ITA', selector_name="//div[@class='portlet-body']//a")
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, "//div[@class='portlet-body']//a")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath("//div[@class='portlet-body']//a").click()
        print('前往主页')
        self.random_sleep()
        driver.maximize_window()

        # 点击查询
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH,
        #                                         '''//ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a''')))
        # except Exception as e:
        #     print('==============error6================')
        self.random_sleep()
        driver.save_screenshot('test.png')
        print('准备点击查询')
        self.wait_until(driver=driver, platform='ITA',
                        selector_name='''//div[@class='page-container']/div[@id='sideBar']/div[@class='page-sidebar navbar-collapse collapse']/ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a[@id='menu_0']''')
        print('已点击查询')
        # driver.find_element_by_xpath(
        #     '''//div[@class='page-container']/div[@id='sideBar']/div[@class='page-sidebar navbar-collapse collapse']/ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a[@id='menu_0']''').click()
        self.random_sleep()
        # 点击标准查询
        self.wait_until(driver=driver, platform='ITA',
                        selector_name="""//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""")
        # try:
        #     element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH,
        #                                                                                """//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath(
        #     """//ul[@class='page-sidebar-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][1]/a""").click()
        self.random_sleep()
        # 点击计划
        self.wait_until(driver=driver, platform='ITA',
                        selector_name="//div[@class='radio-list']/label[@id='Label_Option2']")
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, "//div[@class='radio-list']/label[@id='Label_Option2']")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath("//div[@class='radio-list']/label[@id='Label_Option2']").click()

        for index, item in enumerate(ITA):
            # 检查是否够钟落班
            self.check_workoff()
            self.operation_counts += 1
            self.error = 0
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = round(float(item[1]) * 100, 2)
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                # 点击输入保单号
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='clear')
                print(self.policyNumber, '点击输入保单号')
                # 输入保单号
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").clear()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='send_keys', send_keys=self.policyNumber)
                print(self.policyNumber, '输入保单号')
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").send_keys(self.policyNumber)
                self.random_sleep()
                # 点击搜寻
                self.wait_until(driver=driver, platform='ITA', selector_name="//button[@id='SearchButton']")
                print(self.policyNumber, '点击搜寻')
                # driver.find_element_by_xpath("//button[@id='SearchButton']").click()
                self.random_sleep()
                # 点击计划号码
                try:
                    element = WebDriverWait(driver, 100).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//table[@id='TableReport']//tr[@class='odd']/td[1]/a")))
                except Exception as e:
                    print('==============error6================')
                # self.wait_until(driver=driver,platform='ITA', selector_name="//table[@id='TableReport']//tr[@class='odd']/td[1]/a")
                print(self.policyNumber, '点击计划号码')
                # 切换至新窗口
                policyLink = str(
                    driver.find_element_by_xpath("//table[@id='TableReport']//tr[@class='odd']/td[1]/a").get_attribute(
                        "href"))
                js = 'window.open("' + policyLink + '");'
                driver.execute_script(js)
                # print(driver.window_handles)
                driver.switch_to.window(driver.window_handles[1])
                print(self.policyNumber, '切换至新窗口')
                self.random_sleep()
                driver.maximize_window()
                self.random_sleep(15, 20)
                # 点击主计划
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''')
                print(self.policyNumber, '点击主计划')
                # driver.find_element_by_xpath(
                #     '''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''').click()

                # 点击基金转换&平衡
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='sub-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][3]/a[@id='menu_0']/div[@class='title']''')
                print(self.policyNumber, '点击基金转换&平衡')
                # 勾选基金转换
                self.random_sleep()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//form[@id='Step1']/div[@class='form-body select-option']/div[@class='form-group']/div[@class='radio-list']/label[1]/label")
                print(self.policyNumber, '勾选基金转换')
                # 点击下一个
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='Step1panel']//div[@id='stepsTransferRebalance_1']//div[@class='panel-body form']//form[@id='Step1']//div[@class='form-actions']/input[@type='submit']")
                print(self.policyNumber, '点击下一个')
                self.random_sleep()
                self.random_sleep()
                self.random_sleep()


                # 把当前持有的所有基金全部卖出。ITA的卖出及买入比例可以保留两位小数。

                for i in range(10):
                    try:
                        self.wait_until(driver=driver, platform='ITA',
                                        selector_name="//tr[@class='rowSearch'][1]/td[@class='thCol12']/a")
                        print(self.policyNumber, '点击选择基金')
                        self.random_sleep()
                    except:
                        print('总共有%s个要卖出的基金' % (i-1))
                        break
                self.random_sleep()

                # 点击下一步
                self.wait_until(driver=driver, platform='ITA', selector_name="//div[@class='form-actions']/button")
                print(self.policyNumber, '点击下一个')

                # 点击选择
                # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@id='s2id_fundCode']/a[@class='select2-choice select2-default']/span[@id='select2-chosen-37']")
                buyingPercentList = collections.OrderedDict()  # 有序字典
                buyingPercentList['MFVF'] = 23.53 if self.riskType == '增长型' else 41.18
                buyingPercentList['MSGB'] = 17.65 if self.riskType == '增长型' else 11.76
                buyingPercentList['FTCF'] = 29.41 if self.riskType == '增长型' else 23.53
                buyingPercentList['ACAI'] = 29.41 if self.riskType == '增长型' else 23.53
                buyingPercentList['FIDC'] = 29.41 if self.riskType == '增长型' else 23.53
                row_index = 1
                for name, value in buyingPercentList.items():
                    self.random_sleep()
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='Step2']/div[@class='table-container']/table[@id='datatableFilter']//tr[@class='bg-grey-cararra']/td[1]/div[@id='s2id_fundCode']/a")
                    # # selector_name="//table[@id='datatableFilter']//tr[@class='bg-grey-cararra']/td[1]/div[@id='s2id_fundCode']/a")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清除输入框并输入基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='clear')
                    print(self.policyNumber, '清除输入框并输入基金代码')
                    self.random_sleep()
                    # print(name, value)
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='send_keys', send_keys=name)
                    # 点击基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/ul/li[@class='select2-results-dept-0 select2-result select2-result-selectable custom-panel-select2-option select2-highlighted']/div//span[1]")
                    print(self.policyNumber, '点击基金代码')
                    self.random_sleep()
                    # 点击搜寻
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='Step2']/div[@class='table-container']//tr[@class='bg-grey-cararra']/td/button[@class='btn btn-sm filter-submit green-seagreen']")
                    print(self.policyNumber, '点击搜寻')
                    self.random_sleep(10,15)
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//table[@class='table table-condensed table-hover']//tr[@class='rowTransferRebalance']/td/a[@class='btn btn-xs grey-steel']")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清空买入比例输入框
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='clear')
                    print(self.policyNumber, '清空买入比例输入框')
                    self.random_sleep()
                    # 填入买入比例
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='send_keys', send_keys=value)
                    print(self.policyNumber, '填入买入比例')
                    row_index += 1
                # 四个选择完了
                # 点击下一步
                self.random_sleep()
                # 点击空白处
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='MainBody']")
                self.random_sleep(3, 5)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']//button")
                print(self.policyNumber, '四个选择完了，点击下一步')
                self.random_sleep()
                print('准备点确认了！~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # time.sleep(500000)
                # 点击确认
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='divStep4']/div[@class='form-actions']/button[@class='btn bg-blue pull-right']")
                print(self.policyNumber, '点击确认')
                try:
                    # 点击完成
                    self.random_sleep()
                    driver.find_element_by_xpath(
                        "//div[@id='Step5panel']/div[@id='stepsTransferRebalance_5']//div[@class='form-actions']/a").click()
                    # self.wait_until(driver=driver,platform='ITA',
                    #                 selector_name="//div[@id='Step5panel']/div[@id='stepsTransferRebalance_5']/div[@class='panel-body form']/div[@class='form-actions']/a")
                    print(self.policyNumber, '点击完成')
                    self.random_sleep()
                    self.random_sleep()
                    # 点击两个缩进箭头
                    driver.find_element_by_xpath(
                        "//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a").click()
                    print(self.policyNumber, '点击第一个缩进箭头')
                    # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a")
                    self.random_sleep()
                    driver.find_element_by_xpath(
                        "//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a").click()
                    print(self.policyNumber, '点击第二个缩进箭头')
                    # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a")
                except:
                    if self.error == 0:
                        print(self.policyNumber, '购买ITA保单后报错了,可能截图有问题')
                    else:
                        print(self.policyNumber, 'error!!')
                    # # 点击两个缩进箭头
                    # driver.find_element_by_xpath(
                    #     "//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a").click()
                    # print(self.policyNumber, '点击第一个缩进箭头')
                    # # self.wait_until(driver=driver,platform='ITA',selector_name="//div[@class='portlet box grey'][1]/div[@class='portlet-title']/div[@class='tools']/a")
                    # self.random_sleep()
                    # driver.find_element_by_xpath(
                    #     "//div[@id='GraphBenefitsPorlet']/div[@class='portlet-title']/div[@class='tools']/a").click()
                    # print(self.policyNumber, '点击第二个缩进箭头')
                self.random_sleep()
                # 调仓完毕，截图保存。
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot('成功调仓截图文件夹/ITA/' + str(self.policyNumber) + str(self.riskType) + "调仓.png")
                    print(self.policyNumber, '成功调仓截图中')
                    # self.policy_index = self.ITA_index[index]
                    self.write_excel(policy_index=self.ITA_index[index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')


                # 点击未来配置
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='sub-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][4]/a[@id='menu_0']/div[@class='title']''')
                print(self.policyNumber, '点击未来配置')
                self.random_sleep()
                # 点击新投资组合
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='Step1panel']//form[@id='FormStep1']//div[@class='radio-list']/label[1]/label")
                self.random_sleep()
                # 点击下一步
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//form[@id='FormStep1']/div[@class='form-actions']/button")

                row_index = 1
                for name, value in buyingPercentList.items():
                    self.random_sleep()
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='FormStep2']/div[@class='table-container']/table[@id='datatableFilter']//td[1]/div[@id='s2id_fundCode']/a")
                    # # selector_name="//table[@id='datatableFilter']//tr[@class='bg-grey-cararra']/td[1]/div[@id='s2id_fundCode']/a")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清除输入框并输入基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='clear')
                    print(self.policyNumber, '清除输入框并输入基金代码')
                    self.random_sleep()
                    # print(name, value)
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='send_keys', send_keys=name)
                    # 点击基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/ul/li[@class='select2-results-dept-0 select2-result select2-result-selectable custom-panel-select2-option select2-highlighted']/div//span[1]")
                    print(self.policyNumber, '点击基金代码')
                    self.random_sleep()
                    # 点击搜寻
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='FormStep2']//button[@class='btn btn-sm filter-submit green-seagreen']")
                    print(self.policyNumber, '点击搜寻')
                    self.random_sleep(10,15)
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//table[@class='table table-condensed table-hover']//tr[@class='rowTransferRebalance']/td/a[@class='btn btn-xs grey-steel']")
                    print(self.policyNumber, '点击选择')
                    self.random_sleep()
                    # 清空买入比例输入框
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='clear')
                    print(self.policyNumber, '清空买入比例输入框')
                    self.random_sleep()
                    # 填入买入比例
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11 text-right']/input",
                                    action='send_keys', send_keys=value)
                    print(self.policyNumber, '填入买入比例')
                    row_index += 1
                # 四个选择完了
                # 点击下一步
                self.random_sleep()
                # 点击空白处
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='MainBody']")
                self.random_sleep(3, 5)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='stepsMain_2']//div[@class='form-actions']/button")
                print(self.policyNumber, '四个选择完了，点击下一步')
                self.random_sleep()
                print('准备点确认了！~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # time.sleep(500000)
                # 点击确认
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='stepsMain_3']//div[@class='form-actions']/button")
                print(self.policyNumber, '点击确认')

                # 调仓完毕，截图保存。
                if self.error == 0:
                    driver.save_screenshot('成功调仓截图文件夹/ITA/' + str(self.policyNumber) + str(self.riskType) + "未来配置.png")
                    print(self.policyNumber, '成功调仓截图中')
                    # self.policy_index = self.ITA_index[index]
                    print(str(self.policyNumber) + str(self.riskType), '：未来配置调成功！')


                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/ITA/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.ITA_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])

        print('ITA调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        # 关闭浏览器
        driver.quit()

    def zurich_operation(self, zurich):
        """
        zurich调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        # 打开Chrome浏览器登录
        url = "https://online.zurichinternationalsolutions.com/Login.aspx"
        for index, item in enumerate(zurich):
            # 检查是否够钟落班
            self.check_workoff()
            self.operation_counts += 1
            self.error = 0
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = round(float(item[1]) * 100)
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                username = str(item[3])
                password = str(item[4])
                # PIN = str(item[5]) if len(str(item[5])) >= 4 else '0'+str(item[5])
                username_id = "ctl00_ContentPlaceHolder1_txtUserName"
                password_id = "ctl00_ContentPlaceHolder1_txtPassword"
                submit_id = "ctl00_ContentPlaceHolder1_cmdLogin"
                # 登录
                driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()
                # 判断PIN码的个数（因读excel时会忽略第一个数字0）
                PINCount = 1
                try:
                    while driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(PINCount) + "]/input"):
                        # print('+1')
                        PINCount += 1
                        if PINCount > 11:
                            break
                except:
                    print('PIN的位数为：', str(PINCount - 1))
                PIN = str(item[5]) if len(str(item[5])) == len(str(PINCount - 1)) else '0' * (
                (PINCount - 1) - len(str(item[5]))) + str(item[5])
                # print(PINCount-1)
                # print(len(str(item[5])))
                print('PIN码为：', PIN)
                # 正在输入PIN码补充位
                for index, item in enumerate(str(PIN)):
                    # print(len(driver.find_element_by_xpath("//tr//td")))
                    if not driver.find_element_by_xpath(
                                            "//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").get_attribute(
                            "value"):
                        driver.find_element_by_xpath(
                            "//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").send_keys(item)
                    self.random_sleep()
                # 点击登录
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//input[@id='ctl00_ContentPlaceHolder1_ucPinValidator_btnRandomPinContinue']")
                self.random_sleep()
                # 输入PIN码后，部分账户会出现更改密码的提示
                try:
                    # 勾选
                    self.random_sleep(10,12)
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_cbConfirmIgnore']").click()
                    # 点击continue
                    self.random_sleep()
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_btnConfirmIgnore']").click()
                except:
                    pass
                self.random_sleep()
                self.random_sleep()
                # 进入调仓界面 点击“here”
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@class='pagewrapper']//div[@class='page']//p[@class='dashWel']/a")
                # 切换新窗口
                driver.switch_to.window(driver.window_handles[1])
                # 选择需要进行调仓的保单号
                # self.wait_until(driver=driver, platform='zurich', selector_name="//fieldset[1]//select")
                self.random_sleep()
                try:
                    select = Select(driver.find_element_by_name('ctl00$ContentPlaceHolder1$ddlPolicyNumber'))
                    self.random_sleep()
                    select.select_by_visible_text(self.policyNumber)
                    print('选择下拉框完成')
                except:
                    print('选择下拉框失败')
                self.random_sleep()
                # 点击需要购买的保单号
                # try:
                #     for index in range(1, 20):
                #         if driver.find_element_by_xpath("//fieldset[1]//select/option[" + str(index) + "]").get_attribute("value") == self.policyNumber:
                #             # print(driver.find_element_by_xpath("//fieldset[1]//select/option["+str(index)+"]").get_attribute("value"))
                #             self.wait_until(driver=driver, platform='zurich',selector_name="//fieldset[1]//select/option[" + str(index) + "]")
                #             break
                # except:
                #     print('点击option失败')
                self.random_sleep()
                # 点击圆点
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//input[@id='ctl00_ContentPlaceHolder1_rdoEnableSection2andSection3']")
                self.random_sleep()
                # 输入卖出基金
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d0'][1]/td[1]/input",
                                action='clear')
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d0'][1]/td[1]/input",
                                action='send_keys', send_keys='OVUSD')
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d0'][1]/td[2]/input",
                                action='clear')
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d0'][1]/td[2]/input",
                                action='send_keys', send_keys=self.sellingPercent)
                # 填写买入的基金信息
                buyFundList = collections.OrderedDict()  # 有序字典
                buyFundList['ZUUSD'] = 29 if self.riskType == '增长型' else 24
                buyFundList['ZOUSD'] = 29 if self.riskType == '增长型' else 24
                buyFundList['PJUSD'] = 24 if self.riskType == '增长型' else 35
                buyFundList['PZEUR'] = 18 if self.riskType == '增长型' else 17
                buyFundIndex = 1
                for fundName, percent in buyFundList.items():
                    d_num = str((buyFundIndex + 1) % 2)
                    tr_num = str(int(buyFundIndex / 2)) if (buyFundIndex % 2) == 0 else str(int((buyFundIndex + 1) / 2))
                    print(
                        "//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input")
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='send_keys', send_keys=fundName)
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='send_keys', send_keys=percent)
                    buyFundIndex += 1
                # 点击Total
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[3]/td/input[@id='ctl00_ContentPlaceHolder1_btnTotalSection2']")
                self.random_sleep()
                # 打勾
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr[1]/td/input[@id='ctl00_ContentPlaceHolder1_chkTNC']")
                self.random_sleep()
                # 点击submit
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr[3]/td/input[@id='ctl00_ContentPlaceHolder1_btnsubmit']")
                self.random_sleep()
                # 点击confirm
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@id='ConfirmDialog']/div[@class='DialosgButtons']/input[@id='btnConfirmYes']")
                self.random_sleep()
                # 购买成功，截图
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot('成功调仓截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    print(self.policyNumber, '成功调仓截图中')
                    # self.policy_index = self.ITA_index[index]
                    self.write_excel(policy_index=self.zurich_index[self.enum_index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                # 点击“PDF”
                driver.find_element_by_link_text('PDF').click()
                # 切换到PDF的新窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[2])
                # 点击下载保存PDF文件
                self.random_sleep()
                driver.save_screenshot('成功调仓截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '截图pdf中')
                self.random_sleep()
                driver.find_element_by_xpath("/html/body/embed[@id='plugin']").send_keys(Keys.CONTROL, 's')
                self.random_sleep()
                os.system('保存pdf脚本.exe')
                self.random_sleep()
                driver.close()
                rename1 = 'E:/工作相关/python相关/代码/AUTO_TiaoCan/成功调仓截图文件夹/zurich/pdf/'
                rename2 = str(self.policyNumber) + str(self.riskType)
                rename3 = '.pdf'
                rename = rename1 + rename2 + rename3
                os.rename("E:/工作相关/python相关/代码/AUTO_TiaoCan/成功调仓截图文件夹/zurich/pdf/1.pdf", rename)
                # 关闭当前PDF窗口并切换至原来的窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[1])
                # 点击Finish
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//a[@id='ctl00_ContentPlaceHolder1_lnkFinish']")
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[0])
                # 点击logout
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                self.random_sleep()

            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.zurich_index[self.enum_index], message='调仓失败')
            finally:
                # 关闭浏览器
                driver.quit()

        print('zurich调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def zurich_operation_emergency(self, zurich):
        """
        zurich调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        # 打开Chrome浏览器登录
        url = "https://online.zurichinternationalsolutions.com/Login.aspx"
        for index, item in enumerate(zurich):
            # 检查是否够钟落班
            self.check_workoff()
            self.operation_counts += 1
            self.error = 0
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 卖出比例
                self.sellingPercent = round(float(item[1]) * 100)
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                username = str(item[3])
                password = str(item[4])
                # PIN = str(item[5]) if len(str(item[5])) >= 4 else '0'+str(item[5])
                username_id = "ctl00_ContentPlaceHolder1_txtUserName"
                password_id = "ctl00_ContentPlaceHolder1_txtPassword"
                submit_id = "ctl00_ContentPlaceHolder1_cmdLogin"
                # 登录
                driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()
                # 判断PIN码的个数（因读excel时会忽略第一个数字0）
                PINCount = 1
                try:
                    while driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(PINCount) + "]/input"):
                        # print('+1')
                        PINCount += 1
                        if PINCount > 11:
                            break
                except:
                    print('PIN的位数为：', str(PINCount - 1))
                PIN = str(item[5]) if len(str(item[5])) == len(str(PINCount - 1)) else '0' * (
                (PINCount - 1) - len(str(item[5]))) + str(item[5])
                # print(PINCount-1)
                # print(len(str(item[5])))
                print('PIN码为：', PIN)
                # 正在输入PIN码补充位
                for index, item in enumerate(str(PIN)):
                    # print(len(driver.find_element_by_xpath("//tr//td")))
                    if not driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").get_attribute("value"):
                        driver.find_element_by_xpath(
                            "//tr/td[@class='PintextBox'][" + str(index + 1) + "]/input").send_keys(item)
                    self.random_sleep()
                # 点击登录
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//input[@id='ctl00_ContentPlaceHolder1_ucPinValidator_btnRandomPinContinue']")
                self.random_sleep()
                # 输入PIN码后，部分账户会出现更改密码的提示
                try:
                    # 勾选
                    self.random_sleep(10,12)
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_cbConfirmIgnore']").click()
                    # 点击continue
                    self.random_sleep()
                    driver.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_btnConfirmIgnore']").click()
                except:
                    pass
                self.random_sleep()
                self.random_sleep()
                # 进入调仓界面 点击“see more”
                self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='pHead Savings noBens']/p[@class='seemore']")
                holding_funds = []
                # 读取所持有基金的基金代码：
                xpath_obj = etree.HTML(driver.page_source)
                for i in range(1,20):
                    try:
                        # holding_funds.append(driver.find_element_by_xpath("//div[@class='price-history-padding-inside']["+str(i)+"]/div[@class='price-history-data-div']/div[@class='large-text dark-grey mb-10'][1]").text)
                        holding_funds.append(xpath_obj.xpath("//div[@class='price-history-padding-inside']["+str(i)+"]/div[@class='price-history-data-div']/div[@class='large-text dark-grey mb-10'][1]//text()")[0])
                        print(xpath_obj.xpath("//div[@class='price-history-padding-inside']["+str(i)+"]/div[@class='price-history-data-div']/div[@class='large-text dark-grey mb-10'][1]//text()"))
                    except:
                        print('现有基金有%s支'%(i-1))
                        break
                print('holding_funds',holding_funds)
                self.random_sleep()
                # 点击back
                self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='sysButtons']//tr/td[1]/div")

                # 进入调仓界面 点击“here”
                self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='pagewrapper']//div[@class='page']//p[@class='dashWel']/a")
                # 切换新窗口
                driver.switch_to.window(driver.window_handles[1])

                # 选择需要进行调仓的保单号
                # self.wait_until(driver=driver, platform='zurich', selector_name="//fieldset[1]//select")
                self.random_sleep()
                try:
                    select = Select(driver.find_element_by_name('ctl00$ContentPlaceHolder1$ddlPolicyNumber'))
                    self.random_sleep()
                    select.select_by_visible_text(self.policyNumber)
                    print('选择下拉框完成')
                except:
                    print('选择下拉框失败')
                self.random_sleep()
                # 点击需要购买的保单号
                # try:
                #     for index in range(1, 20):
                #         if driver.find_element_by_xpath("//fieldset[1]//select/option[" + str(index) + "]").get_attribute("value") == self.policyNumber:
                #             # print(driver.find_element_by_xpath("//fieldset[1]//select/option["+str(index)+"]").get_attribute("value"))
                #             self.wait_until(driver=driver, platform='zurich',selector_name="//fieldset[1]//select/option[" + str(index) + "]")
                #             break
                # except:
                #     print('点击option失败')
                self.random_sleep()
                # 点击圆点
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//input[@id='ctl00_ContentPlaceHolder1_rdoEnableSection2andSection3']")
                self.random_sleep()
                # 输入卖出基金
                for index,fund in enumerate(holding_funds):
                    dn = str((index) % 2)
                    tn = str(int(index / 2 + 1)) if (index % 2) == 0 else str(int((index + 1) / 2))

                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d"+dn+"']["+tn+"]/td[1]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d"+dn+"']["+tn+"]/td[1]/input",
                                    action='send_keys', send_keys=fund)
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d"+dn+"']["+tn+"]/td[2]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFundsCodes']//tr[@class='d"+dn+"']["+tn+"]/td[2]/input",
                                    action='send_keys', send_keys=100)

                # 填写买入的基金信息
                buyFundList = collections.OrderedDict()  # 有序字典
                buyFundList['ZUUSD'] = 25 if self.riskType == '增长型' else 20
                buyFundList['ZOUSD'] = 25 if self.riskType == '增长型' else 20
                buyFundList['PJUSD'] = 20 if self.riskType == '增长型' else 30
                buyFundList['PZEUR'] = 15 if self.riskType == '增长型' else 15
                buyFundList['OVUSD'] = 15 if self.riskType == '增长型' else 15
                buyFundIndex = 1

                for fundName, percent in buyFundList.items():
                    d_num = str((buyFundIndex + 1) % 2)
                    tr_num = str(int(buyFundIndex / 2)) if (buyFundIndex % 2) == 0 else str(int((buyFundIndex + 1) / 2))
                    print(
                        "//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input")
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='send_keys', send_keys=fundName)
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//tr/td[1]/fieldset/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td/div/table[@id='ctl00_ContentPlaceHolder1_gvFudCodesBuy']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='send_keys', send_keys=percent)
                    # 未来配置
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//table[@id='ctl00_ContentPlaceHolder1_gvInvestFundcodes']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//table[@id='ctl00_ContentPlaceHolder1_gvInvestFundcodes']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[1]/input",
                                    action='send_keys', send_keys=fundName)
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//table[@id='ctl00_ContentPlaceHolder1_gvInvestFundcodes']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='clear')
                    self.wait_until(driver=driver, platform='zurich',
                                    selector_name="//table[@id='ctl00_ContentPlaceHolder1_gvInvestFundcodes']/tbody/tr[@class='d" + d_num + "'][" + tr_num + "]/td[2]/input",
                                    action='send_keys', send_keys=percent)
                    buyFundIndex += 1
                # 点击Total
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[1]/fieldset/table/tbody/tr[3]/td/input[@id='ctl00_ContentPlaceHolder1_btnTotalSection2']")
                self.random_sleep(8,10)
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr/td[3]/fieldset/table/tbody/tr[3]/td/input[@id='ctl00_ContentPlaceHolder1_btnTotalSection3']")


                # 打勾
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr[1]/td/input[@id='ctl00_ContentPlaceHolder1_chkTNC']")
                self.random_sleep()
                # 点击submit
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//tr[3]/td/input[@id='ctl00_ContentPlaceHolder1_btnsubmit']")
                self.random_sleep(8,10)
                # 点击confirm
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@id='ConfirmDialog']/div[@class='DialosgButtons']/input[@id='btnConfirmYes']")
                self.random_sleep()
                # 购买成功，截图
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot('成功调仓截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    print(self.policyNumber, '成功调仓截图中')
                    # self.policy_index = self.ITA_index[index]
                    self.write_excel(policy_index=self.zurich_index[self.enum_index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                # 点击“PDF”
                driver.find_element_by_link_text('PDF').click()
                # 切换到PDF的新窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[2])
                # 点击下载保存PDF文件
                self.random_sleep()
                driver.save_screenshot('成功调仓截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '截图pdf中')
                self.random_sleep()
                driver.find_element_by_xpath("/html/body/embed[@id='plugin']").send_keys(Keys.CONTROL, 's')
                self.random_sleep()
                os.system('保存pdf脚本.exe')
                self.random_sleep()
                driver.close()
                rename1 = 'E:/工作相关/python相关/代码/AUTO_TiaoCan/成功调仓截图文件夹/zurich/pdf/'
                rename2 = str(self.policyNumber) + str(self.riskType)
                rename3 = '.pdf'
                rename = rename1 + rename2 + rename3
                os.rename("E:/工作相关/python相关/代码/AUTO_TiaoCan/成功调仓截图文件夹/zurich/pdf/1.pdf", rename)
                # 关闭当前PDF窗口并切换至原来的窗口
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[1])
                # 点击Finish
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//a[@id='ctl00_ContentPlaceHolder1_lnkFinish']")
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[0])
                # 点击logout
                self.wait_until(driver=driver, platform='zurich',
                                selector_name="//div[@class='toplinks']/a[@class='rhm logout']")
                self.random_sleep()

            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/zurich/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.zurich_index[self.enum_index], message='调仓失败')
            finally:
                # 关闭浏览器
                driver.quit()

            print('zurich调仓完毕！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def zurich_login_test(self,zurich):
        """
                zurich调仓操作
                :param zurich: zurich data list
                :return: operating
                """
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        for index, item in enumerate(zurich):
            try:
                self.operation_counts += 1
                self.enum_index = index# 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                username = str(item[3])
                password = str(item[4])
                zurich_login_url = 'https://online.zurichinternationalsolutions.com/login.aspx?ReturnUrl=%2fZIO%2fMyPolicies.mvc'
                zurich_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Content-Length": "2108",
                    "Content-Type": "application/x-www-form-urlencoded",
                    # "Cookie":"ASP.NET_SessionId=qzrmgc45czzb5h55tuclvt45; visid_incap_437653=cE9OR25GTS6Qmm1byrRsbYDDOFoAAAAAQUIPAAAAAABC7IzC4DotQBmwEh1HJ3t/; incap_ses_434_437653=8a0VW2bVCWec94AqB+EFBqaLl1oAAAAAgjqOT+B3hJMnZ0Vkre2giw==; RememberMe=Wang8765zheng",
                    "Host": "online.zurichinternationalsolutions.com",
                    "Origin": "https://online.zurichinternationalsolutions.com",
                    "Referer": "https://online.zurichinternationalsolutions.com/login.aspx?ReturnUrl=%2fZIO%2fMyPolicies.mvc",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                }

                zurich_data = {
                    # "__LASTFOCUS": "",
                    "ctl00_ToolkitScriptManager1_HiddenField": ";;AjaxControlToolkit, Version=3.5.51116.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:en-GB:2a06c7e2-728e-4b15-83d6-9b269fb7261e:de1feab2:f2c8e708:720a52bf:f9cec9bc:7311d143",
                    # "__EVENTTARGET": "",
                    # "__EVENTARGUMENT": "",
                    # "__VIEWSTATE": "/wEPDwUKMTI5NDk5NjQzNw8WAh4JUmV0dXJuVXJsBRMvWklPL015UG9saWNpZXMubXZjFgJmD2QWAgIDD2QWAgIDD2QWAgIBD2QWBGYPZBYSAgEPDxYCHgRUZXh0BSRMb2dpbiB0byBadXJpY2ggSW50ZXJuYXRpb25hbCBvbmxpbmVkZAIHDw8WAh4MRXJyb3JNZXNzYWdlBR5Vc2VybmFtZSBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAILDw8WAh8CBR5QYXNzd29yZCBjYW5ub3QgYmUgbGVmdCBibGFuay5kZAINDxAPFgIfAQUUUmVtZW1iZXIgbXkgVXNlcm5hbWVkZGRkAg8PDxYCHwEFCENvbnRpbnVlZGQCEQ8PFgIfAQU1PGEgaHJlZj0iL0xvc3RDcmVkZW50aWFscy9Vc2VyTmFtZS5hc3B4Ij51c2VybmFtZTwvYT5kZAITDw8WAh8BBTU8YSBocmVmPSIvTG9zdENyZWRlbnRpYWxzL1Bhc3N3b3JkLmFzcHgiPnBhc3N3b3JkPC9hPmRkAhUPDxYCHwEFmwFJIGZvcmdvdCBib3RoLiBJZiB5b3UgaGF2ZSBmb3Jnb3R0ZW4gbW9yZSB0aGFuIG9uZSBvZiB5b3VyIGxvZ2luIGRldGFpbHMsIHBsZWFzZSA8YSBocmVmPSIvSW5mb3JtYXRpb24vQ29udGFjdERldGFpbHMuYXNweCIgdGFyZ2V0PSJfYmxhbmsiPmNvbnRhY3QgdXM8L2E+LmRkAhcPZBYCAgEPZBYCZg8PFgQeCENzc0NsYXNzBRBhY2NvcmRpb24taGVhZGVyHgRfIVNCAgJkZAIBD2QWAgIBD2QWAmYPZBYCZg9kFgYCBQ9kFgYCCQ8QZGQWAGQCDw8QZGQWAGQCFQ8QZGQWAGQCBw8WAh4OUG9zdEJhY2tTY3JpcHQFQ19fZG9Qb3N0QmFjaygnY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSR1Y1BpblZhbGlkYXRvciRidG5RdWl0JywnJylkAgsPFgIfBQVMX19kb1Bvc3RCYWNrKCdjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHVjUGluVmFsaWRhdG9yJGJ0blJhbmRvbVBpblF1aXQnLCcnKWQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFJmN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkY2JSZW1lbWJlck1lBSRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJE11bHRpVmlldzEPD2RmZD0Dvsc87o3jOZ3ZPZVuZpVJ3Hfo",
                    # "__VIEWSTATEGENERATOR": "C2EE9ABB",
                    # "__SCROLLPOSITIONX": "0",
                    # "__SCROLLPOSITIONY": "276",
                    # "__EVENTVALIDATION": "/wEWBgLmnay0DQLJ4fq4BwL90KKTCAKipK3+BAKtnJ6XBQLrspm9A1uSQcy1zRVB9AVdXeBqyISrY6YA",
                    "ctl00$ContentPlaceHolder1$txtUserName": username,
                    "ctl00$ContentPlaceHolder1$txtPassword": password,
                    "ctl00$ContentPlaceHolder1$cbRememberMe": "on",
                    "ctl00$ContentPlaceHolder1$cmdLogin": "Continue",
                    "ctl00$ContentPlaceHolder1$MyAccordion_AccordionExtender_ClientState": "-1",
                }

                response = requests.post(url=zurich_login_url, headers=zurich_headers, data=zurich_data).text
                # print(response)

                # zurich
                if 'Memorable number' in response:
                    self.write_excel(policy_index=self.zurich_index[self.enum_index], policy_col=13)
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                else:
                    print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                    self.write_excel(policy_index=self.zurich_index[self.enum_index], policy_col=13, message='登录失败')
            except Exception as e:
                print(self.policyNumber,'error!',e)

    def zurich_spider(self,zurich):
        """
                zurich调仓操作
                :param zurich: zurich data list
                :return: operating
                """
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        for index, item in enumerate(zurich):
            try:
                self.operation_counts += 1
                self.enum_index = index# 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                self.random_sleep()
                username = str(item[2]) # codysunmz
                password = str(item[3]) # Ilovele$shi
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
                driver = self.browser_login(url, username, password, username_id, password_id, submit_id)
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()
                # 判断PIN码的个数（因读excel时会忽略第一个数字0）
                PINCount = 1
                try:
                    while driver.find_element_by_xpath("//tr/td[@class='PintextBox'][" + str(PINCount) + "]/input"):
                        # print('+1')
                        PINCount += 1
                        if PINCount > 11:
                            break
                except:
                    print('PIN的位数为：', str(PINCount - 1))
                PIN = str(item[5]) if len(str(item[5])) == len(str(PINCount - 1)) else '0' * (
                    (PINCount - 1) - len(str(item[5]))) + str(item[5])
                # print(PINCount-1)
                # print(len(str(item[5])))
                print('PIN码为：', PIN)
                # 正在输入PIN码补充位
                for index, item in enumerate(str(PIN)):
                    # print(len(driver.find_element_by_xpath("//tr//td")))
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
                self.random_sleep()
                # 查询各保单号，符合则点击see more

                response0 = driver.page_source
                response = etree.HTML(response0)
                policy_no_list = response.xpath("//span[@id='spnPolNo']//text()")
                for index,policy_no in enumerate(policy_no_list):
                    if policy_no == self.policyNumber:
                        self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='polList']/div["+str(index+1)+"]//span[@class='seemore']")
                        break
                response0 = driver.page_source
                response = etree.HTML(response0)
                # 账户价值
                Date = response.xpath("//span[@class='fund-summary-date'][2]//text()")
                Fund_Name = response.xpath("//div[@class='price-history-padding-inside']/div[@class='price-history-data-div']/div[1]//text()")
                Fund_Code = response.xpath("//div[@class='price-history-padding-inside']/div[@class='price-history-data-div']/div[4]//text()")
                Fund_Bid_Price_Currency = response.xpath("//div[@class='fundTblRow']/div[2]//q//text()")
                Unit = response.xpath("//div[@class='fundTblRow']/div[3]/q//text()")
                Fund_Bid_Price = response.xpath("//div[@class='fundTblRow']/div[4]/q//text()")
                Value_In_Fund_Currency = response.xpath("//div[@class='fundTblRow']/div[5]/q//text()")
                Value_In_Policy_Currency = response.xpath("//div[@class='fundTblRow']/div[6]/q//text()")

                # 未来供款
                self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='fundSumMob']/div[@class='uiTabs']/ul[@class='uitoggle']/li[2]") # Investment strategy
                Investment_Contribution_Fund_Name = response.xpath("//div[@class='tab-pane investmentStrategy sel']//div[@class='fund-portfolio-data']//text()")
                Investment_Contribution_Allocation = response.xpath("//div[@class='tab-pane investmentStrategy sel']//div[@class='fund-portfolio-data']//text()")

                # 保费概况
                Total_Premium = response.xpath("//div[@class='invsDataItm'][4]//h1//span//text()")
                Total_withdrawal = response.xpath("//div[@class='invsDataItm'][5]//h1//span//text()")
                self.wait_until(driver=driver, platform='zurich', selector_name="//div[@class='page']/div[@class='tabs']/a[3]") # payment
                response0 = driver.page_source
                response = etree.HTML(response0)
                Payment_Frequency = response.xpath("//section[@id='pay']/div[@class='accordPanel']/div[@class='regPrem sel']/div[1]/p//text()")
                print('Total_Premium,Total_withdrawal,Payment_Frequency:',Total_Premium,Total_withdrawal,Payment_Frequency)
                # 保费详细表
                Premium_due_Date = []
                Premium_Due = []
                Payment_Date = []
                Premium = []
                Status = []
                page_counts = len(response.xpath("//div[@class='prmTblPg hidePrev']//p"))
                # 判断页数 读取
                for page in range(page_counts-2):
                    Premium_due_Date.append(response.xpath("//div[@class='regPrem sel']/div[@class='table reg']/div/p[1]//text()"))
                    Premium_Due.append(response.xpath("//div[@class='regPrem sel']/div[@class='table reg']/div/p[2]//text()"))
                    Payment_Date.append(response.xpath("//div[@class='regPrem sel']/div[@class='table reg']/div/p[3]//text()"))
                    Premium.append(response.xpath("//div[@class='regPrem sel']/div[@class='table reg']/div/p[4]//text()"))
                    Status.append(response.xpath("//div[@class='regPrem sel']/div[@class='table reg']/div/p[5]//text()"))
                    if not response.xpath("//div[@class='prmTblPg hideNext']"):
                        self.wait_until(driver=driver, platform='zurich',selector_name="//div[@class='accordPanel']/div[@class='regPrem sel']/div/p[page_counts]")
                        self.random_sleep()
                for Premium_due_Date,Premium_Due,Payment_Date,Premium,Status in zip(Premium_due_Date,Premium_Due,Payment_Date,Premium,Status):
                    print('Premium_due_Date,Premium_Due,Payment_Date,Premium,Status:',Premium_due_Date,Premium_Due,Payment_Date,Premium,Status)



            except Exception as e:
                print(self.policyNumber,'error!',e)


    def standard_life_operation(self, standard_life):
        """
        zurich调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        if not standard_life:
            print('standard_life无需调仓的保单！')
            return
        print('------------')
        # 打开Chrome浏览器登录
        url = "https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch"
        for index, item in enumerate(standard_life):
            # 检查是否够钟落班
            self.check_workoff()
            self.error = 0
            self.operation_counts += 1
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                # 卖出基金
                # sellFundCode = '07TU'
                # sellFundPercent = 12
                # buyCompany = ['天達資產管理', '施羅德投資管理(香港)有限公司']
                # buyFundCode = ['天達環球策略基金 - 環球動力基金 - A 累積股份', '施羅德環球基金系列 - 環球進取股票 - A1股']
                # buyFundPercent = [30, 70] if self.riskType == '增长型' else [60, 40]
                # buyFund = zip(buyCompany, buyFundCode, buyFundPercent)
                # fundLength = len(buyFundCode)
                targetFundPercentInit = collections.OrderedDict()
                targetFundPercentInit['施羅德環球基金系列 - 美國大型股 - A1股'] = 15
                targetFundPercentInit['美盛凱利美國增值基金 - A類累積'] = 15
                targetFundPercentInit['天達環球策略基金 - 環球動力基金 - A'] = 15
                targetFundPercentInit['施羅德環球基金系列 - 環球進取股票 - A1股'] = 15
                targetFundPercentInit['貝萊德美國政府房貸債券基金 - 美元(A2股)'] = 15
                targetFundPercentInit['富蘭克林鄧普頓投資基金 - 富蘭克林科技基金 - A累算'] = 15
                targetFundPercentInit['貝萊德全球基金 - 美元貨幣基金 - A2'] = 10

                targetFundPercentCompany = collections.OrderedDict()
                targetFundPercentCompany['天達環球策略基金 - 環球動力基金 - A 累積股份'] = '天達資產管理'
                targetFundPercentCompany['施羅德環球基金系列 - 環球進取股票 - A1股'] = '施羅德投資管理(香港)有限公司'


                self.random_sleep()
                username = str(item[2])
                password = str(item[3])

                # 调出浏览器
                driver = webdriver.Chrome()
                # 发送链接
                driver.get(url)
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()
                # 点击特别安排的OK
                try:
                    driver.find_element_by_xpath("//div[@class='ui-dialog-buttonset']/button/span").click()
                except:
                    pass
                # 登录
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
                                action='clear')
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
                                action='send_keys', send_keys=username)
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
                                action='clear')
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
                                action='send_keys', send_keys=password)
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='btn_Login']")
                self.random_sleep()
                self.random_sleep()
                # 点击轉換投資選擇
                self.wait_until(driver=driver, platform='standard_life', selector_name="//ul[@id='subNav']/li[2]/a")
                self.random_sleep()
                # 选择投资户口
                select = Select(driver.find_element_by_name('ddlInvestmentACC'))
                print('selected')
                self.random_sleep()
                # 选择投资户口數字測試
                # investmentCount = 0
                # self.random_sleep()
                # try:
                #     while select.select_by_index(investmentCount):
                #         print('+1')
                #         investmentCount += 1
                #         if investmentCount > 100:
                #             break
                # except:
                #     print('投資戶口数为：',str(investmentCount))
                # print(investmentCount)
                for index in range(20):
                    try:
                        # 选择户口
                        select.select_by_index(index)
                        self.random_sleep()
                        # 点击自愿卖出
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//input[@id='RBL_sooption_oth']")
                        self.random_sleep()

                        # 计算目标基金配置信息:
                        # 读取“投資基金”、“單位數目”、“戶口基金總值(以保單貨幣計算)”
                        acount_fund_lists = []
                        # sell_percent_list = []
                        # sell_count_list = []
                        acount_total = []
                        # for acount in range(5, 10):
                        buy_adjust_percent_total = 0
                        buy_percent_total = 0
                        fund_length = 0
                        total_value = 0
                        buy_fund_list = []
                        acount_fund_list = []
                        acount_count_list = collections.OrderedDict()
                        acount_value_list = collections.OrderedDict()
                        buy_percent_list = []
                        # print('Now_acount：', acount)
                        try:
                            for i in range(1, 20):
                                try:
                                    print("//div[@id='contentHolder']//tr["+str(i)+"]/td[@class='LightGrey'][1]/a[2]")
                                    fund = driver.find_element_by_xpath(
                                        "//div[@id='contentHolder']//tr["+str(i)+"]/td[@class='LightGrey'][1]/a[2]").text
                                    count = driver.find_element_by_xpath(
                                        "//div[@id='contentHolder']//tr["+str(i)+"]/td[@class='LightGrey'][4]/span[@id='Datagrid3__ctl"+str(i)+"_Label64']").text.replace(',', '')
                                    value = driver.find_element_by_xpath(
                                        "//div[@id='contentHolder']//tr["+str(i)+"]/td[@class='LightGrey'][5]/span[@id='Datagrid3__ctl"+str(i)+"_Label9']").text.replace(',', '')
                                    print('fund,count,value:', fund, count, value)
                                    acount_fund_list.append(fund)
                                    acount_count_list[fund] = float(count)
                                    # acount_count_list.append(float(count))
                                    acount_value_list[fund] = float(value)
                                    # acount_value_list.append(float(value))
                                    total_value += float(value)
                                    fund_length += 1
                                except:
                                    print('fund有%s个' % fund_length)
                                    break

                            # acount_fund_lists.append(acount_fund_list)
                            print('acount_fund_list,acount_fund_lists:', acount_fund_list, acount_fund_lists)
                            targetFundPercent = deepcopy(targetFundPercentInit)
                            print('targetFundPercent1', targetFundPercent)
                            # 找出与目标比例基金所不同的基金
                            for fund_redundant in acount_fund_list:
                                if fund_redundant not in targetFundPercent.keys():
                                    print('有多余的基金', fund_redundant)
                                    targetFundPercent[fund_redundant] = 0
                                    fund_length += 1
                            for fund_redundant in targetFundPercent.keys():
                                if fund_redundant not in acount_fund_list:
                                    print('有需补充的基金', fund_redundant)
                                    acount_fund_list.append(fund_redundant)
                                    acount_count_list[fund_redundant] = 0
                                    acount_value_list[fund_redundant] = 0
                                    fund_length += 1
                            # fund_length = len(targetFundPercent)
                            print('targetFundPercent2', targetFundPercent)
                            print('acount_fund_list', acount_fund_list)
                            print('acount_count_list：', acount_count_list)
                            print('acount_value_list：', acount_value_list)

                            # 计算调整比例的和
                            # for length in range(fund_length):
                            for fund in targetFundPercent.keys():
                                present_percent = (acount_value_list[fund] / total_value) * 100
                                adjust_percent = present_percent - targetFundPercent[fund]
                                if adjust_percent < 0:
                                    buy_adjust_percent_total += adjust_percent
                                    buy_fund_list.append(fund)
                            print('buy_adjust_percent_total:', buy_adjust_percent_total)
                            print('buy_fund_list:', buy_fund_list)

                            # 卖出列表
                            sell_dict = collections.OrderedDict()
                            # 买入列表
                            buy_dict = collections.OrderedDict()
                            # 所有需要操作的基金
                            # for length in range(fund_length):
                            for length, fund in enumerate(targetFundPercent.keys()):
                                print('目前为第%s支个基金：', length + 1)
                                present_percent = (acount_value_list[fund] / total_value) * 100
                                print(fund, 'present_percent', present_percent)
                                adjust_percent = present_percent - targetFundPercent[fund]
                                print(fund, 'adjust_percent', adjust_percent)
                                if adjust_percent > 0:
                                    print('sell')
                                    sell_percent = round(float(adjust_percent / present_percent), 2)
                                    sell_count = round(float(sell_percent * acount_count_list[fund]), 4)
                                    # sell_percent_list.append(sell_percent)
                                    # sell_count_list.append(sell_count)

                                    sell_dict[fund] = sell_count
                                    print('sell_percent,sell_count:', sell_percent, sell_count)

                                elif adjust_percent < 0:
                                    last_fund = fund
                                    print('buy')

                                    buy_percent = int((adjust_percent / buy_adjust_percent_total) * 100)
                                    print('adjust_percent / buy_adjust_percent_total:%s', adjust_percent,
                                          buy_adjust_percent_total)
                                    print(buy_percent)
                                    buy_percent_list.append(buy_percent)

                                    buy_percent_total += buy_percent
                                    buy_dict[fund] = buy_percent
                                    print('buy_percent:', buy_percent)

                            # print('sell_percent_list:',sell_percent_list)
                            # print('sell_count_list:',sell_count_list)
                            print('buy_percent_list:', buy_percent_list)
                            print('sell_dict, buy_dict:', sell_dict, buy_dict)
                            print('buy_percent_total', buy_percent_total)
                            print(last_fund)
                            # 填充100的percent
                            # buy_percent_list[0] += 100 - buy_percent_total
                            buy_dict[last_fund] += 100 - buy_percent_total
                            # acount_total.append([buy_fund_list,sell_percent_list,sell_count_list,buy_percent_list])
                            acount_total.append([sell_dict, buy_dict])
                        except Exception as e:
                            # print('这个acount出错:', acount)
                            print(e)
                            continue
                        else:
                            acount_fund_lists.append(acount_fund_list)
                        print('acount_total~~~~~~~~~~~~:', acount_total)


                        # 点击%
                        self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='P']")
                        # 选择卖出的基金
                        # for index in range(2, 20):
                        for index,fund in enumerate(acount_fund_list):
                            print("//table[@id='Datagrid3']//tr[" + str(index) + "]/td[@class='LightGrey'][2]/span")
                            # if self.wait_until(driver=driver, platform='standard_life',
                            #                    selector_name="//table[@id='Datagrid3']//tr[" + str(
                            #                            index) + "]/td[@class='LightGrey'][2]/span",
                            #                    action='text') == sellFundCode:
                            if fund in sell_dict.keys():
                                self.wait_until(driver=driver, platform='standard_life',
                                                selector_name="//input[@id='Datagrid3__ctl" + str(
                                                    index+2) + "_Textbox1']")
                                # self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='Datagrid3__ctl"+str(index)+"_Textbox1']",action='clear')
                                self.random_sleep()
                                self.wait_until(driver=driver, platform='standard_life',
                                                selector_name="//input[@id='Datagrid3__ctl" + str(
                                                    index+2) + "_Textbox1']", action='send_keys',
                                                send_keys=sell_dict[fund])
                                # break
                        self.random_sleep()
                        # 选择买入的基金
                        buyIndex = 1
                        for buyFundName, buyFundPercent in buy_dict.items():
                            select = Select(driver.find_element_by_name('switch_in:ddl_fundhse_' + str(buyIndex)))
                            self.random_sleep()
                            select.select_by_visible_text(targetFundPercentCompany[buyFundName])
                            self.random_sleep()
                            select = Select(driver.find_element_by_name('switch_in:ddl_fundname_' + str(buyIndex)))
                            self.random_sleep()
                            select.select_by_visible_text(buyFundName)
                            self.random_sleep()
                            self.wait_until(driver=driver, platform='standard_life',
                                            selector_name="//input[@id='switch_in_tbox_alloc_" + str(buyIndex) + "']",
                                            action='clear')
                            self.wait_until(driver=driver, platform='standard_life',
                                            selector_name="//input[@id='switch_in_tbox_alloc_" + str(buyIndex) + "']",
                                            action='send_keys', send_keys=buyFundPercent)
                            if len(buy_dict) > buyIndex:
                                print('buyFundCode,buyIndex：', len(buy_dict), buyIndex)
                                self.wait_until(driver=driver, platform='standard_life',
                                                selector_name="//input[@id='Enable']")
                            buyIndex += 1
                            self.random_sleep()
                        # 点击继续
                        self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='btnNext']")
                        self.random_sleep()
                        # 点击勾选
                        self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='cbox']")
                        self.random_sleep()
                        # 点击确定
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//input[@id='btnConfirm']")
                        self.random_sleep()
                        self.random_sleep()
                        driver.save_screenshot(
                            '成功调仓截图文件夹/standard_life/' + str(self.policyNumber) + str(self.riskType) + ".png")
                        self.random_sleep()
                        # 点击服务专区主页
                        self.wait_until(driver=driver, platform='standard_life', selector_way='LINK_TEXT',
                                        selector_name="服務專區主頁")
                        self.random_sleep()
                    except:
                        print('选择下拉框失败')
                    else:
                        print('选择下拉框完成')
                # 点击未来供款
                self.wait_until(driver=driver, platform='standard_life',
                                selector_name="//ul[@id='subNav']/li[3]/a")
                self.random_sleep()
                # 选择投资户口
                try:
                    select = Select(driver.find_element_by_name('lbInvestmentACCD'))
                    select_range = 20
                except:
                    print('没有投资户口下拉框')
                    select_range = 1
                print('selected')
                self.random_sleep()
                for index in range(select_range):
                    try:
                        try:
                            # 选择户口
                            select.select_by_index(index)
                        except:
                            print('没有投资户口下拉框')
                        self.random_sleep()
                        buyIndex = 1
                        for buyFundName, buyFundPercent in targetFundPercentInit:
                            select = Select(driver.find_element_by_name('switch_in:ddl_fundhse_' + str(buyIndex)))
                            self.random_sleep()
                            select.select_by_visible_text(targetFundPercentCompany[buyFundName])
                            self.random_sleep()
                            select = Select(driver.find_element_by_name('switch_in:ddl_fundname_' + str(buyIndex)))
                            self.random_sleep()
                            select.select_by_visible_text(buyFundName)
                            self.random_sleep()
                            self.wait_until(driver=driver, platform='standard_life',
                                            selector_name="//input[@id='switch_in_tbox_alloc_" + str(buyIndex) + "']",
                                            action='clear')
                            self.wait_until(driver=driver, platform='standard_life',
                                            selector_name="//input[@id='switch_in_tbox_alloc_" + str(buyIndex) + "']",
                                            action='send_keys', send_keys=buyFundPercent)
                            if len(targetFundPercentInit) > buyIndex:
                                print('buyFundCode,buyIndex：', len(targetFundPercentInit), buyIndex)
                                self.wait_until(driver=driver, platform='standard_life',
                                                selector_name="//input[@id='Enable']")
                            buyIndex += 1
                            self.random_sleep()
                        # 点击继续
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//input[@id='btnNext']")
                        self.random_sleep()
                        # 点击勾选
                        self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='cbox']")
                        self.random_sleep()
                        # 点击确定
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//input[@id='btnConfirm']")
                        self.random_sleep()
                        self.random_sleep()
                        # 配置成功，截图
                        if self.error == 0:
                            self.successed += 1
                            driver.save_screenshot(
                                '成功调仓截图文件夹/standard_life/' + str(self.policyNumber) + str(self.riskType) + ".png")
                            print(self.policyNumber, '成功调仓截图中')
                            self.write_excel(policy_index=self.standard_life_index[self.enum_index])
                            print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')

                        self.random_sleep()
                    except:
                        print('选择下拉框失败')
                    else:
                        print('选择下拉框完成')

                driver.quit()
            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/standard_life/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.quit()

    def standard_life_login_test(self, standard_life):
        """
        zurich调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        if not standard_life:
            print('standard_life无需调仓的保单！')
            return
        self.counts = len(standard_life)
        print('------------')
        for index, item in enumerate(standard_life):
            try:
                self.random_sleep(3,10)
                self.operation_counts += 1
                self.enum_index = index
                # 保单号
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                # 用户名及密码
                username = str(item[2])
                password = str(item[3])

                url = 'https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch'

                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    # "Content-Length": "855",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Cookie": "login_from=c; _ga=GA1.2.2035424506.1514431725; _gid=GA1.2.1545079845.1519869848; _dc_gtm_UA-62877774-1=1; hidToken=MjAxOC0wMy0wMSAxMDo0Nzo0NS45MzA=; hidVD=/login; ASP.NET_SessionId=q0ucqq4l12bsomxo4s3kf2hz",
                    "Host": "www.standardlife.hk",
                    "Origin": "https://www.standardlife.hk",
                    "Referer": "https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
                }

                data = {
                    # "__EVENTTARGET": "",
                    # "__EVENTARGUMENT": "",
                    # "__VIEWSTATE": "/wEPDwUKMTI4OTM0MDc3Nw9kFgYCAg9kFgRmDw8WAh4EVGV4dAUJSG9uZyBLb25nZGQCAQ8PFgIfAAUyPGEgaHJlZj0ibG9naW5fYm5jLmFzcHg/bG9naW5fZnJvbT1jJmxhbmc9Y2giPjwvYT5kZAIDD2QWCAIDDxYCHgV2YWx1ZQUG55m75YWlZAIEDxYCHwEFBuWPlua2iGQCBg8PFgQeDEVycm9yTWVzc2FnZQUW6KuL6Ly45YWl55So5oi25ZCN56ixIR4HVmlzaWJsZWhkZAIHDw8WBB8CBRDoq4vovLjlhaXlr4bnorwhHwNoZGQCBA8WBB8BBQbnmbvoqJgeB29uY2xpY2sFQWphdmFzY3JpcHQ6IHNlbGYubG9jYXRpb24uaHJlZj0nc2lnbnVwL3NpZ251cF9vcmkxLmFzcHg/bGFuZz1jaCc7ZGRoLf0sHYaMuosyNYwLu33f6QZcN5+ST4l88V1V5Cc2/A==",
                    # "__VIEWSTATEGENERATOR": "8AA00206",
                    # "__EVENTVALIDATION": "/wEdAAUeH57yDkX4HY5qJ7J0J5vmwTsQWw6y6U5GrbZKe7xDC5F8FshjtXqo3Hg5+xfiAwIv8m/1VahZrxjv/SWm8XxLcNVahIS9ELOYiVfSrKeler2R8SNJd9+8/HyayjlUcGmwY1xoPi3ckN+XQDQ11Otx",
                    "login_from": "c",
                    "txt_name": username,
                    "txt_password": password,
                    "btn_Login": "登入"
                }

                response = requests.post(url=url, headers=headers, data=data).text

                print(response)
                if '登入資料不正確' in response:
                    print(str(self.policyNumber), '：error!登录失败！')
                    self.write_excel(policy_index=self.standard_life_index[self.enum_index], policy_col=13, message='登录失败')
                else:
                    self.successed += 1
                    print(str(self.policyNumber), '：登录成功！')
                    self.write_excel(policy_index=self.standard_life_index[index], policy_col=13)
            except Exception as e:
                print(self.policyNumber,'error!:',e)

    def standard_life_spider(self, standard_life):
        """
        zurich调仓操作
        :param zurich: zurich data list
        :return: operating
        """
        if not standard_life:
            print('standard_life无需spider的保单！')
            return
        print('------------')
        # 调出浏览器
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver_linux64/chromedriver") # , executable_path="./chromedriver_linux64/chromedriver"
        # driver = webdriver.PhantomJS()
        # 打开Chrome浏览器登录
        url = "https://www.standardlife.hk/login/login_bnc.aspx?login_from=c&lang=ch"
        for index, item in enumerate(standard_life):
            # 链接数据库
            self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',database='data_finance_oversea', charset='utf8')
            self.error = 0
            self.operation_counts += 1
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])
                # 卖出基金

                self.random_sleep()
                username = str(item[2])
                password = str(item[3])

                # 发送链接
                driver.get(url)
                driver.set_page_load_timeout(100)
                # 窗口最大化
                # driver.maximize_window()
                self.random_sleep()
                # 点击特别安排的OK
                try:
                    driver.find_element_by_xpath("//div[@class='ui-dialog-buttonset']/button/span").click()
                except:
                    pass
                # 登录
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
                                action='clear')
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_name']",
                                action='send_keys', send_keys=username)
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
                                action='clear')
                self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='txt_password']",
                                action='send_keys', send_keys=password)
                # self.wait_until(driver=driver, platform='standard_life', selector_name="//input[@id='btn_Login']")
                driver.find_element_by_xpath("//input[@id='btn_Login']").click()
                self.random_sleep()
                try:
                    response = driver.page_source
                    responses = etree.HTML(response).xpath("//table[@id='tblPolInfoSum']//tr//td[@class='LightGrey']/a")
                except Exception as e:
                    print(e,'error,可能账户正在被登陆中',username)
                    driver.quit()
                    # 调出浏览器
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--disable-gpu')
                    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="./chromedriver_linux64/chromedriver")  # , executable_path="./chromedriver_linux64/chromedriver"
                    # driver = webdriver.PhantomJS()
                    continue
                print(username, ':Login')
                for index,response in enumerate(responses):
                    print(response.text)
                    Policy_Num = response.text
                    self.random_sleep()
                    # self.wait_until(driver=driver, platform='standard_life', selector_name="//table[@id='tblPolInfoSum']//tr["+str(index+2)+"]/td[@class='LightGrey']/a")
                    # 切换至新窗口
                    policyLink = str(driver.find_element_by_xpath("//table[@id='tblPolInfoSum']//tr["+str(index+2)+"]/td[@class='LightGrey']/a").get_attribute("href"))
                    js = 'window.open("' + policyLink + '");'
                    driver.execute_script(js)
                    # print(driver.window_handles)
                    # 其中一个保单号
                    driver.switch_to.window(driver.window_handles[1])
                    response = etree.HTML(driver.page_source)
                    # response = response.xpath("//table[@id='pol_sum_menu_tableLink']//tr//td/span[@class='blue']/a")
                    Date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                    Currency = response.xpath("//span[@id='pol_details_lbPolCur']//text()")
                    Total_Premium = response.xpath("//span[@id='lbPVSContribution']//text()") if response.xpath("//span[@id='lbPVSContribution']") else ''
                    Total_withdrawal = response.xpath("//span[@id='lbPVSWithdrawals']//text()") if response.xpath("//span[@id='lbPVSWithdrawals']") else ''
                    Payment_Frequency = response.xpath("//span[@id='pay_info_lbPIPayFeq']//text()") if response.xpath("//span[@id='pay_info_lbPIPayFeq']") else ''
                    Regular_Premium = response.xpath("//span[@id='pay_info_lbPIContribution']//text()") if response.xpath("//span[@id='pay_info_lbPIContribution']") else ''
                    print('Policy_Num,Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium:',Policy_Num,Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)
                    if self.cur.execute("select * from standardlife_premium_info where Policy_Num='" + Policy_Num + "';"):
                        self.try_except(self.cur.execute("delete from standardlife_premium_info where Policy_Num='" + Policy_Num + "';"))
                    self.try_except(self.cur.execute("insert into standardlife_premium_info(Policy_Num,Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (Policy_Num,Date,Currency,Total_Premium,Total_withdrawal,Payment_Frequency,Regular_Premium)))

                    # 未来供款
                    titles = response.xpath("//div[@class='largeSizeHolder1000']/div/span[@class='h2']//text()")
                    print(titles)
                    for index,title in enumerate(titles):
                        if '戶口' in title:
                            length = len(response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[3]"))
                            Investment_Account0 = str(re.sub("\D", "", title))
                            Investment_Account = [Investment_Account0[:2]]*length
                            Account_Type = ['01']*length if '最初' in title else ['02']*length
                            account_type = '01' if '最初' in title else '02'
                            Allocation_In_Policy_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[3]//text()")
                            Allocation = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[2]//text()")
                            Allocation_Fund_Name = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@id='Table_Alloc']//tr/td[1]//text()")[1:-1]
                            print(index,'Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name',Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)
                            if self.cur.execute("select * from StandardLife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "';"):
                                self.try_except(self.cur.execute("delete from StandardLife_Future_Investment_Contribution where Policy_Num='" + Policy_Num + "' and Investment_Account='" + Investment_Account0[:2] + "' and Account_Type='" + account_type + "';"))
                            for Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name in zip(Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name):
                                print(Policy_Num,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)
                                self.try_except(self.cur.execute("insert into StandardLife_Future_Investment_Contribution(Policy_Num,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                    (Policy_Num,Date,Investment_Account,Account_Type,Allocation_In_Policy_Currency,Allocation,Allocation_Fund_Name)))
                            Fund_Name = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][1]//text()")
                            Reference_Code = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][2]//text()")
                            Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][3]//text()")
                            Unit = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][4]//text()")
                            Price = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][6]//text()")
                            Weight = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][7]//text()")
                            Value_In_Fund_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][8]//text()")
                            Value_In_Policy_Currency = response.xpath("//div[@class='largeSizeHolder1000']["+str(index)+"]//table[@class='transLogTable'][3]//tr/td[@class='LightGrey'][9]//text()")
                            print('Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency:',Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                            if self.cur.execute("select * from StandardLife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "';"):
                                self.try_except(self.cur.execute("delete from StandardLife_Account_Allocation where Policy_Num='" + Policy_Num + "' and Investment_Account='"+ Investment_Account0[:2]+"' and Account_Type='"+ account_type + "';"))
                            for Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency in zip(Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency):
                                print(Policy_Num,Date,Fund_Name,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)
                                self.try_except(self.cur.execute("insert into StandardLife_Account_Allocation(Policy_Num,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                    (Policy_Num,Date,Fund_Name,Investment_Account,Account_Type,Reference_Code,Currency,Unit,Price,Weight,Value_In_Fund_Currency,Value_In_Policy_Currency)))

                    # 点击交易日志
                    self.wait_until(driver=driver, platform='standard_life', selector_name="//table[@id='pol_sum_menu_tableLink']//tr//td//a[2]")
                    self.random_sleep()
                    response = etree.HTML(driver.page_source)
                    Payment_date = response.xpath("//table[@id='tblPH']/tbody//tr/td[1]//text()")
                    Premium_due_Date = response.xpath("//table[@id='tblPH']/tbody//tr/td[2]//text()")
                    Payment_Method = response.xpath("//table[@id='tblPH']/tbody//tr/td[3]//text()")
                    Policy_Currency = response.xpath("//table[@id='tblPH']/tbody//tr/td[4]//text()")
                    Premium = response.xpath("//table[@id='tblPH']/tbody//tr/td[5]//text()")
                    Status = response.xpath("//table[@id='tblPH']/tbody//tr/td[6]//text()")
                    Remark = response.xpath("//table[@id='tblPH']/tbody//tr/td[7]//text()")
                    print('Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark:',Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
                    for Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark in zip(Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark):
                        print(Policy_Num,Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)
                        if not self.cur.execute("select * from StandardLife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + Payment_date + "';"):
                            # self.try_except(self.cur.execute("delete from StandardLife_Premium where Policy_Num='" + Policy_Num + "' and Payment_date='" + Payment_date + "';"))
                            self.try_except(self.cur.execute("insert into StandardLife_Premium(Policy_Num,Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Policy_Num,Date,Payment_date,Premium_due_Date,Payment_Method,Policy_Currency,Premium,Status,Remark)))
                    # 搞定其中一个保单号
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                self.mysql_client.commit()
                # self.cur.close()
                self.mysql_client.close()
                # 登出
                self.wait_until(driver=driver, platform='standard_life', selector_name="//li[@class='globalCustomerLogin']/a/img")
                print(username,Policy_Num,':Logout')
                # 删除所有cookies，以便下个用户登录
                driver.delete_all_cookies()
                # 单击登出

            except Exception as e:
                # 登出
                self.wait_until(driver=driver, platform='standard_life',
                                selector_name="//li[@class='globalCustomerLogin']/a/img")
                print(username, Policy_Num, ':Logout')
                self.random_sleep(60,61)
                # continue
                print(str(self.policyNumber) + str(self.riskType), e,'：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/standard_life/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.quit()
        driver.quit()
        self.cur.close()
        self.mysql_client.close()

    def axa_operation(self, axa):
        """
        axa调仓操作
        :param axa: axa data list
        :return: operating
        """
        if not axa:
            print('axa无需调仓的保单！')
            return
        print('------------')
        # 打开Chrome浏览器登录
        url = "https://www1.e-axa.com.hk/Life/changeLocale.do?methodName=changeLocale&language=zh&country=HK"
        for index, item in enumerate(axa):
            # 检查是否够钟落班
            self.check_workoff()
            self.operation_counts += 1
            self.error = 0
            self.enum_index = index
            try:
                # 保单号,如 T25W017027
                self.policyNumber = str(item[0])
                # 风险类型
                self.riskType = str(item[1])

                # 调整基金
                adjustFundCode = '07TU'
                # targetFundPercent = [0,0,15,25,20,25,15] if self.riskType == '增长型' else [0,0,15,20,30,20,15]
                targetFundPercentInit = collections.OrderedDict()
                targetFundPercentInit['貝萊德全球基金-新能源基金'] = 10 if self.riskType == '增长型' else 0
                targetFundPercentInit['貝萊德全球基金-世界健康科學基金'] = 15 if self.riskType == '增长型' else 0
                targetFundPercentInit['富達基金-美元現金基金'] = 10 if self.riskType == '增长型' else 15
                targetFundPercentInit['富達基金-美國基金'] = 10 if self.riskType == '增长型' else 20
                targetFundPercentInit['富達基金-美元債券基金'] = 25 if self.riskType == '增长型' else 30
                targetFundPercentInit['富達基金-國際基金'] = 25 if self.riskType == '增长型' else 20
                # targetFundPercentInit['百達-數碼科技'] = 50 if self.riskType == '增长型' else 15
                targetFundPercentInit['百達-數碼科技'] = 5 if self.riskType == '增长型' else 15

                # buyCompany = ['天達資產管理', '施羅德投資管理(香港)有限公司']
                # buyFundCode = ['富達基金-美國基金','富達基金-美元債券基金','富達基金-國際基金','百達-數碼科技']
                # buyFundPercent = [15,25,20,25,15] if self.riskType == '增长型' else [15,20,30,20,15]
                # buyFund = zip(buyCompany, buyFundCode, buyFundPercent)
                # fundLength = len(buyFundCode)

                self.random_sleep()
                username = str(item[2])
                password = str(item[3])

                # 调出浏览器
                driver = webdriver.Chrome()
                # 发送链接
                driver.get(url)
                # 窗口最大化
                driver.maximize_window()
                self.random_sleep()

                # 登录
                self.wait_until(driver=driver, platform='axa', selector_name="//input[1]",
                                action='clear')
                self.wait_until(driver=driver, platform='axa', selector_name="//input[1]",
                                action='send_keys', send_keys=username)
                self.wait_until(driver=driver, platform='axa', selector_name="//input[2]",
                                action='clear')
                self.wait_until(driver=driver, platform='axa', selector_name="//input[2]",
                                action='send_keys', send_keys=password)
                self.wait_until(driver=driver, platform='axa', selector_name="//tr/td[2]/a/img")
                self.random_sleep()
                self.random_sleep()

                # 切换至小页面点击接受
                driver.switch_to.window(driver.window_handles[1])
                self.wait_until(driver=driver, platform='axa', selector_name="//tr/td[1]/input")
                self.random_sleep()

                # 识别对应的保单号，点击进入详情页
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[0])
                for i in range(1,20):
                    # if self.wait_until(driver=driver, platform='axa',selector_name="//tr/td[@class='cellFlesh']["+str(i)+"]/span/a",action='text') == self.policyNumber:
                    if driver.find_element_by_xpath("//tr["+str(i)+"]/td[@class='cellFlesh']/span/a").text == self.policyNumber:
                        # self.wait_until(driver=driver, platform='axa',selector_name="//tr/td[@class='cellFlesh']["+str(i)+"]/span/a")
                        driver.find_element_by_xpath("//tr["+str(i)+"]/td[@class='cellFlesh']/span/a").click()
                        break
                # 点击户口价值
                self.wait_until(driver=driver, platform='axa',selector_name="//tr/td[5]/a[@class='lnkTabTitle']")
                # 读取“投資基金”、“單位數目”、“戶口基金總值(以保單貨幣計算)”
                acount_fund_lists = []
                # sell_percent_list = []
                # sell_count_list = []
                acount_total = []
                for acount in range(5,10):
                    buy_adjust_percent_total = 0
                    buy_percent_total = 0
                    fund_length = 0
                    total_value = 0
                    buy_fund_list = []
                    acount_fund_list = []
                    acount_count_list = collections.OrderedDict()
                    acount_value_list = collections.OrderedDict()
                    buy_percent_list = []
                    print('Now_acount：',acount)
                    try:
                        for i in range(1,20):
                            try:
                                # print("//table["+str(acount)+"]//tr[@class='TROddRowColor']["+str(i)+"]/td[@class='cellGrey'][1]")
                                fund = driver.find_element_by_xpath("//table["+str(acount)+"]//tr[@class='TROddRowColor']["+str(i)+"]/td[@class='cellGrey'][1]").text
                                count = driver.find_element_by_xpath("//table["+str(acount)+"]//tr[@class='TROddRowColor']["+str(i)+"]/td[@class='cellGrey'][5]").text.replace(',','')
                                value = driver.find_element_by_xpath("//table["+str(acount)+"]//tr[@class='TROddRowColor']["+str(i)+"]/td[@class='cellGrey'][9]").text.replace(',','')
                                print('fund,count,value:',fund,count,value)
                                acount_fund_list.append(fund)
                                acount_count_list[fund] = float(count)
                                # acount_count_list.append(float(count))
                                acount_value_list[fund] = float(value)
                                # acount_value_list.append(float(value))
                                total_value += float(value)
                                fund_length += 1
                            except:
                                print('fund有%s个' %fund_length)
                                break

                        # acount_fund_lists.append(acount_fund_list)
                        print('acount_fund_list,acount_fund_lists:',acount_fund_list,acount_fund_lists)
                        targetFundPercent = deepcopy(targetFundPercentInit)
                        print('targetFundPercent1', targetFundPercent)
                        # 找出与目标比例基金所不同的基金
                        for fund_redundant in acount_fund_list:
                            if fund_redundant not in targetFundPercent.keys():
                                print('有多余的基金',fund_redundant)
                                targetFundPercent[fund_redundant] = 0
                                fund_length += 1
                        for fund_redundant in targetFundPercent.keys():
                            if fund_redundant not in acount_fund_list:
                                print('有需补充的基金',fund_redundant)
                                acount_fund_list.append(fund_redundant)
                                acount_count_list[fund_redundant] = 0
                                acount_value_list[fund_redundant] = 0
                                fund_length += 1
                        # fund_length = len(targetFundPercent)
                        print('targetFundPercent2',targetFundPercent)
                        print('acount_fund_list',acount_fund_list)
                        print('acount_count_list：',acount_count_list)
                        print('acount_value_list：',acount_value_list)

                        # 计算调整比例的和
                        # for length in range(fund_length):
                        for fund in targetFundPercent.keys():
                            present_percent = (acount_value_list[fund] / total_value)*100
                            adjust_percent = present_percent - targetFundPercent[fund]
                            if adjust_percent < 0:
                                buy_adjust_percent_total += adjust_percent
                                buy_fund_list.append(fund)
                        print('buy_adjust_percent_total:',buy_adjust_percent_total)
                        print('buy_fund_list:',buy_fund_list)

                        # 卖出列表
                        sell_dict = collections.OrderedDict()
                        # 买入列表
                        buy_dict = collections.OrderedDict()
                        # 所有需要操作的基金
                        # for length in range(fund_length):
                        for length,fund in enumerate(targetFundPercent.keys()):
                            print('目前为第%s支个基金：',length+1)
                            present_percent = (acount_value_list[fund] / total_value)*100
                            print(fund,'present_percent',present_percent)
                            adjust_percent = present_percent - targetFundPercent[fund]
                            print(fund,'adjust_percent', adjust_percent)
                            if adjust_percent > 0:
                                print('sell')
                                sell_percent = round(float(adjust_percent/present_percent),2)
                                sell_count = round(float(sell_percent*acount_count_list[fund]),4)
                                # sell_percent_list.append(sell_percent)
                                # sell_count_list.append(sell_count)

                                sell_dict[fund] = sell_count
                                print('sell_percent,sell_count:',sell_percent,sell_count)

                            elif adjust_percent < 0:
                                last_fund = fund
                                print('buy')

                                buy_percent = int((adjust_percent / buy_adjust_percent_total)*100)
                                print('adjust_percent / buy_adjust_percent_total:%s',adjust_percent,buy_adjust_percent_total)
                                print(buy_percent)
                                buy_percent_list.append(buy_percent)

                                buy_percent_total += buy_percent
                                buy_dict[fund] = buy_percent
                                print('buy_percent:',buy_percent)

                        # print('sell_percent_list:',sell_percent_list)
                        # print('sell_count_list:',sell_count_list)
                        print('buy_percent_list:',buy_percent_list)
                        print('sell_dict, buy_dict:',sell_dict, buy_dict)
                        print('buy_percent_total',buy_percent_total)
                        print(last_fund)
                        # 填充100的percent
                        # buy_percent_list[0] += 100 - buy_percent_total
                        buy_dict[last_fund] += 100 - buy_percent_total
                        # acount_total.append([buy_fund_list,sell_percent_list,sell_count_list,buy_percent_list])
                        acount_total.append([sell_dict,buy_dict])
                    except Exception as e:
                            print('这个acount出错:',acount)
                            print(e)
                            continue
                    else:
                        acount_fund_lists.append(acount_fund_list)
                print('acount_total~~~~~~~~~~~~:',acount_total)


                # # 点击投资基金交易
                # self.wait_until(driver=driver, platform='axa',selector_name="//td[3]//table[1]//tr//td[2]/a")
                # self.random_sleep()
                # # 点击基金投资交易，进入更改未来配置页面
                # self.wait_until(driver=driver, platform='axa',selector_name="//table/tbody/tr/td[3]/a[@class='lnkTabTitle']")
                # self.random_sleep()
                # # 切换窗口点击关闭
                # driver.switch_to.window(driver.window_handles[1])
                # self.random_sleep()
                # self.wait_until(driver=driver, platform='axa',selector_name="//input")
                # self.random_sleep()
                # driver.switch_to.window(driver.window_handles[0])
                # self.random_sleep()
                # futher_fundName_list = ['富達基金-美元現金基金','富達基金-美國基金','富達基金-美元債券基金','富達基金-國際基金','百達-數碼科技']
                # futher_fundPercent_list = [15,25,20,25,15] # if self.riskType =='增长型' else [15,20,30,20,15]
                # futher_fund_list = zip(futher_fundName_list,futher_fundPercent_list)
                # futherIndex = 0
                # # 选择买入基金
                # for futher_fundName,futher_fundPercent in futher_fund_list:
                #     # 选择基金
                #     select = Select(driver.find_element_by_name('fundAllocationChanges[' + str(futherIndex) + '].fundCode'))
                #     self.random_sleep()
                #     select.select_by_visible_text(futher_fundName)
                #     self.random_sleep()
                #     # 清空并输入比例
                #     self.wait_until(driver=driver, platform='standard_life',selector_name="//tr[@id='fundlist" + str(futherIndex+1) + "']/td[2]/input",
                #                     action='clear')
                #     self.wait_until(driver=driver, platform='standard_life',
                #                     selector_name="//tr[@id='fundlist" + str(futherIndex+1) + "']/td[2]/input",
                #                     action='send_keys', send_keys=futher_fundPercent)
                #     futherIndex += 1
                #     self.random_sleep()
                # # self.random_sleep(1000,2000)
                # # 点击提交
                # # self.wait_until(driver=driver, platform='axa',selector_name="//form[1]//tr//td/img[1]")
                # self.random_sleep()
                # self.random_sleep()
                # driver.save_screenshot(
                #     '成功调仓截图文件夹/axa/' + str(self.policyNumber) + str(self.riskType) + ".png")
                # # 点击确认
                # self.random_sleep()
                # # self.wait_until(driver=driver, platform='axa',selector_name="//form[1]//tr//td/img[1]")
                # # 点击保单查询
                # self.wait_until(driver=driver, platform='axa',selector_name="//table[2]/tbody/tr[14]/td[2]//a")
                # self.random_sleep()
                # # 识别对应的保单号，点击进入详情页
                # driver.switch_to.window(driver.window_handles[0])
                # for i in range(1, 20):
                #     if self.wait_until(driver=driver, platform='axa',
                #                        selector_name="//tr/td[@class='cellFlesh'][" + str(i) + "]/span/a",
                #                        action='text') == self.policyNumber:
                #         self.wait_until(driver=driver, platform='axa',
                #                         selector_name="//tr/td[@class='cellFlesh'][" + str(i) + "]/span/a")
                #         break

                # 点击投资基金交易
                self.wait_until(driver=driver, platform='axa',selector_name="//td[3]//table[1]//tr//td[2]/a")
                self.random_sleep()
                # 点击基金转换
                self.wait_until(driver=driver, platform='axa',selector_name="//table[2]//tr/td[5]/a")
                # 切换窗口点击关闭
                driver.switch_to.window(driver.window_handles[1])
                self.random_sleep()
                self.wait_until(driver=driver, platform='axa', selector_name="//input")
                self.random_sleep()
                driver.switch_to.window(driver.window_handles[0])
                self.random_sleep()
                # 根据不同户口，买入和卖出基金

                for index0,acount in enumerate(acount_total):
                    print('index0:',index0)
                    input_add = ''
                    fundlist_add = 'IUA'
                    if index0 == 1:
                        input_add = 'Two'
                        fundlist_add = 'AUA'
                    elif index0 == 2:
                        input_add = 'Three'
                        fundlist_add = 'IUA'
                    elif index0 == 3:
                        input_add = 'Four'
                        fundlist_add = 'AUA'
                    elif index0 == 4:
                        input_add = 'Five'
                    elif index0 == 5:
                        input_add = 'Six'
                    # 点击下一个户口账户
                    if index0 != 0:
                        driver.save_screenshot(
                            '成功调仓截图文件夹/axa/' + str(self.policyNumber) + str(self.riskType) + "0.png")
                        print('点击下一个户口账户')
                        self.wait_until(driver=driver, platform='axa', selector_name="//tr[@id='buttons_showdiv_IUA']/td["+str(2*(index0+1)-1)+"]/span/a[@class='lnkTabTitle']")
                        self.random_sleep()
                        self.random_sleep()
                    self.random_sleep()

                    # 查询需要卖出的基金并且输入赎回单位
                    # all_funds = self.wait_until(driver=driver, platform='axa', selector_name="//tr[@class='TROddRowColor']/td[@class='cellGrey'][1]",action='text')
                    # print(all_funds)
                    print('acount_fund_list',acount_fund_lists[index0])
                    print('``````````',acount[0].keys())
                    for index1,fund in enumerate(acount_fund_lists[index0]):
                    # for index1,fund in enumerate(all_funds):
                        print('~~~~~~~~~~fund',fund)
                        if fund in acount[0].keys():
                            print('index1',index1)
                            print("//tr[@class='TROddRowColor']["+str(index1+1)+"]/td[@class='cellGrey']//input[@id='noOfUnit"+input_add+str(index1)+"']")
                            self.wait_until(driver=driver, platform='axa', selector_name="//tr[@class='TROddRowColor']["+str(index1+1)+"]//td[@class='cellGrey']//input[@id='noOfUnit"+input_add+str(index1)+"']",action='clear')
                            print('clear')
                            self.wait_until(driver=driver, platform='axa', selector_name="//tr[@class='TROddRowColor']["+str(index1+1)+"]//td[@class='cellGrey']//input[@id='noOfUnit"+input_add+str(index1)+"']",action='send_keys',send_keys=acount[0][fund])
                    # 选择买入基金
                    print('------------', acount[1].items())
                    futherIndex = 0
                    for buy_fundName, buy_fundPercent in acount[1].items():

                        # 选择基金
                        select = Select(driver.find_element_by_name('switchToFunds[' + str((index0*10)+futherIndex) + '].fundCode'))
                        self.random_sleep()
                        select.select_by_visible_text(buy_fundName)
                        self.random_sleep()
                        # 清空并输入比例
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//tr[@id='fundlist_"+ fundlist_add + str(futherIndex + 1) + "']/td[2]/input",
                                        action='clear')
                        self.wait_until(driver=driver, platform='standard_life',
                                        selector_name="//tr[@id='fundlist_"+ fundlist_add + str(futherIndex + 1) + "']/td[2]/input",
                                        action='send_keys', send_keys=buy_fundPercent)
                        futherIndex += 1
                        self.random_sleep()

                # 点击确认
                # self.wait_until(driver=driver, platform='axa', selector_name="//table[3]/tbody/tr/td/img[1]")
                # 切换窗口点击关闭
                # driver.switch_to.window(driver.window_handles[1])
                # self.random_sleep()
                # self.wait_until(driver=driver, platform='axa', selector_name="//input")
                # self.random_sleep()
                # driver.switch_to.window(driver.window_handles[0])
                # self.random_sleep()
                # 配置成功，截图
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot(
                        '成功调仓截图文件夹/axa/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    print(self.policyNumber, '成功调仓截图中')
                    self.write_excel(policy_index=self.axa_index[self.enum_index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')

                # 点击确认并接纳
                # self.wait_until(driver=driver, platform='axa', selector_name="//table[3]/tbody/tr/td/img[1]")
                # 点击登出
                self.wait_until(driver=driver, platform='axa', selector_name="//table//tr/td[2]/a/img")

                driver.quit()
            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot(
                    '调仓失败截图文件夹/axa/' + str(self.policyNumber) + str(self.riskType) + ".png")
                print(self.policyNumber, '失败调仓截图中')
                self.write_excel(policy_index=self.axa_index[self.enum_index], message='调仓失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.quit()

    def axa_operation_login_test(self, axa):
        """
        axa调仓操作
        :param axa: axa data list
        :return: operating
        """
        if not axa:
            print('axa无需调仓的保单！')
            return
        print('------------')
        for index, item in enumerate(axa):
            self.random_sleep(3, 10)
            self.operation_counts += 1
            self.enum_index = index
            # 保单号,如 T25W017027
            self.policyNumber = str(item[0])
            # 风险类型
            self.riskType = str(item[1])
            username = str(item[2])
            password = str(item[3])
            try:
                axa_login_url = 'https://www1.e-axa.com.hk/Life/login.do;jsessionid=YXdVhXxcCY9pdFNPlYVyzwpTv9Jkr9pg0BSZ7b39nG6v0n868yCj!31778653?methodName=login'
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

                response = requests.post(url=axa_login_url, headers=axa_headers, data=axa_data).text
                # print(response)

                if 'Welcome,' in response:
                    print('登录成功')
                    self.write_excel(policy_index=self.axa_index[self.enum_index], policy_col=13)
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')

                else:
                    print('登录失败')
                    print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                    self.write_excel(policy_index=self.axa_index[self.enum_index], policy_col=13, message='登录失败')

            except Exception as e:
                print(self.policyNumber,'error!:',e)

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
                    zurich.append((policyNumber,  riskType, userName, passWord))
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
                elif str(policyNumber).startswith("5") and '-' in str(policyNumber) and operationSituation != '调仓成功' and operationSituation != '登录失败':
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
        self.cur = self.mysql_client.cursor()
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
        # print('\n正在进行axa_login_test调仓操作....')
        # self.axa_operation_login_test(data[4])
        # print('\n正在进行Hansard调仓操作....')
        # self.hansard_operation(data[0])
        # print('\n正在进行ITA调仓操作....')
        # self.ita_operation(data[1])
        # print('\n正在进行zurich调仓操作....')
        # self.zurich_operation(data[2])
        # print('\n正在进行zurich_spider调仓操作....')
        # self.zurich_spider(data[2])
        # print('\n正在进行zurich_emergency调仓操作....')
        # self.zurich_operation_emergency(data[2])
        # print('\n正在进行standard_life调仓操作....')
        # self.standard_life_operation(data[3])
        # print('\n正在进行axa调仓操作....')
        # self.axa_operation(data[4])
        print('\r\n调仓完毕！其中调仓成功 %s个/总数%s个。' % (self.successed, self.counts))
        # self.send_email()


if __name__ == '__main__':
    auto_operation = AutoOperation()
    auto_operation.start_work()
