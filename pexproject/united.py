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

def united(origin, destination, searchdate, searchkey):
    #return searchkey
    db = MySQLdb.connect(host="localhost",  
                     user="root",          
                      passwd="1jyT382PWzYP",       
                      db="pex")
    cursor = db.cursor()

    #cursor = connection.cursor()
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%Y-%m-%d')
    date_format = dt.strftime('%a, %b %-d')
    currentdatetime = datetime.datetime.now()
    searchkey = searchkey
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f=" + origin + "&t=" + destination + "&d=" + date + "&tt=1&at=1&sc=7&px=1&taxng=1&idx=1"
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url)
    time.sleep(2)
    try:
        change = driver.find_element_by_link_text("Change").click()
    except:
        print "no change"
    try:
        
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to_alert()
        alert.accept()

    except:
        print "no alert to accept"
    try:
        #print "data check"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fl-results")))
        #print "data check complete"
    except:
        display.stop
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "united", "flag", "flag", "flag", "flag"))
        db.commit()
        return searchkey
    time.sleep(7)
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    # datablock = soup.find("section",{"id":"fl-results"})
    pages = []
    searchid = searchkey
    page = soup.findAll("a", {"class":"page-link"})
    #print page
    for p in page:
       if p['href'] not in pages:
           pages.append(p['href'])
    print pages
    def scrapepage(searchkey, soup3):
        soup = soup3
        datadiv = soup.findAll("li", {"class":"flight-block"})
        detaillinks = soup.findAll("a", {"class":"toggle-flight-block-details ui-tabs-anchor"})
        for dtlink in detaillinks:
            detaillink = dtlink['href'] 
            #print "detaillink",detaillink      
            test = driver.find_element_by_xpath("//a[@href='"+ detaillink +"']")
            driver.execute_script("arguments[0].click();", test);
        time.sleep(0.05)
        html_page4 = driver.page_source
        html_page5 = html_page4.encode('utf-8')
        soup2 = BeautifulSoup(str(html_page5))
        #print len(datadiv)
        for row in datadiv:
            fare1 = 0
            fare2 = 0
            fare3 = 0
            maintax = 0
            businesstax = 0
            firsttax = 0
            cabintype1 = ''
            cabintype2 = ''
            cabintype3 = ''
            flightno = ''
            stoppage = ''
            searchid = searchkey
            source = ''
            Destination = ''
            arivetime2 = ''
            departdetails = ''
            arivedetails = ''
            planedetails = ''
            departtime = ''
            test1 = ''
            operatedbytext = ''
            totaltime = ''
            
            stoppage = row.find("div", {"class":"flight-connection-container"}).text
            
            if '1' in stoppage:
                stoppage = '1 STOP'
            elif '2' in stoppage:
                stoppage = '2 STOPS'
            elif '3' in stoppage:
                stoppage = '3 STOPS'
	    elif '4' in stoppage:
                stoppage = '4 STOPS'
            else :
                if 'Nonstop' in stoppage:
                    stoppage = 'NONSTOP'
            
            source1 = row.find("div", {"class":"flight-station flight-station-origin"}).text
            source2 = source1.split('(')
            source3 = (source2 [1].replace(')', '')).split('-')
            source = source3[0].strip()
            # print source1
            destination1 = row.find("div", {"class":"flight-station flight-station-destination"}).text
            destination2 = destination1.split('(')
            destination3 = (destination2[1].replace(')', '')).split('-')
            Destination = destination3[0].strip()
            # print destination1
            departdlist = []
            arivelist = []
            planelist = []
            operatedby = []
	    depttime = ''
	    arivaltime = ''            
            departtime = row.find("div", {"class":"flight-time flight-time-depart"}).text
            dateduration = ''
            dateinfo = ''
            if row.find("div", {"class":"date-duration"}):
                dateinfo = row.findAll("div", {"class":"date-duration"})
                dateduration = dateinfo[0].text
            # print dateduration
            depttime1 = departtime.replace(dateduration, '').strip()
            if 'Departing' in depttime1:
                depttime1 = (depttime1.replace('Departing','')).strip()
            if 'pm' in depttime1:
                #print depttime1[depttime1.index('pm') + len('pm'):]
                depttime2 = depttime1.split('pm')
                depttime = depttime2[0]+" pm"
            else:
                if 'am' in depttime1:
                    depttime2 = depttime1.split('am')
                    depttime = (depttime2[0]).strip()+" am"
                    #print depttime
            test = (datetime.datetime.strptime(depttime, '%I:%M %p'))
            test1 = test.strftime('%H:%M')
            # print test1
            
            arivetime = row.find("div", {"class":"flight-time flight-time-arrive"}).text
            arivedate = ''
            if row.find("div", {"class":"date-duration"}) and dateinfo[1]:
                arivedate = dateinfo[1].text
            # print arivedate
            arivaltime = arivetime.replace(arivedate, '').strip()
            if 'Arriving' in arivaltime:
                arivaltime = (arivaltime.replace('Arriving','')).strip()
            if '.' in arivaltime:
                arivaltime = arivaltime.replace('.', '')
            if 'pm' in arivaltime:
                arivetime4 = arivaltime.split('pm')
                arivaltime = (arivetime4[0]).strip()+" pm"
            else:
                if 'am' in arivaltime:
                    arivetime4 = arivaltime.split('am')
                    arivaltime = arivetime4[0]+" am"

            arivetime1 = (datetime.datetime.strptime(arivaltime, '%I:%M %p'))
            arivetime2 = arivetime1.strftime('%H:%M')
            # print "arivetime",arivetime2
            
            totaltime = row.find("a", {"class":"flight-duration otp-tooltip-trigger"}).text
            if 'total' in totaltime:
                totaltime1 = totaltime.split('total')
            if 'Duration' in totaltime1[0]:
                totaltime = totaltime1[0].replace('Duration', '')
            flightno = row.find("div", {"class":"segment-flight-number"}).text
            planetype = row.find("div", {"class":"segment-aircraft-type"}).text
            detaillink = row.find("a", {"class":"toggle-flight-block-details ui-tabs-anchor"})['href']        
	    #print "detaillink",detaillink
            test = driver.find_element_by_xpath("//a[@href='"+ detaillink +"']")
            #test = driver.execute_script("document.getElementById('" +detaillink+ "')")
    
            dtlid = detaillink.replace('#', '').strip()
            #driver.execute_script("arguments[0].click();", test);
            
            departuretime = ''
            desttime = ''
            flight_duration = ''
            flight_number = ''
            arival_date = ''
            departure_date = ''
            if soup2.find("div", {"id":dtlid}):
                 detailsinfo = soup2.find("div", {"id":dtlid})
                 infoblock = detailsinfo.findAll("div", {"class":"segment-details-left"})
                 for info in infoblock:
                     origindest1 = info.find("div", {"class":"segment-orig-dest"}).text
                     origindest2 = origindest1.split(' to ')
                     depart = origindest2[0]
                     dest = origindest2[1]
                     if info.find('ul', {"class":"advisories-messages"}):
                         uls = info.find('ul', {"class":"advisories-messages"})
                         lis = uls.findAll("li")
                         if len(lis) > 1:
                              ddate = lis[0].text
                              ardate = lis[1].text 
                              if ':' in ddate and ':' in ardate:
                                  ddate = ddate.split(':')
                                  departure_date = ddate[1]
                                  ardate = ardate.split(':')
                                  arival_date = ardate[1]
                     if info.find("div", {"class":"segment-times"}):
                         timesegmt = info.find("div", {"class":"segment-times"}).text
                         timesegmt1 = timesegmt.split('-')
                         departuretime = timesegmt1[0]
                         timesegmt2 = timesegmt1[1].split('(')
                         desttime = timesegmt2[0]
                         flight_duration = timesegmt2[1].replace(')', '')        
                     if departuretime:
                         departtext = departuretime + " from " + depart
                         if departure_date:
                             departtext = departure_date + " | " + departuretime + " from " + depart
                         else:
                             departtext = date_format + " | " + departuretime + " from " + depart
                             
                     else:
                         departtext = date_format + " | " + depttime + " from " + depart
                     if desttime:
                         dest_text = desttime + " at " + dest
                         if arival_date:
                            dest_text = arival_date + " | " + desttime + " at " + dest
                         else:
                             dest_text = date_format + " | " + desttime + " at " + dest
                              
                     else:
                         dest_text = date_format + " | " + arivaltime + " at " + dest
                     departdlist.append(departtext)
                     arivelist.append(dest_text)
                     flight_number = info.find("div", {"class":"segment-flight-equipment"}).text
                     flight_number = flight_number.strip()
                     #print flight_number
                     if flight_duration:
                         plane_text = flight_number + " (" + flight_duration + ")"
                         planelist.append(plane_text)
                     else:
                         planelist.append(flight_number)
                     
                     operateby = info.find("div", {"class":"segment-operator"})
                     if operateby:
                         operateby = operateby.text
                         if 'Operated by' in operateby:
                             operateby = operateby.replace('Operated by', '')
                         operatedby.append(operateby)
            #driver.execute_script("arguments[0].click();", test);
            priceblock = row.findAll("div", {"class":"flight-block-fares-container"})
            
            for prc in priceblock:
                
                if prc.find("div", {"class":"fare-option bg-economy"}):
                    cabintype1 = "Economy"
                    eco = prc.find("div", {"class":"fare-option bg-economy"})
                    # print "economy"
                    economy = eco.find("div", {"class":"pp-base-price price-point"}).text
                    if "k" in economy:
                        economy = (economy.replace('k', '')).replace("miles", '')
                        fare1 = float(economy) * int('1000')
                    
                    econtax = eco.find("div", {"class":"pp-additional-fare price-point"}).text
                    #print "econtax",econtax
                    if "+$" in econtax:
                        maintax = econtax.replace('+$', '')
                    
                #else:
                    #print " "
                    
                if prc.find("div", {"class":"fare-option bg-business"}):
                    cabintype2 = 'Business'
                    buss = prc.find("div", {"class":"fare-option bg-business"})
                    # print "business"
                    business = buss.find("div", {"class":"pp-base-price price-point"}).text
                    if "k" in business:
                        business = (business.replace('k', '')).replace("miles", '')
                        fare2 = float(business) * int('1000')
                    
                    busstax = buss.find("div", {"class":"pp-additional-fare price-point"}).text
                    #print "busstax",busstax
                    if "+$" in busstax:
                        businesstax = busstax.replace('+$', '')
                    # print "busstax",businesstax
                    
                #else:
                    #print " "
        
                if prc.find("div", {"class":"fare-option bg-first"}):
                    cabintype3 = 'First'
                    first1 = prc.find("div", {"class":"fare-option bg-first"})
                    
                    first = first1.find("div", {"class":"pp-base-price price-point"}).text
                    if "k" in first:
                        first = (first.replace('k', '')).replace("miles", '')
                        fare3 = float(first) * int('1000')
                    
                    firsttax = first1.find("div", {"class":"pp-additional-fare price-point"}).text
                    if "+$" in firsttax:
                        firsttax = firsttax.replace('+$', '')
                    
                #else:
                    #print " "
    
            departdetails = '@'.join(departdlist)
            arivedetails = '@'.join(arivelist)
            planedetails = ('@'.join(planelist)).strip()
            
            # print "operatedby",operatedby
            
            if len(operatedby) > 0:
                operatedbytext = '@'.join(operatedby)
            
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (flightno, str(searchid), stime, stoppage, "test", source, Destination, test1, arivetime2, totaltime, str(fare1), str(maintax), str(fare2), str(businesstax), str(fare3), str(firsttax), cabintype1, cabintype2, cabintype3, "united", departdetails, arivedetails, planedetails, operatedbytext))
            db.commit()
    scrapepage(searchkey, soup)
    for i in pages:
        print "page no",i
        link = driver.find_element_by_xpath("//a[@href='" +i+ "']")
        #link = driver.find_element_by_link_text(pages[i])
        #print "link",link
        driver.execute_script("arguments[0].click();", link);
        #link.send_keys(Keys.ENTER)
        #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
        time.sleep(.5)
        html_page1 = driver.page_source
        soup = BeautifulSoup(html_page1)
        scrapepage(searchkey, soup)
        
    display.stop
    driver.quit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "united", "flag", "flag", "flag", "flag"))
    db.commit()
    return searchid

print "in united"
united(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
