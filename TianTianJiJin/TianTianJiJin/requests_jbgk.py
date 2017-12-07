import json
import pymysql
from lxml import etree
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8'}
html = requests.get(
    url='http://fund.eastmoney.com/f10/jbgk_502000.html',headers=headers).text

response=etree.HTML(html)
print(response.xpath('//div[@class="txt_in"]//tr[1]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[2]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[3]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[4]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[5]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[6]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[7]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[8]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[9]/td[1]//text()'))
print(response.xpath('//div[@class="txt_in"]//tr[10]/td[1]//text()'))
