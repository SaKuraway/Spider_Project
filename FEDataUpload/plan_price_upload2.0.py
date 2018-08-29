import sys
import os
import re
import time
import random
import pandas
import pymysql
from lxml import etree
from copy import deepcopy
import requests
# smtp服务器模块
import smtplib
# 构造邮件模块
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
# 有序字典模块
import collections
# excel操作模块
from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf
# 导入 webdriver
from selenium import webdriver
# 右键操作
from selenium.webdriver import ActionChains
# 引入keys包调用多个键盘按键配合操作
from selenium.webdriver.common.keys import Keys
# WebDriverWait 库，负责循环等待
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
# 导入 Select 类 处理下拉框
from selenium.webdriver.support.ui import Select
# expected_conditions 类，负责条件出发
from selenium.webdriver.support import expected_conditions as EC
# 导入selenium的报头对象
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# base_url = '' # https://analytics.financialexpress.net/CustomInstruments.aspx?s=Save&dft=dd/MM/yyyy&dsp=%20

# data ={
#
# "SessionID":"4E62A68E-3B6E-0EE0-121E-FCF750E64214",
# "UserID":"78D90F3B-17A0-4B97-8F5E-DADFD32409EE",
# "UserDisplayName":"Trussan International Holdings Limited",
# "__VIEWSTATE":"/wEPDwUKMTYxODU0MTU4MWQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgQFI2N0bDAwJE1haW5Db250ZW50JGNoa0luc3RydW1lbnROYW1lBTFjdGwwMCRIaWRkZW5Db250ZW50JGRpYUNvbnRhY3QkY2hrT3JkZXJCeUxhc3ROYW1lBStjdGwwMCRIaWRkZW5Db250ZW50JGRpYVdpbmRvd3MkY2hrT3ZlcndyaXRlBSxjdGwwMCRIaWRkZW5Db250ZW50JGRpYVdpbmRvd3MkY2hrSGlkZVB1YmxpY8/pwiPFeMSd0LtYtV9peiEuNVFO8hy5S6VspqAq2IHt",
# "txtHeader":"",
# "txtHeaderDisplay":"",
# "hdInstrumentName":"000172 - huá tài bó ruì liàng huà zeng qiáng hùn hé",
# "ListCustomInstrument":"Z1911894210",
# "ListCustomInstrumentID":"1911894210",
# "Universe":"127DC997-F42B-E711-8E9C-BC305BEC6E34",
# "ListSector":"_ALL",
# "hdCanModify":"1",
# "hdDateFormat":"dd/MM/yyyy",
# "hdDataSeparator":" ",
# "chkInstrumentName":"on",
# "txtReferenceCode":"000172",
# "ddlUniverse":"127DC997-F42B-E711-8E9C-BC305BEC6E34",
# "ddlSector":"",
# "ddlPriceType":"0",
# "ddlCurrency":"CNY",
# "txtInitialCharge":"0.0000",
# "ddlDateFormat":"dd/MM/yyyy",
# "ddlDataSeperator":" ",
# "ddlPriceCount":"1",
# "txtPrices":\
# "02/08/2013 1\n09/08/2013 1.001\n12/08/2013 1.001\n15/08/2013 1.001\n16/08/2013 1.001\n19/08/2013 1.002\n20/08/2013 1.002\n21/08/2013 1.002\n22/08/2013 1.003\n23/08/2013 1.002\n26/08/2013 1.007\n27/08/2013 1.009\n28/08/2013 1.006\n29/08/2013 1.006\n30/08/2013 1.005\n02/09/2013 1.007\n03/09/2013 1.017\n04/09/2013 1.017\n05/09/2013 1.015\n06/09/2013 1.019\n09/09/2013 1.042\n10/09/2013 1.052\n11/09/2013 1.052\n12/09/2013 1.063\n13/09/2013 1.058\n16/09/2013 1.055\n17/09/2013 1.034\n18/09/2013 1.034\n23/09/2013 1.045\n24/09/2013 1.032\n25/09/2013 1.025\n26/09/2013 1.006\n27/09/2013 1.009\n30/09/2013 1.015\n08/10/2013 1.028\n09/10/2013 1.039\n10/10/2013 1.031\n11/10/2013 1.05\n14/10/2013 1.054\n15/10/2013 1.053\n16/10/2013 1.028\n17/10/2013 1.025\n18/10/2013 1.029\n21/10/2013 1.043\n22/10/2013 1.036\n23/10/2013 1.022\n24/10/2013 1.021\n25/10/2013 1.009\n28/10/2013 1.009\n29/10/2013 1.007\n30/10/2013 1.023\n31/10/2013 1.011\n01/11/2013 1.014\n04/11/2013 1.016\n05/11/2013 1.02\n06/11/2013 1.01\n07/11/2013 1.003\n08/11/2013 0.99\n11/11/2013 0.996\n12/11/2013 1.006\n13/11/2013 0.983\n14/11/2013 0.988\n15/11/2013 1.008\n18/11/2013 1.039\n19/11/2013 1.036\n20/11/2013 1.04\n21/11/2013 1.033\n22/11/2013 1.028\n25/11/2013 1.024\n26/11/2013 1.027\n27/11/2013 1.036\n28/11/2013 1.049\n29/11/2013 1.054\n02/12/2013 1.04\n03/12/2013 1.057\n04/12/2013 1.068\n05/12/2013 1.065\n06/12/2013 1.059\n09/12/2013 1.067\n10/12/2013 1.07\n11/12/2013 1.052\n12/12/2013 1.051\n13/12/2013 1.052\n16/12/2013 1.038\n17/12/2013 1.034\n18/12/2013 1.033\n19/12/2013 1.027\n20/12/2013 1.003\n23/12/2013 1.006\n24/12/2013 1.01\n25/12/2013 1.02\n26/12/2013 0.999\n27/12/2013 1.018\n30/12/2013 1.021\n31/12/2013 1.031\n02/01/2014 1.029\n03/01/2014 1.014\n06/01/2014 0.992\n07/01/2014 0.995\n08/01/2014 0.998\n09/01/2014 0.99\n10/01/2014 0.98\n13/01/2014 0.976\n14/01/2014 0.988\n15/01/2014 0.991\n16/01/2014 0.991\n17/01/2014 0.983\n20/01/2014 0.977\n21/01/2014 0.99\n22/01/2014 1.012\n23/01/2014 1.011\n24/01/2014 1.025\n27/01/2014 1.014\n28/01/2014 1.016\n29/01/2014 1.022\n30/01/2014 1.013\n07/02/2014 1.022\n10/02/2014 1.044\n11/02/2014 1.053\n12/02/2014 1.062\n13/02/2014 1.055\n14/02/2014 1.066\n17/02/2014 1.078\n18/02/2014 1.07\n19/02/2014 1.081\n20/02/2014 1.07\n21/02/2014 1.061\n24/02/2014 1.043\n25/02/2014 1.02\n26/02/2014 1.023\n27/02/2014 1.02\n28/02/2014 1.029\n03/03/2014 1.038\n04/03/2014 1.037\n05/03/2014 1.032\n06/03/2014 1.036\n07/03/2014 1.029\n10/03/2014 1\n11/03/2014 1.005\n12/03/2014 1.011\n13/03/2014 1.021\n14/03/2014 1.017\n17/03/2014 1.03\n18/03/2014 1.031\n19/03/2014 1.03\n20/03/2014 1.013\n21/03/2014 1.041\n24/03/2014 1.049\n25/03/2014 1.049\n26/03/2014 1.048\n27/03/2014 1.04\n28/03/2014 1.034\n31/03/2014 1.035\n01/04/2014 1.048\n02/04/2014 1.056\n03/04/2014 1.05\n04/04/2014 1.059\n08/04/2014 1.079\n09/04/2014 1.082\n10/04/2014 1.093\n11/04/2014 1.095\n14/04/2014 1.095\n15/04/2014 1.076\n16/04/2014 1.079\n17/04/2014 1.075\n18/04/2014 1.074\n21/04/2014 1.059\n22/04/2014 1.061\n23/04/2014 1.059\n24/04/2014 1.057\n25/04/2014 1.046\n28/04/2014 1.028\n29/04/2014 1.04\n30/04/2014 1.042\n05/05/2014 1.045\n06/05/2014 1.046\n07/05/2014 1.035\n08/05/2014 1.036\n09/05/2014 1.036\n12/05/2014 1.058\n13/05/2014 1.057\n14/05/2014 1.055\n15/05/2014 1.04\n16/05/2014 1.039\n19/05/2014 1.031\n20/05/2014 1.032\n21/05/2014 1.041\n22/05/2014 1.04\n23/05/2014 1.047\n26/05/2014 1.052\n27/05/2014 1.049\n28/05/2014 1.06\n29/05/2014 1.049\n30/05/2014 1.053\n03/06/2014 1.051\n04/06/2014 1.04\n05/06/2014 1.051\n06/06/2014 1.045\n09/06/2014 1.047\n10/06/2014 1.06\n11/06/2014 1.061\n12/06/2014 1.058\n13/06/2014 1.07\n16/06/2014 1.077\n17/06/2014 1.065\n18/06/2014 1.058\n19/06/2014 1.036\n20/06/2014 1.045\n23/06/2014 1.047\n24/06/2014 1.054\n25/06/2014 1.049\n26/06/2014 1.061\n27/06/2014 1.066\n30/06/2014 1.077\n01/07/2014 1.078\n02/07/2014 1.085\n03/07/2014 1.09\n04/07/2014 1.089\n07/07/2014 1.091\n08/07/2014 1.099\n09/07/2014 1.084\n10/07/2014 1.085\n11/07/2014 1.094\n14/07/2014 1.112\n15/07/2014 1.111\n16/07/2014 1.108\n17/07/2014 1.105\n18/07/2014 1.111\n21/07/2014 1.11\n22/07/2014 1.123\n23/07/2014 1.123\n24/07/2014 1.139\n25/07/2014 1.15\n28/07/2014 1.175\n29/07/2014 1.177\n30/07/2014 1.174\n31/07/2014 1.185\n01/08/2014 1.175\n04/08/2014 1.2\n05/08/2014 1.201\n06/08/2014 1.199\n07/08/2014 1.181\n08/08/2014 1.184\n11/08/2014 1.203\n12/08/2014 1.199\n13/08/2014 1.203\n14/08/2014 1.192\n15/08/2014 1.207\n18/08/2014 1.214\n19/08/2014 1.214\n20/08/2014 1.209\n21/08/2014 1.207\n22/08/2014 1.213\n25/08/2014 1.201\n26/08/2014 1.187\n27/08/2014 1.189\n28/08/2014 1.181\n29/08/2014 1.192\n01/09/2014 1.206\n02/09/2014 1.222\n03/09/2014 1.229\n04/09/2014 1.237\n05/09/2014 1.246\n09/09/2014 1.244\n10/09/2014 1.241\n11/09/2014 1.239\n12/09/2014 1.25\n15/09/2014 1.254\n16/09/2014 1.229\n17/09/2014 1.237\n18/09/2014 1.241\n19/09/2014 1.248\n22/09/2014 1.229\n23/09/2014 1.241\n24/09/2014 1.262\n25/09/2014 1.26\n26/09/2014 1.263\n29/09/2014 1.27\n30/09/2014 1.272\n08/10/2014 1.288\n09/10/2014 1.287\n10/10/2014 1.285\n13/10/2014 1.282\n14/10/2014 1.28\n15/10/2014 1.29\n16/10/2014 1.276\n17/10/2014 1.275\n20/10/2014 1.287\n21/10/2014 1.276\n22/10/2014 1.266\n23/10/2014 1.254\n24/10/2014 1.252\n27/10/2014 1.246\n28/10/2014 1.277\n29/10/2014 1.296\n30/10/2014 1.302\n31/10/2014 1.322\n03/11/2014 1.327\n04/11/2014 1.323\n05/11/2014 1.319\n06/11/2014 1.321\n07/11/2014 1.318\n10/11/2014 1.348\n11/11/2014 1.333\n12/11/2014 1.352\n13/11/2014 1.339\n14/11/2014 1.335\n17/11/2014 1.336\n18/11/2014 1.328\n19/11/2014 1.327\n20/11/2014 1.33\n21/11/2014 1.355\n24/11/2014 1.389\n25/11/2014 1.403\n26/11/2014 1.421\n27/11/2014 1.437\n28/11/2014 1.458\n01/12/2014 1.464\n02/12/2014 1.513\n03/12/2014 1.526\n04/12/2014 1.588\n05/12/2014 1.592\n08/12/2014 1.642\n09/12/2014 1.57\n10/12/2014 1.616\n11/12/2014 1.606\n12/12/2014 1.616\n15/12/2014 1.629\n16/12/2014 1.674\n17/12/2014 1.701\n18/12/2014 1.679\n19/12/2014 1.68\n22/12/2014 1.676\n23/12/2014 1.648\n24/12/2014 1.618\n25/12/2014 1.667\n26/12/2014 1.718\n29/12/2014 1.717\n30/12/2014 1.727\n31/12/2014 1.757\n05/01/2015 1.808\n06/01/2015 1.805\n07/01/2015 1.801\n08/01/2015 1.765\n09/01/2015 1.763\n12/01/2015 1.747\n13/01/2015 1.75\n14/01/2015 1.751\n15/01/2015 1.799\n16/01/2015 1.81\n19/01/2015 1.692\n20/01/2015 1.712\n21/01/2015 1.762\n22/01/2015 1.769\n23/01/2015 1.767\n26/01/2015 1.775\n27/01/2015 1.769\n28/01/2015 1.757\n29/01/2015 1.742\n30/01/2015 1.73\n02/02/2015 1.711\n03/02/2015 1.737\n04/02/2015 1.727\n05/02/2015 1.715\n06/02/2015 1.695\n09/02/2015 1.704\n10/02/2015 1.727\n11/02/2015 1.735\n12/02/2015 1.741\n13/02/2015 1.755\n16/02/2015 1.761\n17/02/2015 1.772\n25/02/2015 1.76\n26/02/2015 1.786\n27/02/2015 1.787\n02/03/2015 1.802\n03/03/2015 1.769\n04/03/2015 1.775\n05/03/2015 1.769\n06/03/2015 1.76\n09/03/2015 1.779\n10/03/2015 1.779\n11/03/2015 1.778\n12/03/2015 1.8\n13/03/2015 1.811\n16/03/2015 1.845\n17/03/2015 1.865\n18/03/2015 1.899\n19/03/2015 1.901\n20/03/2015 1.921\n23/03/2015 1.947\n24/03/2015 1.945\n25/03/2015 1.945\n26/03/2015 1.946\n27/03/2015 1.959\n30/03/2015 2.001\n31/03/2015 1.992\n01/04/2015 2.026\n02/04/2015 2.033\n03/04/2015 2.057\n07/04/2015 2.093\n08/04/2015 2.11\n09/04/2015 2.1\n10/04/2015 2.136\n13/04/2015 2.17\n14/04/2015 2.177\n15/04/2015 2.151\n16/04/2015 2.192\n17/04/2015 2.217\n20/04/2015 2.175\n21/04/2015 2.222\n22/04/2015 2.284\n23/04/2015 2.282\n24/04/2015 2.251\n27/04/2015 2.289\n28/04/2015 2.275\n29/04/2015 2.284\n30/04/2015 2.28\n04/05/2015 2.304\n05/05/2015 2.224\n06/05/2015 2.197\n07/05/2015 2.17\n08/05/2015 2.203\n11/05/2015 2.253\n12/05/2015 2.276\n13/05/2015 2.266\n14/05/2015 2.256\n15/05/2015 2.218\n18/05/2015 2.202\n19/05/2015 2.279\n20/05/2015 2.29\n21/05/2015 2.332\n22/05/2015 2.381\n25/05/2015 2.446\n26/05/2015 2.482\n27/05/2015 2.479\n28/05/2015 2.339\n29/05/2015 2.351\n01/06/2015 2.456\n02/06/2015 2.491\n03/06/2015 2.492\n04/06/2015 2.507\n05/06/2015 2.54\n08/06/2015 2.587\n09/06/2015 2.562\n10/06/2015 2.562\n11/06/2015 2.564\n12/06/2015 2.585\n15/06/2015 2.545\n16/06/2015 2.481\n17/06/2015 2.509\n18/06/2015 2.44\n19/06/2015 2.324\n23/06/2015 2.389\n24/06/2015 2.439\n25/06/2015 2.385\n26/06/2015 2.241\n29/06/2015 2.203\n30/06/2015 2.3\n01/07/2015 2.21\n02/07/2015 2.141\n03/07/2015 2.044\n06/07/2015 2.089\n07/07/2015 2.031\n08/07/2015 1.899\n09/07/2015 2.015\n10/07/2015 2.124\n13/07/2015 2.188\n14/07/2015 2.145\n15/07/2015 2.072\n16/07/2015 2.098\n17/07/2015 2.169\n20/07/2015 2.173\n21/07/2015 2.175\n22/07/2015 2.175\n23/07/2015 2.224\n24/07/2015 2.19\n27/07/2015 2.029\n28/07/2015 2.035\n29/07/2015 2.085\n30/07/2015 2.034\n31/07/2015 2.031\n03/08/2015 2.037\n04/08/2015 2.093\n05/08/2015 2.062\n06/08/2015 2.046\n07/08/2015 2.079\n10/08/2015 2.163\n11/08/2015 2.151\n12/08/2015 2.13\n13/08/2015 2.155\n14/08/2015 2.155\n17/08/2015 2.16\n18/08/2015 2.037\n19/08/2015 2.068\n20/08/2015 2.011\n21/08/2015 1.931\n24/08/2015 1.79\n25/08/2015 1.682\n26/08/2015 1.677\n27/08/2015 1.759\n28/08/2015 1.825\n31/08/2015 1.825\n01/09/2015 1.811\n02/09/2015 1.808\n07/09/2015 1.774\n08/09/2015 1.821\n09/09/2015 1.852\n10/09/2015 1.833\n11/09/2015 1.83\n14/09/2015 1.787\n15/09/2015 1.735\n16/09/2015 1.806\n17/09/2015 1.78\n18/09/2015 1.787\n21/09/2015 1.816\n22/09/2015 1.831\n23/09/2015 1.798\n24/09/2015 1.809\n25/09/2015 1.782\n28/09/2015 1.792\n29/09/2015 1.766\n30/09/2015 1.782\n08/10/2015 1.826\n09/10/2015 1.848\n12/10/2015 1.899\n13/10/2015 1.898\n14/10/2015 1.883\n15/10/2015 1.918\n16/10/2015 1.934\n19/10/2015 1.933\n20/10/2015 1.953\n21/10/2015 1.902\n22/10/2015 1.927\n23/10/2015 1.949\n26/10/2015 1.964\n27/10/2015 1.964\n28/10/2015 1.936\n29/10/2015 1.94\n30/10/2015 1.942\n02/11/2015 1.917\n03/11/2015 1.913\n04/11/2015 1.987\n05/11/2015 2.024\n06/11/2015 2.063\n09/11/2015 2.086\n10/11/2015 2.08\n11/11/2015 2.079\n12/11/2015 2.063\n13/11/2015 2.045\n16/11/2015 2.063\n17/11/2015 2.066\n18/11/2015 2.052\n19/11/2015 2.075\n20/11/2015 2.077\n23/11/2015 2.069\n24/11/2015 2.072\n25/11/2015 2.092\n26/11/2015 2.084\n27/11/2015 1.989\n30/11/2015 2.004\n01/12/2015 2.02\n02/12/2015 2.084\n03/12/2015 2.098\n04/12/2015 2.068\n07/12/2015 2.069\n08/12/2015 2.038\n09/12/2015 2.048\n10/12/2015 2.04\n11/12/2015 2.037\n14/12/2015 2.087\n15/12/2015 2.076\n16/12/2015 2.072\n17/12/2015 2.107\n18/12/2015 2.114\n21/12/2015 2.16\n22/12/2015 2.166\n23/12/2015 2.165\n24/12/2015 2.148\n25/12/2015 2.154\n28/12/2015 2.104\n29/12/2015 2.124\n30/12/2015 2.124\n31/12/2015 2.11\n04/01/2016 2.005\n05/01/2016 2.015\n06/01/2016 2.044\n07/01/2016 1.937\n08/01/2016 1.966\n11/01/2016 1.885\n12/01/2016 1.887\n13/01/2016 1.86\n14/01/2016 1.887\n15/01/2016 1.837\n18/01/2016 1.843\n19/01/2016 1.886\n20/01/2016 1.865\n21/01/2016 1.824\n22/01/2016 1.839\n25/01/2016 1.846\n26/01/2016 1.757\n27/01/2016 1.746\n28/01/2016 1.712\n29/01/2016 1.756\n01/02/2016 1.736\n02/02/2016 1.769\n03/02/2016 1.765\n04/02/2016 1.784\n05/02/2016 1.774\n15/02/2016 1.762\n16/02/2016 1.806\n17/02/2016 1.821\n18/02/2016 1.817\n19/02/2016 1.813\n22/02/2016 1.848\n23/02/2016 1.834\n24/02/2016 1.844\n25/02/2016 1.746\n26/02/2016 1.761\n29/02/2016 1.721\n01/03/2016 1.749\n02/03/2016 1.816\n03/03/2016 1.82\n04/03/2016 1.829\n07/03/2016 1.837\n08/03/2016 1.841\n09/03/2016 1.821\n10/03/2016 1.794\n11/03/2016 1.796\n14/03/2016 1.826\n15/03/2016 1.828\n16/03/2016 1.831\n17/03/2016 1.849\n18/03/2016 1.879\n21/03/2016 1.921\n22/03/2016 1.91\n23/03/2016 1.91\n24/03/2016 1.883\n25/03/2016 1.895\n28/03/2016 1.878\n29/03/2016 1.862\n30/03/2016 1.902\n31/03/2016 1.902\n01/04/2016 1.904\n05/04/2016 1.927\n06/04/2016 1.925\n07/04/2016 1.906\n08/04/2016 1.892\n11/04/2016 1.921\n12/04/2016 1.916\n13/04/2016 1.942\n14/04/2016 1.947\n15/04/2016 1.946\n18/04/2016 1.923\n19/04/2016 1.928\n20/04/2016 1.893\n21/04/2016 1.884\n22/04/2016 1.896\n25/04/2016 1.89\n26/04/2016 1.901\n27/04/2016 1.897\n28/04/2016 1.899\n29/04/2016 1.897\n03/05/2016 1.927\n04/05/2016 1.926\n05/05/2016 1.928\n06/05/2016 1.885\n09/05/2016 1.851\n10/05/2016 1.851\n11/05/2016 1.861\n12/05/2016 1.869\n13/05/2016 1.863\n16/05/2016 1.872\n17/05/2016 1.866\n18/05/2016 1.849\n19/05/2016 1.847\n20/05/2016 1.853\n23/05/2016 1.863\n24/05/2016 1.852\n25/05/2016 1.849\n26/05/2016 1.852\n27/05/2016 1.853\n30/05/2016 1.851\n31/05/2016 1.904\n01/06/2016 1.901\n02/06/2016 1.905\n03/06/2016 1.916\n06/06/2016 1.912\n07/06/2016 1.912\n08/06/2016 1.906\n13/06/2016 1.857\n14/06/2016 1.861\n15/06/2016 1.886\n16/06/2016 1.877\n17/06/2016 1.892\n20/06/2016 1.897\n21/06/2016 1.894\n23/06/2016 1.907\n24/06/2016 1.888\n27/06/2016 1.91\n28/06/2016 1.919\n29/06/2016 1.926\n30/06/2016 1.928\n01/07/2016 1.93\n04/07/2016 1.965\n05/07/2016 1.975\n06/07/2016 1.981\n07/07/2016 1.979\n08/07/2016 1.972\n11/07/2016 1.976\n12/07/2016 2.011\n13/07/2016 2.02\n14/07/2016 2.019\n15/07/2016 2.019\n18/07/2016 2.016\n19/07/2016 2.008\n20/07/2016 2.001\n21/07/2016 2.01\n22/07/2016 1.993\n25/07/2016 1.999\n26/07/2016 2.02\n27/07/2016 1.989\n28/07/2016 1.999\n29/07/2016 1.999\n01/08/2016 1.985\n02/08/2016 1.994\n03/08/2016 1.994\n04/08/2016 1.998\n05/08/2016 1.997\n08/08/2016 2.013\n09/08/2016 2.023\n10/08/2016 2.014\n11/08/2016 2.008\n12/08/2016 2.038\n15/08/2016 2.085\n16/08/2016 2.077\n17/08/2016 2.076\n18/08/2016 2.074\n19/08/2016 2.07\n22/08/2016 2.055\n23/08/2016 2.058\n24/08/2016 2.054\n25/08/2016 2.044\n26/08/2016 2.044\n29/08/2016 2.046\n30/08/2016 2.05\n31/08/2016 2.055\n01/09/2016 2.042\n02/09/2016 2.045\n05/09/2016 2.05\n06/09/2016 2.063\n07/09/2016 2.063\n08/09/2016 2.062\n09/09/2016 2.05\n12/09/2016 2.021\n13/09/2016 2.019\n14/09/2016 2.005\n19/09/2016 2.023\n20/09/2016 2.022\n21/09/2016 2.025\n22/09/2016 2.039\n23/09/2016 2.033\n26/09/2016 2.005\n27/09/2016 2.019\n28/09/2016 2.017\n29/09/2016 2.023\n30/09/2016 2.03\n10/10/2016 2.047\n11/10/2016 2.053\n12/10/2016 2.052\n13/10/2016 2.054\n14/10/2016 2.055\n17/10/2016 2.043\n18/10/2016 2.069\n19/10/2016 2.065\n20/10/2016 2.068\n21/10/2016 2.076\n24/10/2016 2.095\n25/10/2016 2.1\n26/10/2016 2.089\n27/10/2016 2.088\n28/10/2016 2.08\n31/10/2016 2.08\n01/11/2016 2.093\n02/11/2016 2.075\n03/11/2016 2.091\n04/11/2016 2.085\n07/11/2016 2.091\n08/11/2016 2.095\n09/11/2016 2.083\n10/11/2016 2.102\n11/11/2016 2.113\n14/11/2016 2.117\n15/11/2016 2.116\n16/11/2016 2.116\n17/11/2016 2.118\n18/11/2016 2.111\n21/11/2016 2.118\n22/11/2016 2.132\n23/11/2016 2.139\n24/11/2016 2.147\n25/11/2016 2.161\n28/11/2016 2.17\n29/11/2016 2.18\n30/11/2016 2.165\n01/12/2016 2.18\n02/12/2016 2.163\n05/12/2016 2.138\n06/12/2016 2.136\n07/12/2016 2.143\n08/12/2016 2.143\n09/12/2016 2.156\n12/12/2016 2.122\n13/12/2016 2.122\n14/12/2016 2.112\n15/12/2016 2.094\n16/12/2016 2.096\n19/12/2016 2.091\n20/12/2016 2.085\n21/12/2016 2.098\n22/12/2016 2.098\n23/12/2016 2.088\n26/12/2016 2.095\n27/12/2016 2.092\n28/12/2016 2.085\n29/12/2016 2.086\n30/12/2016 2.092\n03/01/2017 2.109\n04/01/2017 2.123\n05/01/2017 2.121\n06/01/2017 2.114\n09/01/2017 2.121\n10/01/2017 2.118\n11/01/2017 2.109\n12/01/2017 2.099\n13/01/2017 2.096\n16/01/2017 2.092\n17/01/2017 2.1\n18/01/2017 2.107\n19/01/2017 2.101\n20/01/2017 2.114\n23/01/2017 2.118\n24/01/2017 2.122\n25/01/2017 2.126\n26/01/2017 2.133\n03/02/2017 2.124\n06/02/2017 2.134\n07/02/2017 2.133\n08/02/2017 2.14\n09/02/2017 2.147\n10/02/2017 2.154\n13/02/2017 2.161\n14/02/2017 2.162\n15/02/2017 2.151\n16/02/2017 2.16\n17/02/2017 2.148\n20/02/2017 2.176\n21/02/2017 2.185\n22/02/2017 2.195\n23/02/2017 2.188\n24/02/2017 2.186\n27/02/2017 2.172\n28/02/2017 2.179\n01/03/2017 2.181\n02/03/2017 2.173\n03/03/2017 2.176\n06/03/2017 2.187\n07/03/2017 2.188\n08/03/2017 2.184\n09/03/2017 2.173\n10/03/2017 2.176\n13/03/2017 2.189\n14/03/2017 2.188\n15/03/2017 2.192\n16/03/2017 2.203\n17/03/2017 2.186\n20/03/2017 2.186\n21/03/2017 2.195\n22/03/2017 2.187\n23/03/2017 2.187\n24/03/2017 2.201\n27/03/2017 2.199\n28/03/2017 2.193\n29/03/2017 2.188\n30/03/2017 2.175\n31/03/2017 2.186\n05/04/2017 2.211\n06/04/2017 2.214\n07/04/2017 2.217\n10/04/2017 2.214\n11/04/2017 2.219\n12/04/2017 2.211\n13/04/2017 2.214\n14/04/2017 2.199\n17/04/2017 2.192\n18/04/2017 2.187\n19/04/2017 2.177\n20/04/2017 2.183\n21/04/2017 2.188\n24/04/2017 2.165\n25/04/2017 2.165\n26/04/2017 2.172\n27/04/2017 2.172\n28/04/2017 2.174\n02/05/2017 2.169\n03/05/2017 2.163\n04/05/2017 2.159\n05/05/2017 2.147\n08/05/2017 2.135\n09/05/2017 2.136\n10/05/2017 2.129\n11/05/2017 2.135\n12/05/2017 2.146\n15/05/2017 2.154\n16/05/2017 2.171\n17/05/2017 2.168\n18/05/2017 2.166\n19/05/2017 2.165\n22/05/2017 2.159\n23/05/2017 2.149\n24/05/2017 2.153\n25/05/2017 2.18\n26/05/2017 2.18\n31/05/2017 2.184\n01/06/2017 2.176\n02/06/2017 2.175\n05/06/2017 2.172\n06/06/2017 2.179\n07/06/2017 2.2\n08/06/2017 2.208\n09/06/2017 2.213\n12/06/2017 2.216\n13/06/2017 2.223\n14/06/2017 2.207\n15/06/2017 2.209\n16/06/2017 2.208\n19/06/2017 2.22\n20/06/2017 2.219\n21/06/2017 2.232\n22/06/2017 2.234\n23/06/2017 2.25\n26/06/2017 2.282\n27/06/2017 2.286\n28/06/2017 2.277\n29/06/2017 2.29\n30/06/2017 2.291\n03/07/2017 2.291\n04/07/2017 2.283\n05/07/2017 2.3\n06/07/2017 2.304\n07/07/2017 2.316\n10/07/2017 2.319\n11/07/2017 2.314\n12/07/2017 2.315\n13/07/2017 2.328\n14/07/2017 2.333\n17/07/2017 2.305\n18/07/2017 2.316\n19/07/2017 2.349\n20/07/2017 2.355\n21/07/2017 2.354\n24/07/2017 2.359\n25/07/2017 2.349\n26/07/2017 2.35\n27/07/2017 2.349\n28/07/2017 2.354\n31/07/2017 2.371\n01/08/2017 2.381\n02/08/2017 2.379\n03/08/2017 2.372\n04/08/2017 2.365\n07/08/2017 2.38\n08/08/2017 2.381\n09/08/2017 2.378\n10/08/2017 2.37\n11/08/2017 2.335\n14/08/2017 2.353\n15/08/2017 2.36\n16/08/2017 2.358\n17/08/2017 2.371\n18/08/2017 2.375\n21/08/2017 2.383\n22/08/2017 2.383\n23/08/2017 2.38\n24/08/2017 2.372\n25/08/2017 2.39\n28/08/2017 2.401\n29/08/2017 2.401\n30/08/2017 2.405\n31/08/2017 2.403\n01/09/2017 2.406\n04/09/2017 2.407\n05/09/2017 2.41\n06/09/2017 2.409\n07/09/2017 2.401\n08/09/2017 2.403\n11/09/2017 2.407\n12/09/2017 2.419\n13/09/2017 2.415"},
# "hdTriggerAfterAssign":"",
# "initHdDialogWidth":"570px",
# "hdAfterAssignEvent":"ContactDialogClosing",
# "hdCurrentContactName":"",
# "hdLoadingPageName":"plotData/BrowserData.asmx/RetrieveContactDialogItem",
# "hdSavingPageName":"plotData/UpdateService.asmx/SaveContactDialogItem",
# "hdSavedPortfolioName":"",
# "hdResultID":"ListCustomInstrument",
# "hdCallerNameField":"subTitle",
# "hdZindex":"2500",
# "hdShowBack":"0",
# "hdAllowPublic":"1",
# "hdGroupVisibility":"",
# "hdAfterSaveNewCallbackFunctionName":"",
# "hdBeforeCloseFunctionName":"ContactDialogClosing",
# "hdItemType":"CustomInstrument",
# "hdIsNewContact":"",
# "diaWindows_initHdDialogWidth":"0px",
# "diaWindows_initHdDialogHeight":"0px",
# "diaWindows_hdZindex":"",
# "diaWindows_hdTopY":"",
# "diaWindows_hdTitle":"Custom Instrument",
# "diaWindows_hdLoadURL":"CustomInstruments.aspx?userID=78D90F3B-17A0-4B97-8F5E-DADFD32409EE&sessionID=4E62A68E-3B6E-0EE0-121E-FCF750E64214&s=List",
# "diaWindows_hdSaveURL":"CustomInstruments.aspx?s=Save",
# "diaWindows_hdRenameURL":"",
# "diaWindows_hdAllowPublic":"1",
# "diaWindows_hdExtraNamesToCheck":"",
# "diaWindows_hdCollectionID":"",
# "diaWindows_hdFormID":"frmCustomInstruments",
# "diaWindows_hdAfterSaveEvent":"CustomInstrumentSaved",
# "diaWindows_hdOnSaveEvent":"",
# "diaWindows_hdOnChangeEvent":"LoadCustomInstrument",
# "diaWindows_hdOnDeleteEvent":"DeleteCustomInstrument",
# "diaWindows_hdOnRenameEvent":"",
# "diaWindows_hdOnRenamedEvent":"",
# "diaWindows_hdShouldShow":"0",
# "diaWindows_hdRenameMode":"0",
# "diaWindows_hdItemList":"",
# "diaWindows_hdAddedFolders":"",
# "diaWindows_hdCurrentFolder":"",
# "diaWindows_hdItemName":"",
# "diaWindows_hdAssignContactCallBackFunctionName":"ShowContact",
# "diaWindows_hdCurrentItemID":"ListCustomInstrument",
# "diaWindows_hdIsFirstTimeUse":"1",
# "diaWindows_hdNoteText":"",
# "diaWindows_hdContactID":"",
# "diaWindows_hdGroupVisibility":"",
# "diaWindows_hdMode":"",
# "diaWindows_hdUserControlID":"diaWindows",
# "__VIEWSTATEGENERATOR":"2035E2FF",
# "odSearch":"",
# "ddlClientName":"",
# "chkOrderByLastName":"on",
# "txtFirst":"",
# "txtLast":"",
# "txtDob":"",
# "txtEmail":"",
# "DDPrivacyList:number":"0",
# "diaWindows_txtFilter":"",
# "diaWindows_txtNewFolder":"",
# "diaWindows_txtSaveAs":"",
# "diaWindows_rdSecurities":"0",
# "diaWindows_ddlContacts":"",
# "diaWindows_noteText":"",
# "sdItemName":"000172 - huá tài bó ruì liàng huà zeng qiáng hùn hé",
# "sdPath":"",
# "sdName":"000172 - huá tài bó ruì liàng huà zeng qiáng hùn hé",
# "sdContactID":"",
# "sdGroupVisibility":"0",
# "sdNoteText":""}


# 成功的状态返回为：{"itemData":"Z1911894210!000172 - huá tài bó ruì liàng huà zeng qiáng hùn hé","itemID":"Z1911894210","message":"Save successful","status":"Success"}

class FEDataUpload(object):

    def __init__(self):
        # 旧版登录
        # self.login_url = 'https://analytics.financialexpress.net/login.aspx?AllowOldLogin=true'
        # self.group_id = 'txtGroup'
        # self.Groupname = 'Trussan'
        # self.username_id = 'txtUser'
        # self.Username = 'Trussan'
        # self.password_id = 'txtPassword'
        # self.Password = '1357111#'
        # self.submit_id = 'btnAction'
        # 新版登录方式
        self.login_url = 'http://analytics.financialexpress.net/login.aspx '
        self.username_id = 'logonIdentifier'
        self.Username = 'analyst@partnerplus.com.hk'
        self.password_id = 'password'
        self.Password = 'Trussan1357111#'
        self.submit_id = 'next'
        self.error = 0
        # 指定mysql数据库
        self.mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                            database='data_finance', charset='utf8')

    def requesets_spider(self):
        login_response = etree.HTML(login_response.text)
        hidden_names = login_response.xpath("//div//input[@type='hidden']/@name")
        """SessionID
        UserID
        UserDisplayName
        __EVENTTARGET
        __EVENTARGUMENT
        __LASTFOCUS
        __VIEWSTATE
        refresh
        IncludeFilterOnly
        FromMainPage
        ActionType
        TableActionType
        ChartActionType
        ReportActionType
        KIIActionType
        ProductActionType
        RankFullSector
        SavedResultsID
        PortfolioID
        GroupID
        SelectorID
        CustomInstrumentID
        RQInput
        hdLoadedActiveListName
        hdCanModify
        hdActiveListID
        hdnLang
        hdnUniverse
        hdnMenukey
        ReportMovementsActionType
        hdnTimeZone
        TimeZone
        emailModify
        activelistProType
        hdnMessageCount
        hdnFromtopmenubar
        hdnChartPriceType
        KiiSelectionCodes
        hdnCprbClientName
        hdnStartDate
        hdnEndDate
        hdnDividendPortfolio
        ScatterNameX
        ScatterNameY
        isInteractiveScatter
        hdnDefaultRatios
        ra3_opt
        ra1_opt
        ra1_selected
        ra3_selected
        hidSelectedUniverse
        hidSelectedCode
        hidUniverse
        hidCode
        hidSetting
        hidAlertId
        PageId
        userPortfolioScan
        memberInstrCode
        hdnCustomSectorUniverse
        hdnCustomSectorCode
        hdnIPTokenId
        hdnYCTokenId
        ChartPeriodCount
        SavingsWithdrawalCount
        IncomeEarnedCount
        ListRetrieveTablePerformance
        ListRetrieveTablePerformancetext
        ListRetrieveTableRatio
        ListRetrieveTableRatiotext
        ListRetrieveStyleAnalysis
        ListRetrieveStyleAnalysistext
        ListRetrieveTableFactsheet
        ListRetrieveTableFactsheettext
        ListRetrieveTablePrice
        ListRetrieveTablePricetext
        ListRetrieveTablePlatform
        ListRetrieveTablePlatformtext
        ListRetrieveTableDividend
        ListRetrieveTableDividendtext
        ListRetrieveTableFundComparison
        ListRetrieveTableFundComparisontext
        ListRetrieveKiiPerormance
        ListRetrieveKiiPerormancetext
        ListRetrieveSriianalysis
        ListRetrieveSriianalysistext
        ListRetrieveTableStructuredProducts
        ListRetrieveTableStructuredProductstext
        ListRetrieveProduct
        ListRetrieveProducttext
        ListRetrieveChartLine
        ListRetrieveChartLinetext
        ListRetrieveChartSavingsWithdrawal
        ListRetrieveChartSavingsWithdrawaltext
        ListRetrieveChartIncomeEarned
        ListRetrieveChartIncomeEarnedtext
        ListRetrieveChartDistribution
        ListRetrieveChartDistributiontext
        ListRetrieveChartTechnical
        ListRetrieveChartTechnicaltext
        ListRetrieveChartRolling
        ListRetrieveChartRollingtext
        ListRetrieveChartStochastic
        ListRetrieveChartStochastictext
        ListRetrieveChartScatter
        ListRetrieveChartScattertext
        ListRetrieveChartDiscreteAdv
        ListRetrieveChartDiscreteAdvtext
        ListRetrieveTableCustom
        ListRetrieveTableCustomtext
        ListRetrieveChartSnailTrail
        ListRetrieveChartSnailTrailtext
        ListRetrieveChartFERiskScore
        ListRetrieveChartFERiskScoretext
        CustomUniverseFlags
        hdTriggerAfterAssign
        initHdDialogWidth
        hdAfterAssignEvent
        hdCurrentContactName
        hdLoadingPageName
        hdSavingPageName
        hdSavedPortfolioName
        hdResultID
        hdCallerNameField
        hdZindex
        hdShowBack
        hdAllowPublic
        hdGroupVisibility
        hdAfterSaveNewCallbackFunctionName
        hdBeforeCloseFunctionName
        hdItemType
        hdIsNewContact
        diaWindows_initHdDialogWidth
        diaWindows_initHdDialogHeight
        diaWindows_hdZindex
        diaWindows_hdTopY
        diaWindows_hdTitle
        diaWindows_hdLoadURL
        diaWindows_hdSaveURL
        diaWindows_hdRenameURL
        diaWindows_hdAllowPublic
        diaWindows_hdExtraNamesToCheck
        diaWindows_hdCollectionID
        diaWindows_hdFormID
        diaWindows_hdAfterSaveEvent
        diaWindows_hdOnSaveEvent
        diaWindows_hdOnChangeEvent
        diaWindows_hdOnDeleteEvent
        diaWindows_hdOnRenameEvent
        diaWindows_hdOnRenamedEvent
        diaWindows_hdShouldShow
        diaWindows_hdRenameMode
        diaWindows_hdItemList
        diaWindows_hdAddedFolders
        diaWindows_hdCurrentFolder
        diaWindows_hdItemName
        diaWindows_hdAssignContactCallBackFunctionName
        diaWindows_hdCurrentItemID
        diaWindows_hdIsFirstTimeUse
        diaWindows_hdNoteText
        diaWindows_hdContactID
        diaWindows_hdGroupVisibility
        diaWindows_hdMode
        diaWindows_hdUserControlID
        sdItemName
        template"""
        hidden_values = [login_response.xpath("//div//input[@name='" + hidden_name + "']/@value")[0] if login_response.xpath(
                "//div//input[@name='" + hidden_name + "']/@value") else '' for hidden_name in hidden_names]
        print(hidden_names, hidden_values)

        for hidden_name, hidden_value in zip(hidden_names, hidden_values):
            print(hidden_name, ':', hidden_value)
            standard_life_login_data[hidden_name] = hidden_value
        print(standard_life_login_data)

    def browser_login(self, login_url, username, password, username_id, password_id, submit_id, group_id=None, groupname=None):
        """
        调用并操作浏览器对象
        :param url: 网址
        :param username: 用户名
        :param password: 密码
        :param username_id: 用户名输入框ID
        :param password_id: 密码输入框ID
        :param submit_id: 点击确认的ID
        :return: driver对象
        """
        # 调用环境变量指定的Chrome浏览器创建浏览器对象
        # driver = webdriver.Chrome()
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 1000
        cap["phantomjs.page.settings.loadImages"] = True
        cap["phantomjs.page.settings.disk-cache"] = True
        cap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        cap["phantomjs.page.customHeaders.User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        driver = webdriver.PhantomJS(desired_capabilities=cap)


        # 1.登录操作
        # get方法会一直等到页面被完全加载，然后才会继续程序，通常测试会在这里选择 self.random_sleep()
        driver.get(login_url)
        # driver.find_element_by_id(group_id).send_keys(groupname)
        self.random_sleep(8,10)
        driver.find_element_by_id(username_id).send_keys(username)
        self.random_sleep()
        driver.find_element_by_id(password_id).send_keys(password)
        self.random_sleep()
        driver.find_element_by_id(submit_id).click()
        self.random_sleep()
        return driver

    def read_from_mysql(self,fund_code,last_date):
        cur = self.mysql_client.cursor()
        count = cur.execute(
            "select Fund_code,History_NAV_Date,ANAV from history_nav where Fund_code='"+fund_code+"' and History_NAV_Date>'"+last_date+"' ORDER BY History_NAV_Date asc;")
        # 获取查询的结果
        result = cur.fetchall()
        # result = [('565374G','2017-12-29',37706.19),('565390K','2017-12-29',9047.62),('565412B','2017-12-29',17563.84),('565424F','2017-12-29',21971.73),('565428V','2017-12-29',24937.28),('565437U','2017-12-29',10187.15),('565447F','2017-12-29',10466.11),('565449A','2017-12-29',8796.64),('565452M','2017-12-28',9952.91)]
        # 打印查询的结果
        # for policy, date, value in result[0]:
        #     print(policy, date, value)
        # print('.................')
        # for policy, date, value in result[-1]:
        #     print(policy, date, value)
        # 关闭Cursor对象
        cur.close()
        return result

    def start_work(self):
        driver = self.browser_login(login_url=self.login_url,username_id=self.username_id,username=self.Username,password_id=self.password_id,password=self.Password,submit_id=self.submit_id)
        print('登录成功~~')
        self.random_sleep()
        # 窗口最大化
        driver.maximize_window()
        self.random_sleep()
        self.random_sleep()
        self.random_sleep(15,20)
        html = driver.page_source
        # print(html)
        response = etree.HTML(html)
        allFundCode = response.xpath("//select[@id='ListCustomInstrument']//optgroup//option//text()")
        # allFundCode = self.wait_until(driver=driver, selector_name="//select[@id='ListCustomInstrument']//optgroup//option",action='text')
        print('allFundCode',allFundCode)
        if not allFundCode:
            print('无法获取基金，可能账户正被他人登录使用中！')
        # 列表基金的位移
        position_delay = 0

        # 非潽蓝基金
        # for index,fundCode in enumerate(allFundCode[position_delay:]):
        #     select = Select(driver.find_element_by_name('ListCustomInstrument'))
        #     fund_code = re.sub("\D", "", fundCode)
        #     fund_code = fund_code[:6] # 有些fund需要清洗
        # 潽蓝基金
        for index,fundCode in enumerate(['999901 Plan 01 Standard','999902 Plan 02 Standard','999903 Plan 03 Standard','999904 Plan 04 Standard','999905 Plan 05 Standard','999906 Plan 06 Standard','999907 Plan 07 Standard','999908 Plan 08 Standard','999909 Plan 09 Standard','999910 Plan 10 Standard','001061 China AMC Overseas Income Bond Fund-A (QDII)','002393 HuaAn Funds Quanqiu Meiyuan Shouyi Zhaiquan (QDII) C','539001 jian xin quanqiu jiyu hunhe','486002 ICBC Quanqiu Jing Xuan Gupiao Xing Zhengquan Touzi Jijin','000834 da cheng na si da ke 100 zhi shu','000509 Guangfa qián dàizi huòbì','096001  da cheng biao pu 500 deng quan zhong zhi shu']):
            select = Select(driver.find_element_by_name('ListCustomInstrument'))
            fund_code = re.sub("\D", "", fundCode)
            fund_code = fund_code[:6]  # 有些fund需要清洗

            print('fund_code',fund_code) # 999901
            try:
                if len(fund_code) == 6:
                # if len(fund_code) > 6:
                #     fund_code = fund_code[:6]
                # 非潽蓝基金
                #     select.select_by_index(index + 2 + position_delay)
                # 潽蓝基金
                    select.select_by_visible_text(fundCode)
                    self.random_sleep(3,5)
                    self.wait_until(driver=driver, selector_name="//button[@id='lblCIEdit']")
                    self.random_sleep(5,7)
                    driver.switch_to.window(driver.window_handles[1])
                    self.random_sleep()
                    self.wait_until(driver=driver, selector_name="//textarea[@id='txtPrices']")
                    # ctrl+end
                    driver.find_element_by_id("txtPrices").send_keys(Keys.CONTROL,Keys.END)
                    # # ↓
                    # driver.find_element_by_id("txtPrices").send_keys(Keys.ARROW_DOWN)
                    self.random_sleep()
                    ANAV = self.wait_until(driver=driver, selector_name="//textarea[@id='txtPrices']",action='text')
                    # print('-16',ANAV[-16:])
                    enter_split = ANAV.split('\n')[-1]
                    print('enter split',enter_split)
                    # try:
                    #     year_or_day = ANAV.split('\n')[-1].split('/')[0]
                    #     flag = '/'
                    # except:
                    #     try:
                    #         year_or_day = ANAV.split('\n')[-1].split('-')[0]
                    #         flag = '-'
                    #     except:
                    #         year_or_day = ANAV.split('\n')[-1].split('.')[0]
                    #         flag = '.'

                    if '/' in enter_split:
                        year_or_day = enter_split.split('/')[0]
                        flag = '/'
                    elif '-' in enter_split:
                        year_or_day = enter_split.split('-')[0]
                        flag = '-'
                    elif '.' in enter_split:
                        year_or_day = enter_split.split('.')[0]
                        flag = '.'
                    else:
                        year_or_day = ''
                        flag = '/'
                        print('year_or_day_____error!')
                    print('year_or_day',year_or_day)

                    if len(year_or_day) == 2:
                        print('dd%sMM%syyyy'%(flag,flag))
                        format0 = 'dd_MM_yyyy'
                        dd = ANAV.split('\n')[-1].split(flag)[0]
                        mm = ANAV.split('\n')[-1].split(flag)[1]
                        yyyy = ANAV.split('\n')[-1].split(flag)[2][0:4]
                    elif len(year_or_day) == 4:
                        print('yyyy%sMM%sdd'%(flag,flag))
                        format0 = 'yyyy_MM_dd'
                        yyyy = ANAV.split('\n')[-1].split(flag)[0]
                        mm = ANAV.split('\n')[-1].split(flag)[1]
                        dd = ANAV.split('\n')[-1].split(flag)[2][0:2]
                    else:
                        format0 = 'yyyy_MM_dd'
                        yyyy = '2000'
                        mm = '01'
                        dd = '01'
                        print('错误！')

                    date = yyyy+'-'+mm+'-'+dd
                    print('last_date',date)
                    # 潽蓝fund_code
                    if fund_code == '999901':
                        fund_code='Plan01'
                    elif fund_code == '999902':
                        fund_code='Plan02'
                    elif fund_code == '999903':
                        fund_code='Plan03'
                    elif fund_code == '999904':
                        fund_code='Plan04'
                    elif fund_code == '999905':
                        fund_code='Plan05'
                    elif fund_code == '999906':
                        fund_code='Plan06'
                    elif fund_code == '999907':
                        fund_code='Plan07'
                    elif fund_code == '999908':
                        fund_code='Plan08'
                    elif fund_code == '999909':
                        fund_code='Plan09'
                    elif fund_code == '999910':
                        fund_code='Plan10'
                    print('Plan_fund_code', fund_code)

                    result = self.read_from_mysql(fund_code,date)
                    add_part = ''
                    for data in result:
                        add = str(data[1]).split('-')[2]+flag+str(data[1]).split('-')[1]+flag+str(data[1]).split('-')[0] +' '+str(data[2])[:5]+ '\n'if format0 =='dd_MM_yyyy' else str(data[1]).split('-')[0]+flag+str(data[1]).split('-')[1]+flag+str(data[1]).split('-')[2] +' '+str(data[2])[:5]+ '\n'
                        add_part += add
                    print('add_part\n',add_part)
                    print('fund_code',fund_code)
                    self.wait_until(driver=driver, selector_name="//textarea[@id='txtPrices']", action='send_keys',send_keys=add_part)
                    self.random_sleep(5,7)
                    self.wait_until(driver=driver, selector_name="//div[@class='ToolBar']//a[@class='button pinned'][1]")
                    self.random_sleep(5,10)
                    self.wait_until(driver=driver, selector_name="//div[@class='ui-dialog-buttonset']//button[1]")
                    self.random_sleep(5,7)
                    self.wait_until(driver=driver, selector_name="//div[@class='ui-dialog ui-widget ui-widget-content ui-corner-all ui-draggable ui-dialog-buttons'][2]//div[@class='ui-dialog-buttonset']//button[1]")
                    # print('ANAV',ANAV)
                    self.random_sleep(5,7)
                    print(fund_code,'完成')
                    driver.save_screenshot(
                        'succeed_screenshot/' + str(fund_code) + ".png")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except:
                driver.save_screenshot(
                    'failed_screenshot/' + str(fund_code) + ".png")
                print(fund_code,'这个fund上传数据失败')
                if len(driver.window_handles) >= 2:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])

        print('程序结束！')
        self.mysql_client.close()
        self.random_sleep()
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element_by_xpath("//a[@class='menu-close'][2]").click()
        driver.quit()

    def random_sleep(self, least=1, most=1):
        """
        随机休眠一段时间
        :return: No
        """
        time.sleep(random.randint(least, most))

    def wait_until(self, driver, selector_name, selector_way='XPATH', action='click',
                   send_keys=None):
        """
            显式等待延迟 + 元素操作事件
        :param driver: 浏览器对象
        :param selector_name: 操作节点名称
        :param selector_way: 操作节点方式
        :param action: 操作节点的事件
        :param send_keys: 模拟键盘输入keys
        :return:
        """
        if self.error == 1:
            return
        selector = By.XPATH
        find_element = driver.find_element_by_xpath(selector_name)
        if selector_way == 'ID':
            selector = By.ID
            find_element = driver.find_element_by_id(selector_name)
        elif selector_way == 'CLASS_NAME':
            selector = By.CLASS_NAME
            find_element = driver.find_element_by_class_name(selector_name)
        elif selector_way == 'LINK_TEXT':
            selector = By.LINK_TEXT
            find_element = driver.find_element_by_link_text(selector_name)
        try:
            # 页面一直循环，直到 id="myDynamicElement" 出现
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((selector, selector_name)))
        except Exception as e:
            self.error = 1
            print('调仓失败截图失败！',e)
            # driver.save_screenshot('调仓失败截图文件夹/WAIT_UNTIL/' + str(self.policyNumber) + str(self.riskType) + ".png")
            # if platform == 'Hansard':
            #     self.write_excel(policy_index=self.Hansard_index[self.enum_index], message='调仓失败')
            # elif platform == 'ITA':
            #     self.write_excel(policy_index=self.ITA_index[self.enum_index], message='调仓失败')
            # elif platform == 'zurich':
            #     self.write_excel(policy_index=self.zurich_index[self.enum_index], message='调仓失败')
            # elif platform == 'standard_life':
            #     self.write_excel(policy_index=self.standard_life_index[self.enum_index], message='调仓失败')
            # elif platform == 'axa':
            #     self.write_excel(policy_index=self.axa_index[self.enum_index], message='调仓失败')
            #
            # print(str(self.policyNumber) + str(self.riskType), '：error!调仓失败！', action + ':' + selector_name)
            # driver.close()
        else:
            if action == 'click':
                find_element.click()
            elif action == 'clear':
                find_element.clear()
            elif action == 'send_keys':
                find_element.send_keys(str(send_keys))
            elif action == 'text':
                return find_element.text
        finally:
            self.random_sleep()

if __name__ == '__main__':
    fe_data = FEDataUpload()
    fe_data.start_work()