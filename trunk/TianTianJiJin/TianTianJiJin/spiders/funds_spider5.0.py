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
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                            database='data_finance', charset='utf8')
        # # 使用cursor()方法获取操作游标
        # self.cur = self.mysql_client.cursor()

    def start_url(self):
        time.sleep(3)
        # start_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1&v=0.9361817037458058'
        # start_resonse = requests.get(url=start_url, headers=headers).text
        # data_pattern = re.compile(r'var rankData = {datas:(.*?),allRecords', re.S)
        # py_json = json.loads(data_pattern.findall(start_resonse)[0])
        # print(py_json)
        # print(len(py_json))
        # py_json.reverse()
        cur = self.mysql_client.cursor()
        cur.execute("SELECT fund_code from fund_information WHERE Fund_code not in (SELECT Fund_code from setors_configuration);")
        py_json = cur.fetchall()
        cur.close()
        for list in py_json:
            print('-----------------')
            try:
                item = collections.OrderedDict()
                # each = list.split(',')
                item['Fund_code'] = list[0]
                print('Fund_code', list[0])
                # item['Fund_name'] = each[1]
                # # item['fundPinyin'] = each[2]
                # item['Spider_Date'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                # item['Unit_Value'] = each[4]
                # item['Total_Value'] = each[5]
                # item['Daily_Growth_Rate'] = each[6]
                # item['Nearly_1weeks_Rate'] = each[7]
                # item['Nearly_1months_Rate'] = each[8]
                # item['Nearly_3months_Rate'] = each[9]
                # item['Nearly_6months_Rate'] = each[10]
                # item['Nearly_1years_Rate'] = each[11]
                # item['Nearly_2years_Rate'] = each[12]
                # item['Nearly_3years_Rate'] = each[13]
                # item['This_Year_Rate'] = each[14]
                # item['Since_Established_Rate'] = each[15]
                # item['Procedures_Fee'] = each[20]
                # fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(each[0])
                fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(item['Fund_code'])
                # # print(fund_js_url)
                response = etree.HTML(requests.get(url=fund_size_change_url, headers=headers).text)
                self.parse_fund_size_change(response, item)
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

        fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(item['Fund_code'])
        # # print(fund_js_url)
        response = etree.HTML(requests.get(url=fund_size_change_url, headers=headers).text)
        self.parse_fund_size_change(response, item)

    # 3.基金规模变动
    def parse_fund_size_change(self, response, item):
        time.sleep(3)
        # fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(
        #     item['Fund_code'])
        # # # print(fund_js_url)
        # response = etree.HTML(requests.get(url=fund_size_change_url, headers=headers).text)
        print('基金规模变动')
        try:
            item['Fund_size_change_Date'] = response.xpath("//tr//td[1]//text()")
            item['Period_Purchase'] = response.xpath("//tr//td[2]//text()")
            item['Period_Redeem'] = response.xpath("//tr//td[3]//text()")
            item['Ending_shares'] = response.xpath("//tr//td[4]//text()")
            item['Ending_net_asset'] = response.xpath("//tr//td[5]//text()")
            item['Net_asset_change'] = response.xpath("//tr//td[6]//text()")

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        fund_holder_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cyrjg&code={0}'.format(
            item['Fund_code'])
        response = etree.HTML(requests.get(url=fund_holder_url, headers=headers).text)
        self.parse_fund_holder(response, item)

    # 4.基金持有人结构
    def parse_fund_holder(self, response, item):
        time.sleep(3)
        print('基金持有人结构')
        # fund_holder_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cyrjg&code={0}'.format(
        #     item['Fund_code'])
        # response = etree.HTML(requests.get(url=fund_holder_url, headers=headers).text)
        try:
            item['Fund_holder_Date'] = response.xpath("//tr//td[1]//text()")
            item['Institution'] = response.xpath("//tr//td[2]//text()")
            item['Individual'] = response.xpath("//tr//td[3]//text()")
            item['Internal'] = response.xpath("//tr//td[4]//text()")
            item['Total_shares'] = response.xpath("//tr//td[5]//text()")
            item['Fund_holding_season'] = []
            item['Fund_holding_id'] = []
            item['Stock_code'] = []
            item['Stock_name'] = []
            item['Single_stock_percent'] = []
            item['Stock_holding_quantity'] = []
            item['Stock_holding_value'] = []
            self.year = 2018

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(
                    time.strftime('%Y-%m-%d %H:%M:%S',
                                  time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()
        fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year=&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
            item['Fund_code'])
        html = requests.get(url=fund_holding_url, headers=headers).text
        # print('html',html)
        self.parse_fund_holding(html, item)

    # 5.基金持仓明细
    def parse_fund_holding(self, html, item):
        time.sleep(3)
        print('基金持仓明细')
        response = etree.HTML(html)
        try:
            # if response.xpath('//tr/td/text()'):
            for i in response.xpath("//div[@class='box']"):
                # # print(i.xpath('.//label[1]/text()'))
                fund_holding_season = (
                (len(i.xpath('.//tr')) - 1) * str((i.xpath(".//label[1]/text()")[0]).strip() + ',')).split(',')
                del fund_holding_season[-1]
                # print(fund_holding_season)
                item['Fund_holding_season'] += fund_holding_season
                item['Fund_holding_id'] += i.xpath(".//tr//td[1]//text()")
                item['Stock_code'] += i.xpath(".//tr//td[2]//text()")
                item['Stock_name'] += i.xpath(".//tr//td[3]//text()")
                if i.xpath(".//tr//td[9]//text()"):
                    item['Single_stock_percent'] += i.xpath(".//tr//td[7]//text()")
                    item['Stock_holding_quantity'] += i.xpath(".//tr//td[8]//text()")
                    item['Stock_holding_value'] += i.xpath(".//tr//td[9]//text()")
                else:
                    item['Single_stock_percent'] += i.xpath(".//tr//td[5]//text()")
                    item['Stock_holding_quantity'] += i.xpath(".//tr//td[6]//text()")
                    item['Stock_holding_value'] += i.xpath(".//tr//td[7]//text()")
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)

        if current_year <= last_year:
            item['Transaction_details_season'] = []
            item['Transaction_details_id'] = []
            item['Buying_stock_code'] = []
            item['Buying_stock_name'] = []
            item['Accumulated_buy_value'] = []
            item['Accumulated_buy_percent_of_NAV'] = []
            self.year = 2018
            transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=transaction_details_url, headers=headers).text
            self.parse_transaction_details(html, item)
        else:
            self.year -= 1
            fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=fund_holding_url, headers=headers).text
            self.parse_fund_holding(html, item)

    # 6.重大变动
    def parse_transaction_details(self, html, item):
        time.sleep(3)
        print('重大变动')
        response = etree.HTML(html)
        try:
            # if response.xpath('//tr/td/text()'):
            for i in response.xpath("//div[@class='box']"):
                transaction_details_season = (
                (len(i.xpath('.//tr')) - 1) * str((i.xpath(".//label[1]/text()")[0]).strip() + ',')).split(',')
                del transaction_details_season[-1]
                # print(transaction_details_season)
                item['Transaction_details_season'] += transaction_details_season
                item['Transaction_details_id'] += i.xpath(".//tr//td[1]//text()")
                item['Buying_stock_code'] += i.xpath(".//tr//td[2]//text()")
                item['Buying_stock_name'] += i.xpath(".//tr//td[3]//text()")
                item['Accumulated_buy_value'] += i.xpath(".//tr//td[5]//text()")
                item['Accumulated_buy_percent_of_NAV'] += i.xpath(".//tr//td[6]//text()")

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)
        if current_year <= last_year:
            item['Setors_season'] = []  # 年份季度
            item['Setors_id'] = []  # 序号
            item['Setors'] = []  # 行业类别
            # item['Setors_change'] = []  # 行业变动详情
            item['Setors_percent'] = []  # 占净值比例
            item['Setors_value'] = []  # 市值（万元）
            self.year = 2018
            setors_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=setors_url, headers=headers).text
            self.parse_setors(html, item)
        else:
            self.year -= 1
            transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=transaction_details_url, headers=headers).text
            self.parse_transaction_details(html, item)

    # 7.行业配置
    def parse_setors(self, html, item):
        time.sleep(3)
        print('行业配置')
        response = etree.HTML(html)
        try:
            # if response.xpath('//tr/td/text()'):
            for i in response.xpath("//div[@class='box']"):
                setors_season = (
                (len(i.xpath('.//tr')) - 1) * str((i.xpath(".//label[1]/text()")[0]).strip() + ',')).split(',')
                del setors_season[-1]
                # print(setors_season)
                item['Setors_season'] += setors_season
                item['Setors_id'] += i.xpath(".//tr//td[1]//text()")
                item['Setors'] += i.xpath(".//tr//td[2]//text()")
                if i.xpath(".//tr//td[5]"):
                    item['Setors_percent'] += i.xpath(".//tr//td[4]//text()")
                    item['Setors_value'] += i.xpath(".//tr//td[5]//text()")
                else:
                    item['Setors_percent'] += i.xpath(".//tr//td[3]//text()")
                    item['Setors_value'] += i.xpath(".//tr//td[4]//text()")

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2018
            setors_comparation_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=hypzsy&code={0}'.format(
                item['Fund_code'])
            html = requests.get(url=setors_comparation_url, headers=headers).text
            self.parse_setors_comparation(html, item)
        else:
            self.year -= 1
            setors_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=setors_url, headers=headers).text
            self.parse_setors(html, item)

    # 9.行业配置比较表 Setors_comparation
    def parse_setors_comparation(self, html, item):
        time.sleep(3)
        print('行业配置比较表')
        response = etree.HTML(html)
        try:
            year_list_pattern = re.compile(r'日期：(.*?)"};', re.S)
            try:
                date = year_list_pattern.findall(response.body.decode())[0][-17:-7]
            except:
                # print(response.body.decode())
                date = ''
            comparation_date = ((len(response.xpath('//tr')) - 1) * (str(date) + ',')).split(',')
            del comparation_date[-1]
            item['Comparation_date'] = []
            item['Comparation_date'] += comparation_date
            item['CSRC_setors_code'] = response.xpath('//tr/td[1]//text()')
            item['Setors_name'] = response.xpath('//tr/td[2]//text()')
            item['Fund_setor_weight'] = response.xpath('//tr/td[3]//text()')
            item['Similarfund_setor_weight'] = response.xpath('//tr/td[4]//text()')
            item['Fund_setor_different'] = response.xpath('//tr/td[5]//text()')

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        parse_style_box_and_tracking_url = 'http://fund.eastmoney.com/f10/tsdata_{0}.html'.format(item['Fund_code'])
        html = requests.get(url=parse_style_box_and_tracking_url, headers=headers).text
        self.parse_style_box_and_tracking(html, item)

    # 10.投资风格：http://fund.eastmoney.com/f10/tsdata_{0}.html
    # 11.跟踪指数指标Tracking:http://fund.eastmoney.com/f10/tsdata_{0}.html
    def parse_style_box_and_tracking(self, html, item):
        time.sleep(3)
        print('跟踪指数指标Tracking')
        response = etree.HTML(html)
        # print('投资风格--------------------')
        try:
            item['Style_season'] = response.xpath("//div[@class='tzfg']//tr/td[1]//text()")
            item['Style_box'] = response.xpath("//div[@class='tzfg']//tr/td[2]//text()")
            # print('跟踪指数--------------------')
            item['Tracking_index'] = response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[1]//text()")[0] if response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[1]//text()") else ''
            item['Tracking_error'] = response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[2]//text()")[0] if response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[2]//text()") else ''
            item['Similar_average_tracking_error'] = response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[3]//text()")[0] if response.xpath(
                "//div[@id='jjzsfj']//tr[2]/td[3]//text()") else ''

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        fund_manger_change_url = 'http://fund.eastmoney.com/f10/jjjl_{0}.html'.format(item['Fund_code'])
        html = requests.get(url=fund_manger_change_url, headers=headers).text
        self.parse_fund_manger_change(html, item)

    # 12.基金经理变动表 Fund_manager_change：http://fund.eastmoney.com/f10/jjjl_{0}.html
    def parse_fund_manger_change(self, html, item):
        time.sleep(3)

        print('基金经理人------------------------------')
        response = etree.HTML(html)
        try:

            item['Start_date'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i
                                  in response.xpath("//div[@class='txt_in']/div[@class='box']//tr//td[1]")]  # 起始日期
            item['Ending_date'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for
                                   i in response.xpath("//div[@class='txt_in']/div[@class='box']//tr//td[2]")]  # 截止期
            item['Fund_managers'] = [''.join(i.xpath('.//text()')) if i.xpath('.//text()') else ''
                                     for i in
                                     response.xpath("//div[@class='txt_in']/div[@class='box']//tr//td[3]")]  # 基金经理
            item['Current_fund_manager'] = item['Fund_managers'][0] if item['Fund_managers'] else ''  # 基金经理
            item['Appointment_time'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                                        for i in
                                        response.xpath("//div[@class='txt_in']/div[@class='box']//tr//td[4]")]  # 任职时间
            item['Appointment_return'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box']//tr//td[5]")]  # 任职回报

            item['Held_fund_manager'] = ''.join(response.xpath("//div[@class='jl_intro'][1]/div[@class='text']/p[1]/a//text()"))
            item['Held_fund_code'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                                      for i in
                                      response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[1]")]  # 基金名称
            item['Held_fund_name'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                                      for i in
                                      response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[2]")]  # 基金名称
            item['Held_fund_type'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
                                      for i in
                                      response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[3]")]  # 基金类型
            item['Held_fund_start_time'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[4]")]  # 起始日期
            item['Held_fund_end_time'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[5]")]  # 截止日期
            item['Held_fund_appointment_time'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[6]")]  # 任职天数
            item['Held_fund_repayment'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[7]")]  # 任职回报
            item['Held_fund_similar_average'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[8]")]  # 同类平均
            item['Held_fund_similar_ranking'] = [
                i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
                response.xpath("//div[@class='txt_in']/div[@class='box nb']//div[@class='jl_office'][1]//tr//td[9]")]  # 同类排名
            item['Financial_index_date'] = []
            item['Period_realized_revenue'] = []
            item['Period_profits'] = []
            item['Period_profits_of_weighted_average_shares'] = []
            item['Period_profits_rate'] = []
            item['Period_growth_of_NAV'] = []
            item['Ending_distributable_profits'] = []
            item['Ending_distributable_profits_of_shares'] = []
            item['Ending_net_asset_value_of_fund'] = []
            item['Ending_NAV'] = []
            item['Growth_of_ANAV'] = []

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        main_financial_index_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code={0}&showtype=1&year='.format(
            item['Fund_code'])
        html = requests.get(url=main_financial_index_url, headers=headers).text
        self.parse_main_financial_index(html, item)

    # 13.财务报表
    def parse_main_financial_index(self, html, item):
        time.sleep(3)
        print('财务报表-----------------')
        response = etree.HTML(html)
        try:
            item['Financial_index_date'] += response.xpath("//table[1]//th//text()")[1:]  # 日期
            # item['Period_data_and_index'] = response.xpath("//table[1]//tbody/tr[1]//text()")[1:]  # 期间数据和指标
            item['Period_realized_revenue'] += response.xpath("//table[1]//tbody/tr[1]//text()")[1:]  # 本期已实现收益
            item['Period_profits'] += response.xpath("//table[1]//tbody/tr[2]//text()")[1:]  # 本期利润
            item['Period_profits_of_weighted_average_shares'] += response.xpath(
                "//table[1]//tbody/tr[3]//text()")[1:]  # 加权平均基金份额本期利润
            item['Period_profits_rate'] += response.xpath("//table[1]//tbody/tr[4]//text()")[1:]  # 本期加权平均净值利润率
            item['Period_growth_of_NAV'] += response.xpath("//table[1]//tbody/tr[5]//text()")[1:]  # 本期基金份额净值增长率

            # item['Ending_data_and_index'] = response.xpath("//table[1]//tbody/tr[1]//text()")[1:]  # 期末数据和指标
            item['Ending_distributable_profits'] += response.xpath("//table[2]//tbody/tr[1]//text()")[
                                                    1:]  # 期末可供分配利润
            item['Ending_distributable_profits_of_shares'] += response.xpath("//table[2]//tbody/tr[2]//text()")[
                                                              1:]  # 期末可供分配基金份额利润
            item['Ending_net_asset_value_of_fund'] += response.xpath("//table[2]//tbody/tr[3]//text()")[
                                                      1:]  # 期末基金资产净值
            item['Ending_NAV'] += response.xpath("//table[2]//tbody/tr[4]//text()")[1:]  # 期末基金份额净值

            item['Growth_of_ANAV'] += response.xpath("//table[3]//tbody/tr[1]//text()")[1:]  # 基金份额累计净值增长率
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2018

            item['Assets_date'] = []
            item['Bank_deposit'] = []
            item['Settlement_reserve'] = []
            item['Guarantee_deposit_paid'] = []
            item['Trading_financial_asset'] = []
            item['Stock_investment'] = []
            item['Fund_investment'] = []
            item['Bond_investment'] = []
            item['Asset_backed_securities_investment'] = []
            item['Derivative_financial_assets'] = []
            item['Purchase_resale_financial_assets'] = []
            item['Securities_settlement_receivable'] = []
            item['Interest_receivable'] = []
            item['Dividends_receivable'] = []
            item['Purchase_receivable'] = []
            item['Deferred_income_tax_assets'] = []
            item['Other_assets'] = []
            item['Total_assets'] = []
            item['Short_term_loan'] = []
            item['Trading_financial_liability'] = []
            item['Derivative_financial_liability'] = []
            item['Sell_repurchase_financial_assets'] = []
            item['Securities_settlement_payable'] = []
            item['Redeem_payables'] = []
            item['Managerial_compensation_payable'] = []
            item['Trustee_fee_payable'] = []
            item['Sales_service_fee_payable'] = []
            item['Taxation_payable'] = []
            item['Interest_payable'] = []
            item['Profits_receivable'] = []
            item['Deferred_income_tax_liability'] = []
            item['Other_liabilities'] = []
            item['Total_liabilities'] = []
            item['Paid_in_fund'] = []
            item['Total_owner_equity'] = []
            item['Total_debt_and_owner_equity'] = []

            assets_balance_sheet_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zcfzb&code={0}&showtype=1&year='.format(
                item['Fund_code'])

            html = requests.get(url=assets_balance_sheet_url, headers=headers).text
            self.parse_assets_balance_sheet(html, item)
        else:
            self.year -= 1
            main_financial_index_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=main_financial_index_url, headers=headers).text
            self.parse_main_financial_index(html, item)

    # 资产负债平衡
    def parse_assets_balance_sheet(self, html, item):
        time.sleep(3)
        print('资产负债平衡')
        response = etree.HTML(html)
        try:
            # item['Assets'] = []  # 资产
            item['Assets_date'] += response.xpath("//table[1]//th//text()")[1:]  # 资产
            item['Bank_deposit'] += response.xpath("//table[1]//tbody/tr[2]//text()")[1:]  # 银行存款
            item['Settlement_reserve'] += response.xpath("//table[1]//tbody/tr[3]//text()")[1:]  # 结算备付金
            item['Guarantee_deposit_paid'] += response.xpath("//table[1]//tbody/tr[4]//text()")[1:]  # 存出保证金
            item['Trading_financial_asset'] += response.xpath("//table[1]//tbody/tr[5]//text()")[1:]  # 交易性金融资产
            item['Stock_investment'] += response.xpath("//table[1]//tbody/tr[6]//text()")[1:]  # 其中：股票投资
            item['Fund_investment'] += response.xpath("//table[1]//tbody/tr[7]//text()")[2:]  # 其中：基金投资
            item['Bond_investment'] += response.xpath("//table[1]//tbody/tr[8]//text()")[2:]  # 其中：债券投资
            item['Asset_backed_securities_investment'] += response.xpath("//table[1]//tbody/tr[9]//text()")[
                                                          2:]  # 其中：资产支持证券投资
            item['Derivative_financial_assets'] += response.xpath("//table[1]//tbody/tr[10]//text()")[
                                                   1:]  # 衍生金融资产
            item['Purchase_resale_financial_assets'] += response.xpath("//table[1]//tbody/tr[11]//text()")[
                                                        1:]  # 买入返售金融资产
            item['Securities_settlement_receivable'] += response.xpath("//table[1]//tbody/tr[12]//text()")[
                                                        1:]  # 应收证券清算款
            item['Interest_receivable'] += response.xpath("//table[1]//tbody/tr[13]//text()")[1:]  # 应收利息
            item['Dividends_receivable'] += response.xpath("//table[1]//tbody/tr[14]//text()")[1:]  # 应收股利
            item['Purchase_receivable'] += response.xpath("//table[1]//tbody/tr[15]//text()")[1:]  # 应收申购款
            item['Deferred_income_tax_assets'] += response.xpath("//table[1]//tbody/tr[16]//text()")[
                                                  1:]  # 递延所得税资产
            item['Other_assets'] += response.xpath("//table[1]//tbody/tr[17]//text()")[1:]  # 其他资产
            item['Total_assets'] += response.xpath("//table[1]//tbody/tr[18]//text()")[1:]  # 资产总计
            # item['Debt'] = response.xpath("//table[1]//tbody/tr[2]//text()")[1:]  # 负债：
            item['Short_term_loan'] += response.xpath("//table[2]//tbody/tr[2]//text()")[1:]  # 短期借款
            item['Trading_financial_liability'] += response.xpath("//table[2]//tbody/tr[3]//text()")[
                                                   1:]  # 交易性金融负债
            item['Derivative_financial_liability'] += response.xpath("//table[2]//tbody/tr[4]//text()")[
                                                      1:]  # 衍生金融负债
            item['Sell_repurchase_financial_assets'] += response.xpath("//table[2]//tbody/tr[5]//text()")[
                                                        1:]  # 卖出回购金融资产款
            item['Securities_settlement_payable'] += response.xpath("//table[2]//tbody/tr[6]//text()")[
                                                     1:]  # 应付证券清算款
            item['Redeem_payables'] += response.xpath("//table[2]//tbody/tr[7]//text()")[1:]  # 应付赎回款
            item['Managerial_compensation_payable'] += response.xpath("//table[2]//tbody/tr[8]//text()")[
                                                       1:]  # 应付管理人报酬
            item['Trustee_fee_payable'] += response.xpath("//table[2]//tbody/tr[9]//text()")[1:]  # 应付托管费
            item['Sales_service_fee_payable'] += response.xpath("//table[2]//tbody/tr[10]//text()")[1:]  # 应付销售服务费
            item['Taxation_payable'] += response.xpath("//table[2]//tbody/tr[11]//text()")[1:]  # 应付税费
            item['Interest_payable'] += response.xpath("//table[2]//tbody/tr[12]//text()")[1:]  # 应付利息
            item['Profits_receivable'] += response.xpath("//table[2]//tbody/tr[13]//text()")[1:]  # 应收利润
            item['Deferred_income_tax_liability'] += response.xpath("//table[2]//tbody/tr[14]//text()")[
                                                     1:]  # 递延所得税负债
            item['Other_liabilities'] += response.xpath("//table[2]//tbody/tr[15]//text()")[1:]  # 其他负债
            item['Total_liabilities'] += response.xpath("//table[2]//tbody/tr[16]//text()")[1:]  # 负债合计
            # item['Owner_equity'] = response.xpath("//table[2]//tbody/tr[17]//text()")[1:]  # 所有者权益：
            item['Paid_in_fund'] += response.xpath("//table[2]//tbody/tr[18]//text()")[1:]  # 实收基金
            item['Total_owner_equity'] += response.xpath("//table[2]//tbody/tr[19]//text()")[1:]  # 所有者权益合计
            item['Total_debt_and_owner_equity'] += response.xpath("//table[2]//tbody/tr[20]//text()")[
                                                   1:]  # 负债和所有者权益合计
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2018

            item['Income'] = []
            item['Income_date'] = []
            item['Interest_income'] = []
            item['Interest_income_of_deposit'] = []
            item['Interest_income_of_bond'] = []
            item['Interest_income_of_asset_backed_securities'] = []  # 其中：资产支持证券利息收入
            item['Investment_income'] = []
            item['Income_of_stock_investment'] = []
            item['Income_of_fund_investment'] = []
            item['Income_of_bond_investment'] = []
            item['Income_of_asset_backed_securities_investment'] = []  # 其中：资产支持证券投资收益
            item['Income_of_derivatives'] = []
            item['Dividend_income'] = []
            item['Income_of_fair_value_change'] = []
            item['Exchange_earnings'] = []
            item['Other_Income'] = []
            item['Expense'] = []
            item['Managerial_compensation'] = []
            item['Trustee_fee'] = []
            item['Sales_service_fee'] = []
            item['Transaction_cost'] = []
            item['Interest_expense'] = []
            item['Sell_repurchase_financial_assets_expense'] = []  # 其中：卖出回购金融资产支出
            item['Other_expenses'] = []  # 其他费用

            item['Profit_before_tax'] = []  # 利润总额
            item['Income_tax_expense'] = []  # 减：所得税费用

            item['Net_profit'] = []  # 净利润

            income_statements_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=lrfpb&code={0}&showtype=1&year='.format(
                item['Fund_code'])
            html = requests.get(url=income_statements_url, headers=headers).text
            self.parse_income_statements(html, item)

        else:
            self.year -= 1
            assets_balance_sheet_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zcfzb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=assets_balance_sheet_url, headers=headers).text
            self.parse_assets_balance_sheet(html, item)

    # 收入
    def parse_income_statements(self, html, item):
        time.sleep(3)
        print('收入')
        response = etree.HTML(html)
        try:
            item['Income_date'] += response.xpath('//table//tr/th//text()')  # 收入日期
            item['Income'] += response.xpath('//table//tr[1]/td//text()')[1:]  # 收入
            item['Interest_income'] += response.xpath('//table//tr[2]/td//text()')[1:]  # 利息收入
            item['Interest_income_of_deposit'] += response.xpath('//table//tr[3]/td//text()')[1:]  # 其中：存款利息收入
            item['Interest_income_of_bond'] += response.xpath('//table//tr[4]/td//text()')[2:]  # 其中：债券利息收入
            item['Interest_income_of_asset_backed_securities'] += response.xpath('//table//tr[5]/td//text()')[
                                                                  2:]  # 其中：资产支持证券利息收入
            item['Investment_income'] += response.xpath('//table//tr[6]/td//text()')[2:]  # 投资收益
            item['Income_of_stock_investment'] += response.xpath('//table//tr[7]/td//text()')[2:]  # 其中：股票投资收益
            item['Income_of_fund_investment'] += response.xpath('//table//tr[8]/td//text()')[2:]  # 其中：基金投资收益
            item['Income_of_bond_investment'] += response.xpath('//table//tr[9]/td//text()')[2:]  # 其中：债券投资收益
            item['Income_of_asset_backed_securities_investment'] += response.xpath('//table//tr[10]/td//text()')[
                                                                    2:]  # 其中：资产支持证券投资收益
            item['Income_of_derivatives'] += response.xpath('//table//tr[11]/td//text()')[2:]  # 其中：衍生工具收益
            item['Dividend_income'] += response.xpath('//table//tr[12]/td//text()')[2:]  # 其中：股利收益
            item['Income_of_fair_value_change'] += response.xpath('//table//tr[13]/td//text()')[2:]  # 公允价值变动收益
            item['Exchange_earnings'] += response.xpath('//table//tr[14]/td//text()')[2:]  # 汇兑收益
            item['Other_Income'] += response.xpath('//table//tr[15]/td//text()')[2:]  # 其他收入
            item['Expense'] += response.xpath('//table//tr[16]/td//text()')[1:]  # 费用
            item['Managerial_compensation'] += response.xpath('//table//tr[17]/td//text()')[1:]  # 管理人报酬
            item['Trustee_fee'] += response.xpath('//table//tr[18]/td//text()')[1:]  # 托管费
            item['Sales_service_fee'] += response.xpath('//table//tr[19]/td//text()')[1:]  # 销售服务费
            item['Transaction_cost'] += response.xpath('//table//tr[20]/td//text()')[1:]  # 交易费用
            item['Interest_expense'] += response.xpath('//table//tr[21]/td//text()')[1:]  # 利息支出
            item['Sell_repurchase_financial_assets_expense'] += response.xpath('//table//tr[22]/td//text()')[
                                                                1:]  # 其中：卖出回购金融资产支出
            item['Other_expenses'] += response.xpath('//table//tr[23]/td//text()')[1:]  # 其他费用

            item['Profit_before_tax'] += response.xpath('//table//tr[24]/td//text()')[2:]  # 利润总额
            item['Income_tax_expense'] += response.xpath('//table//tr[25]/td//text()')[1:]  # 减：所得税费用

            item['Net_profit'] += response.xpath('//table//tr[26]/td//text()')[2:]  # 净利润
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(html)[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(html)[0])
        last_year = int(year_list[-1]) if year_list else current_year
        # print('last_year:', last_year)
        # print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2018
            income_analysis_url = 'http://fund.eastmoney.com/f10/srfx_{0}.html'.format(item['Fund_code'])
            html = requests.get(url=income_analysis_url, headers=headers).text
            self.parse_income_analysis(html, item)
        else:
            self.year -= 1
            income_statements_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=lrfpb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'], self.year)
            html = requests.get(url=income_statements_url, headers=headers).text
            self.parse_income_statements(html, item)

    # 分析
    def parse_income_analysis(self, html, item):
        time.sleep(3)
        print('分析')
        response = etree.HTML(html)
        try:
            item['Income_analysis_Date'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[1]//text()")  # 报告期
            item['Total_income'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[2]//text()")  # 收入合计
            item['Stock_income'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[3]//text()")  # 股票收入
            item['Stock_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[4]//text()")  # 占比
            item['Bond_income'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[5]//text()")  # 债券收入
            item['Bond_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[6]//text()")  # 占比
            item['Dividends_income'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[7]//text()")  # 股利收入
            item['Dividends_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[8]//text()")  # 占比
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        expenses_analysis_url = 'http://fund.eastmoney.com/f10/fyfx_{0}.html'.format(
            item['Fund_code'])
        html = requests.get(url=expenses_analysis_url, headers=headers).text
        self.parse_expenses_analysis(html, item)

    # 服务费用分析
    def parse_expenses_analysis(self, html, item):
        time.sleep(3)
        print('服务费用分析')
        response = etree.HTML(html)
        try:
            item['Expenses_analysis_date'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[1]//text()")  # 报告期
            item['Total_expenses'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[2]//text()")  # 费用合计
            item['Expenses_analysis_managerial_compensation'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[3]//text()")  # 管理人报酬
            item['Managerial_compensation_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[4]//text()")  # 占比
            item['Expenses_analysis_trustee_fee'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[5]//text()")  # 托管费
            item['Trustee_fee_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[6]//text()")  # 托管费占比
            item['Expenses_analysis_transaction_cost'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[7]//text()")  # 交易费
            item['Transaction_cost_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[8]//text()")  # 交易费占比
            item['Expenses_analysis_sales_service_fee'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[9]//text()")  # 销售服务费
            item['Sales_service_fee_percent'] = response.xpath(
                "//table[@class='w782 comm income']/tbody/tr/td[10]//text()")  # 销售服务费占比
        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        fund_allocations_url = 'http://fund.eastmoney.com/f10/zcpz_{0}.html'.format(item['Fund_code'])
        html = requests.get(url=fund_allocations_url, headers=headers).text
        self.parse_fund_allocations(html, item)

    # 资产分析
    def parse_fund_allocations(self, html, item):
        time.sleep(3)
        print('资产分析')
        response = etree.HTML(html)
        try:
            item['Fund_allocations_Date'] = response.xpath(
                "//table[@class='w782 comm tzxq']//tr/td[1]//text()")  # 报告期
            item['Fund_allocations_Stock_percent'] = response.xpath(
                "//table[@class='w782 comm tzxq']//tr/td[2]//text()")  # 股票占净比
            item['Fund_allocations_Bond_percent'] = response.xpath(
                "//table[@class='w782 comm tzxq']//tr/td[3]//text()")  # 债券占净比
            item['Cash_percent'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[4]//text()")  # 现金占净比
            item['Net_asset'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[5]//text()")  # 净资产（亿元）

        except Exception as e:
            print(e)
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        # history_NAV_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10000&sdate=&edate='.format(item['Fund_code'])
        acworth_url = 'http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode={0}&indexcode=000300&type=se&callback='.format(
            item['Fund_code'])
        html = requests.get(url=acworth_url, headers=headers).text
        self.parse_acworth(html, item)

        # # NAV
        # def parse_history_NAV(self, html,item):
        time.sleep(3)

    #     print('NAV')
    #     response = etree.HTML(html)
    #
    #     item['History_NAV_Date'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
    #                                 for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[1]")]  # 净值日期
    #     item['NAV'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
    #                    response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[2]")]  # 单位净值
    #     item['ANAV'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
    #             response.xpath("//table[@class='w782 comm lsjz']//tr/td[3]")]  # 累计净值
    #     # item['7days_annualised_return'] = '' if response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]") else [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in
    #     #                 response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[3]")] # 累计净值
    #     item['Day_change'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i
    #                           in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[4]")] if response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]") else ['货币基金' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[1]")]  # 收益率
    #     item['Purchase_status'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
    #                                for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[5]")] if response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]") else [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
    #                              for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[4]")]  # 申购状态
    #     item['Redeem_status'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[6]")] if response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]") else [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[5]")]  # 赎回状态
    #     item['Dividends_distribution'] = [i.xpath('.//text()')[0] if i.xpath('.//text()') else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]")] if response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]") else [i.xpath('.//text()')[0] if i.xpath('.//text()') else ''
    #                              for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[6]")] # 分红配送
    #     acworth_url = 'http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode={0}&indexcode=000300&type=se&callback='.format(
    #         item['Fund_code'])
    #     html = requests.get(url=acworth_url, headers=headers).text
    #     self.parse_acworth(html, item)

    # 累计走势
    def parse_acworth(self, html, item):
        time.sleep(3)
        print('累计走势')
        # response = etree.HTML(html)
        try:
            dict_json = json.loads(html)
            item['ACWorth_date'] = [str(int(int(i[0]) / 1000)) for i in dict_json[0]['data']]
            item['this_fund_rate'] = [i[1] for i in dict_json[0]['data']]
            item['similar_fund_rate'] = [i[1] if dict_json[1]['name'] == '同类平均' else '' for i in
                                         dict_json[1]['data']]  # 可以不存在同类排名
            item['hs300_rate'] = [i[1] for i in dict_json[-1]['data']]

        except Exception as e:
            print(e)
            item['ACWorth_date'] = ''
            item['this_fund_rate'] = ''
            item['similar_fund_rate'] = ''
            item['hs300_rate'] = ''
            print('=========null===========')
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('%s正在写入错误信息：fundCode=%s..' % (str(sys._getframe().f_code.co_name), item['Fund_code']), str(e))
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(time.time())) + '：' + '正在写入%s的错误信息：fundCode=%s..' % (
                        str(sys._getframe().f_code.co_name), item['Fund_code']) + str(e))
            f.close()

        self.process_item_mysql(item)

    def process_item_mysql(self, item):
        time.sleep(3)
        # FIFO模式为 blpop，LIFO模式为 brpop，获取redis的键值
        # source, data = rediscli.blpop(["aqi:items"])
        # item = json.loads(data)
        cur = self.mysql_client.cursor()
        try:
            # 使用execute方法执行SQL INSERT语句
            # if cur.execute("select * from Fund_information where Fund_code=" + "'" + item['Fund_code'] + "'" + ";"):
            #     self.try_except(
            #         cur.execute("delete from Fund_information where Fund_code=" + "'" + item['Fund_code'] + "'" + ";"))
            # self.try_except(cur.execute(
            #     "insert into Fund_information(Fund_name,Fund_code,Inception_Date,Launch_Date,Min_Purchase,Max_Initial_Charge,Management_Fee,Max_Redemption_charge,Benchmark,Spider_Date,Unit_Value,Total_Value,Daily_Growth_Rate,Nearly_1weeks_Rate,Nearly_1months_Rate,Nearly_3months_Rate,Nearly_6months_Rate,Nearly_1years_Rate,Nearly_2years_Rate,Nearly_3years_Rate,This_Year_Rate,Since_Established_Rate,Procedures_Fee,Assets_Scale,Share_Scale,Fund_Administrator,Fund_Custodian,Custodian_Rate) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            #     (item['Fund_name'], item['Fund_code'], item['Inception_Date'], item['Launch_Date'], item['Min_Purchase'],
            #     item['Max_Initial_Charge'], item['Management_Fee'], item['Max_Redemption_charge'],
            #     item['Benchmark'], item['Spider_Date'], item['Unit_Value'], item['Total_Value'],
            #     item['Daily_Growth_Rate'], item['Nearly_1weeks_Rate'], item['Nearly_1months_Rate'],
            #     item['Nearly_3months_Rate'], item['Nearly_6months_Rate'], item['Nearly_1years_Rate'],
            #     item['Nearly_2years_Rate'], item['Nearly_3years_Rate'], item['This_Year_Rate'],
            #     item['Since_Established_Rate'], item['Procedures_Fee'], item['Assets_Scale'], item['Share_Scale'],
            #     item['Fund_Administrator'], item['Fund_Custodian'], item['Custodian_Rate'])))
            # # 提交sql事务
            # self.mysql_client.commit()
            # except:
            #     print('Maybe基金代码为%s的Benmark这边有问题,其值为：%s'%(item['Fund_code'],item['Benchmark']))
            # 去重
            cur.execute("select Fund_size_change_Date from Fund_size_change where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Fund_size_change_Date, Period_Purchase, Period_Redeem, Ending_shares, Ending_net_asset, Net_asset_change in zip(
                    item['Fund_size_change_Date'], item['Period_Purchase'], item['Period_Redeem'],
                    item['Ending_shares'], item['Ending_net_asset'], item['Net_asset_change']):
                if Fund_size_change_Date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Fund_size_change(Fund_code,Fund_size_change_Date,Period_Purchase,Period_Redeem,Ending_shares,Ending_net_asset,Net_asset_change) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Fund_size_change_Date, Period_Purchase, Period_Redeem, Ending_shares,
                         Ending_net_asset, Net_asset_change)))
                    # else: self.try_except(cur.execute("insert into bbae_top_5_regions(ISIN，top_5_regions,top_5_regions_percent) VALUES(%s,%s,%s)",(item['ISIN'],top_5_regions,top_5_regions_percent)))
                    #     print('Same to Mysql ,skipping it!')
                    # with open('Data/' + '爬虫日志' + '.log', 'a', encoding='utf-8') as f:
                    #     f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + 'Same to Mysql ,skipping it!' + '\r\n')
                    # f.close()
            # 去重
            cur.execute("select Fund_holder_Date from Fund_holder where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Fund_holder_Date, Institution, Individual, Internal, Total_shares in zip(item['Fund_holder_Date'],
                                                                                         item['Institution'],
                                                                                         item['Individual'],
                                                                                         item['Internal'],
                                                                                         item['Total_shares']):
                if Fund_holder_Date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Fund_holder(Fund_code,Fund_holder_Date,Institution,Individual,Internal,Total_shares) VALUES(%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Fund_holder_Date, Institution, Individual, Internal, Total_shares)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Fund_holding_season,Fund_holding_id from Fund_holding where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_season_id = cur.fetchall()
            print(item['Fund_code'], 'existed_season_id:', existed_season_id)
            for Fund_holding_season, Fund_holding_id, Stock_code, Stock_name, Single_stock_percent, Stock_holding_quantity, Stock_holding_value in zip(
                    item['Fund_holding_season'], item['Fund_holding_id'], item['Stock_code'], item['Stock_name'],
                    item['Single_stock_percent'], item['Stock_holding_quantity'], item['Stock_holding_value']):
                if (Fund_holding_season, Fund_holding_id) not in existed_season_id:

                    self.try_except(cur.execute(
                        "insert into Fund_holding(Fund_code,Fund_holding_season,Fund_holding_id,Stock_code,Stock_name,Single_stock_percent,Stock_holding_quantity,Stock_holding_value) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Fund_holding_season, Fund_holding_id, Stock_code, Stock_name,
                         Single_stock_percent, Stock_holding_quantity, Stock_holding_value)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute(
                "select Transaction_details_season,Transaction_details_id from Transaction_details where Fund_code=" + "'" +
                item['Fund_code'] + "'" + ";")
            existed_season_id = cur.fetchall()
            print(item['Fund_code'], 'existed_season_id:', existed_season_id)
            for Transaction_details_season, Transaction_details_id, Buying_stock_code, Buying_stock_name, Accumulated_buy_value, Accumulated_buy_percent_of_NAV in zip(
                    item['Transaction_details_season'], item['Transaction_details_id'], item['Buying_stock_code'],
                    item['Buying_stock_name'], item['Accumulated_buy_value'], item['Accumulated_buy_percent_of_NAV']):
                if (Transaction_details_season, Transaction_details_id) not in existed_season_id:
                    self.try_except(cur.execute(
                        "insert into Transaction_details(Fund_code,Transaction_details_season,Transaction_details_id,Buying_stock_code,Buying_stock_name,Accumulated_buy_value,Accumulated_buy_percent_of_NAV) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Transaction_details_season, Transaction_details_id, Buying_stock_code,
                         Buying_stock_name, Accumulated_buy_value, Accumulated_buy_percent_of_NAV)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Setors_season,Setors_id from Setors_configuration where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_season_id = cur.fetchall()
            print(item['Fund_code'], 'existed_season_id:', existed_season_id)
            for Setors_season, Setors_id, Setors, Setors_percent, Setors_value in zip(item['Setors_season'],
                                                                                      item['Setors_id'], item['Setors'],
                                                                                      item['Setors_percent'],
                                                                                      item['Setors_value']):
                if (Setors_season, Setors_id) not in existed_season_id:
                    self.try_except(cur.execute(
                        "insert into Setors_configuration(Fund_code,Setors_season,Setors_id,Setors,Setors_percent,Setors_value) VALUES(%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Setors_season, Setors_id, Setors, Setors_percent, Setors_value)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')

            # 去重
            cur.execute("select Comparation_date,CSRC_setors_code from Setors_comparation where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date_code = cur.fetchall()
            print(item['Fund_code'], 'existed_season_id:', existed_season_id)
            for Comparation_date, CSRC_setors_code, Setors_name, Fund_setor_weight, Similarfund_setor_weight, Fund_setor_different in zip(
                    item['Comparation_date'], item['CSRC_setors_code'], item['Setors_name'], item['Fund_setor_weight'],
                    item['Similarfund_setor_weight'], item['Fund_setor_different']):
                if (Comparation_date, CSRC_setors_code) not in existed_date_code:
                    self.try_except(cur.execute(
                        "insert into Setors_comparation(Fund_code,Comparation_date,CSRC_setors_code,Setors_name,Fund_setor_weight,Similarfund_setor_weight,Fund_setor_different) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Comparation_date, CSRC_setors_code, Setors_name, Fund_setor_weight,
                         Similarfund_setor_weight, Fund_setor_different)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute(
                "select Style_season,Style_box from StyleBox where Fund_code=" + "'" + item['Fund_code'] + "'" + ";")
            existed_season_box = cur.fetchall()
            print(item['Fund_code'], 'existed_season_id:', existed_season_id)
            for Style_season, Style_box in zip(item['Style_season'], item['Style_box']):
                if (Style_season, Style_box) not in existed_season_box:
                    self.try_except(
                        cur.execute("insert into StyleBox(Fund_code,Style_season,Style_box) VALUES(%s,%s,%s)",
                                    (item['Fund_code'], Style_season, Style_box)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            if not cur.execute("select * from Tracking where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Tracking_index=" + "'" + item['Tracking_index'] + "'" + " and Tracking_error=" + "'" + item['Tracking_error'] + "'" + ";"):
                self.try_except(cur.execute(
                    "insert into Tracking(Fund_code,Tracking_index,Tracking_error,Similar_average_tracking_error) VALUES(%s,%s,%s,%s)",
                    (item['Fund_code'], item['Tracking_index'], item['Tracking_error'],
                     item['Similar_average_tracking_error'])))
            # else:
            #     print('Same to Mysql ,skipping it!')
            for Start_date, Ending_date, Fund_managers, Appointment_time, Appointment_return in zip(item['Start_date'],
                                                                                                    item['Ending_date'],
                                                                                                    item[
                                                                                                        'Fund_managers'],
                                                                                                    item[
                                                                                                        'Appointment_time'],
                                                                                                    item[
                                                                                                        'Appointment_return']):
                if cur.execute("select * from Current_fund_manager_change where Fund_code=" + "'" + item[
                    'Fund_code'] + "'" + " and Start_date=" + "'" + Start_date + "'" + ";"):
                    self.try_except(cur.execute("delete from Current_fund_manager_change where Fund_code=" + "'" + item[
                        'Fund_code'] + "'" + " and Start_date=" + "'" + Start_date + "'" + ";"))
                self.try_except(cur.execute(
                    "insert into Current_fund_manager_change(Fund_code,Start_date,Ending_date,Fund_managers,Appointment_time,Appointment_return) VALUES(%s,%s,%s,%s,%s,%s)",
                    (item['Fund_code'], Start_date, Ending_date, Fund_managers, Appointment_time, Appointment_return)))
                # else:
                #     print('Same to Mysql ,skipping it!')
            # # 去重
            # cur.execute("select Held_fund_start_time from All_fund_managers where Fund_code=" + "'" + item[
            #     'Fund_code'] + "'" + ";")
            # existed_date = [date[0] for date in cur.fetchall()]
            # print(item['Fund_code'], 'existed_date:', existed_date)


            self.try_except(
                cur.execute("delete from All_fund_managers where Current_fund_manager=" + "'" + item['Held_fund_manager']+ "'" + ";"))
            for Held_fund_code, Held_fund_name, Held_fund_type, Held_fund_start_time, Held_fund_end_time, Held_fund_appointment_time, Held_fund_repayment, Held_fund_similar_average, Held_fund_similar_ranking in zip(
                    item['Held_fund_code'], item['Held_fund_name'], item['Held_fund_type'],
                    item['Held_fund_start_time'], item['Held_fund_end_time'], item['Held_fund_appointment_time'],
                    item['Held_fund_repayment'], item['Held_fund_similar_average'], item['Held_fund_similar_ranking']):
                    print(item['Held_fund_manager'], Held_fund_code, Held_fund_name, Held_fund_type, Held_fund_start_time, Held_fund_end_time, Held_fund_appointment_time, Held_fund_repayment, Held_fund_similar_average, Held_fund_similar_ranking)
                # if not cur.execute("select * from All_fund_managers where Current_fund_manager=" + "'" + item[
                #     'Current_fund_manager'] + "'" + " and Held_fund_code=" + "'" + Held_fund_code + "'" + " and Held_fund_start_time=" + "'" + Held_fund_start_time + "'" + " and Held_fund_repayment=" + "'" + Held_fund_repayment + "'" + ";"):
                    self.try_except(cur.execute("insert into All_fund_managers(Current_fund_manager,Held_fund_code,Held_fund_name,Held_fund_type,Held_fund_start_time,Held_fund_end_time,Held_fund_appointment_time,Held_fund_repayment,Held_fund_similar_average,Held_fund_similar_ranking) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Held_fund_manager'], Held_fund_code, Held_fund_name, Held_fund_type,
                         Held_fund_start_time, Held_fund_end_time, Held_fund_appointment_time, Held_fund_repayment,
                         Held_fund_similar_average, Held_fund_similar_ranking)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Financial_index_date from Main_financial_index where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Financial_index_date, Period_realized_revenue, Period_profits, Period_profits_of_weighted_average_shares, Period_profits_rate, Period_growth_of_NAV, Ending_distributable_profits, Ending_distributable_profits_of_shares, Ending_net_asset_value_of_fund, Ending_NAV, Growth_of_ANAV in zip(
                    item['Financial_index_date'], item['Period_realized_revenue'], item['Period_profits'],
                    item['Period_profits_of_weighted_average_shares'], item['Period_profits_rate'],
                    item['Period_growth_of_NAV'], item['Ending_distributable_profits'],
                    item['Ending_distributable_profits_of_shares'], item['Ending_net_asset_value_of_fund'],
                    item['Ending_NAV'], item['Growth_of_ANAV']):
                if Financial_index_date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Main_financial_index(Fund_code,Financial_index_date,Period_realized_revenue,Period_profits,Period_profits_of_weighted_average_shares,Period_profits_rate,Period_growth_of_NAV,Ending_distributable_profits,Ending_distributable_profits_of_shares,Ending_net_asset_value_of_fund,Ending_NAV,Growth_of_ANAV) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Financial_index_date, Period_realized_revenue, Period_profits,
                         Period_profits_of_weighted_average_shares, Period_profits_rate, Period_growth_of_NAV,
                         Ending_distributable_profits, Ending_distributable_profits_of_shares,
                         Ending_net_asset_value_of_fund, Ending_NAV, Growth_of_ANAV)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute(
                "select Assets_date from Assets_balance_sheet where Fund_code=" + "'" + item['Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Assets_date, Bank_deposit, Settlement_reserve, Guarantee_deposit_paid, Trading_financial_asset, Stock_investment, Fund_investment, Bond_investment, Asset_backed_securities_investment, Derivative_financial_assets, Purchase_resale_financial_assets, Securities_settlement_receivable, Interest_receivable, Dividends_receivable, Purchase_receivable, Deferred_income_tax_assets, Other_assets, Total_assets, Short_term_loan, Trading_financial_liability, Derivative_financial_liability, Sell_repurchase_financial_assets, Securities_settlement_payable, Redeem_payables, Managerial_compensation_payable, Trustee_fee_payable, Sales_service_fee_payable, Taxation_payable, Interest_payable, Profits_receivable, Deferred_income_tax_liability, Other_liabilities, Total_liabilities, Paid_in_fund, Total_owner_equity, Total_debt_and_owner_equity in zip(
                    item['Assets_date'], item['Bank_deposit'], item['Settlement_reserve'],
                    item['Guarantee_deposit_paid'], item['Trading_financial_asset'], item['Stock_investment'],
                    item['Fund_investment'], item['Bond_investment'], item['Asset_backed_securities_investment'],
                    item['Derivative_financial_assets'], item['Purchase_resale_financial_assets'],
                    item['Securities_settlement_receivable'], item['Interest_receivable'], item['Dividends_receivable'],
                    item['Purchase_receivable'], item['Deferred_income_tax_assets'], item['Other_assets'],
                    item['Total_assets'], item['Short_term_loan'], item['Trading_financial_liability'],
                    item['Derivative_financial_liability'], item['Sell_repurchase_financial_assets'],
                    item['Securities_settlement_payable'], item['Redeem_payables'],
                    item['Managerial_compensation_payable'], item['Trustee_fee_payable'],
                    item['Sales_service_fee_payable'], item['Taxation_payable'], item['Interest_payable'],
                    item['Profits_receivable'], item['Deferred_income_tax_liability'], item['Other_liabilities'],
                    item['Total_liabilities'], item['Paid_in_fund'], item['Total_owner_equity'],
                    item['Total_debt_and_owner_equity']):
                if Assets_date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Assets_balance_sheet(Fund_code,Assets_date,Bank_deposit,Settlement_reserve,Guarantee_deposit_paid,Trading_financial_asset,Stock_investment,Fund_investment,Bond_investment,Asset_backed_securities_investment,Derivative_financial_assets,Purchase_resale_financial_assets,Securities_settlement_receivable,Interest_receivable,Dividends_receivable,Purchase_receivable,Deferred_income_tax_assets,Other_assets,Total_assets,Short_term_loan,Trading_financial_liability,Derivative_financial_liability,Sell_repurchase_financial_assets,Securities_settlement_payable,Redeem_payables,Managerial_compensation_payable,Trustee_fee_payable,Sales_service_fee_payable,Taxation_payable,Interest_payable,Profits_receivable,Deferred_income_tax_liability,Other_liabilities,Total_liabilities,Paid_in_fund,Total_owner_equity,Total_debt_and_owner_equity) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Assets_date, Bank_deposit, Settlement_reserve, Guarantee_deposit_paid,
                         Trading_financial_asset, Stock_investment, Fund_investment, Bond_investment,
                         Asset_backed_securities_investment, Derivative_financial_assets,
                         Purchase_resale_financial_assets, Securities_settlement_receivable, Interest_receivable,
                         Dividends_receivable, Purchase_receivable, Deferred_income_tax_assets, Other_assets,
                         Total_assets, Short_term_loan, Trading_financial_liability, Derivative_financial_liability,
                         Sell_repurchase_financial_assets, Securities_settlement_payable, Redeem_payables,
                         Managerial_compensation_payable, Trustee_fee_payable, Sales_service_fee_payable,
                         Taxation_payable, Interest_payable, Profits_receivable, Deferred_income_tax_liability,
                         Other_liabilities, Total_liabilities, Paid_in_fund, Total_owner_equity,
                         Total_debt_and_owner_equity)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute(
                "select Income_date from Income_statements where Fund_code=" + "'" + item['Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Income, Income_date, Interest_income, Interest_income_of_deposit, Interest_income_of_bond, Interest_income_of_asset_backed_securities, Investment_income, Income_of_stock_investment, Income_of_fund_investment, Income_of_bond_investment, Income_of_asset_backed_securities_investment, Income_of_derivatives, Dividend_income, Income_of_fair_value_change, Exchange_earnings, Other_Income, Expense, Managerial_compensation, Trustee_fee, Sales_service_fee, Transaction_cost, Interest_expense, Sell_repurchase_financial_assets_expense, Other_expenses, Profit_before_tax, Income_tax_expense, Net_profit in zip(
                    item['Income'], item['Income_date'], item['Interest_income'], item['Interest_income_of_deposit'],
                    item['Interest_income_of_bond'], item['Interest_income_of_asset_backed_securities'],
                    item['Investment_income'], item['Income_of_stock_investment'], item['Income_of_fund_investment'],
                    item['Income_of_bond_investment'], item['Income_of_asset_backed_securities_investment'],
                    item['Income_of_derivatives'], item['Dividend_income'], item['Income_of_fair_value_change'],
                    item['Exchange_earnings'], item['Other_Income'], item['Expense'], item['Managerial_compensation'],
                    item['Trustee_fee'], item['Sales_service_fee'], item['Transaction_cost'], item['Interest_expense'],
                    item['Sell_repurchase_financial_assets_expense'], item['Other_expenses'], item['Profit_before_tax'],
                    item['Income_tax_expense'], item['Net_profit']):
                if Income_date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Income_statements(Fund_code,Income,Income_date,Interest_income,Interest_income_of_deposit,Interest_income_of_bond,Interest_income_of_asset_backed_securities,Investment_income,Income_of_stock_investment,Income_of_fund_investment,Income_of_bond_investment,Income_of_asset_backed_securities_investment,Income_of_derivatives,Dividend_income,Income_of_fair_value_change,Exchange_earnings,Other_Income,Expense,Managerial_compensation,Trustee_fee,Sales_service_fee,Transaction_cost,Interest_expense,Sell_repurchase_financial_assets_expense,Other_expenses,Profit_before_tax,Income_tax_expense,Net_profit) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Income, Income_date, Interest_income, Interest_income_of_deposit,
                         Interest_income_of_bond, Interest_income_of_asset_backed_securities, Investment_income,
                         Income_of_stock_investment, Income_of_fund_investment, Income_of_bond_investment,
                         Income_of_asset_backed_securities_investment, Income_of_derivatives, Dividend_income,
                         Income_of_fair_value_change, Exchange_earnings, Other_Income, Expense, Managerial_compensation,
                         Trustee_fee, Sales_service_fee, Transaction_cost, Interest_expense,
                         Sell_repurchase_financial_assets_expense, Other_expenses, Profit_before_tax,
                         Income_tax_expense, Net_profit)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Income_analysis_Date from Income_analysis where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Income_analysis_Date, Total_income, Stock_income, Stock_percent, Bond_income, Bond_percent, Dividends_income, Dividends_percent in zip(
                    item['Income_analysis_Date'], item['Total_income'], item['Stock_income'], item['Stock_percent'],
                    item['Bond_income'], item['Bond_percent'], item['Dividends_income'], item['Dividends_percent']):
                if Income_analysis_Date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Income_analysis(Fund_code,Income_analysis_Date,Total_income,Stock_income,Stock_percent,Bond_income,Bond_percent,Dividends_income,Dividends_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                        item['Fund_code'], Income_analysis_Date, Total_income, Stock_income, Stock_percent, Bond_income,
                        Bond_percent, Dividends_income, Dividends_percent)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Expenses_analysis_date from Expenses_analysis where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Expenses_analysis_date, Total_expenses, Expenses_analysis_managerial_compensation, Managerial_compensation_percent, Expenses_analysis_trustee_fee, Trustee_fee_percent, Expenses_analysis_transaction_cost, Transaction_cost_percent, Expenses_analysis_sales_service_fee, Sales_service_fee_percent in zip(
                    item['Expenses_analysis_date'], item['Total_expenses'],
                    item['Expenses_analysis_managerial_compensation'], item['Managerial_compensation_percent'],
                    item['Expenses_analysis_trustee_fee'], item['Trustee_fee_percent'],
                    item['Expenses_analysis_transaction_cost'], item['Transaction_cost_percent'],
                    item['Expenses_analysis_sales_service_fee'], item['Sales_service_fee_percent']):
                if Expenses_analysis_date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Expenses_analysis(Fund_code,Expenses_analysis_date,Total_expenses,Expenses_analysis_managerial_compensation,Managerial_compensation_percent,Expenses_analysis_trustee_fee,Trustee_fee_percent,Expenses_analysis_transaction_cost,Transaction_cost_percent,Expenses_analysis_sales_service_fee,Sales_service_fee_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Expenses_analysis_date, Total_expenses,
                         Expenses_analysis_managerial_compensation, Managerial_compensation_percent,
                         Expenses_analysis_trustee_fee, Trustee_fee_percent, Expenses_analysis_transaction_cost,
                         Transaction_cost_percent, Expenses_analysis_sales_service_fee, Sales_service_fee_percent)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')
            # 去重
            cur.execute("select Fund_allocations_Date from Fund_allocations where Fund_code=" + "'" + item[
                'Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)
            for Fund_allocations_Date, Fund_allocations_Stock_percent, Fund_allocations_Bond_percent, Cash_percent, Net_asset in zip(
                    item['Fund_allocations_Date'], item['Fund_allocations_Stock_percent'],
                    item['Fund_allocations_Bond_percent'], item['Cash_percent'], item['Net_asset']):
                if Fund_allocations_Date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into Fund_allocations(Fund_code,Fund_allocations_Date,Fund_allocations_Stock_percent,Fund_allocations_Bond_percent,Cash_percent,Net_asset) VALUES(%s,%s,%s,%s,%s,%s)",
                        (item['Fund_code'], Fund_allocations_Date, Fund_allocations_Stock_percent,
                         Fund_allocations_Bond_percent, Cash_percent, Net_asset)))
                    # else:
                    #     print('Same to Mysql ,skipping it!')

            # cur.execute("select History_NAV_Date from History_NAV where Fund_code=" + "'" + item['Fund_code'] + "'" + ";")
            # existed_date = [date[0] for date in cur.fetchall()]
            # print(item['Fund_code'], 'existed_date:', existed_date)
            # for History_NAV_Date, NAV, ANAV, Day_change, Purchase_status, Redeem_status, Dividends_distribution in zip(
            #         item['History_NAV_Date'], item['NAV'], item['ANAV'], item['Day_change'], item['Purchase_status'],
            #         item['Redeem_status'], item['Dividends_distribution']):
            #     if History_NAV_Date not in existed_date:
            #         cur.execute(
            #             "insert into History_NAV(Fund_code,History_NAV_Date,NAV,ANAV,7days_annualised_return,Day_change,Purchase_status,Redeem_status,Dividends_distribution) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            #             (item['Fund_code'], History_NAV_Date, NAV, ANAV, ANAV, Day_change, Purchase_status,
            #              Redeem_status,
            #              Dividends_distribution))
            #         print('inserting data to mysql...', item['Fund_code'], History_NAV_Date, NAV, ANAV, Day_change,
            #               Purchase_status,
            #               Redeem_status, Dividends_distribution)
            #     else:
            #         print('existed!skiping...')  # else:
            cur.execute("select ACWorth_date from ACWorth where Fund_code=" + "'" + item['Fund_code'] + "'" + ";")
            existed_date = [date[0] for date in cur.fetchall()]
            print(item['Fund_code'], 'existed_date:', existed_date)

            for ACWorth_date, this_fund_rate, similar_fund_rate, hs300_rate in zip(item['ACWorth_date'],
                                                                                   item['this_fund_rate'],
                                                                                   item['similar_fund_rate'],
                                                                                   item['hs300_rate']):
                if ACWorth_date not in existed_date:
                    self.try_except(cur.execute(
                        "insert into ACWorth(Fund_code,ACWorth_date,this_fund_rate,similar_fund_rate,hs300_rate) VALUES(%s,%s,%s,%s,%s)",
                        (item['Fund_code'], ACWorth_date, this_fund_rate, similar_fund_rate, hs300_rate)))

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
            # finally:
            #     self.mysql_client.commit()
            # return sth


if __name__ == '__main__':
    while True:
        try:
            print('Spider begins！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            funds_spider = TiantianJijinSpider()
            funds_spider.start_url()
            print('Spider finish！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        except Exception as e :
            print('While True ERROR!!! 可能是网络问题.',e)