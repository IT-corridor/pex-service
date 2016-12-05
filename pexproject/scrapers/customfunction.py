#!/usr/bin/env python
import MySQLdb
import sendgrid
from config import config as sys_config


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
is_scrape_alaska = 1 

flag = 0

def dbconnection():
    return MySQLdb.connect(host="localhost",  
                           user=sys_config['DB_USER'],           
                           passwd=sys_config['DB_PASSWORD'],        
                           db=sys_config['DB_NAME'])  


def sendMail(from_email, to_email, subject, bodytext, html_content=None):
    try:
        client = sendgrid.SendGridClient(sys_config['SENDGRID_API_KEY'])
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
        return "sent"
    except Exception as e:
        return "fail"


def get_airport_code(airport):
    airport = airport.split(' (')
    return airport[1][:3]


def get_airport_detail(airport_code):
    db = dbconnection()
    cursor = db.cursor()
    sql = 'select name, cityName, code from pexproject_airports where code="{}"'.format(airport_code.strip())
    cursor.execute(sql)
    r = cursor.fetchone()
    if r:
        return '{} / {} ({})'.format(r[0], r[1], r[2])


AIRCRAFTS = {
    '321': 'Airbus A321',
    '32A': 'Airbus A32A',
    '330': 'Airbus A330',
    '333': 'Airbus A330-300',
    '33A': 'Airbus A33A',
    '747': 'Boeing 747',
    '772': 'Boeing 777-200ER',
    '773': 'Boeing 777-300',
    '77W': 'Boeing 777-300ER',  
    '319': 'Airbus A319',    
    'TRN': 'Boeing 767-33A',    
    'BUS': 'Boeing 777-200LR',    
    '346': 'Airbus A340-600',    
    '332': 'Airbus A330-200',    
    '345': 'Airbus A340-500',    
    '320': 'Airbus A320',    
    '789': 'Boeing 787-9',    
    '388': 'Airbus A380-800',    
    '77L': 'Boeing 777-200LR',
    '744': 'Boeing 747-400',
    '763': 'Boeing 767-300',
    '767': 'Boeing 767',
    'E90': 'Embraer ERJ-190',
    'CRJ': 'Bombardier CRJ',
    'E70': 'Embraer EMB 170',
    'E75': 'Embraer ERJ 175',
    'E7W': 'Embraer EMB 175',
    'ERJ': 'Embraer ERJ 145',
    '75W': 'Boeing 757-200',
    'M88': 'McDonnell Douglas MD 88',
    '739': 'Boeing 737-900',
    '738': 'Boeing 737-800',
    '753': 'Boeing 757-300',
    '752': 'Boeing 757-200',
    '777': 'Boeing 777-200',
    '757': 'Boeing 757',
    '717': 'Boeing 717-200',
    '73H': 'Boeing 737-800',
    '380': 'Airbus A380',
    '764': 'Boeing 767-400ER',
    '73W': 'Boeing 737-700',
    'CR7': 'Bombardier CRJ-700',
    'M90': 'McDonnell Douglas MD 90',
    'CR9': 'Bombardier CRJ-900',
    '76W': 'Boeing 767-300ER',
    '359': 'Airbus A350-900',
    '32B': 'Airbus A321',
    'SU9': 'Sukhoi Superjet-100-95B',
    'CS1': 'Bombardier CS100'
}

