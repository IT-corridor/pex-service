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
#from pyvirtualdisplay import Display
import socket
import urllib
#from pexproject import settings




def delta(orgn, dest, searchdate, searchkey):
    #return searchkey
    db = MySQLdb.connect(host="localhost",  
                     user="pex",           
                      passwd="pex@1234",        
                      db="pex")  
    cursor = db.cursor()
    url = "http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
   
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    driver = webdriver.Chrome()
    try:
        driver.implicitly_wait(20)
        driver.get(url)
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "oneWayBtn")))
        oneway = driver.find_element_by_id('oneWayBtn')
        driver.execute_script("arguments[0].click();", oneway)
        
        origin = driver.find_element_by_id("originCity")
        origin.clear()
        origin.send_keys(orgn.strip())
        destination = driver.find_element_by_id("destinationCity")
        destination.send_keys(dest.strip())
    
        ddate = driver.find_element_by_id("departureDate")  # .click()
        ddate.send_keys(str(searchdate))
        milebtn = driver.find_element_by_id("milesBtn")
        driver.execute_script("arguments[0].click();", milebtn)
        driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
        
    except:
        #display.stop
        driver.quit()
        return searchkey
    
    try:
        print "test1"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    except:
        print "exception"
        #display.stop()
        driver.quit()
        return searchkey
    
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "showAll")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
    except:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    pricehead = soup.find("tr",{"class":"tblHeadUp"})
    pricecol = pricehead.findAll("label",{"class":"tblHeadBigtext"})
    datatable = soup.findAll("table", {"class":"fareDetails"})
    n = 0
    for content in datatable:
        detailid = content.find("div", {"class":"detailLinkHldr"})['id']
        driver.execute_script("document.getElementById('" + detailid + "').click()")
        print detailid
        time.sleep(0.06)
        page = driver.page_source
        soup2 = BeautifulSoup(page)
        datatable1 = soup2.findAll("table", {"class":"fareDetails"})
        k = 0
        departdetails = []
        arrivedetails = []
        planedetails = []
        operatedbytext = ''
        for cnt in datatable1:
            if cnt.find("div", {"class":"detailsRow" }) and k == n:
                detailblk = cnt.findAll("div", {"class":"detailsRow"})
                for tmp in detailblk:
                    print "----------------------------------"
                    spaninfo = tmp.findAll("p")
                    depart_string = (spaninfo[0].text).replace('DEPARTS', '')
                    if "Opens in a new popup" in depart_string:
                        depart_string = depart_string.replace('Opens in a new popup','')
                    departdetails.append(depart_string)
                    arive_string = (spaninfo[1].text.replace('ARRIVES', ''))
                    if "Opens in a new popup" in arive_string:
                        arive_string = arive_string.replace('Opens in a new popup','')
                    arrivedetails.append(arive_string)
                    flight_duration = spaninfo[2].text.replace('FLIGHT', '')
                    flight_duration1 = flight_duration.split("|")
                    flight_no = flight_duration1[0].strip()
                    plane_duration = flight_duration1[1].strip()
                    extra_string = ''
                    aircraft =''
                    aircraft1 = spaninfo[3].text.replace('PLANE', '')
                    if "-" in aircraft1:
                        aircraft2 = aircraft1.split('-')
                        aircraft = aircraft2[0]
                        if len(aircraft2)>2:
                            aircraft = aircraft+"-"+aircraft2[1]
                    planedetailinfo = flight_no + " | " + aircraft + " (" + plane_duration + ")"
                    planedetails.append(planedetailinfo)
            k = k + 1
        n = n + 1
        #pricecol = content.findAll("th")
        tds = content.findAll("td")
        cabinhead = ''
        detailsblock = tds[0]
        if  len(pricecol) > 1: 
            if tds[1]:
                economy = tds[1]
            if len(tds) > 2:
                business = tds[2]
        else:
            if len(pricecol) < 2:
                cabinhead = pricecol[0].text
                print "cabinhead",cabinhead
                if 'Business' in cabinhead or 'First' in cabinhead:
                    business = tds[1]
                    economy = ''
                else:
                    if 'Main Cabin' in cabinhead:
                       economy =  tds[1]
                       business = ''
        cabintype2 = ''
        fare2 = 0
        timeblock = detailsblock.findAll("div", {"class":"flightDateTime"})
        operatordiv = detailsblock.find("div", {"class":"summaryMessageWrapper"})
        if operatordiv.find("span",{"class":"odIndex_1"}):
            operator = operatordiv.find("span",{"class":"odIndex_1"}).text
            operatedbytext = operator
        for info in timeblock:
            temp = info.findAll("span")
            depature = temp[0].text
            part = depature[-2:]
            depature1 = depature.replace(part, "")
            depaturetime = depature1 + " " + part
            print depaturetime
            test = (datetime.datetime.strptime(depaturetime, '%I:%M %p'))
            test1 = test.strftime('%H:%M')
            arival = temp[3].text
            apart = arival[-2:]
            arival = arival.replace(apart, "")
            arivaltime = arival + " " + apart
            arivalformat = (datetime.datetime.strptime(arivaltime, '%I:%M %p'))
            arivalformat1 = arivalformat.strftime('%H:%M')
            duration = temp[4].text
            
        flite_route = detailsblock.findAll("div", {"class":"flightPathWrapper"})
        fltno = detailsblock.find("a", {"class":"helpIcon"}).text
        for route in flite_route:
            if route.find("div", {"class":"nonStopBtn"}):
                stp = "NONSTOP"
                lyover = ""
                # print "nonstop"
            else:
                if route.find("div", {"class":"nStopBtn"}):
                    stp = route.find("div", {"class":"nStopBtn"}).text
                    # print route.find("div",{"class":"nStopBtn"}).text
                    if route.find("div", {"class":"layOver"}):
                        lyover = route.find("div", {"class":"layOver"}).text
                    elif route.find("div", {"class":"originCityVia2Stops"}):
                        multistop = route.findAll("div", {"class":"originCityVia2Stops"})
                        stoplist = []
                        for sp in multistop:
                            stoplist.append(sp.text)
                        lyover = "|".join(stoplist)
                    else:
                        lyover = ''
                    # print route.find("div",{"class":"layOver"}).find("span").text
                    # print route.find("div",{"class":"layovertoolTip"}).text
                    # layover.append(lyover)
            sourcestn = (route.find("div", {"class":"originCity"}).text)
            destinationstn = (route.find("div", {"class":"destinationCity"}).text)
        print "-------------------- Economy--------------------------------------------------"
        economytax = 0
        businesstax = 0
        fare3 = 0
        firsttax = 0
        cabintype3 = ''
        fare1 = 0 
        cabintype1 = ''
        fare2 = 0 
        cabintype2 = ''
        if economy:
            if economy.findAll("div", {"class":"priceHolder"}):
                fare1 = economy.find("span", {"class":"tblCntBigTxt mileage"}).text
                fare1 = fare1.replace(",", "")
                if economy.find("span", {"class":"tblCntSmallTxt"}):
                    economytax1 = economy.find("span", {"class":"tblCntSmallTxt"}).text
                    ecotax = re.findall("\d+.\d+", economytax1)
                    print ecotax[0]
                    economytax = ecotax[0]
                print economytax
                # lenght = len(fareblock)
                # print fareblock[0].text
                if economy.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype1 = economy.find("div", {"class":"frmTxtHldr flightCabinClass"}).text
                    if 'Main Cabin' in cabintype1:
                        cabintype1 = cabintype1.replace('Main Cabin', 'Economy')
                    if 'Multiple Cabins' in cabintype1:
                        cabintype1 = cabintype1.replace('Multiple Cabins', 'Economy')
            else:
                fare1 = 0 
                cabintype1 = ''
            
        print "-------------------- Business --------------------------------------------------"
        if business:

            if business.findAll("div", {"class":"priceHolder"}):
                fare2 = business.find("span", {"class":"tblCntBigTxt mileage"}).text
                fare2 = fare2.replace(",", "")
                if business.find("span", {"class":"tblCntSmallTxt"}):
                    businesstax1 = business.find("span", {"class":"tblCntSmallTxt"}).text
                    buss_tax = re.findall("\d+.\d+", businesstax1)
                    businesstax = buss_tax[0]  
                       
                print businesstax
                # lenght = len(fareblock)
                # print fareblock[0].text
                if business.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype2 = business.find("div", {"class":"frmTxtHldr flightCabinClass"}).text
                    
            else:
                fare2 = 0 
                cabintype2 = ''
            if 'First' in cabintype2 or ('First' in cabinhead and 'Business' not in cabinhead):
                fare3 = fare2
                fare2 = 0
                cabintype3 = cabintype2
                firsttax = businesstax
                cabintype2 = ''
            else:
                cabintype2 = "Business"

        deptdetail = '@'.join(departdetails)
        arivedetail = '@'.join(arrivedetails)
        planetext = '@'.join(planedetails)
        # print 'arivedetail',arrivedetails
        # print 'plane', planedetails
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno, searchid, stime, stp, lyover, sourcestn, destinationstn, test1, arivalformat1, duration, str(fare1), str(economytax), str(fare2), str(businesstax), str(fare3), str(firsttax), cabintype1.strip(), cabintype2.strip(), cabintype3, "delta", deptdetail, arivedetail, planetext, operatedbytext))
        db.commit()
        print "data inserted"


    
    #display.stop()
    driver.quit()
    return searchkey

def united(origin, destination, searchdate, searchkey):
    #return searchkey
    db = MySQLdb.connect(host="localhost",  #server 
                     user="pex",           # flyfoodies
                      passwd="pex@1234",        # flyfoodies
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
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    driver.implicitly_wait(20)
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
    driver.implicitly_wait(20)
    try:
        print "data check"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "fl-results")))
        print "data check complete"
    except:
        #display.stop
        driver.quit()
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
        print len(datadiv)
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
                    print depttime
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
            test = driver.find_element_by_xpath("//a[@href='"+ detaillink +"']")
            #test = driver.execute_script("document.getElementById('" +detaillink+ "')")
    
            dtlid = detaillink.replace('#', '').strip()
            driver.execute_script("arguments[0].click();", test);
            time.sleep(0.05)
            html_page4 = driver.page_source
            html_page5 = html_page4.encode('utf-8')
            soup2 = BeautifulSoup(str(html_page5))
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
                         departtext = date_format + " | " + departtime + " from " + depart
                     if desttime:
                         dest_text = desttime + " at " + dest
                         if arival_date:
                            dest_text = arival_date + " | " + desttime + " at " + dest
                         else:
                             dest_text = date_format + " | " + desttime + " at " + dest
                              
                     else:
                         dest_text = date_format + " | " + arivetime + " at " + dest
                     departdlist.append(departtext)
                     arivelist.append(dest_text)
                     flight_number = info.find("div", {"class":"segment-flight-equipment"}).text
                     flight_number = flight_number.strip()
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
            driver.execute_script("arguments[0].click();", test);
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
                    print "econtax",econtax
                    if "+$" in econtax:
                        maintax = econtax.replace('+$', '')
                    
                else:
                    print "economy not available"
                    
                if prc.find("div", {"class":"fare-option bg-business"}):
                    cabintype2 = 'Business'
                    buss = prc.find("div", {"class":"fare-option bg-business"})
                    # print "business"
                    business = buss.find("div", {"class":"pp-base-price price-point"}).text
                    if "k" in business:
                        business = (business.replace('k', '')).replace("miles", '')
                        fare2 = float(business) * int('1000')
                    
                    busstax = buss.find("div", {"class":"pp-additional-fare price-point"}).text
                    print "busstax",busstax
                    if "+$" in busstax:
                        businesstax = busstax.replace('+$', '')
                    # print "busstax",businesstax
                    
                else:
                    print "business not available"
        
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
                    
                else:
                    print "first not available"
    
            departdetails = '@'.join(departdlist)
            arivedetails = '@'.join(arivelist)
            planedetails = ('@'.join(planelist)).strip()
            
            # print "operatedby",operatedby
            
            if len(operatedby) > 0:
                operatedbytext = '@'.join(operatedby)
            
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (flightno, str(searchid), stime, stoppage, "test", source, Destination, test1, arivetime2, totaltime, str(fare1), str(maintax), str(fare2), str(businesstax), str(fare3), str(firsttax), cabintype1, cabintype2, cabintype3, "united", departdetails, arivedetails, planedetails, operatedbytext))
            db.commit()
            print "row inserted"
    scrapepage(searchkey, soup)
    for i in pages:
        print "page no",i
        link = driver.find_element_by_xpath("//a[@href='" +i+ "']")
        #link = driver.find_element_by_link_text(pages[i])
        print "link",link
        driver.execute_script("arguments[0].click();", link);
        #link.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
        time.sleep(.5)
        html_page1 = driver.page_source
        soup = BeautifulSoup(html_page1)
        scrapepage(searchkey, soup)
        
    #display.stop
    driver.quit()
    return searchid

def etihad(source, destcode, searchdate, searchkey,scabin):
    #return searchkey
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    date = dt.strftime('%d/%m/%Y')
    print "final date", date
    db = MySQLdb.connect(host="localhost",   
                     user="pex",          
                      passwd="pex@1234",        
                      db="pex")
    cursor = db.cursor()

    #cursor = connection.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    search_cabin = ''
    if scabin == 'maincabin':
        search_cabin = "Radio1"
    elif scabin == 'firstclass':
        search_cabin = "Radio2"
    else:
        search_cabin = "Radio3"
    
    url = "http://www.etihad.com/en-us/plan-and-book/book-redemption-flights/"
    #display = Display(visible=0, size=(800, 600))
    #display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(20)
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "frm_2012158061206151234")))
    time.sleep(5)
    origin = driver.find_element_by_id("frm_2012158061206151234")
    origin.click()
    time.sleep(5)
    origin.send_keys(str(source))
    time.sleep(1)
    origin.send_keys(Keys.TAB)
    to = driver.find_element_by_id("frm_20121580612061235")
    time.sleep(3)
    to.send_keys(str(destcode))
    time.sleep(4)
    to.send_keys(Keys.TAB)
    
    oneway = driver.find_element_by_id("frm_oneWayFlight")
    driver.execute_script("arguments[0].click();", oneway)
    
    search_cabin1 = driver.find_element_by_id(search_cabin)
    driver.execute_script("arguments[0].click();", search_cabin1)
    
    ddate = driver.find_element_by_id("frm_2012158061206151238")
    ddate.clear()
    ddate.send_keys(date)
    ddate.send_keys(Keys.ENTER)
    flightbutton = driver.find_element_by_name("webform")
    flightbutton.send_keys(Keys.ENTER)
    
    time.sleep(3)
    html_page = driver.page_source
    
    soup = BeautifulSoup(html_page)
    datatable = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtcontainer-both")))
	maincontain = soup.find("div", {"id":"dtcontainer-both"})
	print "maincontain",maincontain
    	datatable = maincontain.find("tbody")

    except:
        #display.stop()
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        print "flag inserted" 
        return searchkey
    #maincontain = soup.find("div", {"id":"dtcontainer-both"})
    #print "maincontain",maincontain 
    #datatable = maincontain.find("tbody")

    trblock = datatable.findAll("tr")   
    for tds in trblock:
        duration = ''
        pricemiles = 0
        fare1 = 0
        ecotax = 0
        fare2 = 0
        businesstax = 0
        fare3 = 0
        firsttax = 0
        stoppage = ''
        fltno = ''
        from_code = ''
        from_time = ''
        to_code = ''
        to_time = ''
        departdetailtext = ''
        arivedetailtext = ''
        planedetailtext = ''
        operatortext = ''
        tax = 0
        print "======================================================================"
        
        airport = tds.findAll("td")
        flightnoth = tds.findAll("th",{"class":"flightNumber"})
        from_details = tds.find("th", {"class":"departureDateAndCode"})
        from_detail = ''
        if from_details: 
            from_detail = from_details.findAll("span")
        if len(from_detail) > 1:
            from_code = from_detail[0].text
            from_time = from_detail[2].text
        else:
            #display.stop()
            driver.quit()
            print "no data"
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
            db.commit()
            print "flag inserted" 
            return searchkey

        print from_code, from_time
        to_details = tds.find("th", {"class":"arrivalDateAndCode"})
        to_detail = ''
        if to_details:
            to_detail = to_details.findAll("span")
        if len(to_detail) > 1:
            to_code = to_detail[0].text
            to_time = to_detail[2].text
            print to_code, to_time
        
        totalduration = tds.find("th",{"class":"totalTripDuration"})
        if totalduration:
            duration =  totalduration.text
            print "duration",duration
        stops = tds.find("th",{"class":"stops"})
        if stops:
            stop = stops.text
            if '1' in stop:
                stoppage = "1 STOP"
            elif '2' in stop:
                stoppage = "2 STOPS"
            elif '3' in stop:
                stoppage = "3 STOPS"
            else:
                stoppage = "NONSTOP"
            print "stoppage", stoppage

        if flightnoth:
            fltno = ''
            opt =''
            flightno = flightnoth[0].find("span",{"class":"flight-number"})
            if flightno.find('span',{'id':'otp'}):
                opt = flightno.find('span',{'id':'otp'}).text
            fltno = flightno.text
            fltno = fltno.replace(opt,'')
            flt_link = driver.find_elements_by_xpath("//*[contains(text(), '"+str(fltno)+"')]")
            driver.execute_script("arguments[0].click();", flt_link[0])
            time.sleep(0.05)
            html_page1 = driver.page_source
            soup1 = BeautifulSoup(html_page1)
        
            detailblock = soup1.find("div", {"class":"flight"})
            detailbody = detailblock.find("tbody")
            trbody = detailbody.findAll("tr")
            departdetail = []
            arivedetail = []
            planedetail = []
            operator = []
            for info in trbody:
                tdblock = info.findAll("td")
                operatedby = tdblock[0].text
                operator.append(operatedby)
                ftno = tdblock[1].text
                origin = tdblock[2].text
                origin_tym2 = tdblock[3].find("span")["data-wl-date"]
                origin_tym1 = origin_tym2.split(",")
                origin_tym = origin_tym1[0]
                departinfo = origin_tym + " from " + origin
                departdetail.append(departinfo)
                dest = tdblock[4].text
                dest_tym2 = tdblock[5].find("span")["data-wl-date"]
                dest_tym1 = origin_tym2.split(",")
                dest_tym = dest_tym1[0]
                arivalinfo = dest_tym + " at " + dest
                arivedetail.append(arivalinfo)
                aircraft = tdblock[6].text
                plane = ftno + " | " + aircraft
                planedetail.append(plane)
                print "*************************************************************************"
            departdetailtext = '@'.join(departdetail)
            arivedetailtext = '@'.join(arivedetail)
            planedetailtext = '@'.join(planedetail)
            operatortext = '@'.join(operator)
        
        priceblocks = tds.findAll("td",{"class":"price"})
        if len(priceblocks) == 4:
            tmp = 1
        else:
            tmp = 0
        for j in range(tmp, len(priceblocks)):
            price = priceblocks[j].find("span").text
            if 'Sold out' not in price:
                price1 = re.findall("\d+.\d+", price)
                pricemiles = price1[0]
                currency_symbol = " ".join(re.findall("[a-zA-Z]+", price))
                currency_symbol1 = currency_symbol.split(' ')
                currencychange = urllib.urlopen("https://www.exchangerate-api.com/%s/%s/%f?k=e002a7b64cabe2535b57f764"%(currency_symbol1[1],"USD",float(price1[1])))
                chaged_result = currencychange.read()
                print "currencychange",chaged_result
                tax = chaged_result
                #tax = price1[1]
                break
        if scabin == 'maincabin':
            fare1 = pricemiles
            ecotax = tax
        elif scabin == 'firstclass':
            fare2 = pricemiles
            businesstax = tax
        else:
            fare3 = pricemiles
            firsttax = tax      
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno, str(searchkey), stime, stoppage, "test", from_code, to_code, from_time, to_time, duration, str(fare1), str(ecotax), str(fare2),str(businesstax), str(fare3), str(firsttax), "Economy", "Business", "First", "etihad", departdetailtext, arivedetailtext, planedetailtext, operatortext))
        db.commit()   
        print "data inserted"
     
    #display.stop()
    driver.quit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    print "flag inserted" 
    return searchkey

print "in delta"
print "origin",sys.argv[6],sys.argv[7],sys.argv[3],sys.argv[5],sys.argv[8]

delta(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[5])
united(sys.argv[1],sys.argv[2],sys.argv[4],sys.argv[5])
etihad(sys.argv[6],sys.argv[7],sys.argv[3],sys.argv[5],sys.argv[8])


