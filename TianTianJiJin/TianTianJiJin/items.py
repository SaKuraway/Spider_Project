# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JijinDataItem(scrapy.Item):
    # 定义字段

    # 基金概况页面：http://fund.eastmoney.com/f10/jbgk_{0}.html
    # Fund_code = scrapy.Field()   # 基金代码
    # Fund_name = scrapy.Field()   # 基金名称
    # fundFullname = scrapy.Field()   # 基金全称
    # fundPinyin = scrapy.Field()    # 基金拼音名称
    # fundType = scrapy.Field()       # 基金类型
    # riskLevel = scrapy.Field()       # 风险等级
    # issueDate = scrapy.Field()  # 发行时间
    # establishmentDate = scrapy.Field()  # 成立时间
    assetsScale = scrapy.Field()    # 资产管理规模
    shareScale = scrapy.Field()     # 份额规模
    fundAdministrator = scrapy.Field()  # 基金管理人
    fundCustodian = scrapy.Field()      # 基金托管人
    operationRate = scrapy.Field()      # 管理费率
    custodianRate = scrapy.Field()      # 托管费率
    #
    # #累计净值页面：http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page=1&per=10000
    # # valueDate = scrapy.Field()       # 净值日期
    # # unitValue = scrapy.Field()      # 单位净率
    # # totalValue = scrapy.Field()     # 累计净率
    # # dailyGrowthRate = scrapy.Field()    #每日增长率
    # # subscriptionStatus = scrapy.Field()    #申购状态
    # # redemptionStatus = scrapy.Field()    # 赎回状态
    # # dividendsDistribution = scrapy.Field()    # 分红送配
    # ACWorth = scrapy.Field()        # 净值日期,单位净率,累计净率,每日增长率,申购状态,赎回状态,分红送配
    #
    # # 基金排行页面：http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&sd=2016-11-10&ed=2017-11-10&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1&v=0.9361817037458058
    # nearly1weeksRate = scrapy.Field()   # 近一周增长率
    # nearly1monthsRate = scrapy.Field()  # 近一月增长率
    # nearly3monthsRate = scrapy.Field()  # 近三月增长率
    # nearly6monthsRate = scrapy.Field()  # 近六月增长率
    # nearly1yearsRate = scrapy.Field()   # 近一年增长率
    # nearly2yearsRate = scrapy.Field()   # 近二年增长率
    # nearly3yearsRate = scrapy.Field()   # 近三年增长率
    # thisYearRate = scrapy.Field()       # 今年增长率
    #
    # # JS页面：http://fund.eastmoney.com/pingzhongdata/{0}.js
    # SinceEstablishedRate = scrapy.Field()   # 自创建来的增长率
    # proceduresFee = scrapy.Field()          # 手续费
    # ACWorthTrend = scrapy.Field()           # 累计净值走势
    # currentFundManager = scrapy.Field()     # 当前基金经理人
    # assetAllocation = scrapy.Field()        # 资产配置占比
    # grandTotal = scrapy.Field()             # 累计收益率走势(本基金、沪深300、同类平均)

    # Platform = scrapy.Field()           # 平台
    # Fund_currency = scrapy.Field()      # 基金货币
    # Domicile = scrapy.Field()           # 基金注册地

    # 1.基金概况页面：http://fund.eastmoney.com/f10/jbgk_{0}.html
    Fund_Type = scrapy.Field()       # 基金类型
    Inception_Date = scrapy.Field()     # 成立时间
    Launch_Date = scrapy.Field()        # 发行时间
    Fund_name = scrapy.Field()          # 基金名称
    Min_Purchase = scrapy.Field()       # 基金申购门槛
    Max_Initial_Charge = scrapy.Field() # 最高申购费率
    Management_Fee = scrapy.Field()     # 管理费率
    Max_Redemption_charge = scrapy.Field()# 最高赎回费率
    Benchmark = scrapy.Field()           # 基金基准
    Risk_Level = scrapy.Field()       # 风险等级

    # 2.基金排行页面：http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=all&rs=&gs=0&sc=zzf&st=desc&sd=2016-11-10&ed=2017-11-10&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1&v=0.9361817037458058
    Fund_code = scrapy.Field()           # ISIN/基金代码
    Spider_Date = scrapy.Field()         # 爬取日期
    Unit_Value = scrapy.Field()          # 单位净率
    Total_Value = scrapy.Field()         # 累计净率
    Daily_Growth_Rate = scrapy.Field()    # 每日增长率
    Nearly_1weeks_Rate = scrapy.Field()   # 近一周增长率
    Nearly_1months_Rate = scrapy.Field()  # 近一月增长率
    Nearly_3months_Rate = scrapy.Field()  # 近三月增长率
    Nearly_6months_Rate = scrapy.Field()  # 近六月增长率
    Nearly_1years_Rate = scrapy.Field()   # 近一年增长率
    Nearly_2years_Rate = scrapy.Field()   # 近二年增长率
    Nearly_3years_Rate = scrapy.Field()   # 近三年增长率
    This_Year_Rate = scrapy.Field()       # 今年增长率
    Since_Established_Rate = scrapy.Field()   # 自创建来的增长率
    Procedures_Fee = scrapy.Field()       # 手续费

    # 3.基金规模：http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=gmbd&mode=0&code=000457
    # Fund_size = scrapy.Field()           # 基金管理规模
    Fund_size_change_Date = scrapy.Field()# 日期
    Period_Purchase = scrapy.Field()     # 期间申购（亿份）
    Period_Redeem = scrapy.Field()       # 期间赎回（亿份）
    Ending_shares = scrapy.Field()      # 期末总份额（亿份）
    Ending_net_asset = scrapy.Field()   # 期末净资产（亿份）
    Net_asset_change = scrapy.Field()    # 净资产变动率

    # 4.基金持有人结构（机构、个人、内部）:http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cyrjg&code=000457
    Fund_holder_Date = scrapy.Field()    # 公告日期
    Institution = scrapy.Field()         # 机构持有比例
    Individual = scrapy.Field()          # 个人持有比例
    Internal = scrapy.Field()            # 内部持有比例
    Total_shares = scrapy.Field()        # 总份额（亿份）

    #5.基金持仓明细:http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=jjcc&code=000457&topline=10&year=2016&month=1,2,3,4,5,6,7,8,9,10,11,12
    Fund_holding_season = scrapy.Field()   # 年份季节
    Fund_holding_id = scrapy.Field()     # 序号
    Stock_code = scrapy.Field()          # 股票代码
    Stock_name = scrapy.Field()          # 股票名称
    Single_stock_percent = scrapy.Field()# 占净值比例
    Stock_holding_quantity = scrapy.Field()# 持股数（万股）
    Stock_holding_value = scrapy.Field()   # 持仓市值（万元）

    # 6.重大变动:http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zdbd&code={0}&zdbd=1&year={1}
    Transaction_details_season = scrapy.Field()   # 年份季节
    Transaction_details_id = scrapy.Field()   # 序号
    Buying_stock_code = scrapy.Field()             # 股票代码
    Buying_stock_name = scrapy.Field()             # 股票名称
    Accumulated_buy_value = scrapy.Field()  # 本期累计买入金额（万元）
    Accumulated_buy_percent_of_NAV = scrapy.Field()# 占期初基金资产净值比例

    # 7.行业配置:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hypz&code={0}&year={1}
    Setors_season = scrapy.Field()              # 年份季度
    Setors_id = scrapy.Field()                  # 序号
    Setors = scrapy.Field()                     # 行业类别
    Setors_change = scrapy.Field()              # 行业变动详情
    Setors_percent = scrapy.Field()             # 占净值比例
    Setors_value = scrapy.Field()               # 市值（万元）

    # 8.行业市盈率：
    #           ①制造业：http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=C&Y=2017&Q=3&lastestYear=1
    #           ②电力、热力、燃气及水生产和供应业：http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=D&Y=2017&Q=3&lastestYear=1
    #           ③信息业：http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=I&Y=2017&Q=3&lastestYear=1
    #           ④批发和零售业:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=F&Y=2017&Q=3&lastestYear=1
    #           ⑤文化、体育和娱乐业:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=R&Y=2017&Q=3&lastestYear=1
    #           ⑥卫生和社会工作行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=Q&Y=2017&Q=3&lastestYear=1
    #           ⑦租赁和商务服务业行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=L&Y=2017&Q=3&lastestYear=1
    #           ⑧水利、环境和公共设施管理业行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=N&Y=2017&Q=3&lastestYear=1
    #           ⑨科学研究和技术服务业行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=M&Y=2017&Q=3&lastestYear=1
    #           ⑩采矿业行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=B&Y=2017&Q=3&lastestYear=1
    #           ⑪交通运输、仓储和邮政业行业市盈率:http://fund.eastmoney.com/f10/F10DataApi.aspx?type=hysyl&indcode=G&Y=2017&Q=3&lastestYear=1
    Setoes_PE = scrapy.Field()                  # 行业市盈率

    # 9.行业配置比较 Setors_comparation:
    Comparation_date = scrapy.Field()           # 证监会行业代码
    CSRC_setors_code = scrapy.Field()           # 证监会行业代码
    Setors_name = scrapy.Field()                # 行业名称
    Fund_setor_weight = scrapy.Field()          # 基金行业配置
    Similarfund_setor_weight = scrapy.Field()   # 同类平均
    Fund_setor_different = scrapy.Field()       # 比同类配置

    # 10.投资风格 StyleBox：http://fund.eastmoney.com/f10/tsdata_{0}.html
    # （大 中 小、价值 均衡 成长）
    # Large = scrapy.Field()
    # Middle = scrapy.Field()
    # Small = scrapy.Field()
    # Value = scrapy.Field()
    # Blend = scrapy.Field()
    # Growth = scrapy.Field()
    Style_season = scrapy.Field()
    Style_box = scrapy.Field()

    # 11.跟踪指数指标 Tracking:http://fund.eastmoney.com/f10/tsdata_{0}.html
    Tracking_index = scrapy.Field()  # 跟踪指数
    Tracking_error = scrapy.Field()  # 跟踪误差
    Similar_average_tracking_error = scrapy.Field()  # 同类平均跟踪误差

    # 12.基金经理变动表 Fund_manager_change：http://fund.eastmoney.com/f10/jjjl_{0}.html
    Start_date = scrapy.Field()                 # 起始日期
    Ending_date = scrapy.Field()                # 截止期
    Fund_managers = scrapy.Field()              # 任职基金经理
    Appointment_time = scrapy.Field()           # 任职时间
    Appointment_return = scrapy.Field()         # 任职回报

    # 13.基金经理人历任基金表
    Current_fund_manager = scrapy.Field()       # 当前基金经理
    Held_fund_code = scrapy.Field()# 基金名称
    Held_fund_name = scrapy.Field()# 基金名称
    Held_fund_type = scrapy.Field()# 基金类型
    Held_fund_start_time = scrapy.Field()# 起始日期
    Held_fund_end_time = scrapy.Field()# 截止日期
    Held_fund_appointment_time = scrapy.Field()# 任职天数
    Held_fund_repayment = scrapy.Field()# 任职回报
    Held_fund_similar_average = scrapy.Field()# 同类平均
    Held_fund_similar_ranking = scrapy.Field()# 同类排名

    # 12.财务报表 Main_financial_index ：http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code=502000&showtype=1&year=
    Financial_index_date = scrapy.Field()   # 日期
    # Period_data_and_index = scrapy.Field()  # 期间数据和指标
    Period_realized_revenue = scrapy.Field()# 本期已实现收益
    Period_profits = scrapy.Field()# 本期利润
    Period_profits_of_weighted_average_shares = scrapy.Field()  # 加权平均基金份额本期利润
    Period_profits_rate = scrapy.Field()  # 利润率
    Period_growth_of_NAV = scrapy.Field()  # 本期基金份额净值增长率

    # Ending_data_and_index = scrapy.Field()  # 期末数据和指标
    Ending_distributable_profits = scrapy.Field()  # 期末可供分配利润
    Ending_distributable_profits_of_shares = scrapy.Field()  # 期末可供分配基金份额利润
    Ending_net_asset_value_of_fund = scrapy.Field()  # 期末基金资产净值
    Ending_NAV = scrapy.Field()  # 期末基金份额净值

    Growth_of_ANAV = scrapy.Field()  # 基金份额累计净值增长率

    # 14.资产负债表 Assets_balance_sheet：http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=zcfzb&code={0}&showtype=1&year=
    # Assets = scrapy.Field()    # 资产
    Assets_date = scrapy.Field()    # 资产
    Bank_deposit = scrapy.Field()    # 银行存款
    Settlement_reserve = scrapy.Field()    # 结算备付金
    Guarantee_deposit_paid = scrapy.Field()    # 存出保证金
    Trading_financial_asset = scrapy.Field()    # 交易性金融资产
    Stock_investment = scrapy.Field()    # 其中：股票投资
    Fund_investment = scrapy.Field()    # 其中：基金投资
    Bond_investment = scrapy.Field()    # 其中：债券投资
    Asset_backed_securities_investment = scrapy.Field()    # 其中：资产支持证券投资
    Derivative_financial_assets = scrapy.Field()    # 衍生金融资产
    Purchase_resale_financial_assets = scrapy.Field()    # 买入返售金融资产
    Securities_settlement_receivable = scrapy.Field()    # 应收证券清算款
    Interest_receivable = scrapy.Field()    # 应收利息
    Dividends_receivable = scrapy.Field()    # 应收股利
    Purchase_receivable = scrapy.Field()    # 应收申购款
    Deferred_income_tax_assets = scrapy.Field()    # 递延所得税资产
    Other_assets = scrapy.Field()    # 其他资产
    Total_assets = scrapy.Field()    # 资产总计

    # Debt = scrapy.Field()    # 负债：
    Short_term_loan = scrapy.Field()    # 短期借款
    Trading_financial_liability = scrapy.Field()    # 交易性金融负债
    Derivative_financial_liability = scrapy.Field()    # 衍生金融负债
    Sell_repurchase_financial_assets = scrapy.Field()    # 卖出回购金融资产款
    Securities_settlement_payable = scrapy.Field()    # 应付证券清算款
    Redeem_payables = scrapy.Field()    # 应付赎回款
    Managerial_compensation_payable = scrapy.Field()    # 应付管理人报酬
    Trustee_fee_payable = scrapy.Field()    # 应付托管费
    Sales_service_fee_payable = scrapy.Field()    # 应付销售服务费
    Taxation_payable = scrapy.Field()    # 应付税费
    Interest_payable = scrapy.Field()    # 应付利息
    Profits_receivable = scrapy.Field()    # 应收利润
    Deferred_income_tax_liability = scrapy.Field()    # 递延所得税负债
    Other_liabilities = scrapy.Field()    # 其他负债
    Total_liabilities = scrapy.Field()    # 负债合计

    # Owner_equity = scrapy.Field()    # 所有者权益：
    Paid_in_fund = scrapy.Field()    # 实收基金
    Total_owner_equity = scrapy.Field()    # 所有者权益合计
    Total_debt_and_owner_equity = scrapy.Field()    # 负债和所有者权益合计

    # 15.利润表 Income_statements：http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=lrfpb&code=000457&showtype=1&year=
    Income = scrapy.Field()  # 收入
    Income_date = scrapy.Field()  # 收入
    Interest_income = scrapy.Field()  # 利息收入
    Interest_income_of_deposit = scrapy.Field()  # 其中：存款利息收入
    Interest_income_of_bond = scrapy.Field()  # 其中：债券利息收入
    Interest_income_of_asset_backed_securities = scrapy.Field()  # 其中：资产支持证券利息收入
    Investment_income = scrapy.Field()  # 投资收益
    Income_of_stock_investment = scrapy.Field()  # 其中：股票投资收益
    Income_of_fund_investment = scrapy.Field()  # 其中：基金投资收益
    Income_of_bond_investment = scrapy.Field()  # 其中：债券投资收益
    Income_of_asset_backed_securities_investment = scrapy.Field()  # 其中：资产支持证券投资收益
    Income_of_derivatives = scrapy.Field()  # 其中：衍生工具收益
    Dividend_income = scrapy.Field()  # 其中：股利收益
    Income_of_fair_value_change = scrapy.Field()  # 公允价值变动收益
    Exchange_earnings = scrapy.Field()  # 汇兑收益
    Other_Income = scrapy.Field()  # 其他收入

    Expense = scrapy.Field()  # 费用
    Managerial_compensation = scrapy.Field()  # 管理人报酬
    Trustee_fee = scrapy.Field()  # 托管费
    Sales_service_fee = scrapy.Field()  # 销售服务费
    Transaction_cost = scrapy.Field()  # 交易费用
    Interest_expense = scrapy.Field()  # 利息支出
    Sell_repurchase_financial_assets_expense = scrapy.Field()  # 其中：卖出回购金融资产支出
    Other_expenses = scrapy.Field()  # 其他费用

    Profit_before_tax = scrapy.Field()  # 利润总额
    Income_tax_expense = scrapy.Field()  # 减：所得税费用

    Net_profit = scrapy.Field()  # 净利润

    # 16.收入分析表 Income_analysis：http://fund.eastmoney.com/f10/srfx_000457.html
    Income_analysis_Date = scrapy.Field()  # 报告期
    Total_income = scrapy.Field()  # 收入合计
    Stock_income = scrapy.Field()  # 股票收入
    Stock_percent = scrapy.Field()  # 占比
    Bond_income = scrapy.Field()  # 债券收入
    Bond_percent = scrapy.Field()  # 占比
    Dividends_income = scrapy.Field()  # 股利收入
    Dividends_percent = scrapy.Field()  # 占比

    #17.费用分析表 Expenses_analysis：http://fund.eastmoney.com/f10/fyfx_{0}.html
    Expenses_analysis_date = scrapy.Field()  # 报告期
    Total_expenses = scrapy.Field()  # 费用合计
    Expenses_analysis_managerial_compensation = scrapy.Field()  # 管理人报酬
    Managerial_compensation_percent = scrapy.Field()  # 占比
    Expenses_analysis_trustee_fee = scrapy.Field()  # 托管费
    Trustee_fee_percent = scrapy.Field()  # 托管费占比
    Expenses_analysis_transaction_cost = scrapy.Field()  # 交易费
    Transaction_cost_percent = scrapy.Field()  # 交易费占比
    Expenses_analysis_sales_service_fee = scrapy.Field()  # 销售服务费
    Sales_service_fee_percent = scrapy.Field()  # 销售服务费占比

    #18.基金资产分类配置 Fund_allocations: http://fund.eastmoney.com/f10/zcpz_000457.html
    Fund_allocations_Date = scrapy.Field()  # 报告期
    Fund_allocations_Stock_percent = scrapy.Field()  # 股票占净比
    Fund_allocations_Bond_percent = scrapy.Field()  # 债券占净比
    Cash_percent = scrapy.Field()  # 现金占净比
    Net_asset = scrapy.Field()  # 净资产（亿元）

    #19.历史净值明细表 History_NAV：http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=000457&page=1&per=10000&sdate=&edate=
    History_NAV_Date = scrapy.Field()  # 净值日期
    NAV = scrapy.Field()  # 单位净值
    ANAV = scrapy.Field()  # 累计净值
    Day_change = scrapy.Field()  # 日增长率
    Purchase_status = scrapy.Field()  # 申购状态
    Redeem_status = scrapy.Field()  # 赎回状态
    Dividends_distribution = scrapy.Field()  # 分红送配

    #20.收益率走势表 ACWorth ：http://fund.eastmoney.com/api/PingZhongApi.ashx?m=0&fundcode={0}&indexcode=000300&type=se&callback=
    ACWorth_date = scrapy.Field()     #本基金
    this_fund_rate = scrapy.Field()     #本基金
    similar_fund_rate = scrapy.Field()  #同类
    hs300_rate = scrapy.Field()         #沪深300
