import requests,pymysql
from PIL import Image
from lxml import etree

class MorningStarSpider(object):

    def __init__(self):
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                        database='data_finance_oversea', charset='utf8')
        self.cur = self.mysql_client.cursor()
        self.cur.execute("SELECT isin from funds_isin;")
        isin_tuple = self.cur.fetchall()
        all_search_url = ['http://www.morningstar.co.uk/uk/funds/SecuritySearchResults.aspx?search=' + str(ISIN[0]) for ISIN in isin_tuple]

        self.headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.9",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            # "Cookie":"cookies=true; cookies=true; RT_uk_LANG=en-GB; __utmz=192614060.1533181618.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); uk-AudeniceTypeBackFill-hasShown=true; ad-profile=%7b%22AudienceType%22%3a6%2c%22UserType%22%3a0%2c%22PortofolioCreated%22%3a0%2c%22IsForObsr%22%3afalse%2c%22NeedRefresh%22%3atrue%2c%22NeedPopupAudienceBackfill%22%3afalse%2c%22EnableInvestmentInUK%22%3a1%7d; _evidon_consent_cookie={"vendors":{"10":[60,82,167,174,242,249,479,2449,2858]},"consent_date":"2018-08-02T03:47:14.908Z"}; ASP.NET_SessionId=ncfrq2bfslgqcw2gueyeveij; __utmc=192614060; HPTopAd_uk=no; BackButton_=goBackCount=-1&backButtonLabel=; __utma=192614060.1261565156.1533181618.1534904278.1535012159.3; __utmb=192614060.2.10.1535012159; uk-OrdinalOfPages=3",
            "Host":"www.morningstar.co.uk",
            "Referer":"http://www.morningstar.co.uk/",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        for start_url in all_search_url:
            ssion = requests.session()
            response = etree.HTML(ssion.get(start_url,headers=self.headers).text)
            item = {}
            try:
                spider_url = 'http://www.morningstar.co.uk/' + response.xpath(
                    "//tr[@class='gridItem']/td[@class='msDataText searchLink']/a/@href")[0]
            except:
                print('error,skip!url:', response.url)
            else:
                self.funds_information(ssion,spider_url,item)

    def funds_information(self,ssion,spider_url,item):
        response = etree.HTML(ssion.get(spider_url,headers = self.headers).text)
        # xxx = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''

        for index,title in enumerate(response.xpath("//div[@id='mainContentDiv']//tr/td[@class='line heading']/text()")):
            spider_index = str(index + 2)
            if title == 'ISIN': # index = 5 , position = 4 ,
                item['ISIN'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n', '')
            elif title == 'Morningstar Category™':
                item['category'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line value text']//text()")).strip().replace('\n', '')
            elif title == 'Fund Size (Mil)':
                item['fund_size_mil'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n','')[4:]
            elif title == 'Share Class Size (Mil)':
                item['share_class_size'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n','')[4:]
            elif title == 'NAV':
                item['currency'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n','')[:3]
            elif title == 'Max Initial Charge':
                item['max_initial_charge'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n','')[:3]
            elif title == 'Ongoing Charge':
                item['ongoing_charge'] = ''.join(response.xpath("//div[@id='mainContentDiv']//tr["+spider_index+"]/td[@class='line text']//text()")).strip().replace('\n','')[:3]

        item['fund_benchmark'] = ''.join(response.xpath("//tr[7]/td[@class='footer']/span[@class='value']//text()")).strip().replace('\n','')
        item['style_box_src'] = 'http://www.morningstar.co.uk'+response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src")[0] if response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src") else ''
        if response.xpath("//div[@id='overviewPortfolioEquityStyleDiv']//tr[1]/td[1]/img/@src"):
            style_box_img = requests.get(item['style_box_src']).content
            with open(str(item['ISIN'])+'_StyleBox.gif','wb') as f:
                f.write(style_box_img)
            f.close()
            img = Image.open(str(item['ISIN'])+'_StyleBox.gif')
            img_1 = img.convert("1")
            img_1_rgb = img_1.convert("RGB")
            width = img.size[0]
            height = img.size[1]
            # print(width, height)
            item['style_box'] = ''
            for x in range(width):
                for y in range(height):
                    r, g, b = img_1_rgb.getpixel((x, y))
                    if x == int(width / 3 / 2) and y == int(height / 3 / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Large'
                        item['style'] = 'Value'
                        break
                    elif x == int(width / 2) and y == int(height / 3 / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Large'
                        item['style'] = 'Blend'
                        break
                    elif x == int(width * 5 / 6) and y == int(height / 3 / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Large'
                        item['style'] = 'Growth'
                        break
                    elif x == int(width / 3 / 2) and y == int(height / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Mid'
                        item['style'] = 'Value'
                        break
                    elif x == int(width / 2) and y == int(height / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Mid'
                        item['style'] = 'Blend'
                        break
                    elif x == int(width * 5 / 6) and y == int(height / 2) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Mid'
                        item['style'] = 'Growth'
                        break
                    elif x == int(width / 3 / 2) and y == int(height * 5 / 6) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Small'
                        item['style'] = 'Value'
                        break
                    elif x == int(width / 2) and y == int(height * 5 / 6) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Small'
                        item['style'] = 'Blend'
                        break
                    elif x == int(width * 5 / 6) and y == int(height * 5 / 6) and r == 0 and g == 0 and b == 0:
                        item['cap'] = 'Small'
                        item['style'] = 'Growth'
                        break
                    else:
                        # print('None')
                        continue

            # print('Style-Box：', item['style_box'])

        item['stock_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][1]//text()")).strip().replace('\n','')
        item['stock_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][2]//text()")).strip().replace('\n','')
        item['stock_net'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[4]/td[@class='value number'][3]//text()")).strip().replace('\n','')
        item['bond_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][1]//text()")).strip().replace('\n','')
        item['bond_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][2]//text()")).strip().replace('\n','')
        item['bond_net'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[5]/td[@class='value number'][3]//text()")).strip().replace('\n','')
        item['property_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][1]//text()")).strip().replace('\n','')
        item['property_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][2]//text()")).strip().replace('\n','')
        item['property_net'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[6]/td[@class='value number'][3]//text()")).strip().replace('\n','')
        item['cash_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][1]//text()")).strip().replace('\n','')
        item['cash_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][2]//text()")).strip().replace('\n','')
        item['cash_net'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[7]/td[@class='value number'][3]//text()")).strip().replace('\n','')
        item['other_long'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][1]//text()")).strip().replace('\n','')
        item['other_short'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][2]//text()")).strip().replace('\n','')
        item['other_net'] = ''.join(response.xpath("//div[@id='overviewPortfolioAssetAllocationDiv']//tr[8]/td[@class='value number'][3]//text()")).strip().replace('\n','')


















        fund_name = response.xpath("//div[@class='snapshotTitleBox']/h1//text()")[0].strip().replace('\n','') if response.xpath("//div[@class='snapshotTitleBox']/h1") else ''
        isin = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        category = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        fund_size_Mil = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        share_class_size = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        currency = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        max_initial_charge = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        ongoing_charge = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        inception_date = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        fund_benchmark = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        cap = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''
        style = response.xpath("")[0].strip().replace('\n','') if response.xpath("") else ''

