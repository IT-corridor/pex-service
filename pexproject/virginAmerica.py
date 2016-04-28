#!/usr/bin/env python
import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import MySQLdb
import re
from selenium.webdriver.common.proxy import *
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.db import connection, transaction
import customfunction
from pyvirtualdisplay import Display
import socket

def virginAmerica(from_airport,to_airport,searchdate,searchid):
  
    db = customfunction.dbconnection()
    cursor = db.cursor()
    from_airport = from_airport.strip()
    to_airport = to_airport.strip()
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    date = dt.strftime('%m-%d-%Y')
    searchdate = dt.strftime('%Y%m%d')
    airport = from_airport+"_"+to_airport
    
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.virginamerica.com/book/ow/a1/"+airport+"/"+str(searchdate)
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    #driver = webdriver.Chrome()
    driver.get(url)
    value_string = []
    recordcount = 1
    try:
        time.sleep(1)
        #time.sleep(7)
        milesbtn = driver.find_elements_by_name("payment_type")
        driver.execute_script("arguments[0].click();", milesbtn[1]);
        time.sleep(1)
        #time.sleep(2)
        lgn = driver.find_element_by_link_text("Close")
        lgn.click()
        time.sleep(2)
        #time.sleep(5)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        datadiv = soup.findAll("div",{"class":"fare-map-row ng-scope"})
    except:
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        display.stop()
        driver.quit()
        return searchid
    try:
    #if searchid:
        for data in datadiv:
            trblock = data.findAll("tr")
            for content in trblock:
                detailblock =  content.find("div",{"class":"fare-map__flight-details"})
                if detailblock:
                    deptinfo = detailblock.findAll("li",{"class":"flight-details__flight-info--dep"})
                    durationinfo = detailblock.findAll("li",{"class":"flight-details__flight-dur"})
                    ariveinfo = detailblock.findAll("li",{"class":"flight-details__flight-info--arr"})
                    flightnum = ''
                    totalduration=''
                    departfrom=''
                    arriveat = ''
                    departtime=''
                    arivetime = ''
                    stop = ''
                    deptdetail=[]
                    arivedetail=[]
                    plaindetail=[]
                    maincabin =0
                    maintax = 0
                    business = 0
                    businesstax = 0
                    First = 0
                    Firsttax = 0
                    for a in range(0,len(deptinfo)):
                        flight_duration=''
                        origin = deptinfo[a].find("span",{"class":"flight-info__time ng-binding"})
                        flight = deptinfo[a].find("span",{"bo-text":"leg.flightNum"}).text
                        flight = "Flight "+str(flight)
                        origin_airport = origin.find("span").text
                        origin_time = (origin.text).replace(origin_airport,'')
                        origin_time = origin_time.strip()
                        if '()' in  origin_time:
                            origin_time = origin_time.replace('()','').strip()
                        origin_time1 = (datetime.datetime.strptime(origin_time, '%I:%M%p'))
                        dept_time = origin_time1.strftime('%H:%M')
                        origin_airport = origin_airport.replace('(','').replace(')','')
                        
                        departinfo = str(date)+" | "+origin_time+" from "+origin_airport
                        deptdetail.append(departinfo)
                        if a < 1:
                            departtime = dept_time
                            departfrom = origin_airport
                            flightnum = flight
                        
                        duration = durationinfo[a].findAll("span")
                        if len(duration)>0:
                           stop = (duration[0].text).replace('Leg','')
                           flight_duration = duration[1].text
                        
                        destination = ariveinfo[a].find("span",{"class":"flight-info__time--arr ng-binding"})
                        
                        if ariveinfo[a].find("span",{"class":"flight-info__total ng-scope"}):
                            totalduration = ariveinfo[a].find("span",{"class":"flight-info__total ng-scope"}).text
                            
                        else:
                            totalduration = flight_duration
                        planeinfo =  flight+"("+flight_duration+")"
                        plaindetail.append(planeinfo)
                        dest_airport = destination.find("span").text
                        dest_airport = dest_airport.replace('(','').replace(')','')
                        dest_time = (destination.text).replace(dest_airport,'')
                        dest_time = dest_time.strip()
                        if '()' in  dest_time:
                            dest_time = dest_time.replace('()','').strip()
                        dest_time1 = (datetime.datetime.strptime(dest_time, '%I:%M%p'))
                        dest_time2 = dest_time1.strftime('%H:%M')
                        
                        arivetime = dest_time2
                        arriveat = dest_airport
                        arivalinfo = str(date)+" | "+dest_time+" at "+dest_airport
                        arivedetail.append(arivalinfo)
                        
                    maincabinfare = content.findAll("div",{"class":"fare-map__price-details ng-scope"})
                    count = 0
                    for fare in maincabinfare:
                        if fare.find("a"):
                            fareblock = (fare.find("a").text).strip()
                            fareblock1 = re.findall("\d+.\d+", fareblock)
                            miles = fareblock1[0]
                            tax = fareblock1[1]
                            if ',' in miles:
                                miles = miles.replace(',','')
                            if miles:
                                if count == 0:
                                    maincabin = miles
                                    maintax = tax
                                    
                                elif count == 1:
                                    business = miles
                                    businesstax = tax
                                    
                                else:
                                    if count == 2:
                                        First = miles
                                        Firsttax = tax
                                
                        count = count+1
                    if 'stop' in stop:
                        stop = "NONSTOP"
                    if (stop.strip()).isdigit():
                        stop = int(stop)-1
                        if int(stop) > 1:
                            stop = stop+" STOPS"
                        else:
                            stop = str(stop)+" STOP"
                        
                
                    if 'total travel time' in totalduration:
                        totalduration = totalduration.replace('total travel time','')
                    if maincabin > 0 or business > 0 or First > 0:
                        departdetailtext= '@'.join(deptdetail)
                        arivedetailtext = '@'.join(arivedetail)
                        planedetailtext = '@'.join(plaindetail)
                        operatortext = '' 
                        value_string.append((str(flightnum), str(searchid), stime, stop, "test", departfrom, arriveat, departtime, arivetime, totalduration, str(maincabin), str(maintax), str(business),str(businesstax), str(First), str(Firsttax), "Economy", "Business", "First", "Virgin America", departdetailtext, arivedetailtext, planedetailtext, operatortext))                                                                                                                                                                                                                                                                                                                    
                        recordcount = recordcount+1
                        if recordcount > 50: 
                            cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                            db.commit()
                            value_string =[]
                            recordcount = 1
    except:
        print "somethinf wrong"
    if len(value_string) > 0:
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
        db.commit()
        print "last inserted"
    display.stop()
    driver.quit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    return searchid


if __name__=='__main__':
    virginAmerica(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    
