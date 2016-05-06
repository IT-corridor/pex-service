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
import customfunction
from pyvirtualdisplay import Display
import socket
import urllib

def jetblue(from_airport,to_airport,searchdate,searchid):
    #return searchid
    from_airport = from_airport.strip()
    to_airport = to_airport.strip()
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    date = dt.strftime('%d-%m-%Y')
    
    db = customfunction.dbconnection()
    cursor = db.cursor()
    
    url = "https://book.jetblue.com/shop/search/#/book/from/"+from_airport+"/to/"+to_airport+"/depart/"+str(date)+"/return/false/pax/ADT-1/redemption/true/promo/false"
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    display = Display(visible=0, size=(800, 600))
    display.start()
    #chromedriver = "/usr/bin/chromedriver"
    #os.environ["webdriver.chrome.driver"] = chromedriver
    #driver = webdriver.Chrome(chromedriver)
    driver = webdriver.Chrome()
    #driver=webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    #driver.set_window_size(1120, 550)
    
    driver.get(url)
    #driver.implicitly_wait(50)
    #time.sleep(2)
    try:
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "jbBookerPOS")))
        driver.find_elements_by_css_selector("input[type='submit'][value='Find it']")[0].click()
        #time.sleep(4)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "AIR_SEARCH_RESULT_CONTEXT_ID0")))
    except:
        print "nodata on jetblue"
        display.stop
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "jetblue", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        return searchid
     
    try:
        time.sleep(2)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        maintable = soup.find("table",{"id":"AIR_SEARCH_RESULT_CONTEXT_ID0"})
        databody =  maintable.findAll("tbody")
        #print "databody",len(databody)
        value_string = []
        recordCount = 1
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
                #print "stop=",n
            departdetails = []
            arivedetails = []
            plaindetails = []
            operatedby = []
            echoFareCode=[]
            businessFareCode=[]
            firstFareCode=[]
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
                        #print "arival_time",arivetime
                        if '+' in arivetime:
                            arive_time = arivetime.split("+")
                            #print arive_time
                            arivetime = arive_time[0]
                            
                        arive_fullname = arivetd.find("b").text
                        dest_code = arivetd.find("span",{"class":"location-code"}).text
                        if '(' in dest_code:
                            dest_code = dest_code.replace('(','')
                        if ')' in dest_code:
                            dest_code = dest_code.replace(')','')
                        arivedetail = str(date)+" | "+arival_time+" at "+arive_fullname
                        arivedetails.append(arivedetail)
                        echoFareCode.append("Blue")
                        businessFareCode.append("Blue plus")
                        firstFareCode.append("Blue flex")
                    if content.findAll("td",{"class":"colDuration"}):
                        duration = content.findAll("td",{"class":"colDuration"})
                        if duration:
                            totaltime = duration[0].text.strip()
                            #print "Flight Duration",totaltime
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
                        if len(departdetails) > 0:
                            departtexts = '@'.join(departdetails)
                            arivetexts = '@'.join(arivedetails) 
                            plaiintexts = '@'.join(plaindetails) 
                            operatedtexts = '@'.join(operatedby)
                            ecoFareText = '@'.join(echoFareCode)
                            businessFareText = '@'.join(businessFareCode)
                            firstFareText = '@'.join(firstFareCode)
                        recordCount = recordCount+1
                        value_string.append((str(fltno), str(searchid), stime, stoppage, "test", origin_code, dest_code, depttime2, arivetime2, totaltime, str(economy_miles), str(econ_tax), str(business_miles), str(businesstax), str(first_miles), str(firsttax),"Economy", "Business", "First", "jetblue", departtexts, arivetexts, plaiintexts, operatedtexts,ecoFareText,businessFareText,firstFareText))
                        
                    else:
                        if n < 2:
                            depttime1 = (datetime.datetime.strptime(orgntime, '%I:%M %p'))
                            depttime2 = depttime1.strftime('%H:%M')
                            arivetime1 = (datetime.datetime.strptime(arivetime, '%I:%M %p'))
                            arivetime2 = arivetime1.strftime('%H:%M')
                            if len(departdetails) > 0:
                                departtexts = '@'.join(departdetails)
                                arivetexts = '@'.join(arivedetails) 
                                plaiintexts = '@'.join(plaindetails) 
                                operatedtexts = '@'.join(operatedby)
                                ecoFareText = '@'.join(echoFareCode)
                                businessFareText = '@'.join(businessFareCode)
                                firstFareText = '@'.join(firstFareCode)
                                recordCount = recordCount+1
                            value_string.append((str(flightno), str(searchid), stime, stoppage, "test", orgncode, dest_code, depttime2, arivetime2, totaltime, str(economy_miles), str(econ_tax), str(business_miles), str(businesstax), str(first_miles), str(firsttax), "Economy", "Business", "First", "jetblue", departtexts, arivetexts, plaiintexts, operatedtexts,ecoFareText,businessFareText,firstFareText))
                            
                    if recordCount > 50:
                        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                        print "row inserted"
                        db.commit()
                        recordCount = 1
                        value_string = []
                    n = n-1
        if len(value_string) > 0:
            cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
            print "final row inserted"
            db.commit()
    except:
        print "please change your seach filter"
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "jetblue", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    display.stop
    driver.quit()
    return searchid




if __name__=='__main__':
    jetblue(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
