import os,time

from scrapy import cmdline
# cmdline.execute("scrapy crawl tiantian_jijin".split())

while True:
    os.system("scrapy crawl tiantian_jijin")
    time.sleep(100000)  #每隔一天2小时运行一次 27*60*60≈100000s

