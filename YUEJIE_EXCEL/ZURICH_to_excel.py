#-*-coding:utf-8-*-
# 有序字典模块
import collections
import os,pymysql,datetime,pandas as pd
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf

# 有序字典模块
import collections
import os, pymysql, datetime
import pandas as pd
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf


class Csv_To_Excel(object):
    def __init__(self, sheet_name):
        self.sheet_name = sheet_name
        # 指定mysql数据库
        self.mysql_client = pymysql.connect(host='112.74.93.48', port=3306, user='root', password='962ced336f',
                                            database='statement', charset='utf8')
        self.month = 1 # int(input("请输入月份："))
        # self.excel_name = './Excel/'+str(input("请输入需要录入的Excel表格名字："))+'.xlsx'
        self.excel_name = './Excel/' + "客户名单" + '.xls'

        excel_name = self.excel_name
        excel_content = open_workbook(excel_name, formatting_info=False)
        self.new_xls_file = copy(excel_content)
        if not self.sheet_name:
            print('保费')
            self.sheet = self.new_xls_file.get_sheet(0)
        else:
            print('价值')
            self.sheet = self.new_xls_file.get_sheet(1)

    def charge_weekday(self, year=2018):
        month = self.month
        index = 3
        excel_day_row = collections.OrderedDict()  # 有序字典
        # try:
        for day in range(1, 32):
            day0 = day
            if int(datetime.datetime(int(year), int(month), int(day0)).strftime("%w")) in range(1, 6):
                if int(day0) < 10:
                    day0 = '0' + str(day0)
                if int(month) < 10:
                    # month = '0' + str(month)
                    excel_day_row[str(year) + '-' + '0' +  str(month) + '-' + str(day0)] = index
                elif int(month) >= 10:
                    excel_day_row[str(year) + '-' + str(month) + '-' + str(day0)] = index
                # print(year,month,day0)
                index += 1
        # except:
        #     print('weekdayError!!')
        self.len_weekdays = len(excel_day_row)
        # print('excel_day_row',excel_day_row)
        return excel_day_row

    def read_from_csv(self):
        for csv_date in range(1,32):
            try:
                if csv_date < 10:
                    csv_date = '0' + str(csv_date)
                csv_data = pd.read_csv('./Excel/policy/201801/Zurich/ZI Policy for cbc 201801'+str(csv_date)+'.csv')
                result = []
                date = '2018-01-'+str(csv_date)
                print(date)
                weekday = self.charge_weekday()
                if date not in weekday.keys():
                    continue
                for index in range(csv_data.iloc[:,0].size):
                    policy = csv_data.loc[index,'PolicyNum']
                    value = csv_data.loc[index,'PremiumsPaidTotal']
                    if self.sheet_name == 1:
                        value = csv_data.loc[index,'Currentfundholding']
                    # 获取查询的结果
                    result.append((policy,date,value))
                    # result = [('562499G','2017-11-30',13333.32),('562499G','2017-12-28',3333.33)]
                # 打印查询的结果
                for policy, date, value in result:
                    # print(type(policy),type(date),type(value))
                    print(policy, date, value)
                    self.read_from_excel(policy, str(date), value)
            except Exception as e:
                print(e)

    def read_from_excel(self, policy, csv_date, value):
        if not self.sheet_name:
            # 0为保费，1为价值 的sheet
            print('保费')
            excel_data = pd.read_excel(self.excel_name)
        else:
            print('价值')
            excel_data = pd.read_excel(self.excel_name, sheetname=1)
        # print(excel_data)
        policy_index = 'unexist!'
        orignal_value = 'unexist!'
        try:
            policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
            orignal_value = round(float(excel_data.iloc[policy_index, 2]),2)
            print('policy_index,orignal_value:', policy_index + 2, orignal_value)
            weekday = self.charge_weekday()
            # while csv_date not in weekday.keys():
            #     if csv_date == '2017/11/29' or csv_date == '2017/11/30':
            #         csv_date = '2017/12/01'
            #         break
            #     csv_date = csv_date[:-2] + str(int(csv_date[-2:]) - 1) if int(
            #         csv_date[-2:]) > 10 else csv_date[:-2] + '0' + str(int(csv_date[-2:]) - 1)
            date_col = weekday[str(csv_date)]
            message = round(float(value),2)
            print('date_col,message:', date_col, message)
            if int(excel_data.iloc[policy_index, date_col - 1]) == 0  and message != 0:
                for col in range(3, date_col):
                    self.write_to_excel(policy_index, col, orignal_value)
                    print('col1,orignal_value:', col, orignal_value)

            # else:
            #     message = float(excel_data.iloc[policy_index, date_col - 1]) + float(value)
            for col in range(date_col, self.len_weekdays+3):
                self.write_to_excel(policy_index, col, message)
                print('col2,message:', col, message)
            self.save_excel()
        except Exception as e:
            print('error!:', e)
            with open('error.txt', 'a', encoding='utf-8') as f:
                f.write(str(policy) +'\t'+ str(csv_date)  +'\t'+ str(value)  +'\t'+ str(e))
                # reset_col = 3
                # self.write_to_excel(-1, 2, '2017-11-30')
                # for key,value in weekday.items():
                #     self.write_to_excel(-1, reset_col, key)
                #     reset_col += 1

    def write_to_excel(self, policy_index, date_col, message):
        """
        写入调仓情况信息
        :param message:
        :return: No
        """
        policy_row = policy_index + 1
        # excel_name = self.excel_name
        # excel_content = open_workbook(excel_name, formatting_info=False)
        # new_xls_file = copy(excel_content)
        # if not self.sheet_name:
        #     # print('保费')
        #     sheet = new_xls_file.get_sheet(0)
        # else:
        #     # print('价值')
        #     sheet = new_xls_file.get_sheet(1)
        self.sheet.write(policy_row, date_col, message)
        # print('writed!')
        # os.rename(excel_name, './Excel/old_客户名单_for_csv.xls')
        # new_xls_file.save(excel_name)
        # print('saved')
        # os.remove('./Excel/old_客户名单_for_csv.xls')
        # print('deleted')

    def save_excel(self):
        excel_name = self.excel_name
        os.rename(excel_name, './Excel/old_客户名单.xls')
        self.new_xls_file.save(excel_name)
        # print('saved')
        os.remove('./Excel/old_客户名单.xls')

if __name__ == '__main__':
    yuejie_data_baofei = Csv_To_Excel(0)
    yuejie_data_baofei.read_from_csv()
    yuejie_data_jiazhi = Csv_To_Excel(1)
    yuejie_data_jiazhi.read_from_csv()
