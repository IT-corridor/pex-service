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

def sendMail(from_email,to_email,subject,bodytext,html_comtent=None):
    try:
        print from_email,to_email,subject,bodytext,html_comtent
        mailcontent = EmailMultiAlternatives(subject,"test",from_email,[to_email])
        mailcontent.attach_alternative(html_comtent, "text/html")
        mailcontent.send()
        return "sent"
    except:
        return "fail"
    


    
    

    
