import os
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf

def write_excel(policy_row,excel_name):
    excel_content = open_workbook(excel_name,formatting_info=False)
    new_xls_file = copy(excel_content)
    sheet = new_xls_file.get_sheet(0)
    sheet.write(policy_row,3,'调仓完毕')
    os.remove(excel_name)
    new_xls_file.save(excel_name)