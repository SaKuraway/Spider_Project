import requests


class JingLiRenSpider(object):
    def __init__(self, url):
        self.url = url
        print("start..")

    def start_work(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.howbuy.com",
            "Referer": "https://www.baidu.com/link?url=ntcH0Gb0KzPdSoCGMKXiY71Yp_4mjF9Eku2wMhJ3tNp_hMMlJY6lFxrnBiXD4ExP&ck=4040.4.112.385.162.435.158.472&shh=www.baidu.com&sht=baiduhome_pg&wd=&eqid=9f370c5f00032460000000065a042bee",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        }
        # formdata = {
        #     "index": "1510208904",
        # }
        # proxies = {
        #     "http": "192.168.100.113:8888",
        #     "https": "192.168.100.113:8888",
        # }
        print("running..")
        response = requests.post(url=self.url, params=None, headers=headers)  # ,proxies = proxies
        html = response.content
        print('状态码：', response.status_code)
        print('返回结果：', html.decode())

        #     self.save_files(html)
        #
        # def save_files(self, html):
        #     print("printing")
        #     with open("./taobao_cartshow_HTML/cartshow2.html", 'wb') as f:
        #         f.write(html)
        #         print('ok')


if __name__ == '__main__':
    url = "https://www.howbuy.com/fund/manager/"
    jueCeBaoSpider = JingLiRenSpider(url)
    jueCeBaoSpider.start_work()
