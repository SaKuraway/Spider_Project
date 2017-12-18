import sys
import os
import re
import time
import random
import pandas
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
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# WebDriverWait 库，负责循环等待
from selenium.webdriver.support.ui import WebDriverWait
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

        self.Hansard_index = []
        self.ITA_index = []
        self.zurich_index = []

    def _format_addr(self, address):
        """
        规范邮件地址
        :param address:
        :return:
        """
        name, addr = parseaddr(address)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def browser_login(self, url, username, password, username_id, password_id, submit_id):
        """
        调用并操作浏览器对象
        :param url:
        :param username:
        :param password:
        :param username_id:
        :param password_id:
        :param submit_id:
        :return:
        """
        # 调用环境变量指定的Chrome浏览器创建浏览器对象
        driver = webdriver.Chrome()

        # 先随机获取一个user-agent
        # agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        # 将PhantomJS浏览器报头 转为字典对象，可以修改键对应的值
        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        # 修改PhantomJS的user-agent
        # dcap["phantomjs.page.settings.userAgent"] = agent
        # 如果没有在环境变量指定PhantomJS位置
        # driver = webdriver.PhantomJS()
        # driver = webdriver.PhantomJS(executable_path="./phantomjs-2.1.1-linux-x86_64/bin/phantomjs")

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
        :param driver:
        :param Hansard:
        :return:
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
                # self.random_sleep()
                # self.random_sleep(10,15)
                # self.wait_until(driver=driver, selector_name="//div[@class='controls']//button[@class='submit']")
                # self.random_sleep()
                # driver.implicitly_wait(2)

                # 获取调仓完成的页面截图：
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot(
                        '成功调仓截图文件夹/' + str(self.policyNumber) + str(self.riskType) + ".png")
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
                driver.save_screenshot('调仓失败截图文件夹/' + str(self.policyNumber) + str(self.riskType) + ".png")
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
        :param driver:
        :param ITA:
        :return:
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

        # 点击前往主页
        self.wait_until(driver=driver, platform='ITA', selector_name="//div[@class='portlet-body']//a")
        driver.save_screenshot('test.png')
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, "//div[@class='portlet-body']//a")))
        # except Exception as e:
        #     print('==============error6================')
        # driver.find_element_by_xpath("//div[@class='portlet-body']//a").click()
        self.random_sleep()

        # 点击查询
        # try:
        #     element = WebDriverWait(driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH,
        #                                         '''//ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a''')))
        # except Exception as e:
        #     print('==============error6================')
        self.random_sleep()
        self.wait_until(driver=driver, platform='ITA',
                        selector_name='''//div[@class='page-container']/div[@id='sideBar']/div[@class='page-sidebar navbar-collapse collapse']/ul[@class='page-sidebar-menu']/li[@class='id="0"'][2]/a[@id='menu_0']''')
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
                self.sellingPercent = int(round(float(item[1]) * 100))
                # 风险类型
                self.riskType = str(item[2])
                self.random_sleep()
                # 点击输入保单号
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='clear')
                # 输入保单号
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").clear()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']",
                                action='send_keys', send_keys=self.policyNumber)
                # driver.find_element_by_xpath("//table[@id='TableReport']/thead/tr//input[@id='PlanNumberFilter']").send_keys(self.policyNumber)
                self.random_sleep()
                # 点击搜寻
                self.wait_until(driver=driver, platform='ITA', selector_name="//button[@id='SearchButton']")
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
                policyLink = str(
                    driver.find_element_by_xpath("//table[@id='TableReport']//tr[@class='odd']/td[1]/a").get_attribute(
                        "href"))
                js = 'window.open("' + policyLink + '");'
                driver.execute_script(js)
                # print(driver.window_handles)
                driver.switch_to.window(driver.window_handles[1])
                self.random_sleep()
                driver.maximize_window()
                self.random_sleep(15, 20)
                # 点击主计划
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''')
                # driver.find_element_by_xpath(
                #     '''//ul[@class='page-sidebar-menu']/li[@id='0']/ul[@class='sub-menu']/li[@class='id="0"']/a/div[@class='title']''').click()
                # 点击基金转换&平衡
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name='''//ul[@class='sub-menu']/li[@class='id="0" open']/ul[@class='sub-menu']/li[@class='id="0"'][3]/a[@id='menu_0']/div[@class='title']''')
                # 勾选基金转换
                self.random_sleep()
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//form[@id='Step1']/div[@class='form-body select-option']/div[@class='form-group']/div[@class='radio-list']/label[1]/label")
                # 点击下一个
                self.random_sleep(10, 15)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='Step1panel']//div[@id='stepsTransferRebalance_1']//div[@class='panel-body form']//form[@id='Step1']//div[@class='form-actions']/input[@type='submit']")
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
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//tr[@class='rowSearch'][" + str(
                                    FIDC_index) + "]/td[@class='thCol12']/a")
                # 清除买入比例
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']/div[@class='table-scroll']//tr/td/input",
                                action='clear')
                # 填入买入比例
                self.random_sleep()
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']/div[@class='table-scroll']//tr/td/input",
                                action='send_keys', send_keys=self.sellingPercent)
                self.random_sleep(10, 15)
                # 点击下一个
                self.wait_until(driver=driver, platform='ITA', selector_name="//div[@class='form-actions']/button")
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
                    self.random_sleep()
                    # 清除输入框并输入基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='clear')
                    self.random_sleep()
                    # print(name, value)
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/div[@class='select2-search']/input",
                                    action='send_keys', send_keys=name)
                    # 点击基金代码
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//div[@id='select2-drop']/ul/li[@class='select2-results-dept-0 select2-result select2-result-selectable custom-panel-select2-option select2-highlighted']/div//span[1]")
                    self.random_sleep()
                    # 点击搜寻
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//form[@id='Step2']/div[@class='table-container']//tr[@class='bg-grey-cararra']/td/button[@class='btn btn-sm filter-submit green-seagreen']")
                    self.random_sleep()
                    # 点击选择
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//table[@class='table table-condensed table-hover']//tr[@class='rowTransferRebalance']/td/a[@class='btn btn-xs grey-steel']")
                    self.random_sleep()
                    # 清空买入比例输入框
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='clear')
                    self.random_sleep()
                    # 填入买入比例
                    self.wait_until(driver=driver, platform='ITA',
                                    selector_name="//tr[@class='rowTransferRebalance'][" + str(
                                        row_index) + "]/td[@class='thCol11Percent text-right']/input",
                                    action='send_keys', send_keys=value)
                    row_index += 1
                # 点击下一步
                self.random_sleep()
                self.random_sleep(3, 5)
                self.wait_until(driver=driver, platform='ITA',
                                selector_name="//div[@id='fundSelected']/div[@class='form-actions']/button")
                self.random_sleep(3, 5)
                # time.sleep(5000)
                # # 点击确认
                # self.wait_until(driver=driver,platform='ITA',
                #                 selector_name="//div[@id='divStep4']/div[@class='form-actions']/button[@class='btn bg-blue pull-right']")
                # # 点击完成
                # self.wait_until(driver=driver,platform='ITA',
                #                 selector_name="//div[@id='Step5panel']/div[@id='stepsTransferRebalance_5']/div[@class='panel-body form']/div[@class='form-actions']/a")
                # # 调仓完毕，截图保存。
                if self.error == 0:
                    self.successed += 1
                    driver.save_screenshot('成功调仓截图文件夹/' + str(self.policyNumber) + str(self.riskType) + ".png")
                    # self.policy_index = self.ITA_index[index]
                    self.write_excel(policy_index=self.ITA_index[index])
                    print(str(self.policyNumber) + str(self.riskType), '：调仓成功！')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！')
                self.error = 1
                driver.save_screenshot('调仓失败截图文件夹/' + str(self.policyNumber) + str(self.riskType) + ".png")
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
        :param zurich:
        :return:
        """
        if not zurich:
            print('zurich无需调仓的保单！')
            return
        # 检查是否够钟落班
        self.check_workoff()
        for item in zurich:
            pass

    def wait_until(self, driver, selector_name, platform='Hansard', selector_way='XPATH', action='click',
                   send_keys=None):
        """
        显式等待延迟 + 元素操作事件
        :param driver:
        :param selector_name:
        :param selector_way:
        :param action:
        :param send_keys:
        :return:
        """
        if self.error == 1:
            return
        selector = By.XPATH
        if selector_way == 'ID':
            selector = By.ID
        elif selector_way == 'CLASS_NAME':
            selector = By.CLASS_NAME

        try:
            # 页面一直循环，直到 id="myDynamicElement" 出现
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((selector, selector_name)))
        except:
            self.error = 1
            driver.save_screenshot('调仓失败截图文件夹/' + str(self.policyNumber) + str(self.riskType) + ".png")
            if platform == 'Hansard':
                self.write_excel(policy_index=self.Hansard_index[self.enum_index], message='调仓失败')
            elif platform == 'ITA':
                self.write_excel(policy_index=self.ITA_index[self.enum_index], message='调仓失败')
            elif platform == 'zurich':
                self.write_excel(policy_index=self.zurich_index[self.enum_index], message='调仓失败')

            print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！', action + ':' + selector_name)
            # driver.close()
        else:
            if action == 'click':
                driver.find_element_by_xpath(selector_name).click()
            elif action == 'clear':
                driver.find_element_by_xpath(selector_name).clear()
            elif action == 'send_keys':
                driver.find_element_by_xpath(selector_name).send_keys(str(send_keys))
            elif action == 'text':
                return driver.find_element_by_xpath(selector_name).text
        finally:
            self.random_sleep()

    def random_sleep(self, least=1, most=4):
        """
        随机休眠一段时间
        :return:
        """
        time.sleep(random.randint(least, most))

    def read_excel(self):
        """
        读取excel里的数据
        :return:
        """
        index = 0
        excel = pandas.read_excel(self.excel_name)
        value = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
        # 数据列表
        data_list = []
        Hansard = []
        ITA = []
        zurich = []

        for policyNumber, sellingPercent, riskType, operationSituation in zip(excel['保单号'], excel['卖出比例'],
                                                                              excel['风险属性'], excel['调仓情况']):
            if str(policyNumber).startswith("5") and value.match(str(sellingPercent)) and operationSituation != '调仓成功':
                Hansard.append((policyNumber, sellingPercent, riskType))
                self.Hansard_index.append(index)
            elif str(policyNumber).startswith("T") and value.match(
                    str(sellingPercent)) and operationSituation != '调仓成功':
                ITA.append((policyNumber, sellingPercent, riskType))
                self.ITA_index.append(index)
            elif str(policyNumber).startswith("8") and value.match(
                    str(sellingPercent)) and operationSituation != '调仓成功':
                zurich.append((policyNumber, sellingPercent, riskType))
                self.zurich_index.append(index)
            index += 1
        data_list.append(Hansard)
        data_list.append(ITA)
        data_list.append(zurich)
        # 需要调仓数
        self.counts = len(Hansard) + len(ITA) + len(ITA)
        print('\n需要调仓的保单个数为：%s' % self.counts)
        return data_list

    def write_excel(self, policy_index, message='调仓成功'):
        """
        写入调仓情况信息
        :param message:
        :return:
        """
        policy_row = policy_index + 1
        excel_name = self.excel_name
        excel_content = open_workbook(excel_name, formatting_info=False)
        new_xls_file = copy(excel_content)
        sheet = new_xls_file.get_sheet(0)
        sheet.write(policy_row, 4, message)
        os.remove(excel_name)
        new_xls_file.save(excel_name)

    def check_workoff(self, off_time=1830):
        """
        定时停止程序：到了18:30分，完成当前手头上的调仓任务后便停止调仓操作。
        :param off_time:
        :return:
        """
        if int(time.strftime("%H%M")) >= off_time:
            # while order_time>0:
            #     time.sleep(1)
            #     order = input('够钟落班收工，如需加班请输入SaKura靓仔('+str(order_time)+'):')
            #     if order == 'SaKura靓仔':
            #         return
            print('好，够钟收工！正在发送战绩邮件....', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                  '\n今日战绩：调仓成功 %s个/失败%s个。' % (self.successed, (self.operation_counts - self.successed)))
            # 发送邮件给资管部人员
            self.send_email()
            # 停止程序
            sys.exit(0)

    def send_email(self):
        """
        下班时发送邮件到资管部人员.
        :return:
        """
        # 不带SSL安全套层
        from_addr = 'sakurapan@trussan.com'  # input('From: ')
        password = 'Cbc_123'  # input('Password: ')
        to_addr = [
            'sakurapan@trussan.com','yuwinliang@trussan.com','sarahguo@trussan.com','zainxue@trussan.com','544538297@qq.com','iqpmw@126.com']  # input('To: ')
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

    def start_work(self):
        """
        开始任务调度
        :return:
        """
        # 1.读取Excel表格数据
        data = self.read_excel()
        # 2.进行自动调仓操作
        print('\n正在进行Hansard调仓操作....')
        self.hansard_operation(data[0])
        print('\n正在进行ITA调仓操作....')
        self.ita_operation(data[1])
        print('\n正在进行Hansard调仓操作....')
        self.zurich_operation(data[2])
        print('\r\n调仓完毕！其中调仓成功 %s个/总数%s个。' % (self.successed, self.counts))


if __name__ == '__main__':
    auto_operation = AutoOperation()
    auto_operation.start_work()
