#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-01-26
import  pandas as pd
import numpy as np
import pymysql as DB
import datetime
from matplotlib import pyplot as plt

conn = DB.connect(host='120.55.96.145',user = 'plandev',passwd = 'planner1105',db='data_finance',charset='utf8')
cursor = conn.cursor()
cursor.execute("SELECT * FROM history_nav WHERE Fund_code = '050002' AND History_NAV_Date>='2016-06-15' ORDER BY History_NAV_Date")
datas = cursor.fetchall()
date_index = []




Switch_dates = ['2016-06-15','2016-08-04','2016-08-22','2017-01-12','2017-10-17','2018-03-26',datas[-1][2]]
labels = ['Plan01','Plan02','Plan03','Plan04','Plan05','Plan06','Plan07','Plan08','Plan09','Plan10']
# Switch_dates = ['2016-06-15','2016-08-04','2016-08-22',datas[-2][2]]
Fund_codes =[['000290','000311','000614','118002','270042','519696'],
             ['000217','000834','001426','001593','002393','096001','270049'],
             ['000217','000834','001426','001593','002393','096001','270049'],
             ['000509','000834','001426','002393','096001','270049','539001'],
             ['539001','486002','002393','000509','096001','001061','000834'],
             ['001061','002393','539001','486002','000834','000509','096001']]
# Fund_codes = [['000290','000311','000614','118002','270042','519696'],['000217','000834','001426','001593','002393','096001','270049'],['000217','000834','001426','001593','002393','096001','270049']]
Percents = [
            [[0.50,0.05,0.06,0.13,0.15,0.11],[0.05,0.12,0.15,0.11,0.16,0.09,0.32],[0.05,0.09,0.08,0.06,0.30,0.07,0.35],[0.15,0.10,0.09,0.10,0.12,0.32,0.12],[0.12,0.10,0.05,0.15,0.12,0.36,0.10],[0.36,0.05,0.12,0.10,0.05,0.25,0.07]],
            [[0.44,0.05,0.06,0.15,0.18,0.12],[0.05,0.10,0.14,0.10,0.17,0.08,0.36],[0.05,0.09,0.09,0.08,0.28,0.09,0.32],[0.14,0.12,0.10,0.10,0.12,0.30,0.12],[0.12,0.10,0.05,0.14,0.12,0.35,0.12],[0.35,0.05,0.12,0.10,0.07,0.24,0.07]],
            [[0.40,0.06,0.06,0.16,0.18,0.14],[0.05,0.19,0.21,0.15,0.08,0.19,0.13],[0.05,0.10,0.10,0.10,0.26,0.10,0.29],[0.13,0.13,0.11,0.10,0.15,0.25,0.13],[0.13,0.11,0.05,0.13,0.15,0.30,0.13],[0.30,0.05,0.13,0.11,0.08,0.23,0.10]],
            [[0.36,0.07,0.08,0.16,0.19,0.14],[0.21,0.18,0.10,0.14,0.17,0.15,0.05],[0.05,0.11,0.11,0.11,0.23,0.12,0.27],[0.12,0.14,0.12,0.10,0.16,0.22,0.14],[0.14,0.12,0.05,0.12,0.16,0.27,0.14],[0.27,0.05,0.14,0.12,0.09,0.22,0.11]],
            [[0.30,0.10,0.08,0.17,0.20,0.15],[0.05,0.18,0.18,0.14,0.12,0.16,0.17],[0.05,0.12,0.12,0.12,0.21,0.14,0.24],[0.11,0.16,0.13,0.10,0.20,0.15,0.15],[0.15,0.13,0.05,0.11,0.20,0.20,0.16],[0.20,0.05,0.15,0.13,0.11,0.21,0.15]],
            [[0.27,0.10,0.08,0.19,0.21,0.15],[0.05,0.16,0.17,0.13,0.15,0.13,0.21],[0.05,0.13,0.14,0.13,0.18,0.15,0.22],[0.10,0.16,0.14,0.08,0.24,0.13,0.15],[0.15,0.14,0.05,0.10,0.24,0.16,0.16],[0.16,0.05,0.15,0.14,0.11,0.20,0.19]],
            [[0.23,0.12,0.09,0.18,0.22,0.16],[0.05,0.14,0.17,0.13,0.15,0.11,0.25],[0.05,0.15,0.15,0.15,0.15,0.16,0.19],[0.09,0.19,0.14,0.06,0.27,0.10,0.15],[0.15,0.14,0.05,0.09,0.27,0.11,0.19],[0.11,0.05,0.15,0.14,0.14,0.19,0.22]],
            [[0.18,0.13,0.12,0.20,0.22,0.15],[0.05,0.16,0.15,0.11,0.16,0.09,0.28],[0.05,0.17,0.17,0.16,0.12,0.17,0.16],[0.09,0.19,0.15,0.06,0.25,0.10,0.16],[0.15,0.15,0.05,0.09,0.25,0.11,0.20],[0.11,0.05,0.15,0.15,0.15,0.19,0.20]],
            [[0.16,0.14,0.10,0.21,0.24,0.15],[0.05,0.20,0.20,0.20,0.05,0.20,0.10],[0.05,0.19,0.19,0.18,0.08,0.18,0.13],[0.08,0.20,0.15,0.05,0.27,0.10,0.15],[0.17,0.15,0.00,0.08,0.27,0.13,0.20],[0.13,0.00,0.17,0.15,0.15,0.18,0.22]],
            [[0.15,0.16,0.10,0.21,0.25,0.13],[0.05,0.21,0.20,0.18,0.07,0.19,0.10],[0.05,0.20,0.20,0.20,0.05,0.20,0.10],[0.08,0.21,0.15,0.05,0.28,0.10,0.13],[0.17,0.15,0.00,0.08,0.30,0.10,0.20],[0.10,0.00,0.17,0.15,0.15,0.18,0.25]]

            ]
# Percents = [[[0.44,0.05,0.06,0.15,0.18,0.12],[0.05,0.10,0.14,0.10,0.17,0.08,0.36],[0.05,0.09,0.09,0.08,0.28,0.09,0.32]]]
df_list=[]
def yesterday(date_index,str_date):
    c = date_index[date_index.index(datetime.datetime.strptime(str_date, "%Y-%m-%d").date()) - 1].strftime("%Y-%m-%d")
    return c

for i in range(0,len(datas)):
    date_index.append(datetime.datetime.strptime(datas[i][2], "%Y-%m-%d").date())
for i in range(0,len(Switch_dates)-1):
    df_agg = pd.DataFrame(index = date_index[date_index.index(datetime.datetime.strptime(Switch_dates[i], "%Y-%m-%d").date()):])
    for p in range(0,len(Fund_codes[i])):
    # for Fund_code in Fund_codes:
        cursor.execute("SELECT * FROM history_nav WHERE Fund_code = '"+Fund_codes[i][p]+"' AND History_NAV_Date>='"+Switch_dates[i]+"'ORDER BY History_NAV_Date")
        datas = cursor.fetchall()

        index = []
        price = []
        for data in datas:
            index.append(datetime.datetime.strptime(data[2], "%Y-%m-%d").date())
            price.append(float(data[4]))
        df = pd.DataFrame(price,index = index ,columns=[Fund_codes[i][p]])
        df_agg = df_agg.join(df)
    while df_agg.iloc[-1].count()!=len(df_agg.columns) and i == len(Switch_dates)-1:
        print('the last day have no data')
        print(df_agg)
        df_agg = df_agg.iloc[0:-1]
    df_agg = df_agg.fillna(method = 'pad')
    df_list.append(df_agg)
print(df_list,len(df_list[0]))


df_price_agg = pd.DataFrame(index = date_index)
for p in range(len(Percents)):
    df_price = pd.DataFrame()
    a = 1
    for i in range(0,len(Switch_dates)-1):
        date1 = datetime.datetime.strptime(Switch_dates[i], "%Y-%m-%d").date()
        date2 = datetime.datetime.strptime(Switch_dates[i+1], "%Y-%m-%d").date()
        df = df_list[i]
        # df = df[:date2-datetime.timedelta(days = 1)]
        df = df[:date2]
        shares = np.array(Percents[p][i])*a/np.array(df.iloc[0])
        array = np.array(df.iloc[1:])
        print(len(array))
        # print(array)
        # print(shares)
        # array = np.reshape(array,(len(array[0]),len(array)))
        prices = np.sum(shares*array,axis=1)
        # prices = np.dot(shares , array.T)
        # print(prices)
        # prices = np.dot(shares,array)
        index = date_index[date_index.index(date1)+1:date_index.index(date2)+1]
        price = prices
        print(index, price)
        df = pd.DataFrame(price,index = index,columns=[labels[p]])
        a = price[-1]
        # print(df)
        df_price = df_price.append(df)
        # print(df_price)
    df_price_agg = df_price_agg.join(df_price)
    print(df_price_agg)
df_price_agg.iloc[0] = [1,1,1,1,1,1,1,1,1,1]
print(df_price_agg.loc[datetime.date(2017,9,29):datetime.date(2017,11,1)])

# upload to mysql.
for column in df_price_agg.columns.tolist():
    cursor.execute("select History_NAV_Date from History_NAV where Fund_code=" + "'" + column + "'" + ";")
    existed_date = [date[0] for date in cursor.fetchall()]
    print(column, 'existed_date:', existed_date)
    for i in df_price_agg.index.tolist():
        if str(df_price_agg.loc[i, column]) != 'nan' and str(i) not in existed_date:
            cursor.execute("insert into History_NAV(Fund_Code,History_NAV_Date,ANAV) VALUE (%s,%s,%s)",(str(column), str(i), float(df_price_agg.loc[i, column])))
            print("insert into History_NAV(Fund_Code,History_NAV_Date,ANAV) VALUE (%s,%s,%s)",(str(column), str(i), float(df_price_agg.loc[i, column])))

plt_date = datetime.date(2016,6,15)
df_price_agg = df_price_agg.ix[plt_date:]
fig,ax = plt.subplots()
ax.yaxis.grid(True,which='major')
for i in range(0,10):
    ax.plot(df_price_agg.index, np.array(df_price_agg[labels[i]]),label=labels[i])
ax.legend()
plt.show()
conn.commit()
cursor.close()
conn.close()