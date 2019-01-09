import os, subprocess,sys
import re
import csv
import string
import paramiko
import random
import getpass
import base64
import configparser
import smtplib
import psycopg2
import pprint
from datetime import date, timedelta
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import strftime

from requests import session
import urllib2
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = []
    def handle_starttag(self,tag,attr):
        if tag == 'title':
            self.recording=1
        return
    def handle_endtag(self, tag):
        if tag == 'title' and self.recording:
            self.recording-=1
        return
    def handle_data(self, data):
        if self.recording:
            self.data.append(data)

def db_conn_check():
	print "Checking DB host and service availability"
	db_l = db_ip_list.readlines();
	for data in [line[:-1] for line in db_l]:
		host=data		
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host,username=un ,password=pwd)
		stdin, stdout, stderr = ssh.exec_command(server_cmd)
		op1 = stdout.read().split(',')[0]
		stdin2, stdout2, stderr2 = ssh.exec_command(db_command)
		op2=stdout2.read()
		date = strftime("%d-%m-%Y")
		time = strftime("%H:%M:%S")
		print >>op_file,date,time,host,str(op1)
		print >>op_file,sep
		print >>op_file,date,time,host,str(op2)
		print >>op_file,sep
	
	
def host_conn_check():
	print "Checking ssh connection to ETL and sFTP servers "
	srvr_l = host_ip_list.readlines()
	for data in [line[:-1] for line in srvr_l]:
		host=data
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host,username=un ,password=pwd)
		stdin, stdout, stderr = ssh.exec_command(server_cmd)
		output = stdout.read().split(',')[0]
		date = strftime("%d-%m-%Y")
		time = strftime("%H:%M:%S")
		print >>op_file,date,time,host,str(output)
		
def apprs_conn_check():
	print "Checking RedShift DB connection "
	conn = psycopg2.connect(database=apprs_db_name, user=apprs_username, password=apprs_password, host=apprs_ip, port=apprs_port);
	cursor = conn.cursor();
	print >>op_file,sep
	print  >>op_file,"Connection to Redshift (apprs : 172.x.x.x) DB Successful !\n"
	print >>op_file,sep
	

def smtp_mail_service():
	print("Inside Mail Service")
	msg = MIMEMultipart()
	msg['From'] = from_addr
	msg['To'] = recipients
	smtp_do_tls = True
	msg['Subject'] = ' [ Test Run ] Application Daily Monitoring Report'+" "+strftime("%d.%m.%Y")+" "+strftime("%H:%M:%S")
	#message = 'here is the email'
	#msg.attach(MIMEText(message))

	mailserver = smtplib.SMTP(
		host=smtp_server,
		port=smtp_port,
		timeout=10
	)	
	body = """
        <html>
            <head></head>
            <body>
            <p>Hello Application Team <br><br>
            Your are receiving this email as part of Daily Monitoring process/checklist <br>
            
			Following are the items being monitored :<br><br>
            
            1.  Database (Dev and Prod)<br>
            2.  ETL servers (Dev and Prod )<br>
			3.  Connection to AWS RedShift DB <br>
            4.  sFTP server availability <br><br><br>
            Thank you,<br>
              Managed Services Team
            </p>
            </body>
        </html>
        """
	
	f = open(filename, 'r')
	print(os.stat(filename).st_size)
	attachment = MIMEText(f.read())
	attachment.add_header('Content-Disposition', 'attachment', filename=filename)
	msg.attach(attachment)
	msg.attach(MIMEText(body,'html'))
	
	
	#msg.attach(MIMEText(file(" _Monitoring_Report.txt").read()))
	mailserver.ehlo()
	# secure our email with tls encryption
	mailserver.starttls()
	# re-identify ourselves as an encrypted connection
	mailserver.ehlo()
	mailserver.login(smtp_username, smtp_password)
	
	mailserver.sendmail(from_addr,recipients.split(','),msg.as_string())

	mailserver.quit()
	
def delete_content():
	op_file = open(' Monitoring_Report.txt','w')
	op_file.close()

def del_file():
	if os.path.exists(' _Monitoring_Report.txt'):
		os.remove(' Monitoring_Report.txt')
	else:
		pass
		
def appln_check():
	print 'Checking Application availability for   and Prod'
	with session() as c:
		response1=c.post('http://auth.app.company.com:8080/openam/identity/authenticate?username='+app_username+'&password='+app_password)
	#print(response1.text)
	#print response1.text.split('=')[1]
	cookieString='iPlanetDirectoryPro='+ response1.text.split('=')[1].strip("\n")
	opener = urllib2.build_opener()
	opener.addheaders.append(('Cookie', cookieString))
	f_dev = opener.open("http://dev.app.app.company.com/")
	p = MyHTMLParser()
	html = f_dev.read()
	p.feed(html)
	print >>op_file,'Application Login successful' , p.data
	p.close()
	f_prod = opener.open("http://app.product.company.com")
	p = MyHTMLParser()
	html = f_prod.read()
	p.feed(html)
	print >>op_file,'  Prod Prod Login successful' , p.data
	p.close()
	
try:		
	del_file()
	config = configparser.RawConfigParser()
	config.read('config.properties')

	un=config.get('userInfo','username')
	pwd=base64.b64decode(config.get('userInfo','password'))

	# smtp cofigurations
	smtp_server = config.get('SmtpSection', 'smtp.server')
	smtp_username = config.get('SmtpSection', 'smtp.username')
	smtp_password = config.get('SmtpSection', 'smtp.password')
	smtp_port = int(config.get('SmtpSection', 'smtp.port'))
	#recipients = config.get('SmtpSection', 'smtp.recipients')

	recipients = 'rajesh.hariharan@company.com'
	from_addr = config.get('SmtpSection', 'smtp.fromaddr')

	# # apprs config
	apprs_ip = str(config.get('apprs','apprs.ip'))
	apprs_port = config.get('apprs','apprs.port')
	apprs_db_name = config.get('apprs','apprs.db_name')
	apprs_username = config.get('apprs','apprs.username')
	apprs_password = config.get('apprs','apprs.password')
	
	app_username=config.get('ApplicationLogin','username')
	app_password=base64.b64decode(config.get('ApplicationLogin','password'))
	
	filename = config.get('Logging', 'process_log')
	db_ip_list = open('db_ip_list.txt','r')
	host_ip_list = open('host_ip_list.txt','r')
	op_file = open(' _Monitoring_Report.txt','a')
	server_cmd =  'uptime'
	db_command = 'systemctl status postgresql.service'
	sep = "==============================================================================\n"
	db_conn_check()
	host_conn_check()
	apprs_conn_check()
	smtp_mail_service()
	appln_check()
	op_file.close()
	
except Exception as exe:
    temp = "An exception of type {0} occured. Arguments:\n{1!r}"
    formatted_error_msg = temp.format(type(exe).__name__, exe.args)
    print(formatted_error_msg)




