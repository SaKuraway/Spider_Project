#-*-coding:utf-8-*-
import requests
from lxml import etree

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
  'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",

}
html = requests.get('http://www.morningstar.co.uk//uk/etf/snapshot/snapshot.aspx?id=0P000197HP',headers=DEFAULT_REQUEST_HEADERS).text
selector = etree.HTML(html)
print(selector.xpath("//footer[@class='ec-sustainability__footer']/p//text()"))
print(selector.xpath("//header[@class='ec-sustainability__header']/h1[@class='ec-sustainability__title']/small//text()"))
print(selector.xpath("//div[@class='ec-sustainability__content']/div[@class='ec-columns ec-columns-right']/h3[@class='ec-sustainability__value ng-binding'][2]//text()"))
print(selector.xpath("//div[@class='ec-sustainability__content']//div[@class='ec-sustainability__summary']/p[1]//text()"))
print(selector.xpath("//div[@class='ec-sustainability__content']//div[@class='ec-sustainability__summary']/p[1]//text()"))
print(selector.xpath("//div[@id='TrailingReturnsOverview']//tr[1]/td[@class='heading date']//text()"))
