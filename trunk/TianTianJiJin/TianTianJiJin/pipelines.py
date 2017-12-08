# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import pymysql
import time

# 存到txt文本中
class TiantianjijinPipeline(object):
    def __init__(self):
        self.keyword = 'ALL_TEST'
        self.file = open('Data/' + self.keyword + '.txt', 'a', encoding='utf-8')
        self.count = 1
        print('开始写入:')

    def process_item(self, item, spider):
        self.file.write(str(self.count) + '.\n' + str(item) + ',\r\n')
        self.count += 1
        return item

    def close_spider(self, spider):
        self.file.close()
        print('爬取完毕！共%s个基金。' % self.count)

# 存入MongoDB中
class TiantianjijinMongodbPipeline(object):
    def open_spider(self, spider):
        self.mongo_client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.db_name = self.mongo_client["TianTianJiJin"]
        self.sheet_name = self.db_name['TianTianJiJin_Alldata']

    def process_item(self, item, spider):
        self.sheet_name.insert(dict(item))
        return item

    def close_spider(self, spider):
        self.mongo_client.close()

# 存入MySQL中
class TiantianjijinMysqlPipeline(object):
    def open_spider(self, spider):
        # 指定mysql数据库
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105', database='data_finance',charset='utf8')

    def process_item(self, item, spider):
        # FIFO模式为 blpop，LIFO模式为 brpop，获取redis的键值
        # source, data = rediscli.blpop(["aqi:items"])
        # item = json.loads(data)
        try:
            # 使用cursor()方法获取操作游标
            cur = self.mysql_client.cursor()
            # 使用execute方法执行SQL INSERT语句
            # cur.execute("insert into aqi_data(city, date, aqi, level, pm2_5, pm10, so2, co, no2, o3, rank, spider, crawled) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [item['city'], item['date'], item['aqi'], item['level'], item['pm2_5'], item['pm10'], item['so2'], item['co'], item['no2'], item['o3'], item['rank'], item['spider'], item['crawled']])
            # count = cur.execute("select * from 财务报表 where Fund_code=002196 and Financial_index_date='2017-06-30';")

            if not cur.execute("select * from 基金概况表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Spider_Date=" + "'" + item['Spider_Date'] + "'" + ";"):
                self.try_except(cur.execute("delete from 基金概况表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Spider_Date=" + "'" + item['Spider_Date'] + "'" + ";"))
                self.try_except(cur.execute("insert into 基金概况表(Fund_name,Fund_code,Inception_Date,Launch_Date,Min_Purchase,Max_Initial_Charge,Management_Fee,Max_Redemption_charge,Benchmark,Spider_Date,Unit_Value,Total_Value,Daily_Growth_Rate,Nearly_1weeks_Rate,Nearly_1months_Rate,Nearly_3months_Rate,Nearly_6months_Rate,Nearly_1years_Rate,Nearly_2years_Rate,Nearly_3years_Rate,This_Year_Rate,Since_Established_Rate,Procedures_Fee) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_name'],item['Fund_code'],item['Inception_Date'],item['Launch_Date'],item['Min_Purchase'],item['Max_Initial_Charge'],item['Management_Fee'],item['Max_Redemption_charge'],item['Benchmark'],item['Spider_Date'],item['Unit_Value'],item['Total_Value'],item['Daily_Growth_Rate'],item['Nearly_1weeks_Rate'],item['Nearly_1months_Rate'],item['Nearly_3months_Rate'],item['Nearly_6months_Rate'],item['Nearly_1years_Rate'],item['Nearly_2years_Rate'],item['Nearly_3years_Rate'],item['This_Year_Rate'],item['Since_Established_Rate'],item['Procedures_Fee'])))
            for Fund_size_change_Date,Period_Purchase,Period_Redeem,Ending_shares,Ending_net_asset,Net_asset_change in zip(item['Fund_size_change_Date'],item['Period_Purchase'],item['Period_Redeem'],item['Ending_shares'],item['Ending_net_asset'],item['Net_asset_change']):
                if not cur.execute("select * from 基金规模变动表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Fund_size_change_Date=" + "'" +Fund_size_change_Date + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金规模变动表(Fund_code,Fund_size_change_Date,Period_Purchase,Period_Redeem,Ending_shares,Ending_net_asset,Net_asset_change) VALUES(%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Fund_size_change_Date,Period_Purchase,Period_Redeem,Ending_shares,Ending_net_asset,Net_asset_change)))
                # else:
                #     print('数据已存在！跳过重复！')
                    # with open('Data/' + '爬虫日志' + '.log', 'a', encoding='utf-8') as f:
                    #     f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + '数据已存在！跳过重复！' + '\r\n')
                    # f.close()
            for Fund_holder_Date,Institution,Individual,Internal,Total_shares in zip(item['Fund_holder_Date'],item['Institution'],item['Individual'],item['Internal'],item['Total_shares']):
                if not cur.execute("select * from 基金持有人结构表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Fund_holder_Date=" + "'" + Fund_holder_Date + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金持有人结构表(Fund_code,Fund_holder_Date,Institution,Individual,Internal,Total_shares) VALUES(%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Fund_holder_Date,Institution,Individual,Internal,Total_shares)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Fund_holding_season,Fund_holding_id,Stock_code,Stock_name,Single_stock_percent,Stock_holding_quantity,Stock_holding_value in zip(item['Fund_holding_season'],item['Fund_holding_id'],item['Stock_code'],item['Stock_name'],item['Single_stock_percent'],item['Stock_holding_quantity'],item['Stock_holding_value']):
                if not cur.execute("select * from 基金持仓明细表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Fund_holding_season=" + "'" + Fund_holding_season + "'"+ " and Fund_holding_id=" + "'" + Fund_holding_id + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金持仓明细表(Fund_code,Fund_holding_season,Fund_holding_id,Stock_code,Stock_name,Single_stock_percent,Stock_holding_quantity,Stock_holding_value) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Fund_holding_season,Fund_holding_id,Stock_code,Stock_name,Single_stock_percent,Stock_holding_quantity,Stock_holding_value)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Transaction_details_season,Transaction_details_id,Buying_stock_code,Buying_stock_name,Accumulated_buy_value,Accumulated_buy_percent_of_NAV in zip(item['Transaction_details_season'],item['Transaction_details_id'],item['Buying_stock_code'],item['Buying_stock_name'],item['Accumulated_buy_value'],item['Accumulated_buy_percent_of_NAV']):
                if not cur.execute("select * from 重大变动表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Transaction_details_season=" + "'" + Transaction_details_season + "'"+ " and Transaction_details_id=" + "'" + Transaction_details_id + "'" + ";"):
                    self.try_except(cur.execute("insert into 重大变动表(Fund_code,Transaction_details_season,Transaction_details_id,Buying_stock_code,Buying_stock_name,Accumulated_buy_value,Accumulated_buy_percent_of_NAV) VALUES(%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Transaction_details_season,Transaction_details_id,Buying_stock_code,Buying_stock_name,Accumulated_buy_value,Accumulated_buy_percent_of_NAV)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Setors_season,Setors_id,Setors,Setors_percent,Setors_value in zip(item['Setors_season'],item['Setors_id'],item['Setors'],item['Setors_percent'],item['Setors_value']):
                if not cur.execute("select * from 行业配置表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Setors_season=" + "'" + Setors_season + "'"+ " and Setors_id=" + "'" + Setors_id + "'" + ";"):
                    self.try_except(cur.execute("insert into 行业配置表(Fund_code,Setors_season,Setors_id,Setors,Setors_percent,Setors_value) VALUES(%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Setors_season,Setors_id,Setors,Setors_percent,Setors_value)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Comparation_date,CSRC_setors_code,Setors_name,Fund_setor_weight,Similarfund_setor_weight,Fund_setor_different in zip(item['Comparation_date'],item['CSRC_setors_code'],item['Setors_name'],item['Fund_setor_weight'],item['Similarfund_setor_weight'],item['Fund_setor_different']):
                if not cur.execute("select * from 行业配置比较表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Comparation_date=" + "'" + Comparation_date + "'"+ " and CSRC_setors_code=" + "'" + CSRC_setors_code + "'" + ";"):
                    self.try_except(cur.execute("insert into 行业配置比较表(Fund_code,Comparation_date,CSRC_setors_code,Setors_name,Fund_setor_weight,Similarfund_setor_weight,Fund_setor_different) VALUES(%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Comparation_date,CSRC_setors_code,Setors_name,Fund_setor_weight,Similarfund_setor_weight,Fund_setor_different)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Style_season,Style_box in zip(item['Style_season'],item['Style_box']):
                if not cur.execute("select * from 投资风格表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Style_season=" + "'" + Style_season + "'"+ " and Style_box=" + "'" + Style_box + "'" + ";"):
                    self.try_except(cur.execute("insert into 投资风格表(Fund_code,Style_season,Style_box) VALUES(%s,%s,%s)",(item['Fund_code'],Style_season,Style_box)))
                # else:
                #     print('数据已存在！跳过重复！')
            if not cur.execute("select * from 跟踪指数指标表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Tracking_index=" + "'" + item['Tracking_index'] + "'"+ " and Tracking_error=" + "'" + item['Tracking_error'] + "'" + ";"):
                self.try_except(cur.execute("insert into 跟踪指数指标表(Fund_code,Tracking_index,Tracking_error,Similar_average_tracking_error) VALUES(%s,%s,%s,%s)",(item['Fund_code'],item['Tracking_index'],item['Tracking_error'],item['Similar_average_tracking_error'])))
            # else:
            #     print('数据已存在！跳过重复！')
            for Start_date,Ending_date,Fund_managers,Appointment_time,Appointment_return in zip(item['Start_date'],item['Ending_date'],item['Fund_managers'],item['Appointment_time'],item['Appointment_return']):
                if not cur.execute("select * from 基金经理变动表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Fund_managers=" + "'" + Fund_managers + "'"+ " and Start_date=" + "'" + Start_date + "'"+ " and Ending_date=" + "'" + Ending_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金经理变动表(Fund_code,Start_date,Ending_date,Fund_managers,Appointment_time,Appointment_return) VALUES(%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Start_date,Ending_date,Fund_managers,Appointment_time,Appointment_return)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Held_fund_code,Held_fund_name,Held_fund_type,Held_fund_start_time,Held_fund_end_time,Held_fund_appointment_time,Held_fund_repayment,Held_fund_similar_average,Held_fund_similar_ranking in zip(item['Held_fund_code'],item['Held_fund_name'],item['Held_fund_type'],item['Held_fund_start_time'],item['Held_fund_end_time'],item['Held_fund_appointment_time'],item['Held_fund_repayment'],item['Held_fund_similar_average'],item['Held_fund_similar_ranking']):
                if not cur.execute("select * from 基金经理人历任基金表 where Current_fund_manager=" + "'" + item['Current_fund_manager'] + "'" + " and Held_fund_code=" + "'" + Held_fund_code + "'"+ " and Held_fund_start_time=" + "'" + Held_fund_start_time + "'"+ " and Held_fund_repayment=" + "'" + Held_fund_repayment + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金经理人历任基金表(Current_fund_manager,Held_fund_code,Held_fund_name,Held_fund_type,Held_fund_start_time,Held_fund_end_time,Held_fund_appointment_time,Held_fund_repayment,Held_fund_similar_average,Held_fund_similar_ranking) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Current_fund_manager'],Held_fund_code,Held_fund_name,Held_fund_type,Held_fund_start_time,Held_fund_end_time,Held_fund_appointment_time,Held_fund_repayment,Held_fund_similar_average,Held_fund_similar_ranking)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Financial_index_date,Period_realized_revenue,Period_profits,Period_profits_of_weighted_average_shares,Period_profits_rate,Period_growth_of_NAV,Ending_distributable_profits,Ending_distributable_profits_of_shares,Ending_net_asset_value_of_fund,Ending_NAV,Growth_of_ANAV in zip(item['Financial_index_date'],item['Period_realized_revenue'],item['Period_profits'],item['Period_profits_of_weighted_average_shares'],item['Period_profits_rate'],item['Period_growth_of_NAV'],item['Ending_distributable_profits'],item['Ending_distributable_profits_of_shares'],item['Ending_net_asset_value_of_fund'],item['Ending_NAV'],item['Growth_of_ANAV']):
                if not cur.execute("select * from 财务报表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Financial_index_date=" + "'" + Financial_index_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 财务报表(Fund_code,Financial_index_date,Period_realized_revenue,Period_profits,Period_profits_of_weighted_average_shares,Period_profits_rate,Period_growth_of_NAV,Ending_distributable_profits,Ending_distributable_profits_of_shares,Ending_net_asset_value_of_fund,Ending_NAV,Growth_of_ANAV) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Financial_index_date,Period_realized_revenue,Period_profits,Period_profits_of_weighted_average_shares,Period_profits_rate,Period_growth_of_NAV,Ending_distributable_profits,Ending_distributable_profits_of_shares,Ending_net_asset_value_of_fund,Ending_NAV,Growth_of_ANAV)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Assets_date,Bank_deposit,Settlement_reserve,Guarantee_deposit_paid,Trading_financial_asset,Stock_investment,Fund_investment,Bond_investment,Asset_backed_securities_investment,Derivative_financial_assets,Purchase_resale_financial_assets,Securities_settlement_receivable,Interest_receivable,Dividends_receivable,Purchase_receivable,Deferred_income_tax_assets,Other_assets,Total_assets,Short_term_loan,Trading_financial_liability,Derivative_financial_liability,Sell_repurchase_financial_assets,Securities_settlement_payable,Redeem_payables,Managerial_compensation_payable,Trustee_fee_payable,Sales_service_fee_payable,Taxation_payable,Interest_payable,Profits_receivable,Deferred_income_tax_liability,Other_liabilities,Total_liabilities,Paid_in_fund,Total_owner_equity,Total_debt_and_owner_equity in zip(item['Assets_date'],item['Bank_deposit'],item['Settlement_reserve'],item['Guarantee_deposit_paid'],item['Trading_financial_asset'],item['Stock_investment'],item['Fund_investment'],item['Bond_investment'],item['Asset_backed_securities_investment'],item['Derivative_financial_assets'],item['Purchase_resale_financial_assets'],item['Securities_settlement_receivable'],item['Interest_receivable'],item['Dividends_receivable'],item['Purchase_receivable'],item['Deferred_income_tax_assets'],item['Other_assets'],item['Total_assets'],item['Short_term_loan'],item['Trading_financial_liability'],item['Derivative_financial_liability'],item['Sell_repurchase_financial_assets'],item['Securities_settlement_payable'],item['Redeem_payables'],item['Managerial_compensation_payable'],item['Trustee_fee_payable'],item['Sales_service_fee_payable'],item['Taxation_payable'],item['Interest_payable'],item['Profits_receivable'],item['Deferred_income_tax_liability'],item['Other_liabilities'],item['Total_liabilities'],item['Paid_in_fund'],item['Total_owner_equity'],item['Total_debt_and_owner_equity']):
                if not cur.execute("select * from 资产负债表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Assets_date=" + "'" + Assets_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 资产负债表(Fund_code,Assets_date,Bank_deposit,Settlement_reserve,Guarantee_deposit_paid,Trading_financial_asset,Stock_investment,Fund_investment,Bond_investment,Asset_backed_securities_investment,Derivative_financial_assets,Purchase_resale_financial_assets,Securities_settlement_receivable,Interest_receivable,Dividends_receivable,Purchase_receivable,Deferred_income_tax_assets,Other_assets,Total_assets,Short_term_loan,Trading_financial_liability,Derivative_financial_liability,Sell_repurchase_financial_assets,Securities_settlement_payable,Redeem_payables,Managerial_compensation_payable,Trustee_fee_payable,Sales_service_fee_payable,Taxation_payable,Interest_payable,Profits_receivable,Deferred_income_tax_liability,Other_liabilities,Total_liabilities,Paid_in_fund,Total_owner_equity,Total_debt_and_owner_equity) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Assets_date,Bank_deposit,Settlement_reserve,Guarantee_deposit_paid,Trading_financial_asset,Stock_investment,Fund_investment,Bond_investment,Asset_backed_securities_investment,Derivative_financial_assets,Purchase_resale_financial_assets,Securities_settlement_receivable,Interest_receivable,Dividends_receivable,Purchase_receivable,Deferred_income_tax_assets,Other_assets,Total_assets,Short_term_loan,Trading_financial_liability,Derivative_financial_liability,Sell_repurchase_financial_assets,Securities_settlement_payable,Redeem_payables,Managerial_compensation_payable,Trustee_fee_payable,Sales_service_fee_payable,Taxation_payable,Interest_payable,Profits_receivable,Deferred_income_tax_liability,Other_liabilities,Total_liabilities,Paid_in_fund,Total_owner_equity,Total_debt_and_owner_equity)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Income,Income_date,Interest_income,Interest_income_of_deposit,Interest_income_of_bond,Interest_income_of_asset_backed_securities,Investment_income,Income_of_stock_investment,Income_of_fund_investment,Income_of_bond_investment,Income_of_asset_backed_securities_investment,Income_of_derivatives,Dividend_income,Income_of_fair_value_change,Exchange_earnings,Other_Income,Expense,Managerial_compensation,Trustee_fee,Sales_service_fee,Transaction_cost,Interest_expense,Sell_repurchase_financial_assets_expense,Other_expenses,Profit_before_tax,Income_tax_expense,Net_profit in zip(item['Income'],item['Income_date'],item['Interest_income'],item['Interest_income_of_deposit'],item['Interest_income_of_bond'],item['Interest_income_of_asset_backed_securities'],item['Investment_income'],item['Income_of_stock_investment'],item['Income_of_fund_investment'],item['Income_of_bond_investment'],item['Income_of_asset_backed_securities_investment'],item['Income_of_derivatives'],item['Dividend_income'],item['Income_of_fair_value_change'],item['Exchange_earnings'],item['Other_Income'],item['Expense'],item['Managerial_compensation'],item['Trustee_fee'],item['Sales_service_fee'],item['Transaction_cost'],item['Interest_expense'],item['Sell_repurchase_financial_assets_expense'],item['Other_expenses'],item['Profit_before_tax'],item['Income_tax_expense'],item['Net_profit']):
                if not cur.execute("select * from 利润表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Income_date=" + "'" + Income_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 利润表(Fund_code,Income,Income_date,Interest_income,Interest_income_of_deposit,Interest_income_of_bond,Interest_income_of_asset_backed_securities,Investment_income,Income_of_stock_investment,Income_of_fund_investment,Income_of_bond_investment,Income_of_asset_backed_securities_investment,Income_of_derivatives,Dividend_income,Income_of_fair_value_change,Exchange_earnings,Other_Income,Expense,Managerial_compensation,Trustee_fee,Sales_service_fee,Transaction_cost,Interest_expense,Sell_repurchase_financial_assets_expense,Other_expenses,Profit_before_tax,Income_tax_expense,Net_profit) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Income,Income_date,Interest_income,Interest_income_of_deposit,Interest_income_of_bond,Interest_income_of_asset_backed_securities,Investment_income,Income_of_stock_investment,Income_of_fund_investment,Income_of_bond_investment,Income_of_asset_backed_securities_investment,Income_of_derivatives,Dividend_income,Income_of_fair_value_change,Exchange_earnings,Other_Income,Expense,Managerial_compensation,Trustee_fee,Sales_service_fee,Transaction_cost,Interest_expense,Sell_repurchase_financial_assets_expense,Other_expenses,Profit_before_tax,Income_tax_expense,Net_profit)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Income_analysis_Date,Total_income,Stock_income,Stock_percent,Bond_income,Bond_percent,Dividends_income,Dividends_percent in zip(item['Income_analysis_Date'],item['Total_income'],item['Stock_income'],item['Stock_percent'],item['Bond_income'],item['Bond_percent'],item['Dividends_income'],item['Dividends_percent']):
                if not cur.execute("select * from 收入分析表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Income_analysis_Date=" + "'" + Income_analysis_Date + "'" + ";"):
                    self.try_except(cur.execute("insert into 收入分析表(Fund_code,Income_analysis_Date,Total_income,Stock_income,Stock_percent,Bond_income,Bond_percent,Dividends_income,Dividends_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Income_analysis_Date,Total_income,Stock_income,Stock_percent,Bond_income,Bond_percent,Dividends_income,Dividends_percent)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Expenses_analysis_date,Total_expenses,Expenses_analysis_managerial_compensation,Managerial_compensation_percent,Expenses_analysis_trustee_fee,Trustee_fee_percent,Expenses_analysis_transaction_cost,Transaction_cost_percent,Expenses_analysis_sales_service_fee,Sales_service_fee_percent in zip(item['Expenses_analysis_date'],item['Total_expenses'],item['Expenses_analysis_managerial_compensation'],item['Managerial_compensation_percent'],item['Expenses_analysis_trustee_fee'],item['Trustee_fee_percent'],item['Expenses_analysis_transaction_cost'],item['Transaction_cost_percent'],item['Expenses_analysis_sales_service_fee'],item['Sales_service_fee_percent']):
                if not cur.execute("select * from 费用分析表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Expenses_analysis_date=" + "'" + Expenses_analysis_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 费用分析表(Fund_code,Expenses_analysis_date,Total_expenses,Expenses_analysis_managerial_compensation,Managerial_compensation_percent,Expenses_analysis_trustee_fee,Trustee_fee_percent,Expenses_analysis_transaction_cost,Transaction_cost_percent,Expenses_analysis_sales_service_fee,Sales_service_fee_percent) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Expenses_analysis_date,Total_expenses,Expenses_analysis_managerial_compensation,Managerial_compensation_percent,Expenses_analysis_trustee_fee,Trustee_fee_percent,Expenses_analysis_transaction_cost,Transaction_cost_percent,Expenses_analysis_sales_service_fee,Sales_service_fee_percent)))
                # else:
                #     print('数据已存在！跳过重复！')
            for Fund_allocations_Date,Fund_allocations_Stock_percent,Fund_allocations_Bond_percent,Cash_percent,Net_asset in zip(item['Fund_allocations_Date'],item['Fund_allocations_Stock_percent'],item['Fund_allocations_Bond_percent'],item['Cash_percent'],item['Net_asset']):
                if not cur.execute("select * from 基金资产分类配置表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and Fund_allocations_Date=" + "'" + Fund_allocations_Date + "'" + ";"):
                    self.try_except(cur.execute("insert into 基金资产分类配置表(Fund_code,Fund_allocations_Date,Fund_allocations_Stock_percent,Fund_allocations_Bond_percent,Cash_percent,Net_asset) VALUES(%s,%s,%s,%s,%s,%s)",(item['Fund_code'],Fund_allocations_Date,Fund_allocations_Stock_percent,Fund_allocations_Bond_percent,Cash_percent,Net_asset)))
                # else:
                #     print('数据已存在！跳过重复！')
            for History_NAV_Date,NAV,ANAV,Day_change,Purchase_status,Redeem_status,Dividends_distribution in zip(item['History_NAV_Date'],item['NAV'],item['ANAV'],item['Day_change'],item['Purchase_status'],item['Redeem_status'],item['Dividends_distribution']):
                if not cur.execute("select * from 历史净值明细表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and History_NAV_Date=" + "'" + History_NAV_Date + "'" + ";"):
                    self.try_except(cur.execute("insert into 历史净值明细表(Fund_code,History_NAV_Date,NAV,ANAV,Day_change,Purchase_status,Redeem_status,Dividends_distribution) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(item['Fund_code'],History_NAV_Date,NAV,ANAV,Day_change,Purchase_status,Redeem_status,Dividends_distribution)))
                # else:
                #     print('数据已存在！跳过重复！')
            for ACWorth_date,this_fund_rate,similar_fund_rate,hs300_rate in zip(item['ACWorth_date'],item['this_fund_rate'],item['similar_fund_rate'],item['hs300_rate']):
                if not cur.execute("select * from 收益率走势表 where Fund_code=" + "'" + item['Fund_code'] + "'" + " and ACWorth_date=" + "'" + ACWorth_date + "'" + ";"):
                    self.try_except(cur.execute("insert into 收益率走势表(Fund_code,ACWorth_date,this_fund_rate,similar_fund_rate,hs300_rate) VALUES(%s,%s,%s,%s,%s)",(item['Fund_code'],ACWorth_date,this_fund_rate,similar_fund_rate,hs300_rate)))
                # else:
                #     print('数据已存在！跳过重复！')

            # cur.execute("update 交通运输、仓储和邮政业行业市盈率 set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
            # cur.execute("delete from 制造业行业市盈率 where id > 245")
            # 提交sql事务
            self.mysql_client.commit()
            #关闭本次操作
            cur.close()

        except pymysql.Error as e:
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('正在写入错误信息：',e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'：'+str(e) + '\r\n')
            f.close()

    def close_spider(self, spider):
        self.mysql_client.close()
        print('爬取完毕！',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

    def try_except(self,sth):

        print('正在插入一条数据...')
        try:
            sth
        except pymysql.Error as e:
            with open('Data/' + '错误日志' + '.log', 'a', encoding='utf-8') as f:
                print('正在写入错误信息：',e)
                f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'：'+str(e) + '\r\n')
            f.close()
        self.mysql_client.commit()
        # return sth
