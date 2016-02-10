#!/usr/bin/env python 
import os, sys
from subprocess import call
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
from multiprocessing import Process
import threading
from threading import Thread
import Queue
from pyvirtualdisplay import Display
import socket
import urllib

def jetblue(from_airport,to_airport,searchdate,searchid):
    from_airport = from_airport.strip()
    to_airport = to_airport.strip()
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%d-%m-%Y')
    #date  = dt.strftime('%m-%d-%Y')
    
    
    db = MySQLdb.connect(host="localhost",  
                     user="root",          
                      passwd="1jyT382PWzYP",       
                      db="pex")
    cursor = db.cursor()
    
    #url = "https://www.jetblue.com/flights/#/"
    url = "https://book.jetblue.com/shop/search/#/book/from/"+from_airport+"/to/"+to_airport+"/depart/"+str(date)+"/return/false/pax/ADT-1/redemption/true/promo/false"
    #cursor = connection.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    
    driver.get(url)
    driver.implicitly_wait(50)
    
    try:
	    
        milestype = driver.find_elements_by_xpath("//*[contains(text(), 'TrueBlue Points')]")
        driver.execute_script("arguments[0].click();", milestype[0]);
        driver.find_elements_by_css_selector("input[type='submit'][value='Find it']")[0].click()
        time.sleep(4)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "AIR_SEARCH_RESULT_CONTEXT_ID0")))
    except:
        print "nodata on jetblue"
        display.stop
        driver.quit()
        return searchid
        
    try:
        time.sleep(2)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        maintable = soup.find("table",{"id":"AIR_SEARCH_RESULT_CONTEXT_ID0"})
        databody =  maintable.findAll("tbody")
        print "databody",len(databody)
        for trs in databody:
            
            maintr = trs.findAll("tr")
            flag = 0
            
            if len(maintr) > 1:
                stops = trs.findAll("td",{"class":"colDepart"})
                n = len(stops)
                if (n-1) == 0:
                    stoppage = "NONSTOP"
                else:
                    if (n-1) > 1:
                        stoppage = str(n-1)+" STOPS"
                    else:
                        stoppage = str(n-1)+" STOP"
                print "stop=",n
            departdetails = []
            arivedetails = []
            plaindetails = []
            operatedby = []
            flightno =''
            depttd  = ''
            arivetd = ''
            orgncode = ''
            destcode = ''
            orgntime = ''
            desttime = ''
            arivetime = ''
            dest_code = ''
            planeinfo = ''
            fltno = ''
            totaltime = ''
            economy_miles = 0
            econ_tax = 0
            business_miles = 0
            businesstax = 0
            first_miles = 0
            firsttax = 0
            for content in maintr:
                j = 3
                depttd = content.find("td",{"class":"colDepart"})
                arivetd = content.find("td",{"class":"colArrive"})
                if depttd:
                    if depttd:
                        depttime = depttd.find("div",{"class":"time"}).text
                        origin_fullname = depttd.find("b").text
                        origin_code = depttd.find("span",{"class":"location-code"}).text
                        if '(' in origin_code:
                            origin_code = origin_code.replace('(','')
                        if ')' in origin_code:
                            origin_code = origin_code.replace(')','')
                        #print origin_code,depttime,origin_fullname
                        deptdetail = str(date)+" | "+depttime+" from "+origin_fullname
                        departdetails.append(deptdetail)
                        fltno = depttd.find("span",{"class":"flightCode"}).text
                        fltdetal = depttd.find("a")['onclick']
                        #print fltdetal
                        start = fltdetal.index("companyShortName=") + len( "companyShortName=" )
                        end = fltdetal.index("')", start )
                        #print "operated by", fltdetal[start:end]
                        operatedby.append(fltdetal[start:end])
                        if 'Flight number' in fltno:
                            fltno = (fltno.replace('Flight number','')).strip()
                        if 'With layover' in fltno:
                            fltno = fltno.replace('With layover','')
                        planetype = depttd.find("span",{"class":"equipType"}).text
                        #print fltno,planetype
                        planeinfo = fltno+" | "+planetype
                    if arivetd:
                        arivetime = arivetd.find("div",{"class":"time"}).text
                        arival_time = arivetime 
                        print "arival_time",arivetime
                        if '+' in arivetime:
                            arive_time = arivetime.split("+")
                            print arive_time
                            arivetime = arive_time[0]
                            
                        arive_fullname = arivetd.find("b").text
                        dest_code = arivetd.find("span",{"class":"location-code"}).text
                        if '(' in dest_code:
                            dest_code = dest_code.replace('(','')
                        if ')' in dest_code:
                            dest_code = dest_code.replace(')','')
                        arivedetail = str(date)+" | "+arival_time+" at "+arive_fullname
                        arivedetails.append(arivedetail)
                    if content.findAll("td",{"class":"colDuration"}):
                        duration = content.findAll("td",{"class":"colDuration"})
                        if duration:
                            totaltime = duration[0].text.strip()
                            print "Flight Duration",totaltime
                            planetime = ''
                            if "Total:" in totaltime:
                                totaltime1 = totaltime.split('Total:')
                                planetime = totaltime1[0].strip()
                                totaltime = totaltime1[1].strip()
                            else:
                                planetime = totaltime
                            planeinfo = planeinfo+"("+planetime+")"

                            plaindetails.append(planeinfo)
                       
                    if content.findAll("td",{"class":"colCost"}):
                        priceblock = content.findAll("td",{"class":"colCost"})
                        for fare in priceblock:
                            if fare.find("div",{"class":"colPrice"}):
                                if j > 0:
                                    priceinfo = fare.find("div",{"class":"colPrice"})
                                    miles = priceinfo.find("span",{"class":"ptsValue"}).text
                                    taxes = priceinfo.find("span",{"class":"taxesValue"}).text
                                    taxes = re.findall("\d+.\d+", taxes)
                                    taxes1 = taxes[0]
                                    miles = re.findall("\d+.\d+", miles)
                                    miles1 = miles[0]
                                    if ',' in miles1:
                                        miles1 = miles1.replace(',','')
                                    if j == 3:
                                        economy_miles = miles1
                                        econ_tax = taxes1
                                    elif j == 2:
                                        business_miles = miles1
                                        businesstax = taxes1
                                    else:
                                        if j == 1:
                                            first_miles = miles1
                                            firsttax = taxes1
                                    j = j-1
            
                    if n > 1:
                        flag = n
                        orgncode = origin_code
                        orgntime = depttime
                        flightno = str(fltno)
                        dest_code =''
                        arivetime=''
                        
                    if flag == 0:
                        depttime1 = (datetime.datetime.strptime(depttime, '%I:%M %p'))
                        depttime2 = depttime1.strftime('%H:%M')
                        arivetime1 = (datetime.datetime.strptime(arivetime, '%I:%M %p'))
                        
                        arivetime2 = arivetime1.strftime('%H:%M')
                        print "arivetime2",arivetime2
                        if len(departdetails) > 0:
                            departtexts = '@'.join(departdetails)
                            arivetexts = '@'.join(arivedetails) 
                            plaiintexts = '@'.join(plaindetails) 
                            operatedtexts = '@'.join(operatedby)
                        
                        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (str(fltno), str(searchid), stime, stoppage, "test", origin_code, dest_code, depttime2, arivetime2, totaltime, str(economy_miles), str(econ_tax), str(business_miles), str(businesstax), str(first_miles), str(firsttax),"Economy", "Business", "First", "jetblue", departtexts, arivetexts, plaiintexts, operatedtexts))
                        print "row inserted"
                        db.commit()
                        #transaction.commit()
                        print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                    else:
                        if n < 2:
                            print "ogign stn=",orgncode
                            print "ogign time=",orgntime
                            depttime1 = (datetime.datetime.strptime(orgntime, '%I:%M %p'))
                            print "depttime1",depttime1
                            depttime2 = depttime1.strftime('%H:%M')
                            print "depttime2",depttime2
                            
                            print "dest=",dest_code
                            print "desttime=",arivetime
                            arivetime1 = (datetime.datetime.strptime(arivetime, '%I:%M %p'))
                            print "arivetime1",arivetime1
                            arivetime2 = arivetime1.strftime('%H:%M')
                            print "arivetime2",arivetime2
                            if len(departdetails) > 0:
                                departtexts = '@'.join(departdetails)
                                arivetexts = '@'.join(arivedetails) 
                                plaiintexts = '@'.join(plaindetails) 
                                operatedtexts = '@'.join(operatedby)
                                print departtexts
                                print arivetexts
                                print plaiintexts
                                print operatedtexts
                            print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (str(flightno), str(searchid), stime, stoppage, "test", orgncode, dest_code, depttime2, arivetime2, totaltime, str(economy_miles), str(econ_tax), str(business_miles), str(businesstax), str(first_miles), str(firsttax), "Economy", "Business", "First", "jetblue", departtexts, arivetexts, plaiintexts, operatedtexts))
                            print "row inserted"
                            db.commit()
                            #transaction.commit()
                    n = n-1
    
    except:
        print "please change your seach filter"
    display.stop
    driver.quit()
    return searchid

def virginAmerica(from_airport,to_airport,searchdate,searchid):
    db = MySQLdb.connect(host="localhost",  
                     user="root",          
                      passwd="1jyT382PWzYP",       
                      db="pex")
    cursor = db.cursor()
    #cursor = connection.cursor()
    from_airport = from_airport.strip()
    to_airport = to_airport.strip()
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%m-%d-%Y')
    searchdate = dt.strftime('%Y%m%d')
    airport = from_airport+"_"+to_airport
    
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.virginamerica.com/book/ow/a1/"+airport+"/"+str(searchdate)
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        time.sleep(7)
        milesbtn = driver.find_elements_by_name("payment_type")
        driver.execute_script("arguments[0].click();", milesbtn[1]);
        time.sleep(2)
        lgn = driver.find_element_by_link_text("Close")
        lgn.click()
        time.sleep(5)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        datadiv = soup.findAll("div",{"class":"fare-map-row ng-scope"})
	#print datadiv
    except:
        print "no flights found"
        display.stop()
        driver.quit()
        return searchid
    #try:
    if searchid:
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
                        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (str(flightnum), str(searchid), stime, stop, "test", departfrom, arriveat, departtime, arivetime, totalduration, str(maincabin), str(maintax), str(business),str(businesstax), str(First), str(Firsttax), "Economy", "Business", "First", "Virgin America", departdetailtext, arivedetailtext, planedetailtext, operatortext))
                        #transaction.commit()
                        db.commit()
                        print "row inserted"
                    print "---------------------------- End ---------------------------"
    #except:
    else:
        print "somethinf wrong"
    display.stop()
    driver.quit()
    return searchid


if __name__=='__main__':
    #jetblue(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    virginAmerica(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    jetblue(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
