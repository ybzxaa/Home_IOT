#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 21:30:43 2019

@author: jason
"""


import sys
import web
import json
import pymysql

mysql_host='127.0.0.1'
mysql_port=3306
mysql_db='digithouse'
mysql_user='dhouse'
mysql_pwd='ybzx1008'
mysql_charset='utf8'

urls = ('/', 'index',
        '/get_rate','get_rate',
        '/get_introimages','get_introimages'
)
app = web.application(urls, globals())

class index:
    def GET(self):

        return "OK!"

class get_rate:
    def GET(self):

        i=web.input()

        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        query = 'select a.time_id, a.name,a.code,a.hui_out as icbc, b.hui_out as boc, c.hui_out as cmbchina, d.hui_out as bankcomm '
        query = query+' from rate a '
        query = query+' left join rate b on a.name=b.name '
        query = query+' left join rate c on a.name=c.name '
        query = query+' left join rate d on a.name=d.name '
        query = query+" where a.bank='icbc' and b.bank='boc' and c.bank='cmbchina' and d.bank='bankcomm' and a.time_id="
        query = query+str(i.time_id)
        query = query+" and b.time_id="
        query = query+str(i.time_id)
        query = query+" and c.time_id="
        query = query+str(i.time_id)
        query = query+" and d.time_id="
        query = query+str(i.time_id)

        print(query)

        cursor.execute(query)
        data=cursor.fetchall()

        cursor.close()
        conn.close()

        jsonData=[]

        for row in data:
            re={}
            re['time_id']=row[0]
            re['name']=row[1]
            re['code']=row[2]
            re['icbc']=row[3]
            re['boc']=row[4]
            re['cmbchina']=row[5]
            re['bankcomm']=row[6]
            jsonData.append(re)


        jsonStr=json.dumps(jsonData, ensure_ascii=False)



        return jsonStr

class get_introimages:
    def GET(self):
        i=web.input()

        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        query = 'select *  from intro_imgs order by id asc'

        print(query)

        cursor.execute(query)
        data=cursor.fetchall()

        cursor.close()
        conn.close()

        jsonData=[]

        for row in data:
            re={}
            re['id']=row[0]
            re['url']=row[1]
            jsonData.append(re)


        jsonStr=json.dumps(jsonData, ensure_ascii=False)



        return jsonStr

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
