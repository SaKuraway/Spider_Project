from pymysql import *

if __name__=='__main__':
    # sname = str(input("请输入学生姓名："))
    sage = int(input("请输入学生年龄："))
    """
    # 1.基金概况表
    create table fund_base_info(
    id int unsigned primary key auto_increment not null,
    Platform varchar(20) default 'Plan',            # 平台
    Fund_currency varchar(20) default 'CNY',        # 基金货币
    Domicile varchar(20) default 'China',           # 基金注册地
    Fund_name varchar(50),                          # 基金名称
    Fund_code int,                                  # ISIN/基金代码
    Inception_Date date,                            # 成立时间
    Launch_Date date,                               # 发行时间
    Min_Purchase int,                               # 基金申购门槛
    Max_Initial_Charge float,                       # 最高申购费率
    Management_Fee float,                           # 管理费率
    Max_Redemption_charge float,                    # 最高赎回费率
    Benchmark varchar(70),                          # 基金基准
    Fund_size float                                 # 基金管理规模
    )
    
    
    # 2.规模变动表
    create table Fund_size_change(
    id int unsigned primary key auto_increment not null,
    Fund_code       
    Fund_size_change_Date date,                     # 日期
    Period_Purchase(0.1Billion) float,              # 期间申购（亿份）
    Period_Redeem(0.1Billion) float,                # 期间赎回（亿份）
    Eneding_shares(0.1Billion) float,               # 期末总份额（亿份）
    Eneding_net_asset(0.1Billion) float,            # 期末净资产（亿份）
    Net_asset_change(0.1Billion) float              # 净资产变动率
    )
    
    # 3.持有人结构表Fund_holder(
    Fund_code
    Date date,                                      # 公告日期
    Institution float,                              # 机构持有比例
    Individual float,                               # 个人持有比例
    Internal float,                                 # 内部持有比例
    Total_shares(0.1Billion) float                  # 总份额（亿份）
    )
    
    # 4.基金持仓(股票投资明细)表
    Fund_holding(
    id                                              # 序号
    Fund_code
    Stock_code int,                                 # 股票代码
    Stock_name varchar(20),                         # 股票名称
    single_stock_percent  float,                    # 占净值比例
    Stock_holding_quantity(10Thousand) float,       # 持股数（万股）
    Stock_holding_value(10Thousand) float           # 持仓市值（万元）
    )
    
    # 5.基金买卖股票明细表
    Transaction_details(
    id                                              # 序号
    Fund_code
    Buying_stock_code int,                                 # 股票代码
    Buying_stock_name varchar(10),                         # 股票名称
    //
    Accumulated_buy/sell_value float,               # 本期累计买入金额（万元）
    Accumulated_buy/sell_percent_of_NAV float       # 占期初基金资产净值比例
    ) 
    
    # 6.行业配置表 Setors
    id                                              # 序号
    Fund_code
    Setors varchar(30),                             # 行业类别
    Setors_change varchar，                         # 行业变动详情
    Setors_percent float,                           # 占净值比例
    Setors_value(10Thousand) float,                 # 市值（万元）
    Setoes_PE                                       # 行业市盈率
    
    # 7.行业配置比较表Setors_comparation
    Fund_code
    CSRC_setors_code varchar(2),                    # 证监会行业代码
    Setors_name varchar(30),                        # 行业名称
    Fund_setor_weight float,                        # 基金行业配置
    Similarfund_setor_weight float,                 # 同类平均
    Fund_setor_different                            # 比同类配置
    
    
    # 8.行业市盈率（只需要爬一次）
    Setors_PE                                       # 
    
    # 9.投资风格表StyleBox
    (Large,Middle,Small,Value,Blend,Growth)         # （大 中 小、价值 均衡 成长）
    
    # 10.基金经理变动表Fund_manager_change
    Fund_code
    Start_date date,                                # 起始日期
    Ending_date date,                               # 截止期
    Fund_manager varchar(10),                       # 基金经理
    Appointment_time                                # 任职时间
    Appointment_return                              # 任职回报
    
    # 11.基金经理人详情表 this_manager(
    Fund_code int,                                  # 基金代码
    Fund_name varchar(50),                          # 基金名称
    Fund_type varchar(10),                          # 基金类型
    Start_time date,                                # 起始日期
    End_time varchar(20),                           # 截止日期
    Appointment_time varchar(20),                   # 任职天数
    Repayment float,                                # 任职回报
    Similar_average float,                          # 同类平均
    Similar_ranking varchar(20)                     # 同类排名
    )
    
    # 12.财务报表 Main_financial_index      http://fund.eastmoney.com/f10/FundArchivesDatas.aspx?type=cwzb&code={0}&showtype=1
    Fund_code
    Financial_index_date                                            # 日期
    Period_data_and_index :                         # 期间数据和指标
    Period_realized_revenue float,                  # 本期已实现收益
    Period_profits float,                           # 本期利润
    Period_profits_of_weighted_average_shares,      # 加权平均基金份额本期利润
    Period_profits_rate                             # 本期加权平均净值利润率
    Period_growth_of_NAV                            # 本期基金份额净值增长率
    
    Ending_data_and_index:                          # 期末数据和指标
    Ending_distributable_profits,                   # 期末可供分配利润
    Ending_distributable_profits_of_shares,         # 期末可供分配基金份额利润
    Ending_net_asset_value_of_fund,                 # 期末基金资产净值
    Ending_NAV,                                     # 期末基金份额净值
    
    Accumulated_ending_index:                       
    Growth_of_ANAV                                  # 基金份额累计净值增长率
    
    
    # 13.资产负债表 Balance_sheet
    Fund_code
    Assets                                          # 资产
    Bank_deposit                                    # 银行存款
    Settlement_reserve                              # 结算备付金
    Guarantee_deposit_paid                          # 存出保证金
    Trading_financial_asset                         # 交易性金融资产
    Stock_investment                                # 其中：股票投资
    Fund_investment                                 # 其中：基金投资
    Bond_investment                                 # 其中：债券投资
    Asset_backed_securities_investment              # 其中：资产支持证券投资
    Derivative_financial_assets                     # 衍生金融资产
    Purchase_resale_financial_assets                # 买入返售金融资产
    Securities_settlement_receivable                # 应收证券清算款
    Interest_receivable                             # 应收利息
    Dividends_receivable                            # 应收股利
    Purchase_receivable                             # 应收申购款
    Deferred_income_tax_assets                      # 递延所得税资产    
    Other_assets                                    # 其他资产
    Total_assets                                    # 资产总计

    Debt                                            # 负债：
    Short_term_loan                                 # 短期借款    
    Trading_financial_liability                     # 交易性金融负债
    Derivative_financial_liability                  # 衍生金融负债
    Sell_repurchase_financial_assets                # 卖出回购金融资产款
    Securities_settlement_payable                   # 应付证券清算款
    Redeem_payables                                 # 应付赎回款
    Managerial_compensation_payable                 # 应付管理人报酬
    Trustee_fee_payable                             # 应付托管费
    Sales_service_fee_payable                       # 应付销售服务费
    Taxation_payable                                # 应付税费
    Interest_payable                                # 应付利息
    Profits_receivable                              # 应收利润
    Deferred_income_tax_liability                   # 递延所得税负债
    Other_liabilities                               # 其他负债
    Total_liabilities                               # 负债合计
    
    Owner_equity：                                  # 所有者权益：
    Paid_in_fund                                    # 实收基金
    Total_owner_equity                              # 所有者权益合计
    Total_debt_and_owner_equity                     # 负债和所有者权益合计
    
    #14.利润表 Income_statements           
    Fund_code
    Income：                                        # 收入     
    Interest_income                                 # 利息收入    
    Interest_income_of_deposit                      # 其中：存款利息收入    
    Interest_income_of_bond                         # 其中：债券利息收入
    Interest_income_of_asset_backed_securities      # 其中：资产支持证券利息收入
    Investment_income                               # 投资收益
    Income_of_stock_investment                      # 其中：股票投资收益
    Income_of_fund_investment                       # 其中：基金投资收益
    Income_of_bond_investment                       # 其中：债券投资收益
    Income_of_asset_backed_securities_investment    # 其中：资产支持证券投资收益
    Income_of_derivatives                           # 其中：衍生工具收益
    Dividend_income                                 # 其中：股利收益
    Income_of_fair_value_change                     # 公允价值变动收益
    Exchange_earnings                               # 汇兑收益
    Other_Income                                    # 其他收入
    
    Expense：                                       # 费用     
    Managerial_compensation                         # 管理人报酬    
    Trustee_fee                                     # 托管费    
    Sales_service_fee                               # 销售服务费    
    Transaction_cost                                # 交易费用
    Interest_expense                                # 利息支出
    Sell_repurchase_financial_assets_expense        # 其中：卖出回购金融资产支出
    Other_expenses                                  # 其他费用
    
    Profit_before_tax：                             # 利润总额 
    Income_tax_expense                              # 减：所得税费用
    
    Net_profit                                      # 净利润

    # 15.收入分析表Income_analysis:    
    Fund_code
    Date                                            # 报告期    
    Total_income                                    # 收入合计
    Stock_income                                    # 股票收入    
    Stock_percent                                   # 占比
    Bond_income                                     # 债券收入
    Bond_percent                                    # 占比
    Dividends_income                                # 股利收入    
    Dividends_percent                               # 占比    
    10Thousand                                      # 单位：万元    
    
    
    # 16.费用分析表 Expenses_analysis：
    Fund_code
    Date                                            # 报告期
    Total_expenses                                  # 费用合计
    Managerial_compensation                         # 管理人报酬                
    Managerial_compensation_percent                 # 占比
    Trustee_fee                                     # 托管费    
    Trustee_fee_percent                             # 托管费占比
    Transaction_cost                                # 交易费    
    Transaction_cost_percent                        # 交易费占比
    Sales_service_fee                               # 销售服务费
    Sales_service_fee_percent                       # 销售服务费占比
    10Thousand                                      # 单位：万元    


    # 17.指数基金指标表 Index_fund_index、
    Fund_code
    Tracking_index                                  # 跟踪指数    
    Tracking_error                                  # 跟踪误差
    Similar_average_tracking_error                  # 同类平均跟踪误差


    # 18.资产配置表
    Fund_code
    Date                                            # 报告期
    Stock_percent                                   # 股票占净比
    Bond_percent                                    # 债券占净比
    Cash_percent                                    # 现金占净比
    Net_asset(0.1Billion)                           # 净资产（亿元）
    
    # 19.历史净值明细表
    Fund_code
    History_AV_Date                                 # 净值日期
    NAV                                             # 单位净值
    ANAV                                            # 累计净值
    Day_change                                      # 收益率
    Purchase_status                                 # 申购状态
    Redeem_status                                   # 赎回状态
    
    # 20.收益率表（本基金、同类、沪深300）
    this_fund_rate = scrapy.Field()                 #本基金
    similar_fund_rate = scrapy.Field()              #同类
    hs300_rate = scrapy.Field()                     #沪深300
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    age tinyint unsigned default 0,
    height decimal(5,2),
    gender enum('男','女','人妖','保密'),
    cls_id int unsigned default 0
)
    """


