# -*-coding:utf-8-*-
import requests, time, re, json, pymysql, datetime
from lxml import etree


class ITA_Spider(object):
    def fees_to_mysql(self, NO, product, fee_json):
        fees = fee_json['ListFundActivityTable']
        # data=[]

        for fee in fees:
            policy_no = NO
            product = product
            # date = datetime.datetime.strptime(fee['ActivityDate'], '%d/%m/%Y')
            date = datetime.datetime.strptime(fee['ActivityDate'], '%d/%m/%Y').date()
            currency = 'USD' if '$' in fee['Amount'] else 'other'
            fund = fee['FundCode']
            fee_type = fee['ActivityType']
            status = fee['Status']
            price = fee['UnitRate'].replace(',', '')
            value = fee['Amount'].replace('$', '').replace(',', '')
            units = fee['Units'].replace(',', '')
            spider_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # print (element['policy_no'],element['date'],element['fund'],element['type'])
            if (policy_no, date, fund, fee_type) not in self.existed_fee:
                print(
                    "insert into test(policy_no,spider_date,product,date,fund,type,status,price,currency,value,units)",
                    (
                        policy_no, spider_date, product, date, fund, fee_type, status, price, currency, value, units))
                self.cursor.execute(
                    "insert into test(policy_no,spider_date,product,date,fund,type,status,price,currency,value,units) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        policy_no, spider_date, product, date, fund, fee_type, status, price, currency, value, units))
            else:
                print('skip!')
        self.conn.commit()

    def start_work(self):
        headers = {
            "authority": "ita.secureaccountaccess.com",
            "method": "GET",
            "path": "/Account/Login?ReturnUrl=%2f",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            # # "cookie":"ASP.NET_SessionId=ttcqusc1gi5na3kezwvidpaq; __RequestVerificationToken=YBq5hhf0lol8BbZvpjdlfClsujfjrhC9MwL4EwLmgj0KP3PoDIBLgaSssT53d2JqlrXyG13rHRjwW7AGDiDHowNm3MI1; _ga=GA1.2.550487300.1512549105; _gid=GA1.2.1013929078.1524732680; _gat=1",
            "referer": "https://ita.secureaccountaccess.com/",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",

        }
        login_formdata = {
            # __RequestVerificationToken:BoiBBemiWBbNpcrfrTfqUXKbvKVY9J0jqlcC9npB9D2VZQxrJF-bIwSoms5L7n00kWNYfO1_S3H7dTHfwpfyHT-PBDM1
            # LockSession:
            "UserName": "trussan",
            "Password": "Trussan1105",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.ssion = requests.session()
        start_response = etree.HTML(
            self.ssion.get(url='https://ita.secureaccountaccess.com/Account/Login', headers=headers).text)
        hidden_names = start_response.xpath("//input[@type='hidden']//@name")
        # print(hidden_names)
        hidden_values = [start_response.xpath("//input[@name='" + hidden_name + "']/@value") for hidden_name in
                         hidden_names]
        # print(hidden_values)
        for hidden_name, hidden_value in zip(hidden_names, hidden_values):
            login_formdata[hidden_name] = hidden_value[0] if hidden_value else ''
        # print(login_formdata)

        # login
        self.ssion.post(url='https://ita.secureaccountaccess.com/Account/Login?ReturnUrl=%2F', headers=headers,
                        data=login_formdata).text
        # redirect
        self.ssion.get(url='https://ita.secureaccountaccess.com/', headers=headers).text
        # sarah:44, trussan:1
        eq_html = self.ssion.get(
            url="https://ita.secureaccountaccess.com/Home/GetPartialIntroducerMainPageContent?ID=1_516290&AccountNumber=516290&_=" + str(
                int(time.time())) + "238", headers=headers, data=login_formdata).text
        # print(eq_html)
        pattern = re.compile('\?eq=(.*?)">', re.S)
        eq = pattern.findall(eq_html)[0]
        home_url = 'https://ita.secureaccountaccess.com/Introducer/StandardQueries?eq=' + eq
        home_html = self.ssion.get(url=home_url, headers=headers).text

        index = home_html.index('?ObjectID=')
        index = home_html.index("'", index) + 1
        index2 = home_html.index("'", index)
        id = home_html[index:index2]
        search_page_html = self.ssion.get(
            url='https://ita.secureaccountaccess.com/Introducer/StandardQueries/GetPlanSearch?ObjectID=' + id + '&AccountType=2',
            headers=headers).text
        params = {
            'TableReport_length': '100',
            'FilterCriteria.PlanNumberFilter': '',
            'FilterCriteria.SequenceFilter': '',
            'FilterCriteria.PolicyHolderNameFilter': '',
            'FilterCriteria.ProductFilter': '',
            'FilterCriteria.EffectiveDateFromFilter': '',
            'FilterCriteria.EffectiveDateToFilter': '',
            'FilterCriteria.PaidToDateFromFilter': '',
            'FilterCriteria.PaidToDateToFilter': '',
            'FilterCriteria.ContributionFromFilter': '',
            'FilterCriteria.ContributionToFilter': '',
            'FilterCriteria.AccountValueFromFilter': '',
            'FilterCriteria.AccountValueToFilter': '',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # search all page
        search_page_response = etree.HTML(search_page_html)
        hidden_names = search_page_response.xpath("//input[@type='hidden']//@name")
        # print(hidden_names)
        hidden_values = [search_page_response.xpath("//input[@name='" + hidden_name + "']/@value") for hidden_name in
                         hidden_names]
        # print(hidden_values)
        for hidden_name, hidden_value in zip(hidden_names, hidden_values):
            params[hidden_name] = hidden_value[0] if hidden_value else ''
        # print(params)
        print('**********************')
        data_page = self.ssion.post(
            url='https://ita.secureaccountaccess.com/Introducer/StandardQueries/SearchPlanSearch', headers=headers,
            data=params).text
        print(data_page)
        data_dict = json.loads(data_page)

        print('**********************')
        # connect mysql..
        self.conn = pymysql.connect(host="112.74.93.48", user="root", passwd="962ced336f", db="statement",
                                    charset="utf8")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT policy_no,date,fund,type from test;")
        self.existed_fee = self.cursor.fetchall()
        # print existed_fee

        for item in data_dict['ListPlanTable']:
            try:
                NO = item['PlanNumber']
                product = item['Product']
                print('https://ita.secureaccountaccess.com' + item['UrlPolicy'])
                # print(item['UrlPolicy'][8:])
                eq = item['UrlPolicy'][11:]
                # element = {'policy_no':NO,'product':self.switch_product_name(product)}
                # element['name'] = item['PolicyHolderName']

                headers = {
                    "Host": "ita.secureaccountaccess.com",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": '1',
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    # "Referer":"https://ita.secureaccountaccess.com/Policy?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    # "Cookie":"_ga=GA1.2.758213080.1533626117; _gid=GA1.2.690528990.1535940277; mfesecure_visit=1; ASP.NET_SessionId=bjzvbt1sz5lpagazuqrn2eib; __RequestVerificationToken=h2BmH8e_lGF4FhDiEfS8avq1hWoL-BnOw_p37-ChKU0SkPDYp2sv8m5hLSbRpbdcY7S5N8QhT3P8oYzvR1O7zW11Wzg1; .ASPXFORMSAUTH=07F9F0B0B955F998FA1627873A73E06C579AE676C0F6B9EE202C0BE308ECFE1023F95E552F45E05ECD0DDA23B4837D536641FC3594A0437D5716079AC895ABF208679A3FB9D5470683004B230E00F64CE76FA1CBD31C193C9D535391D6147F117846441D1EBE4BC145FCF4C73D27AEC754C7CCBEE7228A83CCFD19EB6C9D96922FFDC53B44B517E244A02810E97DF44C27FBDD6C; _gat=1",
                    "Accept-Encoding": "gzip, deflate"
                }

                headers['Referer'] = home_url
                # 保单页面
                policy_page = self.ssion.get(url='https://ita.secureaccountaccess.com' + item['UrlPolicy'],
                                             headers=headers).text
                # print(policy_page)
                headers['Referer'] = 'https://ita.secureaccountaccess.com' + item['UrlPolicy']
                # # 供款页面
                # # premium_pattern = re.compile("Policy\/Billing\?eq=(.*?) ")
                # print(self.ssion.get(url='https://ita.secureaccountaccess.com/Policy/Billing?eq=' + eq,headers=headers).text)
                #
                # # allocation页面
                # # allocation_pattern = re.compile("Policy\/Benefit\?eq=(.*?) ")
                # print(self.ssion.get(url='https://ita.secureaccountaccess.com/Policy/Summary/GetFunds?eq=' + eq,headers=headers).text)

                # 成本页面
                fee_pattern = re.compile("Policy\/FundActivity\?eq=(.*?) ")
                fee_url = 'https://ita.secureaccountaccess.com/Policy/FundActivity?eq=' + fee_pattern.findall(policy_page)[
                    0]

                # print(fee_url)
                fees_page_response = etree.HTML(self.ssion.get(url=fee_url, headers=headers).text)
                fee_data = {
                    # "FundActivityIDEncrypt":"Dfqs%2Byrn0M3lyqNo%2F5SU6V6Itpp8fmAjqNcHm9B2t3iwliWVmazGFjFF%2F%2FU0D9DFbOE%2FUeNjJXxVJe%2F474zPqntjmN0CihcMPvkjA4ARoi7DZS83uTeB0HlfUfenaS6fwYwxDJU66HkaYpn2j53VotR7SiQWb4CxvweYb4fTrQJkIoKTIazAcKAml%2BenZs1B5iJyMBJQIoh02jqZBWUwIjIWyV7WN%2BCTT8W%2FuPaxuyVrIPRP1HwUv3ifx4HdlYW%2FSh9rTaR%2Bp8g%3D",
                    "ActivityDateFromFilter": "01/01/2017",
                    "ActivityDateToFilter": time.strftime('%d/%m/%Y', time.localtime(time.time())),
                    "ActivityTypeFilter": "",
                    "StatusFilter": "",
                    "FundCodeFilter": "",
                    "AmountFromFilter": "",
                    "AmountToFilter": "",
                    "UnitsFromFilter": "",
                    "UnitsToFilter": "",
                    "UnitRateFromFilter": "",
                    "UnitRateToFilter": "",
                    "X-Requested-With": "XMLHttpRequest"
                }
                hidden_names = fees_page_response.xpath("//input[@type='hidden']//@name")
                # print(hidden_names)
                hidden_values = [fees_page_response.xpath("//input[@name='" + hidden_name + "']/@value") for hidden_name in
                                 hidden_names]
                # print(hidden_values)
                for hidden_name, hidden_value in zip(hidden_names, hidden_values):
                    if hidden_name == 'FundActivityIDEncrypt':
                        fee_data[hidden_name] = hidden_value[0] if hidden_value else ''
                # print(fee_data)
                time.sleep(2)
                # 成本fee_json
                headers['Referer'] = fee_url
                fee_json = self.ssion.post(url='https://ita.secureaccountaccess.com/Policy/FundActivity/SearchFundActivity',
                                           headers=headers, data=fee_data).json()
                # to_mysql
                self.fees_to_mysql(NO, product, fee_json)
                time.sleep(1)
                print('~~~~~~~~~~~~~~')
            except Exception as e :
                print('error!',e)
                time.sleep(10)

        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    ita_spider = ITA_Spider()
    ita_spider.start_work()

"""

fee_headers1 = {
    "Host":"ita.secureaccountaccess.com",
    "Connection":"keep-alive",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    # "Referer":"https://ita.secureaccountaccess.com/Policy?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d",
    "Accept-Language":"zh-CN,zh;q=0.9",
    # "Cookie":"_ga=GA1.2.758213080.1533626117; _gid=GA1.2.690528990.1535940277; mfesecure_visit=1; ASP.NET_SessionId=bjzvbt1sz5lpagazuqrn2eib; __RequestVerificationToken=h2BmH8e_lGF4FhDiEfS8avq1hWoL-BnOw_p37-ChKU0SkPDYp2sv8m5hLSbRpbdcY7S5N8QhT3P8oYzvR1O7zW11Wzg1; .ASPXFORMSAUTH=07F9F0B0B955F998FA1627873A73E06C579AE676C0F6B9EE202C0BE308ECFE1023F95E552F45E05ECD0DDA23B4837D536641FC3594A0437D5716079AC895ABF208679A3FB9D5470683004B230E00F64CE76FA1CBD31C193C9D535391D6147F117846441D1EBE4BC145FCF4C73D27AEC754C7CCBEE7228A83CCFD19EB6C9D96922FFDC53B44B517E244A02810E97DF44C27FBDD6C; _gat=1",
    "Accept-Encoding":"gzip, deflate"
}
fee_headers2 = {
    "Host":"ita.secureaccountaccess.com",
    "Connection":"keep-alive",
    "Accept":"*/*",
    "Origin":"https://ita.secureaccountaccess.com",
    "X-Requested-With":"XMLHttpRequest",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    # "Referer":"https://ita.secureaccountaccess.com/Policy/FundActivity?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYEAdRwNCiVS74VX50w0O4GhinLI75IZvUi47mSv6ME4dV5ASbz05zPHuQuAQ4sZtb0QYB5fuh%2baH3Q7n8JM%2fXuuxUGWLBel0yqq9rtIEa%2fpM6iiCikgyevR8Vxc63Pdam7N1kVb3qirVVjy4oZ7uR3a0ofa02kfqfI",
    "Accept-Language":"zh-CN,zh;q=0.9",
    # "Cookie":"_ga=GA1.2.758213080.1533626117; _gid=GA1.2.690528990.1535940277; mfesecure_visit=1; ASP.NET_SessionId=bjzvbt1sz5lpagazuqrn2eib; __RequestVerificationToken=h2BmH8e_lGF4FhDiEfS8avq1hWoL-BnOw_p37-ChKU0SkPDYp2sv8m5hLSbRpbdcY7S5N8QhT3P8oYzvR1O7zW11Wzg1; .ASPXFORMSAUTH=07F9F0B0B955F998FA1627873A73E06C579AE676C0F6B9EE202C0BE308ECFE1023F95E552F45E05ECD0DDA23B4837D536641FC3594A0437D5716079AC895ABF208679A3FB9D5470683004B230E00F64CE76FA1CBD31C193C9D535391D6147F117846441D1EBE4BC145FCF4C73D27AEC754C7CCBEE7228A83CCFD19EB6C9D96922FFDC53B44B517E244A02810E97DF44C27FBDD6C; _gat=1",
    "Accept-Encoding":"gzip, deflate",
    # "Content-Length":"574",
}


'/Policy?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d'
'/Policy?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d'
'        eq=O5%2fu6AMIiIEfz%2b01JNnXBWMHIywnPDCAp%2fI9VhKFFrfn89ybWAveKa%2fckLHpzJ5ST1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d'
'/Policy?eq=O5%2fu6AMIiIGJA9cqVqxbLwfMuDQDtIzIbSRRrh1e%2bJN6K2CZAM%2bXt0rYuN30OsoeT1mA%2fbHRboVFdCHw%2fJt8sART5VHL1vsqVddBB342k7d3x302DD1WNPtEdPKYiWYE9Rbh5lRFVKXSF4AA7frSrA%3d%3d'


# 正确：
GET https://ita.secureaccountaccess.com/Policy?eq=FBVPeXxBAT7jUmAQlSV33FIBJp3lcCPEUp5GtjHkmRIc2uYM5OXGVrcf7%2b4JL8CMMSyblTeJCKacHh5%2bxL91NhZtmFP2fHEbKskE0ewSV5tWRI0Xa6WnDPgZAV9V3YJ5oSCioWbuNdRsaVP3Q3BhlQ%3d%3d HTTP/1.1
Host: ita.secureaccountaccess.com
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Referer: https://ita.secureaccountaccess.com/Introducer/StandardQueries?eq=FBVPeXxBAT5twLDpBNOSqhjx92RuqHhe44tLpww7UGRBno5UVhZqYuUKgJ1Uc8fhMSyblTeJCKacHh5%2bxL91NhZtmFP2fHEbKskE0ewSV5tWRI0Xa6WnDPgZAV9V3YJ5oSCioWbuNdRsaVP3Q3BhlQ%3d%3d
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: ASP.NET_SessionId=4erkecxjowg2tfpaf3xzid31; __RequestVerificationToken=Zabx_NvFSZWF43kAlid_MiJ1jqZgzbrpeEBmxPc8qW5OVNw4kQDiu8p20r48sAGw37elnoyJ8-elLKZ1oDLN-oS7L8Q1; .ASPXFORMSAUTH=0EF07629CB4FCC96FFB47FEF82BC74CFA51974753C2F481FA86AD3CBDB37593BC4A3A8BA020685E688679CEC7DD67D6499E28F30F829D1DDAB37F8CC7EE74A0B56E6C5C1900699A9B6A88D544F3F91845F1967CBFECA2D5BDA5A8F09EA9B8AF3AE857A25DF2D1BA1B34558D96608C13ECD1C64A6D78A711C701A749805D6CE7518B979E12E9365435D583EBF06EFAB27D6750814; _gat=1; _ga=GA1.2.550487300.1512549105; _gid=GA1.2.530969408.1525334275

# 错误1：
GET https://ita.secureaccountaccess.com/Policy?eq=EbEeZEkUitchES6RUbJFHCgFuNaifvsMBEDAKJnmwAGH7TFiViSxns3hc3AoDZzC8yQyAbShjriQRw0fOL06DcOtQwbv0voPdjiwVPtpFgkyDtxVPi90b75PtBU9RfOhr7Es2Hi0VEfU7XZAG7DT2w%3d%3d HTTP/1.1
Host: ita.secureaccountaccess.com
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
referer: https://ita.secureaccountaccess.com/Introducer/StandardQueries?eq=EbEeZEkUitesY5kFbk4iqNhU4UELGBDW1AN0yRMwFF0hja2NPYdOgl6UsWnQVCuq8yQyAbShjriQRw0fOL06DcOtQwbv0voPdjiwVPtpFgkyDtxVPi90b75PtBU9RfOhr7Es2Hi0VEezeVwq6Fh6eg%3d%3d
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie: .ASPXFORMSAUTH=4A8843987D6D0EB39C608A6794534730DDF8512651A3506C76657D926BC9935D7C50ED0026957031617E4964EEE8FA11CE57488EA7BB5160E5A800CE0BDEEA863D3ED0C3670047BBCFD571EB8137B05F6C6C75C5AC3902E3C786F3C46C203802B167020EAE0824C068FF9F70CA173EBEA125B037E95880C50640EDD3CEC62330E0C7E9DBFAE55EC41CBCFE96AE9CB8164B976DB7; ASP.NET_SessionId=b535qrj0pao2ilsiyr5fnxlq; __RequestVerificationToken=pgvaActll6QunA8oSgLUN46N5qkkllgylQYGd7vc1Dki3iHCUt0st8iB8YuMD7jU-7nSTmApqhza2JwFoC8wKgnFwf01

# 错误2
GET https://ita.secureaccountaccess.com/Policy?eq=ke4Np8YZCEtaB%2fIpBAoMzChCFg1o2vrW2jVj%2bo7SFvp9jXfn8On2JGFrkUtgo%2feJjW4mS1mMk7lqCwBSw8LyY2kUFJQM5HKBBr6hTby5fJqks7cHAQfc1BH7p0zoybl1kKpuyOy%2fwpmr4OPt8UhSLw%3d%3d HTTP/1.1
Host: ita.secureaccountaccess.com
user-agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
accept-encoding: gzip, deflate, br
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Connection: keep-alive
authority: ita.secureaccountaccess.com
method: GET
path: /Account/Login?ReturnUrl=%2f
scheme: https
accept-language: zh-CN,zh;q=0.9
cache-control: max-age=0
referer: https://ita.secureaccountaccess.com/Introducer/StandardQueries?eq=ke4Np8YZCEuNtPzqOY%2fwU6QfmzcFu51f7i7yrDgIgTgOntdEOHKhmoK7mQIbqxSZjW4mS1mMk7lqCwBSw8LyY2kUFJQM5HKBBr6hTby5fJqks7cHAQfc1BH7p0zoybl1kKpuyOy%2fwpkPGc9qA4zOtQ%3d%3d
upgrade-insecure-requests: 1
Cookie: .ASPXFORMSAUTH=ED7ABE75632CCE837F8BC34619FF704EDE6A82BB42F9AB6F481BBA58FB21F4F36678CB5699F2DEC2889174E9F67318467FBB0035F7219EC689528040529D79DB72798E9FF4C454349BB3F6D29CA760033F92A252A97F45CE107D610346BF4025BD624ED82B341FF7C9B67E157FDA2D6BDF2864D62F2B3EF0D6521BA0304C8A0A039138174B01335B660A152B15DD0CA139439502; ASP.NET_SessionId=o1512bine35atzjec5lxg5ve; __RequestVerificationToken=89izMlyNIexUsZJ2ihSDoXLu3ydBl8Gpkrsv8yxPLxRmxyS04CXI5BLoaYKxp1M57qYXRGmKxAuhAGdi5zP22EEY83A1


"""
