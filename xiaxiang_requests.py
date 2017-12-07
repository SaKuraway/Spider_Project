import requests
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    "Cookie": '__cfduid=d0c81848a2eebad51210d4c147cc190711511316905; __lc.visitor_id.8854324=S1511316915.8257f737d5; age=qualified; productHistory=8a357eae91d29c1d6e79314e7cecfc68dd8807d5829b90bc0b2966dedcaa37e0s%3A28%3A%2210631%2C10537%2C2255%2C11278%2C11347%22%3B; PHPSESSID=io98q9pmad6d6egpq2pc0lc7m6; _csrf=f8a85ccb84e56528020f391a65725311d98d52e9e2d191ce30108f6f479b070fs%3A32%3A%225UOKazj6fxFxkIN9k7Dgf_y_GLyYgOVt%22%3B; _ga=GA1.2.348931940.1511316919; _gid=GA1.2.981967218.1512005703; _gat=1; _identity=c31c979569920ccb44ace89d393b2badd0a7d030eac00091e7f9ff9d94c0aee6s%3A50%3A%22%5B26690%2C%22q6xVGtNRU3X6Qg5vY0kKg8zBN7Iopnwz%22%2C2592000%5D%22%3B; lc_window_state=minimized',
}
html = requests.get(
    url='https://www.elegomall.com/brands/joyetech.html?page=1',headers=headers).text
# print(html)
print(etree.HTML(html).xpath('//div[@class="price-box"]/span[1]/text()'))
print(etree.HTML(html).xpath('//div[@class="price-box"]/span[2]/del/text()'))