# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql, time


class BbaeSpiderPipeline(object):
    def process_item(self, item, spider):
        print(item)
        return item


# 存入MySQL中
class BbaeSpiderMysqlPipeline(object):
    def open_spider(self, spider):
        # 指定mysql数据库
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                            database='data_finance', charset='utf8')

    def process_item(self, item, spider):
        # FIFO模式为 blpop,LIFO模式为 brpop,获取redis的键值
        # source, data = rediscli.blpop(["aqi:items"])
        # item = json.loads(data)

        # 使用cursor()方法获取操作游标
        cur = self.mysql_client.cursor()
        try:
            if cur.execute("select * from bbae_funds where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_funds where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            # print(item['fund_name'],item['closing_price'],item['day_change'],item['morningstar_category'],item['volume'],item['exchange'],item['ISIN'],item['fund_size_mil'],item['category'],item['category_benchmark'],item['morningstar_research'],item['morningstar_sustainability'],item['sustainability_mandate'],item['percent_rank_in_category'],item['sustainability_score'],item['investment_objective'],item['trailing_returns'],item['YTD'],item['three_years_annualised'],item['five_years_annualised'],item['ten_years_annualised'],item['fund_benchmark'],item['morningstar_benchmark'],item['style_box_src'],item['stock_long'],item['stock_short'],item['stock_net_assets'],item['bond_long'],item['bond_short'],item['bond_net_assets'],item['property_long'],item['property_short'],item['property_net_assets'],item['cash_long'],item['cash_short'],item['cash_net_assets'],item['other_long'],item['other_short'],item['other_net_assets'],item['top_5_regions'],item['top_5_regions_percent'],item['top_5_sectors'],item['top_5_sectors_percent'],item['top_5_holdings'],item['top_5_holdings_sector'],item['top_5_holdings_percent'],item['name_of_company'],item['phone'],item['website'],item['address'],item['domicile'],item['legal_structure'],item['UCITS'],item['inception_date'],item['max_initial_charge'],item['max_exit_charge'],item['max_annual_management_charge'],item['ongoing_charge'],item['minimum_investments_initial'],item['minimum_investments_additional'],item['minimum_investments_savings'],item['tax_free_savings_schemes_purchase_details'])
            self.try_except(cur.execute(
                "insert into bbae_funds(fund_name,closing_price,day_change,morningstar_category,volume,exchange,ISIN,fund_size_mil,category,category_benchmark,morningstar_research,morningstar_sustainability,sustainability_mandate,percent_rank_in_category,sustainability_score,investment_objective,trailing_returns,YTD,three_years_annualised,five_years_annualised,ten_years_annualised,fund_benchmark,morningstar_benchmark,style_box,stock_long,stock_short,stock_net_assets,bond_long,bond_short,bond_net_assets,property_long,property_short,property_net_assets,cash_long,cash_short,cash_net_assets,other_long,other_short,other_net_assets,name_of_company,phone,website,address,domicile,legal_structure,UCITS,inception_date,max_initial_charge,max_exit_charge,max_annual_management_charge,ongoing_charge,minimum_investments_initial,minimum_investments_additional,minimum_investments_savings,tax_free_savings_schemes_purchase_details) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (item['fund_name'], item['closing_price'], item['day_change'], item['morningstar_category'],
                 item['volume'], item['exchange'], item['ISIN'], item['fund_size_mil'], item['category'],
                 item['category_benchmark'], item['morningstar_research'], item['morningstar_sustainability'],
                 item['sustainability_mandate'], item['percent_rank_in_category'], item['sustainability_score'],
                 item['investment_objective'], item['trailing_returns'], item['YTD'], item['three_years_annualised'],
                 item['five_years_annualised'], item['ten_years_annualised'], item['fund_benchmark'],
                 item['morningstar_benchmark'], item['style_box'], item['stock_long'], item['stock_short'],
                 item['stock_net_assets'], item['bond_long'], item['bond_short'], item['bond_net_assets'],
                 item['property_long'], item['property_short'], item['property_net_assets'], item['cash_long'],
                 item['cash_short'], item['cash_net_assets'], item['other_long'], item['other_short'],
                 item['other_net_assets'], item['name_of_company'], item['phone'], item['website'], item['address'],
                 item['domicile'], item['legal_structure'], item['UCITS'], item['inception_date'],
                 item['max_initial_charge'], item['max_exit_charge'], item['max_annual_management_charge'],
                 item['ongoing_charge'], item['minimum_investments_initial'], item['minimum_investments_additional'],
                 item['minimum_investments_savings'], item['tax_free_savings_schemes_purchase_details'])))

            if cur.execute("select * from bbae_top_10_holdings where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_top_10_holdings where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for top_10_holdings_name, top_10_holdings_sector,top_10_holdings_country,top_10_holdings_percent_of_assets in zip(item['top_10_holdings_name'],item['top_10_holdings_sector'],item['top_10_holdings_country'],item['top_10_holdings_percent_of_assets']):
                self.try_except(cur.execute("insert into bbae_top_10_holdings(ISIN,top_10_holdings_name,top_10_holdings_sector,top_10_holdings_country,top_10_holdings_percent_of_assets) VALUES(%s,%s,%s,%s,%s)",
                    (item['ISIN'],top_10_holdings_name,top_10_holdings_sector,top_10_holdings_country,top_10_holdings_percent_of_assets)))

            if cur.execute("select * from bbae_top_10_holdings_portfolio where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_top_10_holdings_portfolio where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for top_10_holdings, top_10_holdings_portfolio in zip(item['top_10_holdings'],item['top_10_holdings_portfolio']):
                self.try_except(cur.execute("insert into bbae_top_10_holdings_portfolio(ISIN,top_10_holdings,top_10_holdings_portfolio) VALUES(%s,%s,%s)",
                    (item['ISIN'], top_10_holdings, top_10_holdings_portfolio)))

            if cur.execute("select * from bbae_top_5_regions where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_top_5_regions where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for top_5_regions, top_5_regions_percent in zip(item['top_5_regions'], item['top_5_regions_percent']):
                self.try_except(cur.execute("insert into bbae_top_5_regions(ISIN,top_5_regions,top_5_regions_percent) VALUES(%s,%s,%s)",
                    (item['ISIN'], top_5_regions, top_5_regions_percent)))

            if cur.execute("select * from bbae_top_5_sectors where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_top_5_sectors where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for top_5_sectors, top_5_sectors_percent in zip(item['top_5_sectors'], item['top_5_sectors_percent']):
                self.try_except(cur.execute("insert into bbae_top_5_sectors(ISIN,top_5_sectors,top_5_sectors_percent) VALUES(%s,%s,%s)",
                    (item['ISIN'], top_5_sectors, top_5_sectors_percent)))

            if cur.execute("select * from bbae_top_5_holdings where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(cur.execute("delete from bbae_top_5_holdings where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for top_5_holdings, top_5_holdings_sector, top_5_holdings_percent in zip(item['top_5_holdings'],
                                                                                     item['top_5_holdings_sector'],
                                                                                     item['top_5_holdings_percent']):
                self.try_except(cur.execute(
                    "insert into bbae_top_5_holdings(ISIN,top_5_holdings,top_5_holdings_sector,top_5_holdings_percent) VALUES(%s,%s,%s,%s)",
                    (item['ISIN'], top_5_holdings, top_5_holdings_sector, top_5_holdings_percent)))

            if cur.execute("select * from bbae_valuations_and_growth_rates where ISIN=" + "'" + item[
                'ISIN'] + "'" + ";"):
                self.try_except(cur.execute(
                    "delete from bbae_valuations_and_growth_rates where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for valuations_and_growth_rates, equity_portfolio, relative_to_category in zip(
                    item['valuations_and_growth_rates'], item['equity_portfolio'], item['relative_to_category']):
                self.try_except(cur.execute(
                    "insert into bbae_valuations_and_growth_rates(ISIN,valuations_and_growth_rates,equity_portfolio,relative_to_category) VALUES(%s,%s,%s,%s)",
                    (item['ISIN'], valuations_and_growth_rates, equity_portfolio, relative_to_category)))

            if cur.execute("select * from bbae_market_capitalisation_equity where ISIN='" + item['ISIN'] + "';"):
                self.try_except(cur.execute(
                    "delete from bbae_market_capitalisation_equity where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            self.try_except(cur.execute(
                "insert into bbae_market_capitalisation_equity(ISIN,market_capitalisation_giant_equity,market_capitalisation_large_equity,market_capitalisation_medium_equity,market_capitalisation_small_equity,market_capitalisation_micro_equity) VALUES(%s,%s,%s,%s,%s,%s)",
                (item['ISIN'], item['market_capitalisation_giant_equity'], item['market_capitalisation_large_equity'],
                 item['market_capitalisation_medium_equity'], item['market_capitalisation_small_equity'],
                 item['market_capitalisation_micro_equity'])))

            if cur.execute("select * from bbae_world_regions where ISIN=" + "'" + item['ISIN'] + "'" + ";"):
                self.try_except(
                    cur.execute("delete from bbae_world_regions where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
            for world_regions, world_regions_equity, world_regions_relative_to_category in zip(item['world_regions'],
                                                                                               item[
                                                                                                   'world_regions_equity'],
                                                                                               item[
                                                                                                   'world_regions_relative_to_category']):
                self.try_except(cur.execute(
                    "insert into bbae_world_regions(ISIN,world_regions,world_regions_equity,world_regions_relative_to_category) VALUES(%s,%s,%s,%s)",
                    (item['ISIN'], world_regions, world_regions_equity, world_regions_relative_to_category)))
                # for size_name, size_value, size_rel_to_cat, market_capitalisation, market_capitalisation_equity, valuations_and_growth_rates, equity_portfolio, world_regions, world_regions_equity, world_regions_relative_to_category, relative_to_category, sector_weightings, sector_weightings_equity, sector_weightings_relative_to_category, top_10_holdings_summary, top_10_holdings_summary_portfolio, top_10_holdings_name, top_10_holdings_sector, top_10_holdings_country, top_10_holdings_percent_of_assets in zip(
                #         item['size_name'], item['size_value'], item['size_rel_to_cat'], item['market_capitalisation'],
                #         item['market_capitalisation_equity'], item['valuations_and_growth_rates'], item['equity_portfolio'],
                #         item['world_regions'], item['world_regions_equity'], item['world_regions_relative_to_category'],
                #         item['relative_to_category'], item['sector_weightings'], item['sector_weightings_equity'],
                #         item['sector_weightings_relative_to_category'], item['top_10_holdings_summary'],
                #         item['top_10_holdings_summary_portfolio'], item['top_10_holdings_name'], item['top_10_holdings_sector'],
                #         item['top_10_holdings_country'], item['top_10_holdings_percent_of_assets']):
                #     if cur.execute("select * from bbae_portfolio where ISIN=" + "'" + item[
                #         'ISIN'] + "'" + " and equity_portfolio=" + "'" + equity_portfolio + "'" + ";"):
                #         self.try_except(cur.execute("delete from bbae_portfolio where ISIN=" + "'" + item['ISIN'] + "'" + ";"))
                #     self.try_except(cur.execute(
                #         "insert into bbae_portfolio(ISIN,portfolio_title,size_name,size_value,size_rel_to_cat,market_capitalisation,market_capitalisation_equity,valuations_and_growth_rates,equity_portfolio,world_regions,world_regions_equity,world_regions_relative_to_category,relative_to_category,sector_weightings,sector_weightings_equity,sector_weightings_relative_to_category,top_10_holdings_summary,top_10_holdings_summary_portfolio,top_10_holdings_name,top_10_holdings_sector,top_10_holdings_country,top_10_holdings_percent_of_assets) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                #         (item['ISIN'], item['portfolio_title'], size_name, size_value, size_rel_to_cat, market_capitalisation,
                #          market_capitalisation_equity, valuations_and_growth_rates, equity_portfolio, world_regions,
                #          world_regions_equity, world_regions_relative_to_category, relative_to_category, sector_weightings,
                #          sector_weightings_equity, sector_weightings_relative_to_category, top_10_holdings_summary,
                #          top_10_holdings_summary_portfolio, top_10_holdings_name, top_10_holdings_sector,
                #          top_10_holdings_country, top_10_holdings_percent_of_assets)))

            for fund_manager, manager_start_date, biography in zip(item['fund_managers'], item['manager_start_dates'],
                                                                   item['biographies']):
                if not cur.execute("select * from bbae_fund_managers where ISIN=" + "'" + item[
                    'ISIN'] + "'" + " and fund_manager=" + "'" + fund_manager + "'" + " and manager_start_date=" + "'" + manager_start_date + "'" + ";"):
                    self.try_except(cur.execute(
                        "insert into bbae_fund_managers(ISIN, fund_advisor, fund_manager, manager_start_date, biography) VALUES(%s,%s,%s,%s,%s)",
                        (item['ISIN'], item['fund_advisor'], fund_manager, manager_start_date,
                         biography.replace('\n', ''))))
                    #
        except pymysql.Error as e:
            with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
                print('Writing Error info...', e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
            f.close()
        finally:
            # 提交sql事务
            self.mysql_client.commit()
            # 关闭本次操作
            cur.close()

    def close_spider(self, spider):
        tableNameList = ['bbae_funds', 'bbae_top_10_holdings_portfolio', 'bbae_top_5_regions', 'bbae_top_5_sectors',
                         'bbae_top_5_holdings', 'bbae_valuations_and_growth_rates', 'bbae_valuations_and_growth_rates',
                         'bbae_market_capitalisation_equity', 'bbae_world_regions', 'bbae_fund_managers']
        print('正在排序数据表中的id列....')
        cur = self.mysql_client.cursor()
        for tableName in tableNameList:
            cur.execute("ALTER TABLE " + tableName + " DROP id;")
            cur.execute("ALTER  TABLE " + tableName + " ADD id MEDIUMINT( 8 ) NOT NULL  FIRST;")
            cur.execute(
                "ALTER  TABLE " + tableName + " MODIFY COLUMN id MEDIUMINT( 8 ) NOT NULL  AUTO_INCREMENT,ADD PRIMARY  KEY(id);")
        cur.close()
        self.mysql_client.close()
        print('Spider finish！', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def try_except(self, sth):

        print('inserting data to mysql ...')
        try:
            sth
        except pymysql.Error as e:
            print(e)
            with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
                print('Writing Error info...', e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
            f.close()
