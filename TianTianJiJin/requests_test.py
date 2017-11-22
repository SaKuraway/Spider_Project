import requests,json

# html = requests.get(url='http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code=000457&topline=10&year=2016&month=1,2,3,4,5,6,7,8,9,10,11,12').content.decode('utf-8')
# print(html[-44:-2])
# print(json.loads(html[44:-2]))
json1 = "['content:123,arryear:[2017,2016,2015,2014],curyear:2016']"
print(json.loads(json1))