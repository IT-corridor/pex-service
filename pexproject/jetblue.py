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
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%m-%d-%Y')
    #date = curdate.strftime('%m-%d-%Y')
    url = "https://www.jetblue.com/flights/#/"
    cursor = connection.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(50)
    try:
        oneway = driver.find_element_by_id("jbBookerItinOW")
        driver.execute_script("arguments[0].click();", oneway)
        time.sleep(2)
        origin = driver.find_element_by_id("jbBookerDepart")
        origin.clear()
        origin.send_keys(from_airport)
        origin.send_keys(Keys.ARROW_DOWN)
        origin.send_keys(Keys.ENTER)
        destination = driver.find_element_by_id("jbBookerArrive")
        destination.send_keys(to_airport)  #("Seattle, WA (SEA)")
        #driver.find_element_by_css_selector("css selector that matches all the auto complete suggestions")
        #driver.find_element_by_id("ui-active-menuitem").send_keys(Keys.ENTER)
        destination.send_keys(Keys.ARROW_DOWN)
        destination.send_keys(Keys.ENTER)
        doj = driver.find_element_by_id("jbBookerCalendarDepart")
        doj.send_keys(date)
        doj.send_keys(Keys.ENTER)
        
        milestype = driver.find_elements_by_xpath("//*[contains(text(), 'TrueBlue Points')]")
        
        driver.execute_script("arguments[0].click();", milestype[0]);
        driver.find_elements_by_css_selector("input[type='submit'][value='Find it']")[0].click()
        time.sleep(2)
        print "searchid",searchid
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "AIR_SEARCH_RESULT_CONTEXT_ID0")))
    except:
        print "nodata on jetblue"
        display.stop
        driver.quit()
        return searchid
        

    try:
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        maintable = soup.find("table",{"id":"AIR_SEARCH_RESULT_CONTEXT_ID0"})
        #print soup.prettify()
        #print soup.findAll("div",{"class":"popupBlockFlightDetails"})
        #exit()
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
                        print fltno,planetype
                        planeinfo = fltno+" | "+planetype
                    if arivetd:
                        arivetime = arivetd.find("div",{"class":"time"}).text
                        arive_fullname = arivetd.find("b").text
                        dest_code = arivetd.find("span",{"class":"location-code"}).text
                        if '(' in dest_code:
                            dest_code = dest_code.replace('(','')
                        if ')' in dest_code:
                            dest_code = dest_code.replace(')','')
                        arivedetail = str(date)+" | "+arivetime+" at "+arive_fullname
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
                        print "ogign stn=",origin_code
                        print "ogign time=",depttime
                        depttime1 = (datetime.datetime.strptime(depttime, '%I:%M %p'))
                        print "depttime1",depttime1
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
                        transaction.commit()
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
                            transaction.commit()
                    n = n-1
    #return searchid
    except:
        print "please change your seach filter"
    display.stop
    driver.quit()
    return searchid

if __name__=='__main__':
    jetblue(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])