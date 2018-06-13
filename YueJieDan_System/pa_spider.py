# -*-coding:utf-8-*-
import requests, pymysql, time,json,datetime,re
from lxml import etree


def return_fundcode(fund):
    """
    根据fund_name返回fund_code
    :param fund:
    :return:transfromed_fund_code
    """
    axa_fundcodes_dict = {}
    # 中、英文基金名称对应：
    axa_fundcodes_dict['AB - American Growth Portfolio'] = 'ACMAGP'
    axa_fundcodes_dict['AB - Emerging Markets Growth Portfolio'] = 'ACMEMGP'
    axa_fundcodes_dict['AB - Global Equity Blend Portfolio'] = 'M-ALLBP'
    axa_fundcodes_dict['AB - Global Growth Trends Portfolio'] = 'ACMGGTP'
    axa_fundcodes_dict['AB - Global High Yield Portfolio'] = 'M-ABGHY'
    axa_fundcodes_dict['AB - Global Value Portfolio'] = 'ACMGVP'
    axa_fundcodes_dict['AB - India Growth Portfolio'] = 'INDACM'
    axa_fundcodes_dict['AB - International Health Care Portfolio'] = 'ALLHCFA'
    axa_fundcodes_dict['AB - International Technology Portfolio'] = 'M-ACMITP'
    axa_fundcodes_dict['AB - US Thematic Research Portfolio'] = 'M-ALBSC'
    axa_fundcodes_dict['FT - Franklin Biotechnology Discovery Fund'] = 'FBDIX'
    axa_fundcodes_dict['FT - Franklin Global Growth Fund'] = 'M-FTGGA'
    axa_fundcodes_dict['FT - Franklin Global Small/Mid Cap Growth Fund'] = 'FTTGGF'
    axa_fundcodes_dict['FT - Franklin India Fund'] = 'INDFT'
    axa_fundcodes_dict['FT - Franklin Natural Resources Fund'] = 'M-FTNRA'
    axa_fundcodes_dict['FT - Templeton Asian Growth Fund'] = 'FTTAGF'
    axa_fundcodes_dict['FT - Templeton BRIC Fund'] = 'M-FMBFA'
    axa_fundcodes_dict['FT - Templeton China Fund'] = 'FTTCF'
    axa_fundcodes_dict['FT - Templeton Emerging Markets Fund'] = 'FTTEM'
    axa_fundcodes_dict['FT - Templeton Global Bond Fund'] = 'FTTGBF'
    axa_fundcodes_dict['Direxion iBillionaire Index ETF'] = 'IBLN'
    axa_fundcodes_dict['Invesco -  PRC Equity Fund (China) Fund'] = 'INOPRCC'
    axa_fundcodes_dict['Invesco - Asian Equity Fund'] = 'INOAE'
    axa_fundcodes_dict['Invesco - Emerging Europe Equity Fund'] = 'INOEMSE'
    axa_fundcodes_dict['Invesco - Global Bond Fund'] = 'INOGB'
    axa_fundcodes_dict['Invesco - Global Select Equity Fund'] = 'INOUSVE'
    axa_fundcodes_dict['Powershares - Buyback Achievers Portfolio'] = 'BAP'
    axa_fundcodes_dict['Powershares - DWA Momentum Portfolio'] = 'M-PDP'
    axa_fundcodes_dict['Powershares - DWA Smallcap Momentum Portfolio'] = 'DSTL'
    axa_fundcodes_dict['Powershares - Emerging Markets Sovereign Debt Portfolio'] = 'EMSDP'
    axa_fundcodes_dict['Powershares - Global Agriculture Portfolio'] = 'GAP'
    axa_fundcodes_dict['Powershares - QQQ'] = 'M-PQQQ'
    axa_fundcodes_dict['Powershares - S&P 500 High Quality Portfolio'] = 'SPHQP'
    axa_fundcodes_dict['Powershares - Water Resources Portfolio'] = 'WRP'
    axa_fundcodes_dict['Investec GSF - Asian Equity Fund'] = 'INCAEF'
    axa_fundcodes_dict['Investec GSF - Emerging Markets Local Currency Dynamic Debt Fund'] = 'INCLCD'
    axa_fundcodes_dict['Investec GSF - Global Energy Fund'] = 'INCGEF'
    axa_fundcodes_dict['Investec GSF - Global Equity Fund'] = 'INCGEQF'
    axa_fundcodes_dict['Investec GSF - Global Gold Fund'] = 'INCGLD'
    axa_fundcodes_dict['Investec GSF - Global Natural Resources Fund'] = 'INCGNR'
    axa_fundcodes_dict['Investec GSF - Global Strategic Equity Fund'] = 'INCGSVF'
    axa_fundcodes_dict['Investec GSF - Global Strategic Managed Fund'] = 'INCGSF'
    axa_fundcodes_dict['iShares Asia 50 ETF'] = 'IXY012'
    axa_fundcodes_dict['iShares Cohen & Steers REIT ETF'] = 'B-IXY005'
    axa_fundcodes_dict['iShares Core Aggressive Allocation ETF'] = 'AGAL'
    axa_fundcodes_dict['iShares Core Conservative Allocation ETF'] = 'AOK'
    axa_fundcodes_dict['iShares Core Moderate Allocation ETF'] = 'AOM'
    axa_fundcodes_dict['iShares Core MSCI EAFE ETF'] = 'IXMSCI'
    axa_fundcodes_dict['iShares Core MSCI Emerging Markets ETF'] = 'IEMGUS'
    axa_fundcodes_dict['iShares Core S&P 500 ETF'] = 'IXSP500'
    axa_fundcodes_dict['iShares Core S&P Mid-Cap ETF'] = 'IJH'
    axa_fundcodes_dict['iShares Core S&P Small Cap ETF'] = 'CSPSC'
    axa_fundcodes_dict['iShares Core U.S. Aggregate Bond ETF'] = 'CTUBM'
    axa_fundcodes_dict['iShares Core US Credit Bond ETF'] = 'B-IXY013'
    axa_fundcodes_dict['iShares Currency Hedged MSCI Japan ETF'] = 'HEWJ'
    axa_fundcodes_dict['iShares Dow Jones US ETF'] = 'B-IXY004'
    axa_fundcodes_dict['iShares Emerging Markets Local Currency Bond ETF'] = 'IXY016'
    axa_fundcodes_dict['iShares Global Clean Energy ETF'] = 'M-ICLN'
    axa_fundcodes_dict['iShares Global Consumer Staples ETF'] = 'KXI'
    axa_fundcodes_dict['iShares Global High Yield Corporate Bond ETF'] = 'GHYCB'
    axa_fundcodes_dict['iShares Gold Trust'] = 'IXY017'
    axa_fundcodes_dict['iShares Growth Allocation ETF'] = 'GRAL'
    axa_fundcodes_dict['iShares High Yield Corporate Bond ETF'] = 'B-IXY014'
    axa_fundcodes_dict['iShares International Property ETF'] = 'B-IXY006'
    axa_fundcodes_dict['iShares Japan Large-Cap ETF'] = 'IXSPTO'
    axa_fundcodes_dict['iShares JP Morgan USD Emerging Markets Bond ETF'] = 'IXY015'
    axa_fundcodes_dict['iShares Latin America 40 ETF'] = 'M-IXSPLA'
    axa_fundcodes_dict['iShares MSCI Brazil Capped ETF'] = 'EWZ'
    axa_fundcodes_dict['iShares MSCI Brazil Small Cap ETF'] = 'IXY009'
    axa_fundcodes_dict['iShares MSCI Frontier 100 ETF'] = 'MS100'
    axa_fundcodes_dict['iShares MSCI India ETF'] = 'INDA'
    axa_fundcodes_dict['iShares MSCI India Small-Cap ETF'] = 'SMIN'
    axa_fundcodes_dict['iShares MSCI Pacific ex-Japan ETF'] = 'IXY011'
    axa_fundcodes_dict['iShares MSCI Sweden ETF'] = 'EWD'
    axa_fundcodes_dict['iShares Russell 1000 Growth ETF'] = 'B-IXY001'
    axa_fundcodes_dict['iShares Russell 2000 Growth ETF'] = 'B-IXY003'
    axa_fundcodes_dict['iShares Russell Mid-Cap Growth ETF'] = 'B-IXY002'
    axa_fundcodes_dict['iShares S&P Europe ETF'] = 'IXSPEU'
    axa_fundcodes_dict['iShares S&P GSCI Commodity Indexed Trust'] = 'SPGCI'
    axa_fundcodes_dict['iShares Select Dividend ETF'] = 'DVY'
    axa_fundcodes_dict['iShares Short Treasury Bond ETF'] = 'STB'
    axa_fundcodes_dict['iShares Silver Trust'] = 'B-IXY018'
    axa_fundcodes_dict['iShares TIPS Bonds ETF'] = 'TIP'
    axa_fundcodes_dict['iShares U.S. Oil & Gas Exploration & Production ETF'] = 'IEO'
    axa_fundcodes_dict['iShares U.S. Preferred Stock ETF'] = 'PFF'
    axa_fundcodes_dict['Legg Mason - Batterymarch Asia Ex-Japan Equity Fund'] = 'LMBATPA'
    axa_fundcodes_dict['Legg Mason - Batterymarch Managed Volatility European Equity Fund'] = 'LMBATEU'
    axa_fundcodes_dict['Legg Mason - Clearbridge Value Fund'] = 'LMVAL'
    axa_fundcodes_dict['Legg Mason - Royce US Small Cap Opportunity Fund'] = 'LMRYCE'
    axa_fundcodes_dict['Legg Mason - Royce US Smaller Companies Fund'] = 'LMRYE'
    axa_fundcodes_dict['MFS Meridian - Emerging Markets Debt Fund'] = 'MFSEMDF'
    axa_fundcodes_dict['MFS Meridian - Emerging Markets Debt Local Currency Fund'] = 'M-MFEDC'
    axa_fundcodes_dict['MFS Meridian - European Research Fund'] = 'MFSEEF'
    axa_fundcodes_dict['MFS Meridian - Global Equity Fund'] = 'MFSGEF'
    axa_fundcodes_dict['MFS Meridian - Global Research Fund'] = 'M-MFSRI'
    axa_fundcodes_dict['MFS Meridian - Global Total Return Fund'] = 'MFSGTR'
    axa_fundcodes_dict['MFS Meridian - US Concentrated Growth Fund'] = 'MFSUSEGF'
    axa_fundcodes_dict['MFS Meridian - US Value Fund'] = 'MFSVF'
    axa_fundcodes_dict['Morgan Stanley  - Global Quality'] = 'MORGLQA'
    axa_fundcodes_dict['Morgan Stanley - Asian Equity'] = 'M-MAEQA'
    axa_fundcodes_dict['Morgan Stanley - Emerging Europe Middle East & Africa Equity'] = 'M-MSEUI'
    axa_fundcodes_dict['Morgan Stanley - Global Brands'] = 'M-MSGBA'
    axa_fundcodes_dict['Morgan Stanley - Global Infrastructure'] = 'M-GLINF'
    axa_fundcodes_dict['Morgan Stanley - Latin American Equity'] = 'M-LAEQ'
    axa_fundcodes_dict['Morgan Stanley - US Advantage'] = 'M-USADV'
    axa_fundcodes_dict['Morgan Stanley - US Growth'] = 'M-MNAEI'
    axa_fundcodes_dict['Morgan Stanley Investment Funds - US Property Fund'] = 'MORIUSR'
    axa_fundcodes_dict['Prestige Alternative Finance (Asset Based Lending)'] = 'PRSAF'
    axa_fundcodes_dict['Prestige Commercial Finance Opportunities'] = 'PRCFO'
    axa_fundcodes_dict['Prestige Equity Option Advantage (Index Options)'] = 'PRSEO'
    axa_fundcodes_dict['Prestige Select Finance $ (International Lending)'] = 'PRSSF'
    axa_fundcodes_dict['威望另類財務基金有 (美元) - 資產為基礎的借貸 - 農業金融'] = 'PRSAFC'
    axa_fundcodes_dict['威望股票期权优势基金 (美元) - 全球/股票指数-市场中立策略'] = 'PRSEOC'
    axa_fundcodes_dict['Bullmark Latin America Select Leaders ETF'] = 'BMLA'
    axa_fundcodes_dict['Recon Capital DAX Germany ETF'] = 'DAX'
    axa_fundcodes_dict['Recon Capital NASDAQ 100 Covered Call ETF'] = 'QYLD'
    axa_fundcodes_dict['SPDR S&P Emerging Asia Pacific ETF'] = 'GMFUS'
    axa_fundcodes_dict['SSGA - SPDR Barclays High Yield Bond ETF'] = 'BHYB'
    axa_fundcodes_dict['SSGA - SPDR Dow Jones International Real Estate ETF'] = 'DJIRE'
    axa_fundcodes_dict['SSGA - SPDR Emerging Middle East & Africa ETF'] = 'EMEA'
    axa_fundcodes_dict['SSGA - SPDR EURO STOXX 50 ETF'] = 'FEZ'
    axa_fundcodes_dict['SSGA - SPDR MSCI ACWI IMI ETF'] = 'ACIM'
    axa_fundcodes_dict['SSGA - SPDR S&P China ETF'] = 'SPCETF'
    axa_fundcodes_dict['SSGA - SPDR S&P International Health Care Sector ETF'] = 'IHCS'
    axa_fundcodes_dict['CITI Market-Linked Note to Global Equity Basket'] = 'M-PCDB04'
    axa_fundcodes_dict['Credit Suisse AG $ Trigger Return Optimization Securities Linked to EURO STOXX 50 Index (3/29/2019)'] = 'CSLEUR'
    axa_fundcodes_dict['Vanguard Emerging Markets Government Bond ETF'] = 'VWOB'
    axa_fundcodes_dict['Vanguard Energy ETF'] = 'VDE'
    axa_fundcodes_dict['Vanguard Extended Market ETF'] = 'VXF'
    axa_fundcodes_dict['Vanguard FTSE Emerging Markets ETF'] = 'VWO'
    axa_fundcodes_dict['Vanguard High Dividend Yield ETF'] = 'VYM'
    axa_fundcodes_dict['Vanguard Prime Money Market Fund'] = 'VMMXX'
    axa_fundcodes_dict['Vanguard REIT ETF'] = 'VNQ'
    axa_fundcodes_dict['Wisdom Tree Europe Hedged Equity'] = 'HEDJ'
    axa_fundcodes_dict['Wisdom Tree Japan Hedged Equity'] = 'DXJ'
    axa_fundcodes_dict['WT - Emerging Markets Corporate Bond Fund'] = 'EMCB'
    axa_fundcodes_dict['WT - International MidCap Dividend Fund'] = 'DIM'
    axa_fundcodes_dict['WT - International SmallCap Dividend Fund'] = 'DLS'
    axa_fundcodes_dict['WT - Total Earnings Fund'] = 'EXT'
    axa_fundcodes_dict['S&P Asia 50 (USD) Index'] = 'S&P Asia 50 (USD) Index'
    axa_fundcodes_dict['S&P 500  (USD) Index'] = 'S&P 500  (USD) Index'
    axa_fundcodes_dict['MSCI ACWI IMI (USD) Index'] = 'MSCI ACWI IMI (USD) Index'

    for fund_name in axa_fundcodes_dict.keys():
        if fund.lower() in fund_name.lower():
            return axa_fundcodes_dict[fund_name]

def frequency_to_num(input_x):
    x = input_x.strip().lower()
    if x == 'monthly':
        return 1
    if x == 'quarterly' :
        return 3
    if x == 'half-yearly' or x == 'semi-annual':
        return 6
    if x == 'annually' or x == 'annual':
        return 12
    else:
        print('frequency_error:',input_x)
        return input_x

def getday(y=2018, m=5, d=1, n=0):
    the_date = datetime.datetime(y, m, d)
    result_date = the_date + datetime.timedelta(days=n)
    d = result_date.strftime('%Y-%m-%d')
    return d

def try_except(sth):

    # 使用cursor()方法获取操作游标
    # self.cur = self.mysql_client.cursor()
    # print('inserting data to mysql ...')
    try:
        sth
    except pymysql.Error as e:
        with open('Data/' + 'error_log' + '.log', 'a', encoding='utf-8') as f:
            print('Writing Error info...', e)
            f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + '：' + str(e) + '\r\n')
        f.close()
        # finally:
        #     self.cur.close()
        # self.mysql_client.commit()
        # return sth

Spider_Date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
mysql_client = pymysql.connect(host="112.74.93.48",port=3306,user="root",password="962ced336f",database="statement",charset="utf8")
cur = mysql_client.cursor()

# id = '14187'
userName = 'HK100040'
passWord = 'Trussan1105'
start_url = 'https://lyncone.lyncpay.com/Pages/Public/Login.aspx'
login_url = 'https://lyncone.lyncpay.com/pages/public/login.aspx'
page_url = 'https://lyncone.lyncpay.com/webservice//UserModuleProvider.svc/GetAccessibleUsersList'

# # Get方式：固定项有/id/3/4     1910+N位数    时间戳+3位数
# # 个人资料信息
# personal_info_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetParticipantInformation/"+str(id)+"/3/4/PremierTrust?callback=jQuery19108936877663145584_"+str(int(time.time()))+"660&_="+str(int(time.time()))+"661"
# # 计划编号与类型
# product_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetPlanInformation/"+str(id)+"/3/4/PremierTrust?callback=jQuery19108936877663145584_"+str(int(time.time()))+"663&_="+str(int(time.time()))+"664"
# # 保费与分红
# premium_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetPlanStatus/"+str(id)+"/3/4/"+str(year)+"-"+str(month)+"-"+str(day)+"?callback=jQuery19108936877663145584_"+str(int(time.time()))+"665&_="+str(int(time.time()))+"666"
# # allocation数据
# # allocation_url = 'https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetAccountSummaries/14187/3/4/2018-04-12?callback=jQuery19108936877663145584_1523614703669&_=1523614703670'
# allocation_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetAccountSummaries/"+str(id)+"/3/4/"+str(year)+"-"+str(month)+"-"+str(day)+"?callback=jQuery19108936877663145584_"+str(int(time.time()))+"669&_="+str(int(time.time()))+"670"

login_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    # "Content-Length":"1098",
    "Content-Type": "application/x-www-form-urlencoded",
    # "Cookie":"ASP.NET_SessionId=qxpxqgqtsicm0cwm0gve201y; .ASPXAUTH=7D5F58E9FC4944EB07099B5EDBD3709B2E253929F597374937EF2AEDFCEAA70B575CC5FD25AA57D7A29442E69A739D824C306A08107DE798AEB87E5742A92E9B40BB9DD6219C440093C4401586C74812A9F35B2F2288192AE9C3F1B97E0898250501C08DD3D50B34AE4B53E1F03316F69F1A31D890689ADA268D0F41E953ACFE496937F91D8ABFEB061A80966BC23BFD; _ga=GA1.2.1220542440.1523603053; _gid=GA1.2.557169587.1523603053; _gat=1",
    "Host": "lyncone.lyncpay.com",
    "Origin": "https://lyncone.lyncpay.com",
    "Referer": "https://lyncone.lyncpay.com/pages/public/login.aspx",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
}
login_formData = {
    # hidden token:
    # "__LASTFOCUS":"",
    # "MasterScriptManager_HiddenField":"",
    # "__EVENTTARGET":"",
    # "__EVENTARGUMENT":"",
    # "__VIEWSTATE":"/wEPDwULLTE1NTgwNTEzMTkPZBYCZg9kFgICAQ9kFgYCAQ9kFgJmDxYCHgtfIUl0ZW1Db3VudAIFFgpmD2QWAmYPFQMBMQVibG9jawdFTkdMSVNIZAIBD2QWAmYPFQMBMgRub25lCEVTUEHDkU9MZAICD2QWAmYPFQMBMwRub25lClBPUlRVR1XDilNkAgMPZBYCZg8VAwE0BG5vbmUG5Lit5paHZAIED2QWAmYPFQMBNQRub25lCeaXpeacrOiqnmQCAw9kFgZmDxYCHgdWaXNpYmxlaGQCAg88KwAKAQAPFggeFFBhc3N3b3JkUmVjb3ZlcnlUZXh0BRJGb3Jnb3QgbXkgUGFzc3dvcmQeEVVzZXJOYW1lTGFiZWxUZXh0BQpVc2VyIE5hbWU6HhFQYXNzd29yZExhYmVsVGV4dAUJUGFzc3dvcmQ6Hg9Mb2dpbkJ1dHRvblRleHQFBkxvZyBJbmRkAgMPZBYCZg8WAh8BaGQCBQ9kFgJmDxYCHgRUZXh0BRQmY29weTsgMjAxOCBQQSBHcm91cGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFJGN0bDAwJGNwaE1haW4kbG9naW4kTG9naW5JbWFnZUJ1dHRvbm6UOH6khdmWX0Bb6BYrpShX4mhaa1Ks7m9bdn5th1iX",
    # "__VIEWSTATEGENERATOR":"6DC167F9",
    # "__EVENTVALIDATION":"/wEdAAQfr6bRs94moL3d6xNMDabmMY8ZkZ7FD7dYAf5YJPP5t+Mm+dgDcMmJLYazpf1BSorQs1tqCVsyYz0sEAFmSl+RIB3jYJhx9W31uhCGnBzyDz2LQGGor5kXdj0JOnfAQk4=",
    # 固定项
    "ctl00$cphMain$login$UserName": userName,
    "ctl00$cphMain$login$Password": passWord,
    "ctl00$cphMain$login$LoginButton": "Log In",
}
page_formData = """{
    "userID":"",
    "userName":"HK100040",
    "search4agents":'0',
    "currMod":"PremierTrust",
    "code":"",
    "firstName":"",
    "lastName":"",
    "currentPage":'1',
    "rowsPerPage":'50',
    "sortBy":"ParticipantCode",
    "sortDir":""
}"""
# page_formData_json = json.dumps(page_formData)
# 正确：{"userID":"","userName":"HK100040","search4agents":0,"currMod":"PremierTrust","code":"","firstName":"","lastName":"","currentPage":2,"rowsPerPage":5,"sortBy":"ParticipantCode","sortDir":""}
# 错误1：userID=&userName=HK100040&search4agents=0&currMod=PremierTrust&code=&firstName=&lastName=&currentPage=2&rowsPerPage=5&sortBy=ParticipantCode&sortDir=
# 错误2：page_formData = {"userID":"","userName":"HK100040","search4agents":0,"currMod":"PremierTrust","code":"","firstName":"","lastName":"","currentPage":2,"rowsPerPage":5,"sortBy":"ParticipantCode","sortDir":""}
# 错误3：%7B%22userID%22%3A%22%22%2C%22userName%22%3A%22HK100040%22%2C%22search4agents%22%3A0%2C%22currMod%22%3A%22PremierTrust%22%2C%22code%22%3A%22%22%2C%22firstName%22%3A%22%22%2C%22lastName%22%3A%22%22%2C%22currentPage%22%3A2%2C%22rowsPerPage%22%3A5%2C%22sortBy%22%3A%22ParticipantCode%22%2C%22sortDir%22%3A%22%22%7D=

"""
$.ajax({            
            url: url,
            data: JSON.stringify({
                userID: "",
                userName: environment.memberCode,
                search4agents: 0,
                currMod: environment.CurrentPageModule,
                code: myAcc_Participants_filterCode,
                firstName: myAcc_Participants_filterFirstName,
                lastName: myAcc_Participants_filterLastName,
                currentPage: myAcc_Participants_current_page,
                rowsPerPage: myAcc_Participants_rows_x_page,
                sortBy: myAcc_Participants_sortBy,
                sortDir: myAcc_Participants_sortDir
            }),

"""

# 获取登录参数
ssion = requests.session()
print('start_url---------------------')
login_html = ssion.get(url=start_url, headers=login_headers).text  # ,
# print(login_html)
login_html_xpathobj = etree.HTML(login_html)
hidden_names = login_html_xpathobj.xpath("//input[@type='hidden']//@name")
# print(hidden_names)
hidden_values = [login_html_xpathobj.xpath("//input[@name='" + hidden_name + "']/@value") for hidden_name in
                 hidden_names]
# print(hidden_values)
for hidden_name, hidden_value in zip(hidden_names, hidden_values):
    login_formData[hidden_name] = hidden_value[0] if hidden_value else ''
# print(login_formData)

time.sleep(1)
# login
after_login_html = ssion.post(url=login_url,headers=login_headers,data=page_formData)
# print(after_login_html.text)
print('login~~~~~~~~~')
# print(after_login_html.request.headers)
# print(after_login_html.cookies)
time.sleep(1)

# page
page_html = ssion.post(url=page_url,headers=login_headers,data=page_formData)
# print(page_html.text)
policy_nos_dict = json.loads(page_html.text)
policy_no_lists = policy_nos_dict['rows'] # list
# policy_no_lists.reverse()
for policy_no_dict in policy_no_lists:
    try:
        id = policy_no_dict['id']
        print('id',id)
        # policy_no_list = policy_no_dict['data']
        # print(policy_no_list)
        pattern = re.compile('\((.*?)\);',re.S)
        # json接口
        # Get方式：固定项有/id/3/4   ,  1910+N位数   ,  时间戳+3位数
        # 个人资料信息
        personal_info_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetParticipantInformation/" + str(id) + "/3/4/PremierTrust?callback=jQuery19108936877663145584_" + str(int(time.time())) + "660&_=" + str(int(time.time())) + "661"
        # 计划编号与类型
        product_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetPlanInformation/" + str(id) + "/3/4/PremierTrust?callback=jQuery19108936877663145584_" + str(int(time.time())) + "663&_=" + str(int(time.time())) + "664"

        # personal_info_json = pattern.findall(ssion.get(url=personal_info_url,headers=login_headers).text)
        #
        # personal_info_list = json.loads(personal_info_json[0] if personal_info_json else '')
        # print(personal_info_list)

        time.sleep(1)
        product_info_json = pattern.findall(ssion.get(url=product_url,headers=login_headers).text)
        product_info_list = json.loads(product_info_json[0] if product_info_json else '')
        print(product_info_list)
        for product_info_dict in product_info_list:
            if product_info_dict['Key'] == '计划编号':
                policy_no = product_info_dict['Value']
            if product_info_dict['Key'] == '计划类型':
                product = product_info_dict['Value']
            if product_info_dict['Key'] == '供款金额':
                currency ='USD' if product_info_dict['Value'][0] == '$' else ''
                regular_premium = product_info_dict['Value'][0].strip().replace('$','').replace(' ','').replace(',','')
            if product_info_dict['Key'] == '付款频率':
                frequency = product_info_dict['Value']
        print('policy_no,product,currency:',policy_no,product,currency)

        time.sleep(1)
        year = str(datetime.datetime.now())[:4] # '2018' #
        month = str(getday(int(str(datetime.datetime.now())[:4]),int(str(datetime.datetime.now())[5:7]),int(str(datetime.datetime.now())[8:10]),-25))[5:7] # '04' #
        # print(month)
        day = '32' # str(datetime.datetime.now())[8:10] # '13'
        notRepeat = 1   # 为了不重复存入frequency和premium的变化更新
        for day in range(1,int(day)):
        # for day in range(int(day)-1,int(day)):
            try:
                print('===========')
                print(year,month,day)
                date = str(year) + '-' + str(month) + '-' + str(day) if day >= 10 else str(year) + '-' + str(month) + '-0' + str(day)
                time.sleep(1)
                # 保费与分红
                premium_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetPlanStatus/" + str(id) + "/3/4/" + str(year) + "-" + str(month) + "-" + str(day) + "?callback=jQuery19108936877663145584_" + str(int(time.time())) + "665&_=" + str(int(time.time())) + "666"
                # allocation数据
                allocation_url = "https://lyncone.lyncpay.com/webservice//MyAccountsProvider.svc/GetAccountSummaries/" + str(id) + "/3/4/" + str(year) + "-" + str(month) + "-" + str(day) + "?callback=jQuery19108936877663145584_" + str(int(time.time())) + "669&_=" + str(int(time.time())) + "670"
                # print(allocation_url)

                premium_info_json = pattern.findall(ssion.get(url=premium_url,headers=login_headers).text)
                # print(ssion.get(url=premium_url,headers=login_headers).text)
                premium_info_list = json.loads(premium_info_json[0] if premium_info_json else '')
                print(premium_info_list)

                for premium_info_dict in premium_info_list:
                    if premium_info_dict['Key'] == '已付保费':
                        premium = premium_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',','')
                    if premium_info_dict['Key'] == '红利分配':
                        bonus = premium_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',','')
                    if premium_info_dict['Key'] == '帐户价值':
                        total_value = premium_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',','')
                if not total_value:
                    continue

                # 存入tb_client和tb_supply
                if frequency and notRepeat:
                    notRepeat = 0
                    check = cur.execute(
                        "select name,product,platform,regular_contribution,payment_frequency from tb_client where policy_no='" + policy_no + "';")
                    tb_name, tb_product, tb_platform, before_premium, before_frequency = cur.fetchall()[
                        0] if check else ('', '')
                    if int(float(premium)) != int(float(before_premium)):
                        print(policy_no, 'premium changed!')
                        # print(
                        #     "insert into tb_account_supply(policy_no,name,platform,product,event_type,event_date,before_change,after_change) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                        #     (policy_no, tb_name, tb_platform, tb_product, 'regular_contribution', Spider_Date,
                        #      float(before_premium), premium))
                        try_except(cur.execute(
                            "insert into tb_account_supply(policy_no,name,platform,product,event_type,event_date,before_change,after_change) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                            (policy_no, tb_name, tb_platform, tb_product, 'regular_contribution', Spider_Date,
                             float(before_premium), premium)))
                        cur.execute(
                            "update tb_client set regular_contribution = '" + premium + "' where policy_no='" + policy_no + "';")
                        print(policy_no, 'premium updated.')

                    before_frequency = before_frequency
                    if str(frequency_to_num(frequency)) != str(before_frequency):
                    # if frequency_to_num(frequency) != frequency_to_num(before_frequency):
                        print(policy_no, 'frequency changed!')
                        try_except(cur.execute(
                            "insert into tb_account_supply(policy_no,name,platform,product,event_type,event_date,before_change,after_change) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                            (policy_no, tb_name, tb_platform, tb_product, 'payment_frequency', Spider_Date,
                             before_frequency, frequency_to_num(frequency))))
                        cur.execute("update tb_client set payment_frequency = '" + str(frequency_to_num(frequency)) + "' where policy_no='" + policy_no + "';")
                        print(policy_no, 'frequency updated.')


                print('premium,bonus,total_value:', premium, bonus, total_value)
                if not cur.execute("select * from tb_accountvalue where policy_no='" + policy_no + "' and date='" + date + "';"):
                    print('inserting data into mysql...')
                    cur.execute("insert into tb_accountvalue(policy_no,date,currency,total_value) values(%s,%s,%s,%s)",(policy_no, date, currency, total_value))
                if not cur.execute("select * from tb_premium where policy_no='" + policy_no + "' and date='" + date + "';"):
                    print('inserting data into mysql...')
                    cur.execute("insert into tb_premium(policy_no,Spider_Date,date,currency,value,bonus,frequency) values(%s,%s,%s,%s,%s,%s,%s)",(policy_no,Spider_Date,date,currency, premium,bonus,frequency))
                time.sleep(1)
                allocation_info_json = pattern.findall(ssion.get(url=allocation_url,headers=login_headers).text)
                allocation_info_list = json.loads(allocation_info_json[0] if allocation_info_json else '')
                print(allocation_info_list)
                total_value1 = 0
                for allocation_info_dict in allocation_info_list:
                    value1 = allocation_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',','')
                    try:
                        total_value1 += float(value1)
                    except:
                        break
                if not value1:
                    continue
                if not cur.execute("select * from tb_allocation where policy_no='" + policy_no + "' and date='" + date + "';"):
                    for allocation_info_dict in allocation_info_list:
                        fund = allocation_info_dict['FundName']
                        price = allocation_info_dict['UnitPrice'].strip().replace('$','').replace(' ','').replace(',','')
                        unit = allocation_info_dict['Units'].strip().replace('$','').replace(' ','').replace(',','')
                        value1 = allocation_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',','')
                        percent = float(allocation_info_dict['Value'].strip().replace('$','').replace(' ','').replace(',',''))/total_value1 if total_value1 else 0
                        # print('fund,price,unit,total_value1,percent:',fund,price,unit,total_value1,percent)
                        # if not cur.execute("select * from tb_premium where policy_no='" + policy_no + "' and date='" + date + "';"):
                        print("insert into tb_allocation(policy_no,date,price_date,product,fund,fund_code,fund_currency,price,value1,policy_currency,value2,unit,percent)",policy_no,Spider_Date,date,product,fund,return_fundcode(fund),currency,price,value1,currency,value1,unit,percent)
                        cur.execute("insert into tb_allocation(policy_no,date,price_date,product,fund,fund_code,fund_currency,price,value1,policy_currency,value2,unit,percent) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(policy_no,Spider_Date,date,product,fund,return_fundcode(fund),currency,price,value1,currency,value1,unit,percent))
                        # print('inserting data into mysql...')
            except Exception as e:
                print('error!这个policy_no这一天有问题：', policy_no, date, e)
            else:
                mysql_client.commit()
                print('committed.')
            time.sleep(1)
    except Exception as e:
        print('error!这个policy_no_dict有问题：',e,policy_no_dict)

cur.close()
mysql_client.close()

# [{"ID":1,"FundName":"iShares Core S&P 500 ETF","Percentage":"15.00","UnitPrice":"267.79","Units":"10.07","CreatedDate":"\/Date(1523574225993-0400)\/","Value":"2,697.40"},{"ID":2,"FundName":"MFS Meridian - Global Equity Fund","Percentage":"25.00","UnitPrice":"56.75","Units":"81.03","CreatedDate":"\/Date(1523574225993-0400)\/","Value":"4,598.43"},{"ID":3,"FundName":"AB - International Technology Portfolio","Percentage":"15.00","UnitPrice":"312.85","Units":"8.72","CreatedDate":"\/Date(1523574225993-0400)\/","Value":"2,727.79"},{"ID":4,"FundName":"iShares Global High Yield Corporate Bond ETF","Percentage":"20.00","UnitPrice":"50.43","Units":"71.66","CreatedDate":"\/Date(1523574225993-0400)\/","Value":"3,613.92"},{"ID":5,"FundName":"iShares Core U.S. Aggregate Bond ETF","Percentage":"25.00","UnitPrice":"106.77","Units":"42.06","CreatedDate":"\/Date(1523574225993-0400)\/","Value":"4,490.95"}]


# logout
ssion.get(url='https://lyncone.lyncpay.com/Pages/Public/Login.aspx?logout=1',headers=login_headers)
print('logout.')


