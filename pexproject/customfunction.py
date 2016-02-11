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

def sendMail(from_email,to_email,subject,bodytext,html_content=None):
    try:
        mailcontent = EmailMultiAlternatives(subject,bodytext,from_email,[to_email])
    	if html_content:
            mailcontent.attach_alternative(html_content, "text/html")
        mailcontent.send()
    	print "success"
        return "sent"
    except:
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

                

    
    

    
