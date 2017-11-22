import requests


class JueCeBaoSpider(object):
    def __init__(self, url):
        self.url = url
        print("start..")

    def start_work(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; SBM302SH Build/S0014) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, sdch",
            # "Accept-Language": "zh-CN,zh;q=0.8",
            # "Cache-Control": "max-age=0",
            # "Connection": "keep-alive",
            # "Cookie": "RK=bMV2aj2KfD; pac_uid=1_544538297; tvfe_boss_uuid=7a6b90fda4f0db8d; mobileUV=1_15e364d4304_d713a; pgv_pvi=648893440; ptui_loginuin=544538297; o_cookie=544538297; ptcz=f2fe79bfbbce6b31e3fc8c8d6af9be34c653936e4c8de1bf2f0432044b813f42; pt2gguin=o0544538297; pgv_pvid=486272310",
            # "Host": "pingma.qq.com",
            # "Upgrade-Insecure-Requests": "1",
        }
        formdata = {
            "index": "1510208904",
        }
        # proxies = {
        #     "http": "192.168.100.113:8888",
        #     "https": "192.168.100.113:8888",
        # }
        print("running..")
        response = requests.post(url=self.url, params=None, data=formdata, headers=headers)  # ,proxies = proxies
        html = response.content
        print('状态码：',response.status_code)
        print('返回结果：',html.decode())

        #     self.save_files(html)
        #
        # def save_files(self, html):
        #     print("printing")
        #     with open("./taobao_cartshow_HTML/cartshow2.html", 'wb') as f:
        #         f.write(html)
        #         print('ok')


if __name__ == '__main__':
    url = "http://pingma.qq.com/mstat/report/?index=1510208904"
    jueCeBaoSpider = JueCeBaoSpider(url)
    jueCeBaoSpider.start_work()
