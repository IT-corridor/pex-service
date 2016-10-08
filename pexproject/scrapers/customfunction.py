#!/usr/bin/env python
import os, sys
import datetime
from datetime import timedelta
import time
import MySQLdb
import re
from email.mime.text import MIMEText
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from django.db import connection, transaction
from django.core.mail import send_mail,EmailMultiAlternatives
import rewardScraper
import sendgrid
from sendgrid.helpers.mail import *
from django.conf import settings

sendgrid_api_key = "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"
mailchimp_api_key = "def631e53845c0b9f251db8fdd8d2ae6-us12"
mailchiml_List_ID = "bda2a62002"
mailchimp_username = "pradeep@techencephalon.com"

is_scrape_delta =1
is_scrape_united = 1
is_scrape_virgin_atlantic = 1
is_scrape_virginAmerica = 1
is_scrape_jetblue = 0
is_scrape_vAUS = 1
is_scrape_aa = 0
is_scrape_etihad = 1
is_scrape_aeroflot = 1
is_scrape_s7 = 1
is_scrape_airchina = 1 

flag = 0


def dbconnection():
    db = MySQLdb.connect(host="localhost",  
                        user="root",           
                        passwd="1jyT382PWzYP",        
                        db="pex")  
    return db


def sendMail(from_email, to_email, subject, bodytext, html_content=None):
    try:
        sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api_key)
#        message = sendgrid.Mail()
    
#        message.add_to(to_email)
#        message.set_from(from_email)
#        message.set_subject(subject)
#        if bodytext:
#            message.set_html(bodytext)
#        else:
#            if html_content:
#                message.set_html(html_content)
#        resp = client.send(message)
	from_email = getattr(settings, "FROM_MAIL", 'support@pexportal.com')
	print "stage 1"
	print from_email
	print to_email
	fromemail = Email("pardeepkk@gmail.com")
	toemail = Email(to_email)
	print "stage 2"
	if bodytext:
		content = Content("text/plain",bodytext )
	else:
		if html_content:
			content = Content("text/html",html_content)
	print "stage 3"
	mail = Mail(fromemail, subject, toemail, content)
	print "stage 4"
	response = sg.client.mail.send.post(request_body=mail.get())
	print "stage 5"
	print(response.status_code)
	print(response.body)
	print(response.headers)
        return "sent"
    except Exception as e:
	print e.message
        return "fail"
    

def syncPoints(airline,userid,username,skymiles_number,password):
    resp = ''
    if airline == 'delta':
        resp = rewardScraper.deltaPoints(skymiles_number,password,userid)   
    elif airline == 'united':
        resp = rewardScraper.unitedPoints(skymiles_number,password,userid)           
    else:
        if airline == 'virgin':
            resp = rewardScraper.virginPoints(username,password,userid)
    return resp
