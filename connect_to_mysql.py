# -*- coding:utf-8 -*- 
import pymysql

def main():
    mysql_client = pymysql.connect(host='120.55.96.145', port=3306, user='plandev', password='planner1105',
                                   database='data_finance', charset='utf8')

    try:
        # 使用cursor()方法获取操作游标
        cur = mysql_client.cursor()
        # code = '002196'
        # date = "2017-06-30"
        # count = cur.execute("select * from 财务报表 where Fund_code="+"'"+code+"'"+" and Financial_index_date="+"'"+date +"'"+";")
        count1 = cur.execute("ALTER TABLE 科学研究和技术服务业行业市盈率 DROP id;")
        count2 = cur.execute("ALTER  TABLE 科学研究和技术服务业行业市盈率 ADD id MEDIUMINT( 8 ) NOT NULL  FIRST;")
        count3 = cur.execute("ALTER  TABLE 科学研究和技术服务业行业市盈率 MODIFY COLUMN id MEDIUMINT( 8 ) NOT NULL  AUTO_INCREMENT,ADD PRIMARY  KEY(id);")
        print(count1)
        print(count2)
        print(count3)
        # print(cur.fetchall())
        # cur.execute("insert into 交通运输、仓储和邮政业行业市盈率(id,date,static_PE) VALUES(%s,%s,%s)",
        #             (int(flag), int((int(item[0]) / 1000)), float(item[1])))
        # cur.execute("update 交通运输、仓储和邮政业行业市盈率 set dynamic_PE=%s where id=%s", (float(item[1]), int(flag)))
        # cur.execute("delete from 制造业行业市盈率 where id > 245")
        # print('正在插入第%s条数据...' % flag)
        cur.close()
    except pymysql.Error as e:
        print(e)
    # finally:
        # print(int((int(i) / 1000)))
        # 关闭本次操作

    # 提交sql事务
    mysql_client.commit()
    mysql_client.close()
    # print('操作完成！共%s条数据.' % (flag - 1))


if __name__ == "__main__":
    main()