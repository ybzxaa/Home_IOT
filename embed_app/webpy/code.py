#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys

import web
#from web import form
import pymysql
import os

mysql_host='127.0.0.1'
mysql_port=3306
mysql_db='home_dev'
mysql_user='mqttr1'
mysql_pwd='ybzx1008'
mysql_charset='utf8'




render = web.template.render('templates/')



urls = ('/', 'index',
        '/reboot','reboot',
        '/dev_modify','dev_modify',
        '/refresh','refresh',
        '/cam_add1','cam_add1',
        '/cam_add2','cam_add2',
        '/cam_del','cam_del',
        '/cam_edit','cam_edit',
        '/cam_modify','cam_modify'
)
app = web.application(urls, globals())

class reboot:
    def POST(self):
        #os.system("killall -9 mqtt_server")
        os.system("killall -9 ffmpeg")
        os.system("killall -9 create_ap")
        os.system("reboot")

class index:
    def GET(self):
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        cursor.execute("select * from  dev")
        dev_data=cursor.fetchall()
        print(dev_data)

        cursor.execute("select * from  cam order by id asc")
        cam_data=cursor.fetchall()

        cursor.close()
        conn.close()

       # env_data=cur1.execute("select * from  envdata order by id desc limit 10").fetchall()

       # count=cur2.execute("select count(*) as count  from  envdata")


        return render.form(dev_data,cam_data)

class dev_modify:
    def POST(self):
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        i=web.input()
        sql="update dev set ";
        sql=sql+"dev_name='"+i.dev_name+"',"
        sql=sql+"dev_ip='"+i.dev_ip+"',"
        sql=sql+"dev_info='"+i.dev_info+"',"
        sql=sql+"com='"+i.com+"',"
        sql=sql+"baudRate='"+i.baudRate+"',"
        sql=sql+"ssh_port='"+i.ssh_port+"',"
        sql=sql+"http_port='"+i.http_port+"',"
        sql=sql+"gateway='"+i.gateway+"',"
        sql=sql+"dns='"+i.dns+"' "
        sql=sql+"where dev_id='"+i.dev_id+"'"

        print(sql)

        cursor.execute(sql)
        conn.commit()  #只要是修改了表内容

        cursor.close()
        conn.close()

        os.system("sudo mv /etc/network/interfaces /etc/network/interfaces.1")

        f= open("/etc/network/interfaces",'w')
        f.write('auto lo\n')
        f.write('iface lo inet loopback\n')

        f.write('\n')
        f.write('auto eth0\n')
        f.write('iface eth0 inet dhcp\n')

        f.write('\n')

        f.write('allow-hotplug eth1\n')
        f.write('iface eth1 inet static\n')
        f.write('address '+i.dev_ip+'\n')
        f.write('netmask 255.255.255.0\n')
        f.write('gateway '+i.gateway+'\n')
        f.write('dns-nameservers '+i.dns+'\n')


        f.close()

        os.system("sudo mv /opt/setdns.sh /opt/setdns.sh.1")


        f1=open("/opt/setdns.sh",'w')
        f1.write('rm -f /etc/resolv.conf\n')
        f1.write('touch /etc/resolv.conf\n')
        f1.write('echo "nameserver '+i.dns+'" >> /etc/resolv.conf\n')

        f1.close()

        os.system("sudo chmod +x /opt/setdns.sh")


        raise web.seeother('/')

class refresh:
    def POST(self):

        raise web.seeother('/')

class cam_edit:
    def POST(self):
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        i=web.input()

        sql="select * from  cam where id="+i.cam_id
        #print(sql)
        cursor.execute(sql)
        cam_data1=cursor.fetchall()

        cursor.close()
        conn.close()

        return render.camedit(cam_data1)

class cam_modify:
    def POST(self):
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        i=web.input()
        sql="update cam set ";
        sql=sql+"cam_ip='"+i.cam_ip+"',"
        sql=sql+"cam_label='"+i.cam_label+"',"
        sql=sql+"cam_info='"+i.cam_info+"',"
        sql=sql+"stream='"+i.stream+"' "
        sql=sql+"where id="+i.id

        #print(sql)
        cursor.execute(sql)
        conn.commit()  #只要是修改了表内容

        cursor.close()
        conn.close()

        raise web.seeother('/')

class cam_add1:
    def POST(self):
        return render.camadd()

class cam_add2:
    def POST(self):
        try:
            conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
            cursor = conn.cursor()

            i=web.input()
            sql="insert into cam values("
            sql=sql+i.cam_id+","
            sql=sql+"'"+i.cam_ip+"',"
            sql=sql+"'"+i.cam_label+"',"
            sql=sql+"'"+i.cam_info+"',"
            sql=sql+"'"+i.stream+"')"

        #print(sql)

            cursor.execute(sql)
            conn.commit()  #只要是修改了表内容

            cursor.close()
            conn.close()

            raise web.seeother('/')
        except:
            print('cant open serial port')

class cam_del:
    def POST(self):
        conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd, database=mysql_db, charset=mysql_charset)
        cursor = conn.cursor()

        i=web.input()
        sql="delete from cam  ";
        sql=sql+"where id="+i.cam_id

        #print(sql)

        cursor.execute(sql)
        conn.commit()  #只要是修改了表内容

        cursor.close()
        conn.close()

        raise web.seeother('/')

  #  def POST(self):
  #      form = myform()
  #      if not form.validates():
  #          return render.formtest(form)
  #      else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
  #          return "Grrreat success! boe: %s, bax: %s" % (form.d.boe, form['bax'].value)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()