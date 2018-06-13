#-*-coding:utf-8-*-
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def autorun_selenium():
    driver = webdriver.Chrome()
    driver.get('http://spyder.planplus.cn/')
    print('帐号：admin\n密码：pulan1105')
    sleep(20)
    # print(driver.switch_to.alert.authenticate())
    driver.find_element_by_xpath("//tr[8]/td[@class='project-status']/span[@class='status-TODO editable editable-click']").click()
    sleep(2)
    # driver.find_element_by_xpath("//tr[9]/td[@class='project-status']/span[@class='status-STOP editable editable-click']").click()

    select = Select(driver.find_element_by_css_selector(".form-control.input-sm"))
    sleep(2)
    select.select_by_value("RUNNING")
    sleep(61200)
    driver.find_element_by_xpath("//button[@class='btn btn-primary btn-sm editable-submit']/i[@class='glyphicon glyphicon-ok']").click()

def autorun_requests():
    project_name = 'ITA_Spyder_sakura03'
    status_update_url = 'http://spyder.planplus.cn/update'
    click_run_url = 'http://spyder.planplus.cn/run'
    headers = {
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "Authorization":"Basic YWRtaW46cHVsYW4xMTA1",
    # 可以不加cookie的！它是用上面的Authorization来验证用户密码的。
    "Cookie":"UM_distinctid=162cd3e7026198-08a104b28c9d97-6010107f-1fa400-162cd3e702777a",
    "Host":"spyder.planplus.cn",
    "Origin":"http://spyder.planplus.cn",
    "Referer":"http://spyder.planplus.cn/",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "X-Requested-With":"XMLHttpRequest"
    }
    update_postData = {
        # pyspider项目名称
        "name": "status",
        "value": "RUNNING",
        "pk": project_name
    }
    click_postData = {
        # pyspider项目名称
        "project": project_name
    }
    ssion = requests.session()
    print('status_update_result:',ssion.post(url=status_update_url,headers=headers,data=update_postData).text)
    sleep(2)
    print('click_run_result:',ssion.post(url=click_run_url,headers=headers,data=click_postData).text)

if __name__ == '__main__':
    # autorun_selenium()
    autorun_requests()