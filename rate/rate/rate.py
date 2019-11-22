# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 21:57:56 2019

@author: jason
"""

import requests
from ShowapiRequest import ShowapiRequest
import time 
import datetime
import json
import pymysql

mysql_host='127.0.0.1'
mysql_port=3306
mysql_db='digithouse'
mysql_user='dhouse'
mysql_pwd=''
mysql_charset='utf8'

va=''

def print_keyvalue_by_key(input_json,key):
    global va
    key_value=''
    if isinstance(input_json,dict):
        for json_result in input_json.values():
            if key in input_json.keys():
                key_value = input_json.get(key)
            else:
                print_keyvalue_by_key(json_result,key)
    elif isinstance(input_json,list):
        for json_array in input_json:
            print_keyvalue_by_key(json_array,key)
    if key_value!='':
        # print(key_value)
        va=va+str(key_value)


time_id = time.strftime('%Y%m%d',time.localtime(time.time()))
print(time_id)

conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
cursor = conn.cursor()
        
url="http://route.showapi.com/105-32"
r = ShowapiRequest(url, '96868','f3b213d1467f4616bc12f45162b731a8')

bank_code='icbc'
r.addBodyPara("bankCode", bank_code)
res = r.post()
result=json.loads(res.text) # 返回信息
print_keyvalue_by_key(result,'codeList')
a=eval(va)
for b in a:
    if(b['name']=='澳大利亚元' or b['name']=='新西兰元' or b['name']=='美元'
     or b['name']=='欧元' or b['name']=='日元' or b['name']=='港币' ):
        print(b['name']+str(b['hui_out']))
        query = 'replace into rate(time_id,bank,name,code,hui_in,chao_in,hui_out,chao_out) values('               
        query=query+str(time_id)+",'"     
        query=query+bank_code+"','"
        query=query+str(b['name'])+"','"
        query=query+str(b['code'])+"',"       
        query=query+str(b['hui_in'])+","     
        query=query+str(b['chao_in'])+","
        query=query+str(b['hui_out'])+","
        query=query+str(b['chao_out'])+")"
         
        print(query)        
        cursor.execute(query)
        conn.commit() #只要是修改了表内容   
        
va=''
bank_code='boc'
r.addBodyPara("bankCode", bank_code)
res = r.post()
result=json.loads(res.text) # 返回信息
print_keyvalue_by_key(result,'codeList')
a=eval(va)
for b in a:
    if(b['name']=='澳大利亚元' or b['name']=='新西兰元' or b['name']=='美元'
     or b['name']=='欧元' or b['name']=='日元' or b['name']=='港币' ):
        print(b['name']+str(b['hui_out']))
        query = 'replace into rate(time_id,bank,name,code,hui_in,chao_in,hui_out,chao_out) values('               
        query=query+str(time_id)+",'"     
        query=query+bank_code+"','"
        query=query+str(b['name'])+"','"
        query=query+str(b['code'])+"',"       
        query=query+str(b['hui_in'])+","     
        query=query+str(b['chao_in'])+","
        query=query+str(b['hui_out'])+","
        query=query+str(b['chao_out'])+")"
         
        print(query)        
        cursor.execute(query)
        conn.commit() #只要是修改了表内容      
        
va=''
bank_code='cmbchina'
r.addBodyPara("bankCode", bank_code)
res = r.post()
result=json.loads(res.text) # 返回信息
print_keyvalue_by_key(result,'codeList')
a=eval(va)
for b in a:
    if(b['name']=='澳大利亚元' or b['name']=='新西兰元' or b['name']=='美元'
     or b['name']=='欧元' or b['name']=='日元' or b['name']=='港币' ):
        print(b['name']+str(b['hui_out']))
        query = 'replace into rate(time_id,bank,name,code,hui_in,chao_in,hui_out,chao_out) values('               
        query=query+str(time_id)+",'"     
        query=query+bank_code+"','"
        query=query+str(b['name'])+"','"
        query=query+str(b['code'])+"',"       
        query=query+str(b['hui_in'])+","     
        query=query+str(b['chao_in'])+","
        query=query+str(b['hui_out'])+","
        query=query+str(b['chao_out'])+")"
         
        print(query)        
        cursor.execute(query)
        conn.commit() #只要是修改了表内容      
        
va=''
bank_code='bankcomm'
r.addBodyPara("bankCode", bank_code)
res = r.post()
result=json.loads(res.text) # 返回信息
print_keyvalue_by_key(result,'codeList')
a=eval(va)
for b in a:
    if(b['name']=='澳大利亚元' or b['name']=='新西兰元' or b['name']=='美元'
     or b['name']=='欧元' or b['name']=='日元' or b['name']=='港币' ):
        print(b['name']+str(b['hui_out']))
        query = 'replace into rate(time_id,bank,name,code,hui_in,chao_in,hui_out,chao_out) values('               
        query=query+str(time_id)+",'"     
        query=query+bank_code+"','"
        query=query+str(b['name'])+"','"
        query=query+str(b['code'])+"',"       
        query=query+str(b['hui_in'])+","     
        query=query+str(b['chao_in'])+","
        query=query+str(b['hui_out'])+","
        query=query+str(b['chao_out'])+")"
         
        print(query)        
        cursor.execute(query)
        conn.commit() #只要是修改了表内容      
        
        
        
        
        
        
        
        
        
