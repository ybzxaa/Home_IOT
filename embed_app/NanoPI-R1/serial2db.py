# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 20:53:28 2019

@author: jason
"""
from bs4 import BeautifulSoup
#from email.mime.text import MIMEText
#import smtplib
import requests
import serial
import threading
#import binascii
from datetime import datetime
import time
#import struct
import csv
import json
import pymysql
import paho.mqtt.client as mqtt
import os,sys
import re
import psutil

mysql_host='127.0.0.1'
mysql_port=3306
mysql_db='home_dev'
mysql_user='mqttr1'
mysql_pwd='ybzx1008'
mysql_charset='utf8'

i_ip=''

dev_cfg={}
envdata_pub={}
cam_cfg=[]
hw_info={}

serialPort = ''  # 串口
baudRate = 0  # 波特率
is_exit=False
data_bytes=bytearray()


sql_h24="select date_format(createdtime, '%d-%H') as time, round(avg(co2)) as co2,round(avg(ch20)) as ch20," \
                   "round(avg(tvoc)) as tvoc,round(avg(pm25)) as pm25,round(avg(pm10)) as pm10," \
                   "round(avg(humi)) as humi,round(avg(temp)) as temp " \
                   "from envdata where createdtime >=NOW()- interval 24 hour " \
                   "group by time  order by time"


sql_m30="select date_format(createdtime, '%d') as time, round(avg(co2)) as co2,round(avg(ch20)) as ch20," \
                   "round(avg(tvoc)) as tvoc,round(avg(pm25)) as pm25,round(avg(pm10)) as pm10," \
                   "round(avg(humi)) as humi,round(avg(temp)) as temp " \
                   "from envdata where createdtime >=NOW()- interval 30 day " \
                   "group by time  order by time"


sql_y12="select date_format(createdtime, '%m') as time, round(avg(co2)) as co2,round(avg(ch20)) as ch20," \
                   "round(avg(tvoc)) as tvoc,round(avg(pm25)) as pm25,round(avg(pm10)) as pm10," \
                   "round(avg(humi)) as humi,round(avg(temp)) as temp " \
                   "from envdata where createdtime >=NOW()- interval 12 month " \
                   "group by time  order by time"

# 获取外网IP
def get_out_ip():
    internet_ip=''
    try:
        req=requests.get("http://2019.ip138.com/ic.asp")
        txt = req.text
        ip=re.findall(r'\d+.\d+.\d+.\d+',txt)
        #ip = re.search(r'(\d+\.\d+\.\d+\.\d+)',r.text).group(1)
        internet_ip= ip[0]
    except:
         internet_ip=''

    return internet_ip


def isRunning(process_name):
    try:
        process=len(os.popen('ps -aux |grep "'+process_name +'" |grep -v grep').readline())
        if process>=1:
            return True
        else:
            return False
    except:
        #print("check process error!!!")
        return False

def keep_onRunning():
    global i_ip

    while not is_exit:

        i_ip=get_out_ip()

        isrunning=isRunning("nginx")
        if isrunning==False:
            try:
                os.system("/usr/local/nginx/sbin/nginx")
            except:
                print("start nginx faild ...........")
        else:
            print("nginx is running,no need restart...........")


        for row in cam_cfg:
            isrunning=isRunning(row['cam_ip'])
            if isrunning==False:
                try:
                    cam_str="ffmpeg -i "+row['stream']

                    cam_str=cam_str +" -v error -c copy -f hls -hls_time 5.0 -hls_list_size 0 -hls_wrap 5 /opt/hls/live_"

                    cam_str=cam_str+str(row['cam_No'])+".m3u8 &"
                    #print(cam_str)
                    os.system(cam_str)

                except:
                    print("ffmpeg -i rtsp://"+row['cam_ip']+" is faild...........")
            else:
                print("ffmpeg"+ row['cam_ip'] +"is running,no need restart...........")


        time.sleep(300)



def get_config():

    global dev_cfg
    global cam_cfg

    conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
    cursor = conn.cursor()

    query = 'select * from dev limit 1'
    #print(query)

    cursor.execute(query)
    data=cursor.fetchall()

    #print(data)

    for row in data:
        dev_cfg['dev_id']=row[0]
        dev_cfg['dev_name']=row[1]
        dev_cfg['dev_ip']=row[2]
        dev_cfg['dev_info']=row[3]
        dev_cfg['mqtt_server_name']=row[4]
        dev_cfg['mqtt_server_port']=row[5]
        dev_cfg['mqtt_user']=row[6]
        dev_cfg['mqtt_pwd']=row[7]
        dev_cfg['com']=row[8]
        dev_cfg['baudRate']=row[9]
        dev_cfg['sock_port']=row[10]
        dev_cfg['ssh_port']=row[11]
        dev_cfg['http_port']=row[12]
        dev_cfg['gateway']=row[13]
        dev_cfg['dns']=row[14]
        dev_cfg['inet_ip']=i_ip

    #print(dev_cfg)

    query = 'select * from cam'

    cursor.execute(query)
    data=cursor.fetchall()

    for row in data:
        re={}
        re['cam_No']=row[0]
        re['cam_ip']=row[1]
        re['cam_label']=row[2]
        re['cam_info']=row[3]
        re['stream']=row[4]
        cam_cfg.append(re)

    #print(cam_cfg)

    cursor.close()
    conn.close()

class SerialPort:
    def __init__(self, port, buand):
        try:
            self.port = serial.Serial(port, buand, timeout=1)
            self.port.close()
            if not self.port.isOpen():
                self.port.open()
        except:
            print('cant open serial port')

    def port_open(self):
        if not self.port.isOpen():
            self.port.open()

    def port_close(self):
        self.port.close()

    def send_data(self):
        self.port.write('')

    def read_data(self):
        global is_exit
        global data_bytes
        global envdata_pub
        while not is_exit:
            count = self.port.inWaiting()
            if count > 0:
                rec_str = self.port.read(count)
                data_bytes=rec_str

                data_tol=0
                data_len=len(data_bytes)
                #print('当前数据接收总字节数：'+str(data_len)+' 本次接收字节数：'+str(len(rec_str)))
                #print(str(datetime.now()),':',binascii.b2a_hex(rec_str))

                if data_len==17:
                    for i in  range(data_len-1):
                        # print(data_bytes[i])
                         data_tol=data_tol+data_bytes[i]

                   # print('data_bytes[data_len-1]='+str(data_bytes[data_len-1]))
                   # print('data_tol='+str(data_tol))
                    if data_bytes[data_len-1]==data_tol%256 and data_bytes[0]==0x3c and data_bytes[1]==0x02:

                        envdata_pub['env_co2']=data_bytes[2]*256+data_bytes[3]
                        envdata_pub['env_ch20']=data_bytes[4]*256+data_bytes[5]
                        envdata_pub['env_tvoc']=data_bytes[6]*256+data_bytes[7]
                        envdata_pub['env_pm25']=data_bytes[8]*256+data_bytes[9]
                        envdata_pub['env_pm10']=data_bytes[10]*256+data_bytes[11]

                        if data_bytes[12]<128:
                            h_tmp=data_bytes[12];
                            l_tmp=data_bytes[13];
                            envdata_pub['env_temp']=h_tmp+l_tmp*0.1;
                        else:
                            h_tmp=data_bytes[12]-128;
                            l_tmp=data_bytes[13]*0.1;
                            envdata_pub['env_temp']=-(h_tmp+l_tmp);

                        envdata_pub['env_humi']=data_bytes[14]+data_bytes[15]*0.1;


                   # print(envdata_pub)
            time.sleep(0.1)




class Mqtt_Process:
    def __init__(self):

        client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        self.client = mqtt.Client(client_id) # ClientId不能重复，所以使用当前时间


    def client_loop(self):
        self.client.username_pw_set(dev_cfg['mqtt_user'], dev_cfg['mqtt_pwd']) # 必须设置，否则会返回「Connected with result code 4」
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print(dev_cfg['mqtt_server_name']+'   '+str(dev_cfg['mqtt_server_port']))
        self.client.connect(dev_cfg['mqtt_server_name'], dev_cfg['mqtt_server_port'], 60)
        self.client.loop_start()

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        str1=dev_cfg['dev_id']+'_req'
        print(str1)
        self.client.subscribe(str1)


    def on_message(self,client, userdata, msg):
        print(msg.topic+" "+msg.payload.decode())
        msg1=msg.topic + "," + msg.payload.decode()
        #print(msg1)

        if 'password' in  msg1:
            send_msg={}
            str1=msg1.split(':')
            #print(str1[1]+ " " + dev_cfg['dev_name'])

            if str1[1]==dev_cfg['dev_name']:
                send_msg['is_auth']=1
                send_msg['dev']=dev_cfg
                send_msg['cam']=cam_cfg

            else:
                send_msg['is_auth']=0

           # print(json.dumps(send_msg))

            self.client.publish(dev_cfg['dev_id']+"_auth", json.dumps(send_msg))

        if 'reset' in  msg1:
            self.client.publish(dev_cfg['dev_id']+"_rebooting", "1")
            time.sleep(5)
            os.popen('reboot')



        if ('avg_h2400' in  msg1) or ('avg_month' in  msg1) or ('avg_year0' in  msg1):
            conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
            cursor = conn.cursor()

            #print(sql_h24)
            if 'avg_h2400' in  msg1:
                cursor.execute(sql_h24)

            if 'avg_month' in  msg1:
                cursor.execute(sql_m30)

            if 'avg_year0' in  msg1:
                cursor.execute(sql_y12)


            data=cursor.fetchall()

            #print(data)

            sendmsg1={}
            p_date=[]
            p_co2=[]
            p_ch20=[]
            p_tvoc=[]
            p_pm10=[]
            p_pm25=[]
            p_humi=[]
            p_temp=[]

            i=0
            for row in data:
                p_date.append(row[0])
                p_co2.append(row[1])
                p_ch20.append(row[2])
                p_tvoc.append(row[3])
                p_pm10.append(row[4])
                p_pm25.append(row[5])
                p_humi.append(row[6])
                p_temp.append(row[7])

                i=i+1

            sendmsg1['date']=p_date
            sendmsg1['co2']=p_co2
            sendmsg1['ch20']=p_ch20
            sendmsg1['tvoc']=p_tvoc
            sendmsg1['pm10']=p_pm10
            sendmsg1['pm25']=p_pm25
            sendmsg1['humi']=p_humi
            sendmsg1['temp']=p_temp

            #print(sendmsg1)

            cursor.close()
            conn.close()


            if 'avg_h2400' in  msg1:
                self.client.publish(dev_cfg['dev_id']+"_h24", json.dumps(sendmsg1))

            if 'avg_month' in  msg1:
                self.client.publish(dev_cfg['dev_id']+"_m30", json.dumps(sendmsg1))

            if 'avg_year0' in  msg1:
                self.client.publish(dev_cfg['dev_id']+"_y12", json.dumps(sendmsg1))

        if 'system' in  msg1:
            global hw_info
            f=open("/sys/class/thermal/thermal_zone0/temp",'r')
            cpu_temp=float(f.readline())/1000

            hw_info['cpu_temp']=round(cpu_temp,1)

            cpu_usage=psutil.cpu_percent()

            hw_info['cpu_usage']=round(cpu_usage,1)

            mem_usage=psutil.virtual_memory()

           # print(mem_usage)

            hw_info['mem_total']=int(mem_usage.total/1024/1024)
            hw_info['mem_used']=int(mem_usage.active/1024/1024)

           # print(psutil.disk_usage('/'))

            disk_usage=psutil.disk_usage('/')

            hw_info['disk_total']=round(disk_usage.total/1024/1024/1024,1)
            hw_info['disk_used']=round(disk_usage.used/1024/1024/1024,1)

            interval = 1                        # 每隔 interval 秒获取一次网络IO信息, 数值越小, 测得的网速越准确
            k = 1024                            # 一 K 所包含的字节数
            m = 1048576                         # 一 M 所包含的字节数

            byteSent1 = io_get_bytes(sent=True)  # 获取开机以来上传的字节数
            byteRecv1 = io_get_bytes(recv=True)  # 获取开机以来下载的字节数
            time.sleep(interval)                           # 间隔 interval 秒

            byteSent2 = io_get_bytes(sent=True)  # 再次获取开机以来上传的字节数
            byteRecv2 = io_get_bytes(recv=True)  # 再次获取开机以来下载的字节数
            sent = byteSent2-byteSent1                     # interval 秒内所获取的上传字节数
            recv = byteRecv2-byteRecv1                     # interval 秒内所获取的下载字节数
            unit = 'B/秒'                 # 显示的速度单位, 每次显示前重置单位为( 字节(B)/秒(S) )
            if sent > m or recv > m :             # 字节数达到 m 级别时以 M 作为单位
                sent = sent / m
                recv = recv / m
                unit = 'M/秒'
            if sent > k or recv > k:              # 字节数达到 k 级别时以 K 作为单位
                sent = sent / k
                recv = recv / k
                unit = 'K/秒'
            #print('上传速度: %5d %s' %(int(sent),unit))
            #print('下载速度: %5d %s' %(int(recv),unit))

            hw_info['net_unit']=unit
            hw_info['net_send']=int(sent)
            hw_info['net_recv']=int(recv)

            boot_time = psutil.boot_time() # 返回时间戳 # 将时间戳转换为datetime类型的时间2019-01-15 08:59:01
            boot_time_obj = datetime.fromtimestamp(boot_time) # print(type(boot_time_obj))
            now_time = datetime.now()
            delta_time = now_time - boot_time_obj #
            #print(type(delta_time))
            #print("开机时间: ", boot_time_obj)
            #print("当前时间: ", str(now_time).split('.')[0]) # str是为了将对象转换为字符串， 实现分离; # split分离是为了去掉毫秒
            #print("开机时长: ", str(delta_time).split('.')[0]) # split分离是为了去掉毫秒


            #print(str(delta_time.days))

            s_days=delta_time.days

            s_hours_temp=str(delta_time).split(':')

            s_hours=int(s_hours_temp[0])%24


            #print(str(s_hours))

            hw_info['s_days']=s_days
            hw_info['s_hours']=s_hours

            #print(hw_info)

            self.client.publish(dev_cfg['dev_id']+"_sysinfo", json.dumps(hw_info))




    def pub_envdata(self):
        global is_exit
        global dev_cfg
        global envdata_pub
        #print('-------------------------------------------------------------------------------------------------------------')
        while not is_exit:
            self.client.publish(dev_cfg['dev_id'], json.dumps(envdata_pub))
           # print(envdata_pub)

            time.sleep(3)


########
# 获取开机以来 接收/发送 的字节数
# 依赖: psutil 库
# 参数(sent): Ture--返回发送的字节数 , False--不返回
# 参数(recv): Ture--返回接收的字节数 , False--不返回
# 两个参数都为(True): 返回包含 接收/发送 字节数的列表
# 函数失败返回: None
def io_get_bytes(sent=False,recv=False):
    internet = psutil.net_io_counters()  # 获取与网络IO相关的信息
    if internet == None:                 # 如果获取IO信息失败
        return None
    io_sent = internet.bytes_sent        # 开机以来发送的所有字节数
    io_recv = internet.bytes_recv        # 开机以来接收的所有字节数
    if sent == True and recv == True :
        return [io_sent,io_recv]
    elif sent == True:
        return io_sent
    elif recv == True:
        return io_recv
    else:
        return None                      # 参数不正确, 返回None


def write_envdata():
    global envdata_pub
    global i_ip
    while not is_exit:
        if not ('env_co2' in envdata_pub.keys()) or not ('env_humi' in envdata_pub.keys()):
            time.sleep(5*60)
            continue

        if envdata_pub['env_co2']>0 and envdata_pub['env_humi']>0:
           conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
           cursor = conn.cursor()
           query = "replace into envdata(devid,co2,ch20,tvoc,pm25,pm10,humi,temp) values('"
           query=query + dev_cfg['dev_id']+ "',"
           query=query + str(envdata_pub['env_co2'])+ ","
           query=query + str(envdata_pub['env_ch20'])+","
           query=query + str(envdata_pub['env_tvoc'])+","
           query=query + str(envdata_pub['env_pm25'])+","
           query=query + str(envdata_pub['env_pm10'])+","
           query=query + str(envdata_pub['env_humi'])+","
           query=query + str(envdata_pub['env_temp'])+")"

           #print(query)
           cursor.execute(query)
           conn.commit()  #只要是修改了表内容
           cursor.close()
           conn.close()


        time.sleep(5*60)

if __name__ == '__main__':

    i_ip=get_out_ip()

    get_config()


    serialPort = dev_cfg['com']  # 串口
    baudRate = dev_cfg['baudRate']  # 波特率
    #打开串口
    mSerial = SerialPort(serialPort, baudRate)

    #开始数据读取线程
    t1 = threading.Thread(target=mSerial.read_data)
    t1.setDaemon(True)
    t1.start()

    mqtt_process= Mqtt_Process()
    mqtt_process.client_loop()
    t2 = threading.Thread(target=mqtt_process.pub_envdata)
    t2.setDaemon(True)
    t2.start()

    t3 = threading.Thread(target=write_envdata)
    t3.setDaemon(True)
    t3.start()

    t4 = threading.Thread(target=keep_onRunning)
    t4.setDaemon(True)
    t4.start()



    while not is_exit:

        i_ip=get_out_ip()

        time.sleep(600)

        #if data_len==17:
       #     print(str(data_bytes[0]))
