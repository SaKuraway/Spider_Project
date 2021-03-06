# 有序字典模块
import collections
import os, pymysql, datetime, pandas as pd
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf


class YueJie_To_Excel(object):
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
        try:
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
        except:
            print('weekdayError!!')
        # print('excel_day_row',excel_day_row)
        self.len_weekdays = len(excel_day_row.items())
        # print('excel_day_row____lenth',len(excel_day_row.items()))
        return excel_day_row

    # def read_from_mysql(self):
    #     # 获得Cursor对象
    #     cur = self.mysql_client.cursor()
    #     # 执行select语句，并返回受影响的行数：
    #     if not self.sheet_name:
    #         # 0.hansard保费部分
    #         print('保费')
    #         # count = cur.execute(
    #         #     "SELECT policy_no,date,value FROM tb_premium WHERE date>='2017-11-30' AND policy_no LIKE '5%'")
    #         # 2.ITA保费部分
    #         count = cur.execute("SELECT policy_no,date,value FROM tb_premium_test WHERE '2018-01-01'>=date>='2017-11-30'")
    #
    #         csv_data = pd.read_excel('./Excel/policy/20180103爬的ITA 12月premium.xls')
    #         result = []
    #         for index in range(csv_data.iloc[:, 0].size):
    #             policy = csv_data.loc[index, 'policy no.']
    #             date = csv_data.loc[index, 'date']
    #             value = csv_data.loc[index, 'value']
    #             # 获取查询的结果
    #             result.append((policy, str(date), value))
    #     else:
    #         # 1.hansard价值部分
    #         print('价值')
    #         # count = cur.execute(
    #         #     "SELECT policy_no,price_date,SUM(value2) from tb_allocation WHERE date>='2017-12-01' AND policy_no LIKE '5%' GROUP BY policy_no")
    #         # 3.ITA价值部分
    #         count = cur.execute("SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T%' AND date='2017-12-01'")
    #
    #         csv_data = pd.read_excel('./Excel/policy/20180103爬的ITA 12月premium.xls')
    #         result = []
    #         for index in range(csv_data.iloc[:, 0].size):
    #             policy = csv_data.loc[index, 'policy no.']
    #             date = csv_data.loc[index, 'date']
    #             value = csv_data.loc[index, '\nTotal policy value in policy currency for Linked policy']
    #             # 获取查询的结果
    #             result.append((policy, str(date), value))

        # 获取查询的结果
        # result = cur.fetchall()
        # result = [('565374G','2017-12-29',37706.19),('565390K','2017-12-29',9047.62),('565412B','2017-12-29',17563.84),('565424F','2017-12-29',21971.73),('565428V','2017-12-29',24937.28),('565437U','2017-12-29',10187.15),('565447F','2017-12-29',10466.11),('565449A','2017-12-29',8796.64),('565452M','2017-12-28',9952.91)]
        # 打印查询的结果
        # for policy, date, value in result:
        #     # print(type(policy),type(date),type(value))
        #     print(policy, date, value)
        #     self.read_from_excel(policy, str(date), value)
        # # 关闭Cursor对象
        # cur.close()

    def read_from_mysql(self):
        # 获得Cursor对象
        cur = self.mysql_client.cursor()
        weekday = self.charge_weekday()
        # 执行select语句，并返回受影响的行数：
        if not self.sheet_name:
            # 0.hansard保费部分
            print('保费')
            # count = cur.execute(
            #     "SELECT policy_no,date,value FROM tb_premium WHERE date>='2017-11-30' AND policy_no LIKE '5%'")
            # 2.ITA保费部分
            count = cur.execute("SELECT policy_no,date,value FROM tb_premium_test WHERE date>='2018-01-01'")
            # csv_data0 = pd.read_excel('./Excel/policy/20180103爬的ITA 12月premium.xls')
            # 索引倒序排列（但此时索引对应的值还是不变10,9,8,7,6....1，需要重新删掉索引再赋id）
            # csv_data = csv_data0.sort_index(ascending=False)
            # 删掉索引再重新赋id，0,1,2,3......10
            # csv_data = csv_data.reset_index(drop=True)
            # csv_data.sort_values(by='date')
            # print(csv_data)
            # result = []
            # for index in range(csv_data.iloc[:, 0].size):
            #     policy = csv_data.loc[index, 'policy no.']
            #     date = str(csv_data.loc[index, 'date'])
            #     # str_date = str(date) if int(str(date).split('/')[-1]) >= 10 else '0' + str(int(str(date).split('/')[-1]))
            #     print(date)
            #     year = str(date).split('/')[0]
            #     month = str(int(str(date).split('/')[1])) if int(str(date).split('/')[1]) >= 10 else '0' + str(int(str(date).split('/')[1]))
            #     day = str(int(str(date).split('/')[-1])) if int(str(date).split('/')[-1]) >= 10 else '0' + str(int(str(date).split('/')[-1]))
            #     str_date = '/'.join([year, month, day])
            #     print(year, month, day)
            #     value = csv_data.loc[index, 'value']
            #     # 获取查询的结果
            #     result.append((policy, str_date, value))
        else:
            # 1.hansard价值部分
            print('价值')
            # count = cur.execute(
            #     "SELECT policy_no,price_date,SUM(value2) from tb_allocation WHERE date>='2017-12-01' AND policy_no LIKE '5%' GROUP BY policy_no")
            # 3.ITA价值部分
            # count = cur.execute("SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T25W017508' AND date>='2017-12-01' AND date<'2018-01-01'")
            count = cur.execute("SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T%' AND date>='2018-01-01' AND date<'2018-02-01'")
                # "SELECT policy_no,date,total_value FROM tb_accountvalue WHERE policy_no LIKE 'T%' AND date>='2017-12-01'")

        # 获取查询的结果
        result = cur.fetchall()
        # result = [('T25W015492','2017/12/09',300)]

        # 打印查询的结果
        for policy, date, value in result:
            # print(type(policy),type(date),type(value))
            print(policy, date, value)
            # if str(date) in weekday.keys():
            #     mysql_date = int(str(date).split('/')[-1])
            #     print('in~~~~~~~')
            # 清零
            # self.reset_data(policy, str(date), value)
            # 正常
            self.read_from_excel(policy, str(date), value)
        # 关闭Cursor对象
        cur.close()

    def read_from_excel(self, policy, mysql_date, value):
        print('mysql_date',mysql_date)
        if not self.sheet_name:
            # 0为保费，1为价值 的sheet
            print('保费')
            excel_data = pd.read_excel(self.excel_name)
        else:
            excel_data = pd.read_excel(self.excel_name, sheetname=1)
        # print(excel_data)
        policy_index = 'unexist!'
        orignal_value = 'unexist!'
        try:
            policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
            orignal_value = round(float(excel_data.iloc[policy_index, 2]),2)
            print('policy_index,orignal_value:', policy_index + 2, orignal_value)
            weekday = self.charge_weekday()
            while mysql_date not in weekday.keys():
                print(mysql_date)
                if mysql_date == '2017-11-30':
                    mysql_date = '2017-12-01'
                    break
                year = str(mysql_date).split('-')[0]
                month = str(int(str(mysql_date).split('-')[1])) if int(str(mysql_date).split('-')[1]) >= 10 else '0' + str(int(str(mysql_date).split('-')[1]))
                day = str(int(str(mysql_date).split('-')[-1])-1) if int(str(mysql_date).split('-')[-1]) >= 10 else '0' + str(int(str(mysql_date).split('-')[-1])-1)
                mysql_date = '-'.join([year,month,day])
                print('year,month,day,mysql_date:',year,month,day,mysql_date)
                # mysql_date = mysql_date[:8] + str(int(mysql_date[8:]) - 1)
                # mysql_date = mysql_date[:8] + str(int(mysql_date[:8]) - 1) if int(
                #     mysql_date[:8]) > 10 else mysql_date[:8] + '0' + str(int(mysql_date[:8]) - 1)
            date_col = weekday[str(mysql_date)]
            print('---------date_col,mysql_date----------',date_col,mysql_date)
            # message = orignal_value + round(float(value),2)
            # print('date_col,message:', date_col, message)
            # if int(excel_data.iloc[policy_index, date_col]) == 0:
            #     for col in range(3, date_col):
            #         self.write_to_excel(policy_index, col, orignal_value)
            #         print('col1,orignal_value:', col, orignal_value)
            # else:
            #     message = float(excel_data.iloc[policy_index, date_col]) + float(value) if self.sheet_name == 0 else round(float(value),2)
            #     print('date_col的message值---------------',message)
            # print('message---------------',message)

            if self.sheet_name == 1:
                message = round(float(value), 2)
                print('date_col,orignal_value:', date_col, orignal_value)
                if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
                    for col in range(3, date_col):
                        self.write_to_excel(policy_index, col, orignal_value)
                        print('col1,orignal_value:', col, orignal_value)
            else:
                message = orignal_value + round(float(value),2)
                print('date_col,message:', date_col, message)
                if int(excel_data.iloc[policy_index, date_col - 1]) == 0:
                    for col in range(3, date_col):
                        self.write_to_excel(policy_index, col, orignal_value)
                        print('col1,orignal_value:', col, orignal_value)
                elif int(excel_data.iloc[policy_index, date_col - 1]) != 0 and int(excel_data.iloc[policy_index, date_col]) != 0:
                    # 重复日
                    message = float(excel_data.iloc[policy_index, date_col]) + float(value)

            for col in range(date_col, self.len_weekdays+3):
                self.write_to_excel(policy_index, col, message)
                print('col2,message:', col, message)
            self.save_excel()

        except Exception as e:
            print('error!:', e)
            with open('error.txt', 'a', encoding='utf-8') as f:
                f.write(str(policy) + str(mysql_date) + str(value) + '\r\n')
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
        # self.new_xls_file = copy(excel_content)
        # if not self.sheet_name:
        #     print('保费')
        #     self.sheet = self.new_xls_file.get_sheet(0)
        # else:
        #     print('价值')
        #     self.sheet = self.new_xls_file.get_sheet(1)
        self.sheet.write(policy_row, date_col, message)
        # print('writed!')
        # os.rename(excel_name, './Excel/old_客户名单.xls')
        # new_xls_file.save(excel_name)
        # # print('saved')
        # os.remove('./Excel/old_客户名单.xls')
        # print('deleted')

    def save_excel(self):
        excel_name = self.excel_name
        os.rename(excel_name, './Excel/old_客户名单.xls')
        self.new_xls_file.save(excel_name)
        # print('saved')
        os.remove('./Excel/old_客户名单.xls')

    def fill_by_excel(self):
        if not self.sheet_name:
            # 0为保费，1为价值 的sheet
            print('保费')
            excel_data = pd.read_excel(self.excel_name)
        else:
            print('价值')
            excel_data = pd.read_excel(self.excel_name, sheetname=1)
        df = excel_data[excel_data.iloc[:, 3] == 0]
        fill_index = df[df.iloc[:, 2] != 0].index.tolist()
        for index in fill_index:
            try:
                if not str(excel_data.loc[index,'Policy Number']).startswith('T'):
                    continue
                print('填充无缴费保单ing：',excel_data.loc[index,'Policy Number'])
                orignal_value = excel_data.iloc[index,2]
                for date_col in range(3,self.len_weekdays+3):
                    self.write_to_excel(index,date_col,orignal_value)
                self.save_excel()
            except:
                pass


    def reset_data(self, policy, mysql_date, value):
        if not self.sheet_name:
            # 0为保费，1为价值 的sheet
            print('保费')
            excel_data = pd.read_excel(self.excel_name)
        else:
            excel_data = pd.read_excel(self.excel_name, sheetname=1)
        try:
            policy_index = excel_data[excel_data['Policy Number'] == policy].index.tolist()[0]
            for col in range(3, self.len_weekdays+3):
                self.write_to_excel(policy_index, col, 0)
                print('col2清零:', col)
            self.save_excel()
        except:
            print('%s中不存在保单号%s',self.excel_name,policy)



if __name__ == '__main__':
    yuejie_data_baofei = YueJie_To_Excel(0)
    yuejie_data_baofei.read_from_mysql()
    yuejie_data_baofei.fill_by_excel()
    # yuejie_data_jiazhi = YueJie_To_Excel(1)
    # yuejie_data_jiazhi.read_from_mysql()
    # yuejie_data_jiazhi.fill_by_excel()
