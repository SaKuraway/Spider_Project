# -*- coding: utf-8 -*-
import scrapy,requests
import pandas as pd
from ..items import BbaeSpiderItem

class BbaeSpiderSpider(scrapy.Spider):
    name = "bbae_spider"
    allowed_domains = ["morningstar.co.uk"]
    excel_data = pd.read_excel('Excel/BBAE股票信息.xlsx')
    search_ISIN = excel_data['ISIN']
    all_search_url = ['http://www.morningstar.co.uk/uk/funds/SecuritySearchResults.aspx?search='+str(ISIN) for ISIN in search_ISIN]
    # start_urls = all_search_url
    start_urls = ['http://www.morningstar.co.uk/uk/funds/SecuritySearchResults.aspx?search=US92189F7261']

    def parse(self, response):
        try:
            spider_url = 'http://www.morningstar.co.uk/'+response.xpath("//tr[@class='gridItem']/td[@class='msDataText searchLink']/a/@href").extract_first()
        except:
            print('error,skip!')
        else:
            yield scrapy.Request(spider_url,callback=self.parse_overview)

    def parse_overview(self,response):
        item = BbaeSpiderItem()
        item['fund_name'] = response.xpath("//div[@class='snapshotTitleBox']/h1//text()").extract_first().strip().replace('\n','') if response.xpath("//div[@class='snapshotTitleBox']/h1") else ''
        item['closing_price'] = (''.join(response.xpath("//tr[2]/td[@class='line text']//text()").extract()).strip().replace('\n','')+"("+''.join(response.xpath("//tr[2]/td[@class='line heading']/span//text()").extract()).strip().replace('\n','')+")").strip().replace('\xa0','')
        item['day_change'] = ''.join(response.xpath("//tr[3]/td[@class='line text']//text()").extract()).strip().replace('\n','')
        item['morningstar_category'] = ''.join(response.xpath("//tr[4]/td[@class='line value text']//text()").extract()).strip().replace('\n','')
        item['volume'] = ''.join(response.xpath("//tr[5]/td[@class='line text']//text()").extract()).strip().replace('\n','')
        item['exchange'] = ''.join(response.xpath("//tr[6]/td[@class='line text']//text()").extract()).strip().replace('\n','')
        item['ISIN'] = ''.join(response.xpath("//tr[7]/td[@class='line text']//text()").extract()).strip().replace('\n','')
        item['fund_size_mil'] = ''.join(response.xpath("//tr[9]/td[@class='line text']//text()").extract()).strip().replace('\n','')+"("+''.join(response.xpath("//tr[9]/td[@class='line heading']/span//text()").extract()).strip().replace('\n','').replace('\xa0','')+")"
        # item['ongoing_charge'] = ''.join(response.xpath("//tr[10]/td[@class='line text']//text()").extract()).strip().replace('\n','')+"("+''.join(response.xpath("//tr[10]/td[@class='line heading']/span//text()").extract()).strip().replace('\n','')+")"
        item['category'] = ''.join(response.xpath("//tr[6]/td[@class='footer']/span[@class='value']//text()").extract()).strip().replace('\n','')
        item['category_benchmark'] = ''.join(response.xpath("//tr[7]/td[@class='footer']/span[@class='value']//text()").extract()).strip().replace('\n','')
        item['morningstar_research'] = ''.join(response.xpath("//footer[@class='ec-sustainability__footer']/p//text()").extract()).strip('\n')  #
        item['morningstar_sustainability'] = ''.join(response.xpath("//header[@class='ec-sustainability__header']/h1[@class='ec-sustainability__title']/small//text()").extract()).strip('\n')  #
        item['sustainability_mandate'] = ''.join(response.xpath("//div[@class='ec-sustainability__content']/div[@class='ec-columns ec-columns-right']/h3[@class='ec-sustainability__value ng-binding'][2]//text()").extract()).strip('\n')  #
        item['percent_rank_in_category'] = ''.join(response.xpath("//div[@class='ec-sustainability__content']//div[@class='ec-sustainability__summary']/p[1]//text()").extract()).strip('\n')  #
        item['sustainability_score'] = ''.join(response.xpath("//div[@class='ec-sustainability__content']//div[@class='ec-sustainability__summary']/p[2]//text()").extract()).strip('\n')  #
        item['investment_objective'] = ''.join(response.xpath("//div[@id='overviewObjectiveDiv']//tr[2]/td[@class='value text']//text()").extract()).strip().replace('\n','')
        item['trailing_returns'] = ''.join(response.xpath("//div[@id='TrailingReturnsOverview']//tr[1]/td[@class='heading date']//text()").extract()).strip().replace('\n','')
        item['YTD'] = ''.join(response.xpath("//div[@id='TrailingReturnsOverview']//tr[2]/td[@class='value number']//text()").extract()).strip().replace('\n','')
        item['three_years_annualised'] = ''.join(response.xpath("//div[@id='TrailingReturnsOverview']//tr[3]/td[@class='value number']//text()").extract()).strip().replace('\n','')
        item['five_years_annualised'] = ''.join(response.xpath("//div[@id='TrailingReturnsOverview']//tr[4]/td[@class='value number']//text()").extract()).strip().replace('\n','')
        item['ten_years_annualised'] = ''.join(response.xpath("//div[@id='TrailingReturnsOverview']//tr[5]/td[@class='value number']//text()").extract()).strip().replace('\n','')
        # item['manager_name'] = ''.join(response.xpath("//div[@id='FundManagersOverview']//tr//div[@class='overviewManagerNameDiv']//text()").extract()[1:-1]).strip().replace('\n','')
        # item['start_date'] = ''.join(response.xpath("//div[@id='FundManagersOverview']//tr//div[@class='overviewManagerStartDateDiv']//text()").extract()[1:-1]).strip().replace('\n','')
        # item['inception_date'] = ''.join(response.xpath("//div[@id='FundManagersOverview']//tr//div[@class='overviewManagerStartDateDiv']//text()").extract()[-1]).strip().replace('\n','')
        item['fund_benchmark'] = ''.join(response.xpath("//div[@id='overviewBenchmarkDiv2Cols']//tr[4]/td[@class='value text'][1]//text()").extract()).strip().replace('\n','')
        item['morningstar_benchmark'] = ''.join(response.xpath("//div[@id='overviewBenchmarkDiv2Cols']//tr[4]/td[@class='value text'][2]//text()").extract()).strip().replace('\n','')
        item['style_box_src'] = 'http://www.morningstar.co.uk'+response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src").extract_first() if response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src") else ''
        if response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src").extract_first():
            style_box_img = requests.get(item['style_box_src']).content
            with open(str(item['ISIN'])+'_style_box.gif','wb') as f:
                f.write(style_box_img)
            f.close()
        item['stock_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][1]//text()").extract()).strip().replace('\n','')
        item['stock_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][2]//text()").extract()).strip().replace('\n','')
        item['stock_net_assets'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][3]//text()").extract()).strip().replace('\n','')
        item['bond_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][1]//text()").extract()).strip().replace('\n','')
        item['bond_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][2]//text()").extract()).strip().replace('\n','')
        item['bond_net_assets'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][3]//text()").extract()).strip().replace('\n','')
        item['property_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][1]//text()").extract()).strip().replace('\n','')
        item['property_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][2]//text()").extract()).strip().replace('\n','')
        item['property_net_assets'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][3]//text()").extract()).strip().replace('\n','')
        item['cash_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][1]//text()").extract()).strip().replace('\n','')
        item['cash_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][2]//text()").extract()).strip().replace('\n','')
        item['cash_net_assets'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][3]//text()").extract()).strip().replace('\n','')
        item['other_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][1]//text()").extract()).strip().replace('\n','')
        item['other_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][2]//text()").extract()).strip().replace('\n','')
        item['other_net_assets'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][3]//text()").extract()).strip().replace('\n','')

        item['top_5_regions'] = response.xpath("//div[@id='overviewPortfolioTopRegionsDiv']//tr//td[@class='label']//text()").extract()
        item['top_5_regions_percent'] = response.xpath("//div[@id='overviewPortfolioTopRegionsDiv']//tr//td[@class='value number']//text()").extract()
        item['top_5_sectors'] = response.xpath("//div[@id='overviewPortfolioTopSectorsDiv']//tr//td[@class='label']//text()").extract()
        item['top_5_sectors_percent'] = response.xpath("//div[@id='overviewPortfolioTopSectorsDiv']//tr//td[@class='value number']//text()").extract()
        item['top_5_holdings'] = response.xpath("//div[@id='overviewPortfolioTopHoldingsDiv']//tr//td[@class='col1 label']//text()").extract()
        item['top_5_holdings_sector'] = response.xpath("//div[@id='overviewPortfolioTopHoldingsDiv']//tr//td[@class='col2 label']//text()").extract()
        item['top_5_holdings_percent'] = response.xpath("//div[@id='overviewPortfolioTopHoldingsDiv']//tr//td[@class='col3 value number']//text()").extract()
        # with open('123.html','wb') as f:
        #     f.write(response.body)
        # f.close()
        portfolio_url = 'http://www.morningstar.co.uk//uk/etf/snapshot/'+response.xpath("//div[@id='snapshotTabNewDiv']//tr[last()-3]/td/a/@href").extract_first()

        yield scrapy.Request(portfolio_url,callback=self.parse_portfolio,meta={'item':item})

    def parse_portfolio(self,response):
        item = response.meta['item']
        item['portfolio_title'] = ''.join(response.xpath("//div[@id='snapshotTitleDiv']//div[@class='snapshotTitleBox']//text()").extract()).strip().replace('\n','').replace('\t','')
        item['size_name'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]/td[@class='data']//tr//td[@class='col1 label']//text()").extract()).strip().replace('\n','').replace('\t','')
        item['size_value'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]/td[@class='data']//tr//td[@class='col2 value number']//text()").extract()).strip().replace('\n','').replace('\t','')
        item['size_rel_to_cat'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]/td[@class='data']//tr//td[@class='col3 value number']//text()").extract()).strip().replace('\n','').replace('\t','')

        # item['market_capitalisation_giant'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[3]/td[@class='label']//text()").extract()  # list
        item['market_capitalisation_giant_equity'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[3]/td[@class='value number']//text()").extract())  # list
        # item['market_capitalisation_large'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[4]/td[@class='label']//text()").extract()  # list
        item['market_capitalisation_large_equity'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[4]/td[@class='value number']//text()").extract())  # list
        # item['market_capitalisation_medium'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[5]/td[@class='label']//text()").extract()  # list
        item['market_capitalisation_medium_equity'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[5]/td[@class='value number']//text()").extract())  # list
        # item['market_capitalisation_small'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[6]/td[@class='label']//text()").extract()  # list
        item['market_capitalisation_small_equity'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[6]/td[@class='value number']//text()").extract())  # list
        # item['market_capitalisation_micro'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[7]/td[@class='label']//text()").extract()  # list
        item['market_capitalisation_micro_equity'] = ''.join(response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[2]//tr[7]/td[@class='value number']//text()").extract())  # list

        item['valuations_and_growth_rates'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[4]//tr//td[@class='label']//text()").extract()  # list
        item['equity_portfolio'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[4]//tr//td[@class='value number'][1]//text()").extract()  # list
        item['relative_to_category'] = response.xpath("//div[@id='portfolioEquityStyleDiv']//tr[4]//tr//td[@class='value number'][2]//text()").extract()  # list

        item['world_regions'] = response.xpath("//div[@id='portfolioRegionalBreakdownDiv']//tr[2]/td[@class='data']//tr//td[@class='label']//text()").extract()  # list
        item['world_regions_equity'] = response.xpath("//div[@id='portfolioRegionalBreakdownDiv']//tr[2]/td[@class='data']//tr//td[@class='value number'][1]//text()").extract()  # list
        item['world_regions_relative_to_category'] = response.xpath("//div[@id='portfolioRegionalBreakdownDiv']//tr[2]/td[@class='data']//tr//td[@class='value number'][2]//text()").extract()  # list

        item['sector_weightings'] = response.xpath("//div[@id='portfolioSectorBreakdownDiv']//tr[2]/td//tr//td[@class='label']//text()").extract()  # list
        item['sector_weightings_equity'] = response.xpath("//div[@id='portfolioSectorBreakdownDiv']//tr[2]/td//tr//td[@class='value number'][1]//text()").extract()  # list
        item['sector_weightings_relative_to_category'] = response.xpath("//div[@id='portfolioSectorBreakdownDiv']//tr[2]/td//tr//td[@class='value number'][2]//text()").extract()  # list

        # item['total_number_of_equity_holdings'] = ''.join(response.xpath("//div[@id='portfolioTopHoldingsDiv']//div[@id='portfolioTopHoldingsSummaryDiv']//tr[2]/td[@class='label']//text()").extract())  # list
        # item['total_number_of_equity_holdings_portfolio'] = ''.join(response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsSummaryDiv']//tr[2]/td[@class='value number']//text()").extract())  # list
        # item['total_number_of_bond_holdings'] = ''.join(response.xpath("//div[@id='portfolioTopHoldingsDiv']//div[@id='portfolioTopHoldingsSummaryDiv']//tr[2]/td[@class='label']//text()").extract())  # list
        # item['total_number_of_bond_holdings_portfolio'] = ''.join(response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsSummaryDiv']//tr[3]/td[@class='value number']//text()").extract())  # list
        item['top_10_holdings'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']//div[@id='portfolioTopHoldingsSummaryDiv']//tr//td[@class='label']//text()").extract()  # list
        item['top_10_holdings_portfolio'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsSummaryDiv']//tr//td[@class='value number']//text()").extract()  # list
        # item['top_10_holdings_summary'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']//div[@id='portfolioTopHoldingsSummaryDiv']//tr//td[@class='label']//text()").extract()  # list
        # item['top_10_holdings_summary_portfolio'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsSummaryDiv']//tr//td[@class='value number']//text()").extract()  # list
        item['top_10_holdings_name'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']//tr/td[@class='col1 label']//text()").extract()  # list
        item['top_10_holdings_sector'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsDataDiv']//tr//td[@class='col2 value text']/img/@src").extract()  # list
        item['top_10_holdings_country'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsDataDiv']//tr//td[@class='col3 value text']//text()").extract()  # list
        item['top_10_holdings_percent_of_assets'] = response.xpath("//div[@id='portfolioTopHoldingsDiv']/div[@id='portfolioTopHoldingsDataDiv']//tr//td[@class='col4 value number']//text()").extract()  # list
        management_url = 'http://www.morningstar.co.uk//uk/etf/snapshot/'+response.xpath("//div[@id='snapshotTabNewDiv']//tr[last()-2]/td/a/@href").extract_first()
        # yield item
        yield scrapy.Request(management_url,callback=self.parse_management,meta={'item':item})

    def parse_management(self,response):
        item = response.meta['item']
        item['name_of_company'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[1]/td[@class='col2 value number']//text()").extract()).strip()
        item['phone'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[2]/td[@class='col2 value number']//text()").extract()).strip()
        item['website'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[3]/td[@class='col2 value number']//text()").extract()).strip()
        item['address'] = (''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[4]/td[@class='col2 value number']//text()").extract())+''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[5]/td[@class='col2 value number']//text()").extract()).strip()+''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]//div[@id='managementManagementFundCompanyDiv']//tr[6]/td[@class='col2 value number']//text()").extract())).strip().replace('\n','').replace('\xa0','')
        item['domicile'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]/td/div[@id='managementManagementFundManagerDiv']//tr[1]/td[@class='col2 value number']//text()").extract()).strip()
        item['legal_structure'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]/td/div[@id='managementManagementFundManagerDiv']//tr[2]/td[@class='col2 value number']//text()").extract()).strip()
        item['UCITS'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]/td/div[@id='managementManagementFundManagerDiv']//tr[3]/td[@class='col2 value number']//text()").extract()).strip()
        item['inception_date'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]/td/div[@id='managementManagementFundManagerDiv']//tr[4]/td[@class='value number']//text()").extract()).strip()
        item['fund_advisor'] = ''.join(response.xpath("//div[@id='managementManagementDiv']//tr[2]/td/div[@id='managementManagementFundManagerDiv']//tr[last()]/td//text()").extract())
        item['fund_managers'] = [manager.strip().replace('\xa0','') for manager in response.xpath("//div[@id='managementManagementDiv']//div[@id='managementManagementFundCompanyDiv']//tr[1]/td[@class='col2 value number']//text()").extract()[1:]]
        item['manager_start_dates'] = response.xpath("//div[@id='managementManagementDiv']//div[@id='managementManagementFundCompanyDiv']//tr[2]/td[@class='col2 value number']//text()").extract()
        item['biographies'] = response.xpath("//div[@id='managementManagementDiv']//tr[4]/td[@class='value text']//text()").extract()
        fees_url = 'http://www.morningstar.co.uk//uk/etf/snapshot/' + response.xpath(
            "//div[@id='snapshotTabNewDiv']//tr[last()-1]/td/a/@href").extract_first()
        # yield item
        yield scrapy.Request(fees_url, callback=self.parse_fees, meta={'item': item})

    def parse_fees(self,response):
        item = response.meta['item']
        # item['sales_charges_maximum'] = response.xpath("//div[@id='managementFeesDiv']//tr[2]//div[@id='managementFeesSalesFeesDiv']//tr[2]/td[@class='label']//text()").extract()
        # item['sales_charges_maximum'] = response.xpath("//div[@id='managementFeesDiv']//tr[3]//div[@id='managementFeesSalesFeesDiv']//tr[2]/td[@class='label']//text()").extract()
        item['max_initial_charge'] = ''.join(response.xpath("//div[@id='managementFeesDiv']//tr[2]//div[@id='managementFeesSalesFeesDiv']//tr[2]/td[@class='value number']//text()").extract()).strip()
        item['max_exit_charge'] = ''.join(response.xpath("//div[@id='managementFeesDiv']//tr[2]//div[@id='managementFeesSalesFeesDiv']//tr[3]/td[@class='value number']//text()").extract()).strip()
        item['max_annual_management_charge'] = ''.join(response.xpath("//div[@id='managementFeesDiv']//tr[2]/td/div[@id='managementFeesAnnualChargesDiv']//tr[2]/td[@class='value number']//text()").extract()).strip()
        item['ongoing_charge'] = ''.join(response.xpath("//div[@id='managementFeesDiv']//tr[2]/td/div[@id='managementFeesAnnualChargesDiv']//tr[3]/td[@class='value number']//text()").extract()).strip()
        item['minimum_investments_initial'] = ''.join(response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[2]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr[2]/td[@class='value number']//text()").extract()).strip()
        item['minimum_investments_additional'] = ''.join(response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[2]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr[3]/td[@class='value number']//text()").extract()).strip()
        item['minimum_investments_savings'] = ''.join(response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[2]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr[4]/td[@class='value number']//text()").extract()).strip()
        # item['minimum_investments'] = response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[2]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr/td[@class='label']//text()").extract()
        # item['minimum_investments_purchase_details'] = response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[2]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr/td[@class='value number']//text()").extract()
        # item['tax_free_savings_schemes'] = response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[3]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr//td[@class='label']//text()").extract()
        item['tax_free_savings_schemes_purchase_details'] = ''.join(response.xpath("//div[@id='managementPurchaseInformationDiv']//tr[3]/td/div[@id='managementPurchaseInformationMinInvestDiv']//tr//td[@class='value number']//text()").extract())
        yield item














