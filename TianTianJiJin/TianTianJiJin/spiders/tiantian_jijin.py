# -*- coding: utf-8 -*-
import json
import re

import scrapy

from ..items import JijinDataItem


class TiantianJijinSpider(scrapy.Spider):
    name = "tiantian_jijin"
    # allowed_domains = ["http://fund.eastmoney.com"]
    start_urls = [
        'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&sd=2016-11-10&ed=2017-11-10&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1&v=0.9361817037458058']

    # start_urls = ['http://fund.eastmoney.com/pingzhongdata/004450.js']

    # 1.基金排行页面
    def parse(self, response):
        # print(response.body.decode())
        # print(len(response.xpath("//div[@class='mainFrame'][7]//tbody//tr")))
        json_html = response.body.decode()
        # print(json_html)
        py_json = json.loads(json_html[22:-150])
        print(py_json)
        print('len:', len(py_json))
        list1 = py_json[0].split(',')
        list2 = py_json[1].split(',')
        list3 = py_json[2].split(',')
        print(list1)
        print('len:', len(list1))
        print('len:', len(list2))
        print('len:', len(list3))
        for list in py_json:
            item = JijinDataItem()
            each = list.split(',')
            item['Fund_code'] = each[0]
            # item['fundName'] = each[1]
            # item['fundPinyin'] = each[2]
            item['Spider_Date'] = each[3]
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
            fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(each[0])
            yield scrapy.Request(url=fund_info_url, callback=self.parse_fundinfo, meta={'fund_item': item})
            break
        # item = JijinDataItem()
        # item['Fund_code'] = '000457'
        # fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(item['Fund_code'])
        # yield scrapy.Request(url=fund_info_url, callback=self.parse_fundinfo, meta={'fund_item': item})

    # 2.基金概况页面
    def parse_fundinfo(self, response):
        item = response.meta['fund_item']
        table_item = response.xpath('//div[@class="txt_in"]//table[@class="info w790"]//td')
        item['Fund_name'] = ''.join(table_item[0].xpath('.//text()').extract()) if table_item[0] else ''
        item['Min_Purchase'] = ''.join(response.xpath(
            "//div[@id='bodydiv']//div[@class='basic-new ']//div[@class='col-left']//a[@class='btn  btn-red ']//span//text()").extract())
        item['Fund_Type'] = ''.join(table_item[3].xpath('.//text()').extract()) if table_item[3] else ''  # 基金类型
        item['Risk_Level'] = response.xpath(
            "//div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()").extract_first().strip() if response.xpath(
            "//div[@class='detail']/div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()") else ''  # 风险等级
        item['Launch_Date'] = ''.join(table_item[4].xpath('.//text()').extract()) if table_item[4] else ''  # 成立时间
        item['Inception_Date'] = ''.join(table_item[5].xpath('.//text()').extract()) if table_item[5] else ''  # 成立时间
        item['assetsScale'] = ''.join(table_item[6].xpath('.//text()').extract()) if table_item[6] else ''  # 资产管理规模
        item['shareScale'] = ''.join(table_item[7].xpath('.//text()').extract()) if table_item[7] else ''  # 份额规模
        item['fundAdministrator'] = ''.join(table_item[8].xpath('.//text()').extract()) if table_item[
            8] else ''  # 基金管理人
        item['fundCustodian'] = ''.join(table_item[9].xpath('.//text()').extract()) if table_item[9] else ''  # 基金托管人
        item['Management_Fee'] = ''.join(table_item[12].xpath('.//text()').extract()) if table_item[12] else ''  # 管理费率
        item['custodianRate'] = ''.join(table_item[13].xpath('.//text()').extract()) if table_item[13] else ''  # 托管费率
        item['Max_Initial_Charge'] = ''.join(table_item[16].xpath('.//text()').extract()) if table_item[16] else ''
        item['Max_Redemption_charge'] = ''.join(table_item[17].xpath('.//text()').extract()) if table_item[17] else ''
        item['Benchmark'] = ''.join(table_item[18].xpath('.//text()').extract()) if table_item[18] else ''

        fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(
            item['Fund_code'])
        # print(fund_js_url)
        yield scrapy.Request(url=fund_size_change_url, callback=self.parse_fund_size_change, meta={'fund_item': item})


    # def parse_fundjs(self, response):
    #     item = response.meta['fund_item']
    #     json_html = response.body.decode()
    #     # / *基金/股票名称 * /
    #     year_list_pattern_fundName = re.compile(r'var fS_name = "(.*?)";', re.S)
    #     item['Fund_name'] = year_list_pattern_fundName.findall(json_html)[0]
    #     # print(fundName)
    #     # /*股票仓位测算图*/
    #     # year_list_pattern_fundSharesPositions = re.compile(r'var Data_fundSharesPositions = (.*?);',re.S)
    #     # fundSharesPositions = year_list_pattern_fundSharesPositions.findall(json_html)[0]
    #     # print(fundSharesPositions)
    #     # /*单位净值走势 equityReturn-净值回报 unitMoney-每份派送金*/
    #     # year_list_pattern_netWorthTrend  = re.compile(r'var Data_netWorthTrend = (.*?);',re.S)
    #     # netWorthTrend = year_list_pattern_netWorthTrend.findall(json_html)[0]
    #     # print(netWorthTrend)
    #     # /*累计净值走势*/
    #     # year_list_pattern_ACWorthTrend = re.compile(r'var Data_ACWorthTrend = (.*?);', re.S)
    #     # item['ACWorthTrend'] = year_list_pattern_ACWorthTrend.findall(json_html)[0]
    #     # print(ACWorthTrend)
    #     # /*现任基金经理：任职时间、任期收益、同类平均*/
    #     year_list_pattern_currentFundManager = re.compile(r'var Data_currentFundManager =(.*?);', re.S)
    #     item['currentFundManager'] = year_list_pattern_currentFundManager.findall(json_html)[0]
    #     # print(currentFundManager)
    #     # /*资产配置占比*/
    #     year_list_pattern_assetAllocation = re.compile(r'var Data_assetAllocation = {"series":(.*?),"categories"', re.S)
    #     item['assetAllocation'] = year_list_pattern_assetAllocation.findall(json_html)[0]
    #     # print(assetAllocation)
    #     # /*累计收益率走势(本基金、沪深300、同类平均)*/
    #     year_list_pattern_grandTotal = re.compile(r'var Data_grandTotal = (.*?);', re.S)
    #     item['grandTotal'] = year_list_pattern_grandTotal.findall(json_html)[0]
    #     # print(grandTotal)
    #     acworth_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10000'.format(
    #         item['Fund_code'])
    #     # print(fund_js_url)
    #     yield scrapy.Request(url=acworth_url, callback=self.parse_acworth, meta={'fund_item': item})

    # 3.基金规模变动
    def parse_fund_size_change(self, response):
        item = response.meta['fund_item']
        item['Fund_size_change_Date'] = response.xpath("//tr//td[1]//text()").extract()
        item['Period_Purchase'] = response.xpath("//tr//td[2]//text()").extract()
        item['Period_Redeem'] = response.xpath("//tr//td[3]//text()").extract()
        item['Ending_shares'] = response.xpath("//tr//td[4]//text()").extract()
        item['Ending_net_asset'] = response.xpath("//tr//td[5]//text()").extract()
        item['Net_asset_change'] = response.xpath("//tr//td[6]//text()").extract()

        fund_holder_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cyrjg&code={0}'.format(
            item['Fund_code'])
        yield scrapy.Request(url=fund_holder_url, callback=self.parse_fund_holder, meta={'fund_item': item})

    # 4.基金持有人结构
    def parse_fund_holder(self, response):
        item = response.meta['fund_item']
        item['Fund_holder_Date'] = response.xpath("//tr//td[1]//text()").extract()
        item['Institution'] = response.xpath("//tr//td[2]//text()").extract()
        item['Individual'] = response.xpath("//tr//td[3]//text()").extract()
        item['Internal'] = response.xpath("//tr//td[4]//text()").extract()
        item['Total_shares'] = response.xpath("//tr//td[5]//text()").extract()
        item['Fund_holding_season'] = []
        item['Fund_holding_id'] = []
        item['Stock_code'] = []
        item['Stock_name'] = []
        item['Single_stock_percent'] = []
        item['Stock_holding_quantity'] = []
        item['Stock_holding_value'] = []
        self.year = 2017
        fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year=&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
            item['Fund_code'])
        yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})

    # 5.基金持仓明细
    def parse_fund_holding(self, response):
        item = response.meta['fund_item']
        # if response.xpath('//tr/td/text()'):
        for i in response.xpath("//div[@class='box']"):
            # print(i.xpath('.//label[1]/text()').extract())
            fund_holding_season = (
                (len(i.xpath('.//tr')) - 1) * str((
                                                      i.xpath(
                                                          ".//label[1]/text()").extract_first()).strip() + ',')).split(
                ',')
            del fund_holding_season[-1]
            print(fund_holding_season)
            item['Fund_holding_season'] += fund_holding_season
            item['Fund_holding_id'] += i.xpath(".//tr//td[1]//text()").extract()
            item['Stock_code'] += i.xpath(".//tr//td[2]//text()").extract()
            item['Stock_name'] += i.xpath(".//tr//td[3]//text()").extract()
            if i.xpath(".//tr//td[9]//text()"):
                item['Single_stock_percent'] += i.xpath(".//tr//td[7]//text()").extract()
                item['Stock_holding_quantity'] += i.xpath(".//tr//td[8]//text()").extract()
                item['Stock_holding_value'] += i.xpath(".//tr//td[9]//text()").extract()
            else:
                item['Single_stock_percent'] += i.xpath(".//tr//td[5]//text()").extract()
                item['Stock_holding_quantity'] += i.xpath(".//tr//td[6]//text()").extract()
                item['Stock_holding_value'] += i.xpath(".//tr//td[7]//text()").extract()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            item['Transaction_details_season'] = []
            item['Transaction_details_id'] = []
            item['Buying_stock_code'] = []
            item['Buying_stock_name'] = []
            item['Accumulated_buy_value'] = []
            item['Accumulated_buy_percent_of_NAV'] = []
            self.year = 2017
            transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=transaction_details_url, callback=self.parse_transaction_details,
                                 meta={'fund_item': item})
        else:
            self.year -= 1
            fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})

    # 6.重大变动
    def parse_transaction_details(self, response):
        item = response.meta['fund_item']
        # if response.xpath('//tr/td/text()'):
        for i in response.xpath("//div[@class='box']"):
            transaction_details_season = (
                (len(i.xpath('.//tr')) - 1) * str((
                                                      i.xpath(
                                                          ".//label[1]/text()").extract_first()).strip() + ',')).split(
                ',')
            del transaction_details_season[-1]
            print(transaction_details_season)
            item['Transaction_details_season'] += transaction_details_season
            item['Transaction_details_id'] += i.xpath(".//tr//td[1]//text()").extract()
            item['Buying_stock_code'] += i.xpath(".//tr//td[2]//text()").extract()
            item['Buying_stock_name'] += i.xpath(".//tr//td[3]//text()").extract()
            item['Accumulated_buy_value'] += i.xpath(".//tr//td[5]//text()").extract()
            item['Accumulated_buy_percent_of_NAV'] += i.xpath(".//tr//td[6]//text()").extract()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            item['Setors_season'] = []  # 年份季度
            item['Setors_id'] = []  # 序号
            item['Setors'] = []  # 行业类别
            # item['Setors_change'] = []  # 行业变动详情
            item['Setors_percent'] = []  # 占净值比例
            item['Setors_value'] = []  # 市值（万元）
            self.year = 2017
            setors_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=setors_url, callback=self.parse_setors,
                                 meta={'fund_item': item})
        else:
            self.year -= 1
            transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=transaction_details_url, callback=self.parse_transaction_details,
                                 meta={'fund_item': item})

    # 7.行业配置
    def parse_setors(self, response):
        item = response.meta['fund_item']
        # if response.xpath('//tr/td/text()'):
        for i in response.xpath("//div[@class='box']"):
            setors_season = (
                (len(i.xpath('.//tr')) - 1) * str((
                                                      i.xpath(
                                                          ".//label[1]/text()").extract_first()).strip() + ',')).split(
                ',')
            del setors_season[-1]
            print(setors_season)
            item['Setors_season'] += setors_season
            item['Setors_id'] += i.xpath(".//tr//td[1]//text()").extract()
            item['Setors'] += i.xpath(".//tr//td[2]//text()").extract()
            if i.xpath(".//tr//td[5]"):
                item['Setors_percent'] += i.xpath(".//tr//td[4]//text()").extract()
                item['Setors_value'] += i.xpath(".//tr//td[5]//text()").extract()
            else:
                item['Setors_percent'] += i.xpath(".//tr//td[3]//text()").extract()
                item['Setors_value'] += i.xpath(".//tr//td[4]//text()").extract()

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2017
            setors_comparation_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=hypzsy&code={0}'.format(
                item['Fund_code'])
            yield scrapy.Request(url=setors_comparation_url, callback=self.parse_setors_comparation,
                                 meta={'fund_item': item})
        else:
            self.year -= 1
            setors_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=setors_url, callback=self.parse_setors, meta={'fund_item': item})

    # 9.行业配置比较表 Setors_comparation
    def parse_setors_comparation(self, response):
        item = response.meta['fund_item']
        year_list_pattern = re.compile(r'日期：(.*?)"};', re.S)
        try:
            date = year_list_pattern.findall(response.body.decode())[0][-17:-7]
        except:
            print(response.body.decode())
            date = ''
        comparation_date = ((len(response.xpath('//tr')) - 1) * (str(date) + ',')).split(',')
        del comparation_date[-1]
        item['Comparation_date'] = []
        item['Comparation_date'] += comparation_date
        item['CSRC_setors_code'] = response.xpath('//tr/td[1]//text()').extract()
        item['Setors_name'] = response.xpath('//tr/td[2]//text()').extract()
        item['Fund_setor_weight'] = response.xpath('//tr/td[3]//text()').extract()
        item['Similarfund_setor_weight'] = response.xpath('//tr/td[4]//text()').extract()
        item['Fund_setor_different'] = response.xpath('//tr/td[5]//text()').extract()
        parse_style_box_and_tracking_url = 'http://fund.eastmoney.com/f10/tsdata_{0}.html'.format(item['Fund_code'])
        yield scrapy.Request(url=parse_style_box_and_tracking_url, callback=self.parse_style_box_and_tracking,
                             meta={'fund_item': item})

    # 10.投资风格：http://fund.eastmoney.com/f10/tsdata_{0}.html
    # 11.跟踪指数指标Tracking:http://fund.eastmoney.com/f10/tsdata_{0}.html
    def parse_style_box_and_tracking(self, response):
        print('投资风格--------------------')
        item = response.meta['fund_item']
        item['Style_season'] = response.xpath("//div[@class='tzfg']//tr/td[1]//text()").extract()
        item['Style_box'] = response.xpath("//div[@class='tzfg']//tr/td[2]//text()").extract()
        print('跟踪指数--------------------')
        item['Tracking_index'] = response.xpath("//div[@id='jjzsfj']//tr[2]/td[1]//text()").extract_first() if response.xpath("//div[@id='jjzsfj']//tr[2]/td[1]//text()").extract_first() else ''
        item['Tracking_error'] = response.xpath("//div[@id='jjzsfj']//tr[2]/td[2]//text()").extract_first() if response.xpath("//div[@id='jjzsfj']//tr[2]/td[2]//text()").extract_first() else ''
        item['Similar_average_tracking_error'] = response.xpath(
            "//div[@id='jjzsfj']//tr[2]/td[3]//text()").extract_first() if response.xpath(
            "//div[@id='jjzsfj']//tr[2]/td[3]//text()").extract_first() else ''
        fund_manger_change_url = 'http://fund.eastmoney.com/f10/jjjl_{0}.html'.format(item['Fund_code'])
        yield scrapy.Request(url=fund_manger_change_url, callback=self.parse_fund_manger_change,
                             meta={'fund_item': item})

    # 12.基金经理变动表 Fund_manager_change：http://fund.eastmoney.com/f10/jjjl_{0}.html
    def parse_fund_manger_change(self, response):
        print('基金经理人------------------------------')
        item = response.meta['fund_item']
        table1_item = response.xpath("//div[@class='txt_in']/div[@class='box']//tr")
        item['Start_date'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table1_item.xpath('.//td[1]')] # 起始日期
        item['Ending_date'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table1_item.xpath('.//td[2]')]  # 截止期
        item['Fund_managers'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table1_item.xpath('.//td[3]')]  # 基金经理
        item['Current_fund_manager'] = item['Fund_managers'][0]  # 基金经理
        item['Appointment_time'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table1_item.xpath('.//td[4]')]  # 任职时间
        item['Appointment_return'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table1_item.xpath('.//td[5]')]  # 任职回报

        table2_item = response.xpath("//div[@class='txt_in']/div[@class='box nb']//tr")
        item['Held_fund_code'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[1]')]  # 基金名称
        item['Held_fund_name'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[2]')]  # 基金名称
        item['Held_fund_type'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[3]')]  # 基金类型
        item['Held_fund_start_time'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[4]')]  # 起始日期
        item['Held_fund_end_time'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[5]')]  # 截止日期
        item['Held_fund_appointment_time'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[6]')]  # 任职天数
        item['Held_fund_repayment'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[7]')]  # 任职回报
        item['Held_fund_similar_average'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[8]')]  # 同类平均
        item['Held_fund_similar_ranking'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in table2_item.xpath('.//td[9]')]  # 同类排名
        main_financial_index_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code={0}&showtype=1&year='.format(
            item['Fund_code'])
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

        yield scrapy.Request(url=main_financial_index_url, callback=self.parse_main_financial_index,
                             meta={'fund_item': item})

    def parse_main_financial_index(self, response):
        print('财务报表-----------------')
        item = response.meta['fund_item']
        item['Financial_index_date'] += response.xpath("//table[1]//th//text()").extract()[1:]  # 日期
        # item['Period_data_and_index'] = response.xpath("//table[1]//tbody/tr[1]//text()").extract()[1:]  # 期间数据和指标
        item['Period_realized_revenue'] += response.xpath("//table[1]//tbody/tr[1]//text()").extract()[1:]  # 本期已实现收益
        item['Period_profits'] += response.xpath("//table[1]//tbody/tr[2]//text()").extract()[1:]  # 本期利润
        item['Period_profits_of_weighted_average_shares'] += response.xpath(
            "//table[1]//tbody/tr[3]//text()").extract()[1:]  # 加权平均基金份额本期利润
        item['Period_profits_rate'] += response.xpath("//table[1]//tbody/tr[4]//text()").extract()[1:]  # 本期加权平均净值利润率
        item['Period_growth_of_NAV'] += response.xpath("//table[1]//tbody/tr[5]//text()").extract()[1:]  # 本期基金份额净值增长率

        # item['Ending_data_and_index'] = response.xpath("//table[1]//tbody/tr[1]//text()").extract()[1:]  # 期末数据和指标
        item['Ending_distributable_profits'] += response.xpath("//table[2]//tbody/tr[1]//text()").extract()[
                                                1:]  # 期末可供分配利润
        item['Ending_distributable_profits_of_shares'] += response.xpath("//table[2]//tbody/tr[2]//text()").extract()[
                                                          1:]  # 期末可供分配基金份额利润
        item['Ending_net_asset_value_of_fund'] += response.xpath("//table[2]//tbody/tr[3]//text()").extract()[
                                                  1:]  # 期末基金资产净值
        item['Ending_NAV'] += response.xpath("//table[2]//tbody/tr[4]//text()").extract()[1:]  # 期末基金份额净值

        item['Growth_of_ANAV'] += response.xpath("//table[3]//tbody/tr[1]//text()").extract()[1:]  # 基金份额累计净值增长率

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2017
            assets_balance_sheet_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zcfzb&code={0}&showtype=1&year='.format(
                item['Fund_code'])

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

            yield scrapy.Request(url=assets_balance_sheet_url, callback=self.parse_assets_balance_sheet,
                                 meta={'fund_item': item})
        else:
            self.year -= 1
            main_financial_index_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=main_financial_index_url, callback=self.parse_main_financial_index,
                                 meta={'fund_item': item})

    def parse_assets_balance_sheet(self, response):
        item = response.meta['fund_item']
        # item['Assets'] = []  # 资产
        item['Assets_date'] += response.xpath("//table[1]//th//text()").extract()[1:]  # 资产
        item['Bank_deposit'] += response.xpath("//table[1]//tbody/tr[2]//text()").extract()[1:]  # 银行存款
        item['Settlement_reserve'] += response.xpath("//table[1]//tbody/tr[3]//text()").extract()[1:]  # 结算备付金
        item['Guarantee_deposit_paid'] += response.xpath("//table[1]//tbody/tr[4]//text()").extract()[1:]  # 存出保证金
        item['Trading_financial_asset'] += response.xpath("//table[1]//tbody/tr[5]//text()").extract()[1:]  # 交易性金融资产
        item['Stock_investment'] += response.xpath("//table[1]//tbody/tr[6]//text()").extract()[1:]  # 其中：股票投资
        item['Fund_investment'] += response.xpath("//table[1]//tbody/tr[7]//text()").extract()[2:]  # 其中：基金投资
        item['Bond_investment'] += response.xpath("//table[1]//tbody/tr[8]//text()").extract()[2:]  # 其中：债券投资
        item['Asset_backed_securities_investment'] += response.xpath("//table[1]//tbody/tr[9]//text()").extract()[
                                                      2:]  # 其中：资产支持证券投资
        item['Derivative_financial_assets'] += response.xpath("//table[1]//tbody/tr[10]//text()").extract()[
                                               1:]  # 衍生金融资产
        item['Purchase_resale_financial_assets'] += response.xpath("//table[1]//tbody/tr[11]//text()").extract()[
                                                    1:]  # 买入返售金融资产
        item['Securities_settlement_receivable'] += response.xpath("//table[1]//tbody/tr[12]//text()").extract()[
                                                    1:]  # 应收证券清算款
        item['Interest_receivable'] += response.xpath("//table[1]//tbody/tr[13]//text()").extract()[1:]  # 应收利息
        item['Dividends_receivable'] += response.xpath("//table[1]//tbody/tr[14]//text()").extract()[1:]  # 应收股利
        item['Purchase_receivable'] += response.xpath("//table[1]//tbody/tr[15]//text()").extract()[1:]  # 应收申购款
        item['Deferred_income_tax_assets'] += response.xpath("//table[1]//tbody/tr[16]//text()").extract()[
                                              1:]  # 递延所得税资产
        item['Other_assets'] += response.xpath("//table[1]//tbody/tr[17]//text()").extract()[1:]  # 其他资产
        item['Total_assets'] += response.xpath("//table[1]//tbody/tr[18]//text()").extract()[1:]  # 资产总计
        # item['Debt'] = response.xpath("//table[1]//tbody/tr[2]//text()").extract()[1:]  # 负债：
        item['Short_term_loan'] += response.xpath("//table[2]//tbody/tr[2]//text()").extract()[1:]  # 短期借款
        item['Trading_financial_liability'] += response.xpath("//table[2]//tbody/tr[3]//text()").extract()[
                                               1:]  # 交易性金融负债
        item['Derivative_financial_liability'] += response.xpath("//table[2]//tbody/tr[4]//text()").extract()[
                                                  1:]  # 衍生金融负债
        item['Sell_repurchase_financial_assets'] += response.xpath("//table[2]//tbody/tr[5]//text()").extract()[
                                                    1:]  # 卖出回购金融资产款
        item['Securities_settlement_payable'] += response.xpath("//table[2]//tbody/tr[6]//text()").extract()[
                                                 1:]  # 应付证券清算款
        item['Redeem_payables'] += response.xpath("//table[2]//tbody/tr[7]//text()").extract()[1:]  # 应付赎回款
        item['Managerial_compensation_payable'] += response.xpath("//table[2]//tbody/tr[8]//text()").extract()[
                                                   1:]  # 应付管理人报酬
        item['Trustee_fee_payable'] += response.xpath("//table[2]//tbody/tr[9]//text()").extract()[1:]  # 应付托管费
        item['Sales_service_fee_payable'] += response.xpath("//table[2]//tbody/tr[10]//text()").extract()[1:]  # 应付销售服务费
        item['Taxation_payable'] += response.xpath("//table[2]//tbody/tr[11]//text()").extract()[1:]  # 应付税费
        item['Interest_payable'] += response.xpath("//table[2]//tbody/tr[12]//text()").extract()[1:]  # 应付利息
        item['Profits_receivable'] += response.xpath("//table[2]//tbody/tr[13]//text()").extract()[1:]  # 应收利润
        item['Deferred_income_tax_liability'] += response.xpath("//table[2]//tbody/tr[14]//text()").extract()[
                                                 1:]  # 递延所得税负债
        item['Other_liabilities'] += response.xpath("//table[2]//tbody/tr[15]//text()").extract()[1:]  # 其他负债
        item['Total_liabilities'] += response.xpath("//table[2]//tbody/tr[16]//text()").extract()[1:]  # 负债合计
        # item['Owner_equity'] = response.xpath("//table[2]//tbody/tr[17]//text()").extract()[1:]  # 所有者权益：
        item['Paid_in_fund'] += response.xpath("//table[2]//tbody/tr[18]//text()").extract()[1:]  # 实收基金
        item['Total_owner_equity'] += response.xpath("//table[2]//tbody/tr[19]//text()").extract()[1:]  # 所有者权益合计
        item['Total_debt_and_owner_equity'] += response.xpath("//table[2]//tbody/tr[20]//text()").extract()[
                                               1:]  # 负债和所有者权益合计

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2017
            income_statements_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=lrfpb&code={0}&showtype=1&year='.format(
                item['Fund_code'])

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
            yield scrapy.Request(url=income_statements_url, callback=self.parse_income_statements,
                                 meta={'fund_item': item})
        else:
            self.year -= 1
            assets_balance_sheet_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zcfzb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'], self.year)
            yield scrapy.Request(url=assets_balance_sheet_url, callback=self.parse_assets_balance_sheet,
                                 meta={'fund_item': item})

    def parse_income_statements(self, response):
        item = response.meta['fund_item']
        item['Income_date'] += response.xpath('//table//tr/th//text()').extract()  # 收入日期
        item['Income'] += response.xpath('//table//tr[1]/td//text()').extract()[1:]  # 收入
        item['Interest_income'] += response.xpath('//table//tr[2]/td//text()').extract()[1:]  # 利息收入
        item['Interest_income_of_deposit'] += response.xpath('//table//tr[3]/td//text()').extract()[1:]  # 其中：存款利息收入
        item['Interest_income_of_bond'] += response.xpath('//table//tr[4]/td//text()').extract()[2:]  # 其中：债券利息收入
        item['Interest_income_of_asset_backed_securities'] += response.xpath('//table//tr[5]/td//text()').extract()[
                                                             2:]  # 其中：资产支持证券利息收入
        item['Investment_income'] += response.xpath('//table//tr[6]/td//text()').extract()[2:]  # 投资收益
        item['Income_of_stock_investment'] += response.xpath('//table//tr[7]/td//text()').extract()[2:]  # 其中：股票投资收益
        item['Income_of_fund_investment'] += response.xpath('//table//tr[8]/td//text()').extract()[2:]  # 其中：基金投资收益
        item['Income_of_bond_investment'] += response.xpath('//table//tr[9]/td//text()').extract()[2:]  # 其中：债券投资收益
        item['Income_of_asset_backed_securities_investment'] += response.xpath('//table//tr[10]/td//text()').extract()[
                                                               2:]  # 其中：资产支持证券投资收益
        item['Income_of_derivatives'] += response.xpath('//table//tr[11]/td//text()').extract()[2:]  # 其中：衍生工具收益
        item['Dividend_income'] += response.xpath('//table//tr[12]/td//text()').extract()[2:]  # 其中：股利收益
        item['Income_of_fair_value_change'] += response.xpath('//table//tr[13]/td//text()').extract()[2:]  # 公允价值变动收益
        item['Exchange_earnings'] += response.xpath('//table//tr[14]/td//text()').extract()[2:]  # 汇兑收益
        item['Other_Income'] += response.xpath('//table//tr[15]/td//text()').extract()[2:]  # 其他收入
        item['Expense'] += response.xpath('//table//tr[16]/td//text()').extract()[1:]  # 费用
        item['Managerial_compensation'] += response.xpath('//table//tr[17]/td//text()').extract()[1:]  # 管理人报酬
        item['Trustee_fee'] += response.xpath('//table//tr[18]/td//text()').extract()[1:]  # 托管费
        item['Sales_service_fee'] += response.xpath('//table//tr[19]/td//text()').extract()[1:]  # 销售服务费
        item['Transaction_cost'] += response.xpath('//table//tr[20]/td//text()').extract()[1:]  # 交易费用
        item['Interest_expense'] += response.xpath('//table//tr[21]/td//text()').extract()[1:]  # 利息支出
        item['Sell_repurchase_financial_assets_expense'] += response.xpath('//table//tr[22]/td//text()').extract()[
                                                           1:]  # 其中：卖出回购金融资产支出
        item['Other_expenses'] += response.xpath('//table//tr[23]/td//text()').extract()[1:]  # 其他费用

        item['Profit_before_tax'] += response.xpath('//table//tr[24]/td//text()').extract()[2:]  # 利润总额
        item['Income_tax_expense'] += response.xpath('//table//tr[25]/td//text()').extract()[1:]  # 减：所得税费用

        item['Net_profit'] += response.xpath('//table//tr[26]/td//text()').extract()[2:]  # 净利润

        year_list_pattern = re.compile(r'arryear:(.*?),curyear', re.S)
        current_year_pattern = re.compile(r',curyear:(.*?)};', re.S)
        year_list = json.loads(year_list_pattern.findall(response.body.decode())[0])  # [2017,2016,2015,2014]
        current_year = int(current_year_pattern.findall(response.body.decode())[0])
        last_year = int(year_list[-1])
        print('last_year:', last_year)
        print('current_year:', current_year)
        if current_year <= last_year:
            self.year = 2017
            income_analysis_url = 'http://fund.eastmoney.com/f10/srfx_{0}.html'.format(item['Fund_code'])
            yield scrapy.Request(url=income_analysis_url, callback=self.parse_income_analysis, meta={'fund_item': item})
        else:
            self.year -= 1
            income_statements_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=lrfpb&code={0}&showtype=1&year={1}'.format(
                item['Fund_code'],self.year)
            yield scrapy.Request(url=income_statements_url, callback=self.parse_income_statements,
                                 meta={'fund_item': item})

    def parse_income_analysis(self, response):
        item = response.meta['fund_item']
        item['Income_analysis_Date'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[1]//text()").extract()  # 报告期
        item['Total_income'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[2]//text()").extract()  # 收入合计
        item['Stock_income'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[3]//text()").extract()  # 股票收入
        item['Stock_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[4]//text()").extract()  # 占比
        item['Bond_income'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[5]//text()").extract()  # 债券收入
        item['Bond_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[6]//text()").extract()  # 占比
        item['Dividends_income'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[7]//text()").extract()  # 股利收入
        item['Dividends_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[8]//text()").extract()  # 占比
        expenses_analysis_url = 'http://fund.eastmoney.com/f10/fyfx_{0}.html'.format(
            item['Fund_code'])
        yield scrapy.Request(url=expenses_analysis_url, callback=self.parse_expenses_analysis, meta={'fund_item': item})

    def parse_expenses_analysis(self, response):
        item = response.meta['fund_item']
        item['Expenses_analysis_date'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[1]//text()").extract()  # 报告期
        item['Total_expenses'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[2]//text()").extract()  # 费用合计
        item['Expenses_analysis_managerial_compensation'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[3]//text()").extract()  # 管理人报酬
        item['Managerial_compensation_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[4]//text()").extract()  # 占比
        item['Expenses_analysis_trustee_fee'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[5]//text()").extract()  # 托管费
        item['Trustee_fee_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[6]//text()").extract()  # 托管费占比
        item['Expenses_analysis_transaction_cost'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[7]//text()").extract()  # 交易费
        item['Transaction_cost_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[8]//text()").extract()  # 交易费占比
        item['Expenses_analysis_sales_service_fee'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[9]//text()").extract()  # 销售服务费
        item['Sales_service_fee_percent'] = response.xpath(
            "//table[@class='w782 comm income']/tbody/tr/td[10]//text()").extract()  # 销售服务费占比
        fund_allocations_url = 'http://fund.eastmoney.com/f10/zcpz_{0}.html'.format(item['Fund_code'])
        yield scrapy.Request(url=fund_allocations_url, callback=self.parse_fund_allocations, meta={'fund_item': item})

    def parse_fund_allocations(self, response):
        item = response.meta['fund_item']

        item['Fund_allocations_Date'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[1]//text()").extract()  # 报告期
        item['Fund_allocations_Stock_percent'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[2]//text()").extract()  # 股票占净比
        item['Fund_allocations_Bond_percent'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[3]//text()").extract()  # 债券占净比
        item['Cash_percent'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[4]//text()").extract()  # 现金占净比
        item['Net_asset'] = response.xpath("//table[@class='w782 comm tzxq']//tr/td[5]//text()").extract()  # 净资产（亿元）

        history_NAV_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10000&sdate=&edate='.format(
            item['Fund_code'])
        yield scrapy.Request(url=history_NAV_url, callback=self.parse_history_NAV, meta={'fund_item': item})

    def parse_history_NAV(self, response):
        item = response.meta['fund_item']

        item['History_NAV_Date'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[1]")]  # 净值日期
        item['NAV'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[2]")]  # 单位净值
        item['ANAV'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[3]")]  # 累计净值
        item['Day_change'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[4]")]  # 收益率
        item['Purchase_status'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[5]")]  # 申购状态
        item['Redeem_status'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[6]")]  # 赎回状态
        item['Dividends_distribution'] = [i.xpath('.//text()').extract_first() if i.xpath('.//text()').extract_first() else '' for i in response.xpath("//table[@class='w782 comm lsjz']/tbody/tr/td[7]")]  # 分红配送
        acworth_url = 'http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode={0}&indexcode=000300&type=se&callback='.format(item['Fund_code'])
        yield scrapy.Request(url=acworth_url,callback=self.parse_acworth,meta={'fund_item':item})

    def parse_acworth(self,response):
        item = response.meta['fund_item']
        dict_json = json.loads(response.body.decode())
        item['ACWorth_date'] = [int(i[0])/1000  for i in dict_json[0]['data']]
        item['this_fund_rate'] = [i[1] for i in dict_json[0]['data']]
        item['similar_fund_rate'] = [i[1] for i in dict_json[1]['data']]
        item['hs300_rate'] = [i[1] for i in dict_json[2]['data']]
        yield item
