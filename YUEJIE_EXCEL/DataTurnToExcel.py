# -*-coding:utf-8-*-
# 有序字典模块
import collections
import os, pymysql, datetime, pandas as pd
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf
import Hansard_to_excel
import ITA_to_excel
import AXA_to_excel
import ZURICH_to_excel
import SLA_to_excel

# .YueJie_To_Excel
# .Csv_To_Excel
# class Hansard_Mysql_To_Excel(object):
#     def __init__(self, sheet_name):
#         self.sheet_name = sheet_name
#         # 指定mysql数据库
#         self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
#                                             database='statement', charset='utf8')
#         self.month = int(input("请输入月份："))
#         self.excel_name = './Excel/' + str(input("请输入需要录入的Excel表格名字：")) + '.xlsx'
#         # self.excel_name = './Excel/' + "客户名单" + '.xls'
#
#         excel_name = self.excel_name
#         excel_content = open_workbook(excel_name, formatting_info=False)
#         self.new_xls_file = copy(excel_content)
#         if not self.sheet_name:
#             print('保费')
#             self.sheet = self.new_xls_file.get_sheet(0)
#         else:
#             print('价值')
#             self.sheet = self.new_xls_file.get_sheet(1)
#
#     def charge_weekday(self, year=2017):
#         month = self.month
#         index = 3
#         excel_day_row = collections.OrderedDict()  # 有序字典
#         try:
#             for day in range(1, 32):
#                 if int(datetime.datetime(year, month, day).strftime("%w")) in range(1, 6):
#                     if day < 10:
#                         day = '0' + str(day)
#                     excel_day_row[str(year) + '-' + str(month) + '-' + str(day)] = index
#                     # print(year,month,day)
#                     index += 1
#         except:
#             pass
#         # print(excel_day_row)
#         return excel_day_row
#
#     def read_from_mysql(self):
#         # 获得Cursor对象
#         cur = self.mysql_client.cursor()
#         # 执行select语句，并返回受影响的行数：
#         if not self.sheet_name:
#             # 0.hansard保费部分
#             print('保费')
#             count = cur.execute(
#                 "SELECT policy_no,date,value FROM tb_premium WHERE date>='2017-11-30' AND policy_no LIKE '5%'")
#             # 2.ITA保费部分
#             # count = cur.execute("SELECT policy_no,date,value FROM tb_premium_test WHERE date>='2017-11-30'")
#         else:
#             # 1.hansard价值部分
#             print('价值')
#             count = cur.execute(
#                 "SELECT policy_no,price_date,SUM(value2) from tb_allocation WHERE date>='2017-12-01' AND policy_no LIKE '5%' GROUP BY policy_no")
#             # 3.ITA价值部分
#             # count = cur.execute("SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T%' AND date='2017-12-01'")
#         # 获取查询的结果
#         result = cur.fetchall()
#         # result = [('565374G','2017-12-29',37706.19),('565390K','2017-12-29',9047.62),('565412B','2017-12-29',17563.84),('565424F','2017-12-29',21971.73),('565428V','2017-12-29',24937.28),('565437U','2017-12-29',10187.15),('565447F','2017-12-29',10466.11),('565449A','2017-12-29',8796.64),('565452M','2017-12-28',9952.91)]
#         # 打印查询的结果
#         for policy, date, value in result:
#             # print(type(policy),type(date),type(value))
#             print(policy, date, value)
#             self.read_from_excel(policy, str(date), value)
#         # 关闭Cursor对象
#         cur.close()
#
#     def read_from_excel(self, policy, mysql_date, value):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         # print(excel_data)
#         policy_index = 'unexist!'
#         orignal_value = 'unexist!'
#         try:
#             policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
#             orignal_value = int(excel_data.iloc[policy_index, 2])
#             print('policy_index,orignal_value:', policy_index + 2, orignal_value)
#             weekday = self.charge_weekday()
#             while mysql_date not in weekday.keys():
#                 if mysql_date == '2017-11-30':
#                     mysql_date = '2017-12-01'
#                     break
#                 mysql_date = mysql_date[:-2] + str(int(mysql_date[-2:]) - 1) if int(
#                     mysql_date[-2:]) > 10 else mysql_date[:-2] + '0' + str(int(mysql_date[-2:]) - 1)
#             date_col = weekday[str(mysql_date)]
#             message = orignal_value + int(value)
#             print('date_col,message:', date_col, message)
#             if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
#                 for col in range(3, date_col):
#                     self.write_to_excel(policy_index, col, orignal_value)
#                     print('col1,orignal_value:', col, orignal_value)
#             else:
#                 message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
#             for col in range(date_col, 24):
#                 self.write_to_excel(policy_index, col, message)
#                 print('col2,message:', col, message)
#         except Exception as e:
#             print('error!:', e)
#             with open('error.txt', 'a', encoding='utf-8') as f:
#                 f.write(str(policy) + str(mysql_date) + str(value) + '\r\n')
#                 # reset_col = 3
#                 # self.write_to_excel(-1, 2, '2017-11-30')
#                 # for key,value in weekday.items():
#                 #     self.write_to_excel(-1, reset_col, key)
#                 #     reset_col += 1
#
#     def write_to_excel(self, policy_index, date_col, message):
#         """
#         写入调仓情况信息
#         :param message:
#         :return: No
#         """
#         policy_row = policy_index + 1
#         # excel_name = self.excel_name
#         # excel_content = open_workbook(excel_name, formatting_info=False)
#         # new_xls_file = copy(excel_content)
#         # if not self.sheet_name:
#         #     print('保费')
#         #     sheet = new_xls_file.get_sheet(0)
#         # else:
#         #     print('价值')
#         #     sheet = new_xls_file.get_sheet(1)
#         self.sheet.write(policy_row, date_col, message)
#         # print('writed!')
#         # os.rename(excel_name, './Excel/old_客户名单.xls')
#         # new_xls_file.save(excel_name)
#         # # print('saved')
#         # os.remove('./Excel/old_客户名单.xls')
#         # print('deleted')
#
#     def save_excel(self):
#         excel_name = self.excel_name
#         os.rename(excel_name, './Excel/old_客户名单.xls')
#         self.new_xls_file.save(excel_name)
#         # print('saved')
#         os.remove('./Excel/old_客户名单.xls')
#
#     def fill_by_excel(self):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         fill_index = excel_data[excel_data.iloc[:, 3] == 0].index.tolist()
#         for index in fill_index:
#             try:
#                 if not 500000 <= int(str(excel_data.loc[index, 'Policy Number'])[:-1]) <= 600000:
#                     continue
#                 print('填充无缴费保单ing：', excel_data.loc[index, 'Policy Number'])
#                 orignal_value = excel_data.iloc[index, 2]
#                 for date_col in range(3, 24):
#                     self.write_to_excel(index, date_col, orignal_value)
#                 self.save_excel()
#             except:
#                 pass
#
#     def adjust_date_col(self):
#         weekday = self.charge_weekday()
#         reset_col = 3
#         self.write_to_excel(-1, 2, '2017-11-30')
#         for key, value in weekday.items():
#             self.write_to_excel(-1, reset_col, key)
#             reset_col += 1
#         self.save_excel()
#
#
# class ITA_Mysql_To_Excel(object):
#     def __init__(self, sheet_name):
#         self.sheet_name = sheet_name
#         # 指定mysql数据库
#         self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
#                                             database='statement', charset='utf8')
#         self.month = int(input("请输入月份："))
#         self.excel_name = './Excel/' + str(input("请输入需要录入的Excel表格名字：")) + '.xlsx'
#         # self.excel_name = './Excel/' + "客户名单" + '.xls'
#
#         excel_name = self.excel_name
#         excel_content = open_workbook(excel_name, formatting_info=False)
#         self.new_xls_file = copy(excel_content)
#         if not self.sheet_name:
#             print('保费')
#             self.sheet = self.new_xls_file.get_sheet(0)
#         else:
#             print('价值')
#             self.sheet = self.new_xls_file.get_sheet(1)
#
#     def charge_weekday(self, year=2017):
#         month = self.month
#         index = 3
#         excel_day_row = collections.OrderedDict()  # 有序字典
#         try:
#             for day in range(1, 32):
#                 if int(datetime.datetime(year, month, day).strftime("%w")) in range(1, 6):
#                     if day < 10:
#                         day = '0' + str(day)
#                     excel_day_row[str(year) + '-' + str(month) + '-' + str(day)] = index
#                     # print(year,month,day)
#                     index += 1
#         except:
#             pass
#         # print(excel_day_row)
#         return excel_day_row
#
#     def read_from_mysql(self):
#         # 获得Cursor对象
#         cur = self.mysql_client.cursor()
#         # 执行select语句，并返回受影响的行数：
#         if not self.sheet_name:
#             # 0.hansard保费部分
#             print('保费')
#             # count = cur.execute(
#             #     "SELECT policy_no,date,value FROM tb_premium WHERE date>='2017-11-30' AND policy_no LIKE '5%'")
#             # 2.ITA保费部分
#             count = cur.execute("SELECT policy_no,date,value FROM tb_premium_test WHERE date>='2017-11-30'")
#         else:
#             # 1.hansard价值部分
#             print('价值')
#             # count = cur.execute(
#             #     "SELECT policy_no,price_date,SUM(value2) from tb_allocation WHERE date>='2017-12-01' AND policy_no LIKE '5%' GROUP BY policy_no")
#             # 3.ITA价值部分
#             count = cur.execute(
#                 "SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T%' AND date='2017-12-01'")
#         # 获取查询的结果
#         result = cur.fetchall()
#         # result = [('565374G','2017-12-29',37706.19),('565390K','2017-12-29',9047.62),('565412B','2017-12-29',17563.84),('565424F','2017-12-29',21971.73),('565428V','2017-12-29',24937.28),('565437U','2017-12-29',10187.15),('565447F','2017-12-29',10466.11),('565449A','2017-12-29',8796.64),('565452M','2017-12-28',9952.91)]
#         # 打印查询的结果
#         for policy, date, value in result:
#             # print(type(policy),type(date),type(value))
#             print(policy, date, value)
#             self.read_from_excel(policy, str(date), value)
#         # 关闭Cursor对象
#         cur.close()
#
#     def read_from_excel(self, policy, mysql_date, value):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         # print(excel_data)
#         policy_index = 'unexist!'
#         orignal_value = 'unexist!'
#         try:
#             policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
#             orignal_value = int(excel_data.iloc[policy_index, 2])
#             print('policy_index,orignal_value:', policy_index + 2, orignal_value)
#             weekday = self.charge_weekday()
#             while mysql_date not in weekday.keys():
#                 if mysql_date == '2017-11-30':
#                     mysql_date = '2017-12-01'
#                     break
#                 mysql_date = mysql_date[:-2] + str(int(mysql_date[-2:]) - 1) if int(
#                     mysql_date[-2:]) > 10 else mysql_date[:-2] + '0' + str(int(mysql_date[-2:]) - 1)
#             date_col = weekday[str(mysql_date)]
#             message = orignal_value + int(value)
#             print('date_col,message:', date_col, message)
#             if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
#                 for col in range(3, date_col):
#                     self.write_to_excel(policy_index, col, orignal_value)
#                     print('col1,orignal_value:', col, orignal_value)
#             else:
#                 message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
#             for col in range(date_col, 24):
#                 self.write_to_excel(policy_index, col, message)
#                 print('col2,message:', col, message)
#         except Exception as e:
#             print('error!:', e)
#             with open('error.txt', 'a', encoding='utf-8') as f:
#                 f.write(str(policy) + str(mysql_date) + str(value) + '\r\n')
#                 # reset_col = 3
#                 # self.write_to_excel(-1, 2, '2017-11-30')
#                 # for key,value in weekday.items():
#                 #     self.write_to_excel(-1, reset_col, key)
#                 #     reset_col += 1
#
#     def write_to_excel(self, policy_index, date_col, message):
#         """
#         写入调仓情况信息
#         :param message:
#         :return: No
#         """
#         policy_row = policy_index + 1
#         # excel_name = self.excel_name
#         # excel_content = open_workbook(excel_name, formatting_info=False)
#         # new_xls_file = copy(excel_content)
#         # if not self.sheet_name:
#         #     print('保费')
#         #     sheet = new_xls_file.get_sheet(0)
#         # else:
#         #     print('价值')
#         #     sheet = new_xls_file.get_sheet(1)
#         self.sheet.write(policy_row, date_col, message)
#         # print('writed!')
#         # os.rename(excel_name, './Excel/old_客户名单.xls')
#         # new_xls_file.save(excel_name)
#         # # print('saved')
#         # os.remove('./Excel/old_客户名单.xls')
#         # print('deleted')
#
#     def save_excel(self):
#         excel_name = self.excel_name
#         os.rename(excel_name, './Excel/old_客户名单.xls')
#         self.new_xls_file.save(excel_name)
#         # print('saved')
#         os.remove('./Excel/old_客户名单.xls')
#
#     def fill_by_excel(self):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         fill_index = excel_data[excel_data.iloc[:, 3] == 0].index.tolist()
#         for index in fill_index:
#             try:
#                 if not 500000 <= int(str(excel_data.loc[index, 'Policy Number'])[:-1]) <= 600000:
#                     continue
#                 print('填充无缴费保单ing：', excel_data.loc[index, 'Policy Number'])
#                 orignal_value = excel_data.iloc[index, 2]
#                 for date_col in range(3, 24):
#                     self.write_to_excel(index, date_col, orignal_value)
#                 self.save_excel()
#             except:
#                 pass
#
#     def adjust_date_col(self):
#         weekday = self.charge_weekday()
#         reset_col = 3
#         self.write_to_excel(-1, 2, '2017-11-30')
#         for key, value in weekday.items():
#             self.write_to_excel(-1, reset_col, key)
#             reset_col += 1
#         self.save_excel()
#
#
# class AXA_Csv_To_Excel(object):
#     def __init__(self, sheet_name):
#         self.sheet_name = sheet_name
#         # 指定mysql数据库
#         self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
#                                             database='statement', charset='utf8')
#         self.month = int(input("请输入月份："))
#         self.excel_name = './Excel/' + str(input("请输入需要录入的Excel表格名字：")) + '.xlsx'
#         # self.excel_name = './Excel/' + "客户名单" + '.xls'
#
#         excel_name = self.excel_name
#         excel_content = open_workbook(excel_name, formatting_info=False)
#         self.new_xls_file = copy(excel_content)
#         if not self.sheet_name:
#             print('保费')
#             self.sheet = self.new_xls_file.get_sheet(0)
#         else:
#             print('价值')
#             self.sheet = self.new_xls_file.get_sheet(1)
#
#     def charge_weekday(self, year=2017):
#         month = self.month
#         index = 3
#         excel_day_row = collections.OrderedDict()  # 有序字典
#         try:
#             for day in range(1, 32):
#                 if int(datetime.datetime(year, month, day).strftime("%w")) in range(1, 6):
#                     if day < 10:
#                         day = '0' + str(day)
#                     excel_day_row[str(year) + '/' + str(month) + '/' + str(day)] = index
#                     # print(year,month,day)
#                     index += 1
#         except:
#             pass
#         # print(excel_day_row)
#         return excel_day_row
#
#     def read_from_csv(self):
#         print('read_from_csv')
#         for csv_date in range(2, 32):
#             try:
#                 if csv_date < 10:
#                     csv_date = '0' + str(csv_date)
#                 csv_data = pd.read_csv('./Excel/policy/axa policy for cbc 201712' + str(csv_date) + '.csv')
#                 result = []
#                 for index in range(csv_data.iloc[:, 0].size):
#                     policy = csv_data.loc[index, ' Policy Number']
#                     date = csv_data.loc[index, ' Valuation Date']
#                     value = csv_data.loc[index, ' Total Premium Paid']
#                     if self.sheet_name == 1:
#                         value = csv_data.loc[index, '\nTotal policy value in policy currency for Linked policy']
#                     # 获取查询的结果
#                     result.append((policy, date, value))
#                     # result = [('562499G','2017-11-30',13333.32),('562499G','2017-12-28',3333.33)]
#                 # 打印查询的结果
#                 for policy, date, value in result:
#                     # print(type(policy),type(date),type(value))
#                     print(policy, date, value)
#                     self.read_from_excel(policy, str(date), value)
#             except:
#                 print('warning or error:', csv_date)
#
#     def read_from_excel(self, policy, csv_date, value):
#         print('read_from_excel')
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             print('价值')
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         # print(excel_data)
#         policy_index = 'unexist!'
#         orignal_value = 'unexist!'
#         try:
#             policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
#             orignal_value = int(excel_data.iloc[policy_index, 2])
#             print('policy_index,orignal_value:', policy_index + 2, orignal_value)
#             weekday = self.charge_weekday()
#             while csv_date not in weekday.keys():
#                 if csv_date == '2017/11/29' or csv_date == '2017/11/30':
#                     csv_date = '2017/12/01'
#                     break
#                 csv_date = csv_date[:-2] + str(int(csv_date[-2:]) - 1) if int(
#                     csv_date[-2:]) > 10 else csv_date[:-2] + '0' + str(int(csv_date[-2:]) - 1)
#             date_col = weekday[str(csv_date)]
#             message = int(value)
#             print('date_col,message:', date_col, message)
#             if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
#                 for col in range(3, date_col):
#                     self.write_to_excel(policy_index, col, orignal_value)
#                     print('col1,orignal_value:', col, orignal_value)
#             # else:
#             #     message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
#             for col in range(date_col, 24):
#                 self.write_to_excel(policy_index, col, message)
#                 print('col2,message:', col, message)
#             self.save_excel()
#         except Exception as e:
#             print('error!:', e)
#             with open('error.txt', 'a', encoding='utf-8') as f:
#                 f.write(str(policy) + str(csv_date) + str(value) + '\r\n')
#                 # reset_col = 3
#                 # self.write_to_excel(-1, 2, '2017-11-30')
#                 # for key,value in weekday.items():
#                 #     self.write_to_excel(-1, reset_col, key)
#                 #     reset_col += 1
#
#     def write_to_excel(self, policy_index, date_col, message):
#         """
#         写入调仓情况信息
#         :param message:
#         :return: No
#         """
#         policy_row = policy_index + 1
#         # excel_name = self.excel_name
#         # excel_content = open_workbook(excel_name, formatting_info=False)
#         # self.new_xls_file = copy(excel_content)
#         # if not self.sheet_name:
#         #     print('保费')
#         #     self.sheet = self.new_xls_file.get_sheet(0)
#         # else:
#         #     print('价值')
#         #     self.sheet = self.new_xls_file.get_sheet(1)
#         self.sheet.write(policy_row, date_col, message)
#         # print('writed!')
#         # os.rename(excel_name, './Excel/old_客户名单.xls')
#         # new_xls_file.save(excel_name)
#         # # print('saved')
#         # os.remove('./Excel/old_客户名单.xls')
#         # print('deleted')
#
#     def save_excel(self):
#         excel_name = self.excel_name
#         os.rename(excel_name, './Excel/old_客户名单.xls')
#         self.new_xls_file.save(excel_name)
#         # print('saved')
#         os.remove('./Excel/old_客户名单.xls')
#
#     def adjust_date_col(self):
#         weekday = self.charge_weekday()
#         reset_col = 3
#         self.write_to_excel(-1, 2, '2017-11-30')
#         for key, value in weekday.items():
#             self.write_to_excel(-1, reset_col, key)
#             reset_col += 1
#         self.save_excel()
#
#
# class Zurich_Csv_To_Excel(object):
#     def __init__(self, sheet_name):
#         self.sheet_name = sheet_name
#         # 指定mysql数据库
#         self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
#                                             database='statement', charset='utf8')
#         self.month = int(input("请输入月份："))
#         self.excel_name = './Excel/' + str(input("请输入需要录入的Excel表格名字：")) + '.xlsx'
#         # self.excel_name = './Excel/' + "客户名单" + '.xls'
#
#         excel_name = self.excel_name
#         excel_content = open_workbook(excel_name, formatting_info=False)
#         self.new_xls_file = copy(excel_content)
#         if not self.sheet_name:
#             print('保费')
#             self.sheet = self.new_xls_file.get_sheet(0)
#         else:
#             print('价值')
#             self.sheet = self.new_xls_file.get_sheet(1)
#
#     def charge_weekday(self, year=2017):
#         month = self.month
#         index = 3
#         excel_day_row = collections.OrderedDict()  # 有序字典
#         try:
#             for day in range(1, 32):
#                 if int(datetime.datetime(year, month, day).strftime("%w")) in range(1, 6):
#                     if day < 10:
#                         day = '0' + str(day)
#                     excel_day_row[str(year) + '/' + str(month) + '/' + str(day)] = index
#                     # print(year,month,day)
#                     index += 1
#         except:
#             pass
#         # print(excel_day_row)
#         return excel_day_row
#
#     def read_from_csv(self):
#         for csv_date in range(1, 32):
#             try:
#                 if csv_date < 10:
#                     csv_date = '0' + str(csv_date)
#                 csv_data = pd.read_csv('./Excel/policy/ZI Policy for cbc 201712' + str(csv_date) + '.csv')
#                 result = []
#                 date = '2017/12/' + str(csv_date)
#                 print(date)
#                 weekday = self.charge_weekday()
#                 if date not in weekday.keys():
#                     continue
#                 for index in range(csv_data.iloc[:, 0].size):
#                     policy = csv_data.loc[index, 'PolicyNum']
#                     value = csv_data.loc[index, 'PremiumsPaidTotal']
#                     if self.sheet_name == 1:
#                         value = csv_data.loc[2, 'Currentfundholding']
#                     # 获取查询的结果
#                     result.append((policy, date, value))
#                     # result = [('562499G','2017-11-30',13333.32),('562499G','2017-12-28',3333.33)]
#                 # 打印查询的结果
#                 for policy, date, value in result:
#                     # print(type(policy),type(date),type(value))
#                     print(policy, date, value)
#                     self.read_from_excel(policy, str(date), value)
#             except Exception as e:
#                 print(e)
#
#     def read_from_excel(self, policy, csv_date, value):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             print('价值')
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         # print(excel_data)
#         policy_index = 'unexist!'
#         orignal_value = 'unexist!'
#         try:
#             policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
#             orignal_value = int(excel_data.iloc[policy_index, 2])
#             print('policy_index,orignal_value:', policy_index + 2, orignal_value)
#             weekday = self.charge_weekday()
#             # while csv_date not in weekday.keys():
#             #     if csv_date == '2017/11/29' or csv_date == '2017/11/30':
#             #         csv_date = '2017/12/01'
#             #         break
#             #     csv_date = csv_date[:-2] + str(int(csv_date[-2:]) - 1) if int(
#             #         csv_date[-2:]) > 10 else csv_date[:-2] + '0' + str(int(csv_date[-2:]) - 1)
#             date_col = weekday[str(csv_date)]
#             message = int(value)
#             print('date_col,message:', date_col, message)
#             if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
#                 for col in range(3, date_col):
#                     self.write_to_excel(policy_index, col, orignal_value)
#                     print('col1,orignal_value:', col, orignal_value)
#
#             # else:
#             #     message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
#             for col in range(date_col, 24):
#                 self.write_to_excel(policy_index, col, message)
#                 print('col2,message:', col, message)
#             self.save_excel()
#         except Exception as e:
#             print('error!:', e)
#             with open('error.txt', 'a', encoding='utf-8') as f:
#                 f.write(str(policy) + '\t' + str(csv_date) + '\t' + str(value) + '\t' + str(e))
#                 # reset_col = 3
#                 # self.write_to_excel(-1, 2, '2017-11-30')
#                 # for key,value in weekday.items():
#                 #     self.write_to_excel(-1, reset_col, key)
#                 #     reset_col += 1
#
#     def write_to_excel(self, policy_index, date_col, message):
#         """
#         写入调仓情况信息
#         :param message:
#         :return: No
#         """
#         policy_row = policy_index + 1
#         # excel_name = self.excel_name
#         # excel_content = open_workbook(excel_name, formatting_info=False)
#         # new_xls_file = copy(excel_content)
#         # if not self.sheet_name:
#         #     # print('保费')
#         #     sheet = new_xls_file.get_sheet(0)
#         # else:
#         #     # print('价值')
#         #     sheet = new_xls_file.get_sheet(1)
#         self.sheet.write(policy_row, date_col, message)
#         # print('writed!')
#         # os.rename(excel_name, './Excel/old_客户名单_for_csv.xls')
#         # new_xls_file.save(excel_name)
#         # print('saved')
#         # os.remove('./Excel/old_客户名单_for_csv.xls')
#         # print('deleted')
#
#     def save_excel(self):
#         excel_name = self.excel_name
#         os.rename(excel_name, './Excel/old_客户名单.xls')
#         self.new_xls_file.save(excel_name)
#         # print('saved')
#         os.remove('./Excel/old_客户名单.xls')
#
#     def adjust_date_col(self):
#         weekday = self.charge_weekday()
#         reset_col = 3
#         self.write_to_excel(-1, 2, '2017-11-30')
#         for key, value in weekday.items():
#             self.write_to_excel(-1, reset_col, key)
#             reset_col += 1
#         self.save_excel()
#
#
# class SLA_Csv_To_Excel(object):
#     def __init__(self, sheet_name):
#         self.sheet_name = sheet_name
#         # 指定mysql数据库
#         self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
#                                             database='statement', charset='utf8')
#         self.month = int(input("请输入月份："))
#         self.excel_name = './Excel/' + str(input("请输入需要录入的Excel表格名字：")) + '.xlsx'
#         # self.excel_name = './Excel/' + "客户名单" + '.xls'
#         self.policy_number = {}
#
#         excel_name = self.excel_name
#         excel_content = open_workbook(excel_name, formatting_info=False)
#         self.new_xls_file = copy(excel_content)
#         if not self.sheet_name:
#             print('保费')
#             self.sheet = self.new_xls_file.get_sheet(0)
#         else:
#             print('价值')
#             self.sheet = self.new_xls_file.get_sheet(1)
#
#     def charge_weekday(self, year=2017):
#         month = self.month
#         index = 3
#         excel_day_row = collections.OrderedDict()  # 有序字典
#         try:
#             for day in range(1, 32):
#                 if int(datetime.datetime(year, month, day).strftime("%w")) in range(1, 6):
#                     if day < 10:
#                         day = '0' + str(day)
#                     excel_day_row[str(year) + '/' + str(month) + '/' + str(day)] = index
#                     # print(year,month,day)
#                     index += 1
#         except:
#             pass
#         # print(excel_day_row)
#         return excel_day_row
#
#     def read_from_csv(self):
#         for csv_date in range(1, 32):
#             try:
#                 if csv_date < 10:
#                     csv_date = '0' + str(csv_date)
#                 if self.sheet_name == 1:
#                     csv_data = pd.read_csv('./Excel/policy/SLA fund for cbc 201712' + str(csv_date) + '.csv')
#                 else:
#                     csv_data = pd.read_csv('./Excel/policy/SLA policy for cbc 201712' + str(csv_date) + '.csv')
#                 result = []
#                 date = '2017/12/' + str(csv_date)
#                 print(date)
#                 weekday = self.charge_weekday()
#                 if date not in weekday.keys():
#                     continue
#                 for index in range(csv_data.iloc[:, 0].size):
#                     policy = csv_data.loc[index, 'Contract No.']
#                     if self.sheet_name == 1:
#                         if policy in self.policy_number.keys():
#                             self.policy_number[policy] += csv_data.loc[index, 'Amount in Contract Ccy']
#                         else:
#                             self.policy_number[policy] = csv_data.loc[index, 'Amount in Contract Ccy']
#                         # 获取查询的结果
#                         result.append((policy, date))
#                     else:
#                         value = csv_data.loc[index, 'Total Premium Paid']
#                         # 获取查询的结果
#                         result.append((policy, date, value))
#                         # result = [('562499G','2017-11-30',13333.32),('562499G','2017-12-28',3333.33)]
#                 print(self.policy_number)
#                 # print(result)
#                 # 打印查询的结果
#                 if self.sheet_name == 1:
#                     for policy, value in self.policy_number.items():
#                         # print(type(policy),type(date),type(value))
#                         print(policy, date, value)
#                         self.read_from_excel(policy, str(date), value)
#                 else:
#                     for policy, date, value in result:
#                         # print(type(policy),type(date),type(value))
#                         print(policy, date, value)
#                         self.read_from_excel(policy, str(date), value)
#
#             except Exception as e:
#                 print(e)
#
#     def read_from_excel(self, policy, csv_date, value):
#         if not self.sheet_name:
#             # 0为保费，1为价值 的sheet
#             print('保费')
#             excel_data = pd.read_excel(self.excel_name)
#         else:
#             print('价值')
#             excel_data = pd.read_excel(self.excel_name, sheetname=1)
#         # print(excel_data)
#         policy_index = 'unexist!'
#         orignal_value = 'unexist!'
#         try:
#             policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
#             orignal_value = int(excel_data.iloc[policy_index, 2])
#             print('policy_index,orignal_value:', policy_index + 2, orignal_value)
#             weekday = self.charge_weekday()
#             # while csv_date not in weekday.keys():
#             #     if csv_date == '2017/11/29' or csv_date == '2017/11/30':
#             #         csv_date = '2017/12/01'
#             #         break
#             #     csv_date = csv_date[:-2] + str(int(csv_date[-2:]) - 1) if int(
#             #         csv_date[-2:]) > 10 else csv_date[:-2] + '0' + str(int(csv_date[-2:]) - 1)
#             date_col = weekday[str(csv_date)]
#             message = int(value)
#             print('date_col,message:', date_col, message)
#             if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
#                 for col in range(3, date_col):
#                     self.write_to_excel(policy_index, col, orignal_value)
#                     print('col1,orignal_value:', col, orignal_value)
#             # else:
#             #     message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
#             for col in range(date_col, 24):
#                 self.write_to_excel(policy_index, col, message)
#                 print('col2,message:', col, message)
#             self.save_excel()
#         except Exception as e:
#             print('error!:', e)
#             with open('error.txt', 'a', encoding='utf-8') as f:
#                 f.write(str(policy) + str(csv_date) + str(value) + '\r\n' + str(e))
#                 # reset_col = 3
#                 # self.write_to_excel(-1, 2, '2017-11-30')
#                 # for key,value in weekday.items():
#                 #     self.write_to_excel(-1, reset_col, key)
#                 #     reset_col += 1
#
#     def write_to_excel(self, policy_index, date_col, message):
#         """
#         写入调仓情况信息
#         :param message:
#         :return: No
#         """
#         policy_row = policy_index + 1
#         # excel_name = self.excel_name
#         # excel_content = open_workbook(excel_name, formatting_info=False)
#         # new_xls_file = copy(excel_content)
#         # if not self.sheet_name:
#         #     # print('保费')
#         #     sheet = new_xls_file.get_sheet(0)
#         # else:
#         #     # print('价值')
#         #     sheet = new_xls_file.get_sheet(1)
#         self.sheet.write(policy_row, date_col, message)
#         # print('writed!')
#         # os.rename(excel_name, './Excel/old_客户名单_for_csv.xls')
#         # new_xls_file.save(excel_name)
#         # print('saved')
#         # os.remove('./Excel/old_客户名单_for_csv.xls')
#         # print('deleted')
#
#     def save_excel(self):
#         excel_name = self.excel_name
#         os.rename(excel_name, './Excel/old_客户名单.xls')
#         self.new_xls_file.save(excel_name)
#         # print('saved')
#         os.remove('./Excel/old_客户名单.xls')
#
#     def adjust_date_col(self):
#         weekday = self.charge_weekday()
#         reset_col = 3
#         self.write_to_excel(-1, 2, '2017-11-30')
#         for key, value in weekday.items():
#             self.write_to_excel(-1, reset_col, key)
#             reset_col += 1
#         self.save_excel()


if __name__ == '__main__':
    # hansard_baofei = Hansard_to_excel.YueJie_To_Excel(0)
    # hansard_baofei.read_from_mysql()
    # hansard_baofei.fill_by_excel()
    # # hansard_baofei.adjust_date_col()
    # hansard_jiazhi = Hansard_to_excel.YueJie_To_Excel(1)
    # hansard_jiazhi.read_from_mysql()
    # hansard_jiazhi.fill_by_excel()
    # # hansard_jiazhi.adjust_date_col()
    #
    # ita_baofei = ITA_to_excel.YueJie_To_Excel(0)
    # ita_baofei.read_from_mysql()
    # # ita_baofei.fill_by_excel()
    # ita_jiazhi = ITA_to_excel.YueJie_To_Excel(1)
    # ita_jiazhi.read_from_mysql()
    # # ita_jiazhi.adjust_date_col()

    axa_baofei = AXA_to_excel.Csv_To_Excel(0)
    axa_baofei.read_from_csv()
    axa_jiazhi = AXA_to_excel.Csv_To_Excel(1)
    axa_jiazhi.read_from_csv()
    # axa_jiazhi.adjust_date_col()

    zurich_baofei = ZURICH_to_excel.Csv_To_Excel(0)
    zurich_baofei.read_from_csv()
    zurich_jiazhi = ZURICH_to_excel.Csv_To_Excel(1)
    zurich_jiazhi.read_from_csv()
    # zurich_jiazhi.adjust_date_col()

    sla_baofei = SLA_to_excel.Csv_To_Excel(0)
    sla_baofei.read_from_csv()
    sla_jiazhi = SLA_to_excel.Csv_To_Excel(1)
    sla_jiazhi.read_from_csv()
    sla_jiazhi.adjust_date_col()
