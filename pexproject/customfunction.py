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

sendgrid_api_key = "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"



def sendMail(from_email,to_email,subject,bodytext,html_content=None):
    if to_email:
    #try:
	print from_email,to_email,subject
	print "html_content",html_content
	client = sendgrid.SendGridClient(sendgrid_api_key)
	message = sendgrid.Mail()

	message.add_to(to_email)
	message.set_from(from_email)
	message.set_subject(subject)
	if bodytext:
	    message.set_html(bodytext)
	else:
	    if html_content:
		message.set_html(html_content)
	resp = client.send(message)
	print "resp",resp
	print "sent mail"
	return  "sent"
	'''
        mailcontent = EmailMultiAlternatives(subject,bodytext,from_email,[to_email])
    	if html_content:
            mailcontent.attach_alternative(html_content, "text/html")
        mailcontent.send()
    	print "success"
        return "sent"
	'''
    #except:
    else:
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

                

    
    

    
