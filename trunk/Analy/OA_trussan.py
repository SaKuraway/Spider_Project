from requests import session
from time import sleep

status = int(input("请输入打卡的类型（1是上班，2是下班，3是更新下班时间）："))
# 请求参数等：
login_url = 'http://oa.trussan.com/mobile/login.php'
workon_url = 'http://oa.trussan.com/pda/attendance/sign/data.php?action=myattend&type=0&state=1&dutyid=1&coor_id=49'
workoff_url = 'http://oa.trussan.com/pda/attendance/sign/data.php?action=myattend&type=0&state=2&m_id=21498&coor_id=49&dutyid=1'
workoff_update_url = 'http://oa.trussan.com/pda/attendance/sign/data.php?action=upattend&type=0&state=2&m_id=21498&coor_id=49&dutyid=1'
login_headers = {
    "Content-Type":"application/x-www-form-urlencoded",
    "Content-Length":"140",
    "Host":"oa.trussan.com",
    "Connection":"Keep-Alive",
    "Accept-Encoding":"gzip",
    "User-Agent":"okhttp/3.10.0",
}
attend_headers = {
    "Host":"oa.trussan.com",
    "Connection":"keep-alive",
    "Pragma":"no-cache",
    "Cache-Control":"no-cache",
    "User-Agent":"Mozilla/5.0 (Linux; Android 8.1.0; vivo Z1 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36",
    "X-Requested-With":"XMLHttpRequest",
    "Accept":"*/*",
    "Referer":"http://oa.trussan.com/pda/attendance/sign/index.php",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"zh-CN,en-US;q=0.9",
    # "Cookie":"PHPSESSID=ffqa77hl8movv9gukihptharj6; C_VER=20180702"
}
login_formdata = {
    "MOBIL_NO":"+8613265167607",
    "PASSWORD":"Q2JjX18xMjM=",# Q2JjX18xMjM%3D%0A
    "P_VER":"6",
    "DEVICE_NUMBER":"869402032340919",
    "USERNAME":"13265167607",
    "C_VER":"20180702",
    "encode_type":"1"
}

# session_requests
ssion = session()
# 登录
print(ssion.post(url=login_url,headers=login_headers,data=login_formdata).text,'\nlogin..')
sleep(8)
# 打卡
print('开始打卡..')
if status == 1:
    print(ssion.get(url=workon_url, headers=attend_headers).text)
elif status == 2:
    print(ssion.get(url=workoff_url, headers=attend_headers).text)
elif status == 3:
    print(ssion.get(url=workoff_update_url, headers=attend_headers).text)
else:
    print("error!请输入打卡的类型！")

print('over!')