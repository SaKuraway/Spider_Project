# -*- coding: utf-8 -*-
import json

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
            item['fundPinyin'] = each[2]
            # item['spiderDate'] = each[3]
            # item['unitValue'] = each[4]
            # item['totalValue'] = each[5]
            # item['dailyGrowthRate'] = each[6]
            item['nearly1weeksRate'] = each[7]
            item['nearly1monthsRate'] = each[8]
            item['nearly3monthsRate'] = each[9]
            item['nearly6monthsRate'] = each[10]
            item['nearly1yearsRate'] = each[11]
            item['nearly2yearsRate'] = each[12]
            item['nearly3yearsRate'] = each[13]
            item['thisYearRate'] = each[14]
            item['sinceEstablishedRate'] = each[15]
            item['proceduresFee'] = each[20]
            fund_info_url = 'http://fund.eastmoney.com/f10/jbgk_{0}.html'.format(each[0])
            yield scrapy.Request(url=fund_info_url, callback=self.parse_fundinfo, meta={'fund_item': item})

    # 2.基金概况页面
    def parse_fundinfo(self, response):
        item = response.meta['fund_item']
        item['Fund_name'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[1]/td[1]/text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[1]/td[1]/text()') else ''
        item['Min_Purchase'] = ''.join(response.xpath(
            "//div[@id='bodydiv']//div[@class='basic-new ']//div[@class='col-left']//a[@class='btn  btn-red ']//span//text()").extract())
        item['fundType'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[2]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[2]/td[2]//text()') else ''  # 基金类型
        item['riskLevel'] = response.xpath(
            "//div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()").extract_first().strip() if response.xpath(
            "//div[@class='detail']/div[@class='txt_cont']/div[@class='txt_in']/div[@class='box nb']/div[@class='boxitem w790']/p//text()") else ''  # 风险等级
        item['Launch_Date'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[3]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[3]/td[1]//text()') else ''  # 成立时间
        item['Inception_Date'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[3]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[3]/td[2]//text()') else ''  # 成立时间
        item['assetsScale'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[4]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[4]/td[1]//text()') else ''  # 资产管理规模
        item['shareScale'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[4]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[4]/td[2]//text()') else ''  # 份额规模
        item['fundAdministrator'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[5]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[5]/td[1]//text()') else ''  # 基金管理人
        item['fundCustodian'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[5]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[5]/td[2]//text()') else ''  # 基金托管人
        item['Management_Fee'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[7]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[7]/td[1]//text()') else ''  # 管理费率
        item['custodianRate'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[7]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[7]/td[2]//text()') else ''  # 托管费率
        item['Max_Initial_Charge'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[9]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[9]/td[1]//text()') else ''
        item['Max_Redemption_charge'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[9]/td[2]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[9]/td[2]//text()') else ''
        item['Benchmark'] = response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[10]/td[1]//text()').extract_first() if response.xpath(
            '//div[@class="txt_in"]//table[@class="info w790"]//tr[10]/td[1]//text()') else ''

        fund_size_change_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code={0}'.format(
            item['fundCode'])
        # print(fund_js_url)
        yield scrapy.Request(url=fund_size_change_url, callback=self.parse_fund_size_change, meta={'fund_item': item})

    # def parse_fundjs(self, response):
    #     item = response.meta['fund_item']
    #     json_html = response.body.decode()
    #     # / *基金/股票名称 * /
    #     pattern_fundName = re.compile(r'var fS_name = "(.*?)";', re.S)
    #     item['Fund_name'] = pattern_fundName.findall(json_html)[0]
    #     # print(fundName)
    #     # /*股票仓位测算图*/
    #     # pattern_fundSharesPositions = re.compile(r'var Data_fundSharesPositions = (.*?);',re.S)
    #     # fundSharesPositions = pattern_fundSharesPositions.findall(json_html)[0]
    #     # print(fundSharesPositions)
    #     # /*单位净值走势 equityReturn-净值回报 unitMoney-每份派送金*/
    #     # pattern_netWorthTrend  = re.compile(r'var Data_netWorthTrend = (.*?);',re.S)
    #     # netWorthTrend = pattern_netWorthTrend.findall(json_html)[0]
    #     # print(netWorthTrend)
    #     # /*累计净值走势*/
    #     # pattern_ACWorthTrend = re.compile(r'var Data_ACWorthTrend = (.*?);', re.S)
    #     # item['ACWorthTrend'] = pattern_ACWorthTrend.findall(json_html)[0]
    #     # print(ACWorthTrend)
    #     # /*现任基金经理：任职时间、任期收益、同类平均*/
    #     pattern_currentFundManager = re.compile(r'var Data_currentFundManager =(.*?);', re.S)
    #     item['currentFundManager'] = pattern_currentFundManager.findall(json_html)[0]
    #     # print(currentFundManager)
    #     # /*资产配置占比*/
    #     pattern_assetAllocation = re.compile(r'var Data_assetAllocation = {"series":(.*?),"categories"', re.S)
    #     item['assetAllocation'] = pattern_assetAllocation.findall(json_html)[0]
    #     # print(assetAllocation)
    #     # /*累计收益率走势(本基金、沪深300、同类平均)*/
    #     pattern_grandTotal = re.compile(r'var Data_grandTotal = (.*?);', re.S)
    #     item['grandTotal'] = pattern_grandTotal.findall(json_html)[0]
    #     # print(grandTotal)
    #     acworth_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10000'.format(
    #         item['fundCode'])
    #     # print(fund_js_url)
    #     yield scrapy.Request(url=acworth_url, callback=self.parse_acworth, meta={'fund_item': item})

    # 3.基金规模变动
    def parse_fund_size_change(self, response):
        item = response.meta['fund_item']
        item['Fund_size_change_Date'] = response.xpath("//tr//td[1]//text()").extract()
        item['Period_Purchase'] = response.xpath("//tr//td[2]//text()").extract()
        item['Period_Redeem'] = response.xpath("//tr//td[3]//text()").extract()
        item['Eneding_shares'] = response.xpath("//tr//td[4]//text()").extract()
        item['Eneding_net_asset'] = response.xpath("//tr//td[5]//text()").extract()
        item['Net_asset_change'] = response.xpath("//tr//td[6]//text()").extract()

        fund_holder_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cyrjg&code={0}'.format(
            item['fundCode'])
        yield scrapy.Request(url=fund_holder_url, callback=self.parse_fund_holder, meta={'fund_item': item})

    # 4.基金持有人结构
    def parse_fund_holder(self, response):
        item = response.meta['fund_item']
        item['Fund_holder_Date'] = response.xpath("//tr//td[1]//text()").extract()
        item['Institution'] = response.xpath("//tr//td[2]//text()").extract()
        item['Individual'] = response.xpath("//tr//td[3]//text()").extract()
        item['Internal'] = response.xpath("//tr//td[4]//text()").extract()
        item['Total_shares'] = response.xpath("//tr//td[5]//text()").extract()
        self.year = 2017
        item['Fund_holding_season'] = []
        item['Fund_holding_id'] = []
        item['Stock_code'] = []
        item['Stock_name'] = []
        item['single_stock_percent'] = []
        item['Stock_holding_quantity'] = []
        item['Stock_holding_value'] = []
        fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
            item['fundCode'], self.year)
        yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})

    # 5.基金持仓明细
    def parse_fund_holding(self, response):
        item = response.meta['fund_item']
        if response.xpath('//tr/td/text()'):
            for item in response.xpath("//div[@class='box']"):
                fund_holding_season = (
                    (len(item.xpath('//tr')) - 1) * (item.xpath(".//label[1]/text()").extract_first().strip() + ',')).split(
                    ',')
                del fund_holding_season[-1]
                item['Fund_holding_season'] += fund_holding_season
                item['Fund_holding_id'] += item.xpath(".//tr//td[1]//text()").extract()
                item['Stock_code'] += item.xpath(".//tr//td[2]//text()").extract()
                item['Stock_name'] += item.xpath(".//tr//td[3]//text()").extract()
                if item.xpath(".//tr//td[9]//text()"):
                    item['Single_stock_percent'] += item.xpath(".//tr//td[7]//text()").extract()
                    item['Stock_holding_quantity'] += item.xpath(".//tr//td[8]//text()").extract()
                    item['Stock_holding_value'] += item.xpath(".//tr//td[9]//text()").extract()
                else:
                    item['single_stock_percent'] += item.xpath(".//tr//td[5]//text()").extract()
                    item['Stock_holding_quantity'] += item.xpath(".//tr//td[6]//text()").extract()
                    item['Stock_holding_value'] += item.xpath(".//tr//td[7]//text()").extract()
            self.year -= 1
            fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})
        else:
            item['Transaction_details_season'] = []
            item['Transaction_details_id'] = []
            item['Buying_stock_code'] = []
            item['Buying_stock_name'] = []
            item['Accumulated_buy_value'] = []
            item['Accumulated_buy_percent_of_NAV'] = []
            self.year = 2017
            Transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=Transaction_details_url, callback=self.parse_transaction_details,
                                 meta={'fund_item': item})

    # 6.重大变动
    def parse_transaction_details(self, response):
        item = response.meta['fund_item']
        if response.xpath('//tr/td/text()'):
            for item in response.xpath("//div[@class='box']"):
                transaction_details_season = (
                    (len(item.xpath('//tr'))-1) * (item.xpath(".//label[1]/text()").extract_first().strip() + ',')).split(',')
                del transaction_details_season[-1]
                item['Transaction_details_season'] += transaction_details_season
                item['Transaction_details_id'] += item.xpath(".//tr//td[1]//text()").extract()
                item['Buying_stock_code'] += item.xpath(".//tr//td[2]//text()").extract()
                item['Buying_stock_name'] += item.xpath(".//tr//td[3]//text()").extract()
                item['Accumulated_buy_value'] += item.xpath(".//tr//td[5]//text()").extract()
                item['Accumulated_buy_percent_of_NAV'] += item.xpath(".//tr//td[6]//text()").extract()
            self.year -= 1
            fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})
        else:
            item['Setors_season'] = []  # 年份季度
            item['Setors_id'] = []  # 序号
            item['Setors'] = []  # 行业类别
            item['Setors_change'] = []  # 行业变动详情
            item['Setors_percent'] = []  # 占净值比例
            item['Setors_value'] = []  # 市值（万元）
            item['Setoes_PE'] = []  # 行业市盈率
            self.year = 2017
            setors_url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=setors_url, callback=self.parse_setors,
                                 meta={'fund_item': item})

    # 7.行业配置
    def parse_setors(self, response):
        item = response.meta['fund_item']
        if response.xpath('//tr/td/text()'):
            for item in response.xpath("//div[@class='box']"):
                transaction_details_season = (
                    (len(item.xpath('//tr'))-1) * (item.xpath(".//label[1]/text()").extract_first().strip() + ',')).split(',')
                del transaction_details_season[-1]
                item['Setors_season'] += transaction_details_season
                item['Setors_id'] += item.xpath(".//tr//td[1]//text()").extract()
                item['Setors'] += item.xpath(".//tr//td[2]//text()").extract()
                item['Setors_change'] +=  item.xpath(".//tr//td[3]//text()").extract()
                item['Setors_percent'] += item.xpath(".//tr//td[5]//text()").extract()
                item['Setors_value'] += item.xpath(".//tr//td[6]//text()").extract()
                item['Setoes_PE'] += item.xpath(".//tr//td[6]//text()").extract()
            self.year -= 1
            fund_holding_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code={0}&topline=10&year={1}&month=1,2,3,4,5,6,7,8,9,10,11,12'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=fund_holding_url, callback=self.parse_fund_holding, meta={'fund_item': item})
        else:
            self.year = 2017
            Transaction_details_url = 'http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}}'.format(
                item['fundCode'], self.year)
            yield scrapy.Request(url=Transaction_details_url, callback=self.parse_fund_holding,
                                 meta={'fund_item': item})































































    def parse_acworth(self, response):
        item = response.meta['fund_item']
        vals = []
        for values in response.xpath('//table/tbody/tr'):
            vals.append([value for value in values.xpath('./td/text()').extract()])
        item['ACWorth'] = vals
        yield item
