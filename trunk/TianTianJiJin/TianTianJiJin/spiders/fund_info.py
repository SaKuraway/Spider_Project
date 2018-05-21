# -*-coding:utf-8-*-
import requests, pymysql, time, re, json, collections, sys
from lxml import etree



headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8",
    # "Connection": "keep-alive",
    "Host": "fund.eastmoney.com",
    "Referer": "http://fund.eastmoney.com/data/fundranking.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
}

class TiantianJijinSpider(object):
    def __init__(self):
        self.fund_code_list = []
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                            database='data_finance', charset='utf8')
        # # 使用cursor()方法获取操作游标
        # self.cur = self.mysql_client.cursor()

    def start_url(self):
        time.sleep(3)
        start_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1&v=0.9361817037458058'
        start_resonse = requests.get(url=start_url, headers=headers).text
        data_pattern = re.compile(r'var rankData = {datas:(.*?),allRecords', re.S)
        py_json = json.loads(data_pattern.findall(start_resonse)[0])
        # print(py_json)
        print(len(py_json))
        py_json.reverse()
        self.funds_list = []
        for list in py_json:
            self.funds_list.append(list.split(','))
        print(len(self.funds_list),self.funds_list)

        for i in range(len(self.funds_list)):
            print('-----------------')
            try:
                item = collections.OrderedDict()
                # each = list.split(',')
                each = self.funds_list.pop(0)
                item['Fund_code'] = each[0]
                print('Fund_code', each[0])
                item['Fund_name'] = each[1]
                # item['fundPinyin'] = each[2]
                item['Spider_Date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                item['Unit_Value'] = each[4]
                item['Total_Value'] = each[5]
                item['Daily_Growth_Rate'] = each[6]
                item['Nearly_1weeks_Rate'] = each[7]
                item['Nearly_1months_Rate'] = each[8]
                item['Nearly_3months_Rate'] = each[9]
                item['Nearly_6months_Rate'] = each[10]
                item['Nearly_1years_Rate'] = each[11]
                item['Nearly_2years_Rate'] = each[12]
                item['Nearly_3years_Rate'] = each[13]
                item['This_Year_Rate'] = each[14]
                item['Since_Established_Rate'] = each[15]
                item['Procedures_Fee'] = each[20]
                # fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(each[0])
                fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(item['Fund_code'])
                # print(requests.get(url=fund_info_url, headers=headers).text)
                response = etree.HTML(requests.get(url=fund_info_url, headers=headers).text)
                self.parse_fundinfo(response, item)
                print(item)
            except Exception as e:
                print(item['Fund_code'],'error!(可能是网络问题)',e)

        self.mysql_client.close()

    # 2.基金概况页面
    def parse_fundinfo(self, response, item):
        time.sleep(3)
        # fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(item['Fund_code'])
        # response = etree.HTML(requests.get(url=fund_info_url,headers=headers).text)
        print('基金概况页面')
        try:

            table_item = response.xpath('//div[@class="txt_in"]//table[@class="info w790"]//td')
            item['Fund_name'] = ''.join(table_item[0].xpath('.//text()')) if table_item[0] is not None else ''
            item['Min_Purchase'] = ''.join(response.xpath(
                "//div[@id='bodydiv']//div[@class='basic-new ']//div[@class='col-left']//a[@class='btn  btn-red ']//span//text()"))
            item['Fund_Type'] = ''.join(table_item[3].xpath('.//text()')) if table_item[3] is not None else ''  # 基金类型
            item['Risk_Level'] = response.xpath(
                "//div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()")[
                0].strip() if response.xpath(
                "//div[@class='detail']/div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()") else ''  # 风险等级
            item['Launch_Date'] = ''.join(table_item[4].xpath('.//text()')) if table_item[4] is not None else ''  # 成立时间
            item['Inception_Date'] = ''.join(table_item[5].xpath('.//text()')) if table_item[
                                                                                      5] is not None else ''  # 成立时间
            item['Assets_Scale'] = ''.join(table_item[6].xpath('.//text()')) if table_item[
                                                                                    6] is not None else ''  # 资产管理规模
            item['Share_Scale'] = ''.join(table_item[7].xpath('.//text()')) if table_item[7] is not None else ''  # 份额规模
            item['Fund_Administrator'] = ''.join(table_item[8].xpath('.//text()')) if table_item[
                                                                                          8] is not None else ''  # 基金管理人
            item['Fund_Custodian'] = ''.join(table_item[9].xpath('.//text()')) if table_item[
                                                                                      9] is not None else ''  # 基金托管人
            item['Management_Fee'] = ''.join(table_item[12].xpath('.//text()')) if table_item[
                                                                                       12] is not None else ''  # 管理费率
            item['Custodian_Rate'] = ''.join(table_item[13].xpath('.//text()')) if table_item[
                                                                                       13] is not None else ''  # 托管费率
            item['Max_Initial_Charge'] = ''.join(table_item[16].xpath('.//text()')) if table_item[
                                                                                           16] is not None else ''
            item['Max_Redemption_charge'] = ''.join(table_item[17].xpath('.//text()')) if table_item[
                                                                                              17] is not None else ''
            item['Benchmark'] = ''.join(table_item[18].xpath('.//text()')) if table_item[18] is not None else ''

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(
                    time.strftime('%Y-%m-%d %H:%M:%S',
                                  time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(
            item['Fund_code'])
        # # print(fund_js_url)
        response = etree.HTML(requests.get(url=fund_size_change_url, headers=headers).text)
        self.process_item_mysql(item)

    def process_item_mysql(self, item):
        time.sleep(3)
        # FIFO模式为 blpop，LIFO模式为 brpop，获取redis的键值
        # source, data = rediscli.blpop(["aqi:items"])
        # item = json.loads(data)
        cur = self.mysql_client.cursor()
        try:
            # 使用execute方法执行SQL INSERT语句
            if cur.execute("select * from Fund_information where Fund_code=" + "'" + item['Fund_code'] + "'" + ";"):
                self.try_except(
                    cur.execute("delete from Fund_information where Fund_code=" + "'" + item['Fund_code'] + "'" + ";"))
            self.try_except(cur.execute(
                "insert into Fund_information(Fund_name,Fund_code,Inception_Date,Launch_Date,Min_Purchase,Max_Initial_Charge,Management_Fee,Max_Redemption_charge,Benchmark,Spider_Date,Unit_Value,Total_Value,Daily_Growth_Rate,Nearly_1weeks_Rate,Nearly_1months_Rate,Nearly_3months_Rate,Nearly_6months_Rate,Nearly_1years_Rate,Nearly_2years_Rate,Nearly_3years_Rate,This_Year_Rate,Since_Established_Rate,Procedures_Fee,Assets_Scale,Share_Scale,Fund_Administrator,Fund_Custodian,Custodian_Rate) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (item['Fund_name'], item['Fund_code'], item['Inception_Date'], item['Launch_Date'], item['Min_Purchase'],
                item['Max_Initial_Charge'], item['Management_Fee'], item['Max_Redemption_charge'],
                item['Benchmark'], item['Spider_Date'], item['Unit_Value'], item['Total_Value'],
                item['Daily_Growth_Rate'], item['Nearly_1weeks_Rate'], item['Nearly_1months_Rate'],
                item['Nearly_3months_Rate'], item['Nearly_6months_Rate'], item['Nearly_1years_Rate'],
                item['Nearly_2years_Rate'], item['Nearly_3years_Rate'], item['This_Year_Rate'],
                item['Since_Established_Rate'], item['Procedures_Fee'], item['Assets_Scale'], item['Share_Scale'],
                item['Fund_Administrator'], item['Fund_Custodian'], item['Custodian_Rate'])))

        except pymysql.Error as e:
            with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
                print('MYSQL Writing Error info...', e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
            f.close()
            self.mysql_client.close()
            self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev',password='planner1105',database='data_finance', charset='utf8')

        finally:
            # 提交sql事务
            self.mysql_client.commit()
            print('committed.')
            # 关闭本次操作
            cur.close()

    def try_except(self, sth):
        print('inserting data to mysql ...')
        try:
            sth
        except pymysql.Error as e:
            with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
                print('MYSQL Writing Error info...', e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
                self.mysql_client.close()
                self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev',password='planner1105',database='data_finance', charset='utf8')
            f.close()

if __name__ == '__main__':
    while True:
        try:
            print('Spider begins！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            funds_spider = TiantianJijinSpider()
            funds_spider.start_url()

        except Exception as e :
            print('While True ERROR!!! 可能是网络问题.',e)
            print('Spider error！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        else:
            print('Spider finish！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            break