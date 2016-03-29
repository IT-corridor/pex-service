#!/usr/bin/env python 
import os, sys
from subprocess import call
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import _strptime
import MySQLdb
import re
from selenium.webdriver.common.proxy import *
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from django.db import connection, transaction
from multiprocessing import Process
import threading
from threading import Thread
import Queue
from pyvirtualdisplay import Display
import socket
import urllib
#from pexproject import settings




def delta(orgn, dest, searchdate, searchkey):
    #return searchkey
    db = MySQLdb.connect(host="localhost",  
                     user="root",           
                      passwd="1jyT382PWzYP",        
                      db="pex")  
    cursor = db.cursor()
    db.set_character_set('utf8')
    
    #cursor = connection.cursor()
    url = "http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    
    #driver = webdriver.Chrome()
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
        display.stop
        driver.quit()
        return searchkey
    soup = ''
    try:
        #print "test1"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
        print "data found"
	#html_page = driver.page_source
	#soup = BeautifulSoup(html_page)
    except:
        print "exception"
        display.stop()
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
    	db.commit()
        #transaction.commit()
        return searchkey
    
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "showAll")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
        sleep(1)
	#html_page = driver.page_source
	#soup = BeautifulSoup(html_page)
    except:
        print "single page data"
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    pricehead = soup.find("tr",{"class":"tblHeadUp"})
    pricecol = pricehead.findAll("label",{"class":["nextGenHiddenFieldWindow","tblHeadBigtext"]})
    datatable = soup.findAll("table", {"class":"fareDetails"})
    
    
    
    fare_flag = 0
    soup2 = ''
    try:
    	detailids = soup.findAll("div", {"class":"detailLinkHldr"})
    	for detlid in detailids:
            detailid = detlid['id']
            driver.execute_script("document.getElementById('"+detailid+"').click()")
            time.sleep(0.05)
    	time.sleep(0.06)
    	#page = driver.page_source
    	#soup2 = BeautifulSoup(page)
    except:
    	print "something wrong"
    	display.stop()
    	driver.quit()
    	cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
        print "delta flag inserted"
    	db.commit()
        #transaction.commit()
    	return searchkey
    n = 0
    
    htmlpage = driver.page_source
    soup2 = BeautifulSoup(htmlpage)
    cabin_ele = driver.find_elements_by_xpath("//*[@class='miscCabin']")
    #print "cabin_ele",cabin_ele
    for content in datatable:
        #if soup2:
        #time.sleep(0.06)
        #page = driver.page_source
        #page = str(page.encode('ascii', 'ignore'))
        #soup2 = BeautifulSoup(page)
        datatable1 = soup2.findAll("table", {"class":"fareDetails"})
        k = 0
        departdetails = []
        arrivedetails = []
        planedetails = []
        operatedbytext = ''
        efare_class = []
        bfare_class=[]
        ffare_class = []
        for cnt in datatable1:
            if cnt.find("div", {"class":"detailsRow" }) and k == n:
                detailblk = cnt.findAll("div", {"class":"detailsRow"})
                for tmp in detailblk:
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
        business = ''
        tds = content.findAll("td")
        cabinhead = ''
        detailsblock = tds[0]
        print len(pricecol)
        print len(tds)
        if  len(pricecol) > 1:
            if tds[1]:
                economy = tds[1]
            if  'Business' in pricecol[1].text or 'First' in pricecol[1].text:
                cabinhead = pricecol[1].text
                if len(tds) > 2:
                    business = tds[2]
            else:
                if len(pricecol) > 2:
                    cabinhead = pricecol[2].text
                    if 'Business' in cabinhead or 'First' in pricecol[2].text:
                        cabinhead = pricecol[2].text
                        if len(tds) > 3:
                             business = tds[3]
                     
        else:
            if len(pricecol) < 2:
                cabinhead = pricecol[0].text
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
            else:
                if route.find("div", {"class":"nStopBtn"}):
                    stp = route.find("div", {"class":"nStopBtn"}).text
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
            sourcestn = (route.find("div", {"class":"originCity"}).text)
            destinationstn = (route.find("div", {"class":"destinationCity"}).text)
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
                    economytax = ecotax[0]
                if economy.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype1 = economy.find("div", {"class":"frmTxtHldr flightCabinClass"}).text

                    if 'Main Cabin' in cabintype1:
                        cabintype1 = cabintype1.replace('Main Cabin', 'Economy')
                    if 'Multiple Cabins' in cabintype1:
                        #hover_element =  economy.find("div", {"class":"frmTxtHldr flightCabinClass"})
                        #hover_link = hover_element.find("a")['class']
                        hover = ActionChains(driver).move_to_element(cabin_ele[fare_flag])
                        hover.perform()
                        time.sleep(.2)
                        html_page2 = driver.page_source
                        soup = BeautifulSoup(html_page2)
                        hover_string = soup.find("tr",{"class","cabinClass_fly_bodyWrap"})
                        alltd = hover_string.findAll("td",{"class":"subheaderMsg"})
                        for tdtext in alltd:
                            #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                            fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                            efare_class.append(fare_class)
			    fare_flag = fare_flag+1                        
                        
                        
                        cabintype1 = cabintype1.replace('Multiple Cabins', 'Economy')
            else:
                fare1 = 0 
                cabintype1 = ''
            
        if business:
            alltd = ''
            if business.findAll("div", {"class":"priceHolder"}):
                fare2 = business.find("span", {"class":"tblCntBigTxt mileage"}).text
                fare2 = fare2.replace(",", "")
                if business.find("span", {"class":"tblCntSmallTxt"}):
                    businesstax1 = business.find("span", {"class":"tblCntSmallTxt"}).text
                    buss_tax = re.findall("\d+.\d+", businesstax1)
                    businesstax = buss_tax[0]  
                       
                if business.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype2 = business.find("div", {"class":"frmTxtHldr flightCabinClass"}).text
                    #print "cabintype2" ,cabintype2
                    if 'Multiple Cabins' in cabintype2:
                        #print "fare_flag",fare_flag
                        hover = ActionChains(driver).move_to_element(cabin_ele[fare_flag])
                        hover.perform()
                        #get_html  = ele.get_attribute("innerHTML")
                        time.sleep(1)
                        #time.sleep(.2)
                        html_page2 = driver.page_source
                        soup = BeautifulSoup(html_page2)
                        hover_string = soup.find("tr",{"class","cabinClass_fly_bodyWrap"})
                        alltd = hover_string.findAll("td",{"class":"subheaderMsg"})
                        fare_flag = fare_flag+1
                    
            else:
                fare2 = 0 
                cabintype2 = ''
            
            if 'First' in cabintype2 or ('First' in cabinhead and 'Business' not in cabinhead):
                fare3 = fare2
                fare2 = 0
                cabintype3 = cabintype2
                firsttax = businesstax
                cabintype2 = ''
                if alltd:
                    for tdtext in alltd:
                        #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                        fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                        ffare_class.append(fare_class)
                        #print "--------------------------- ----------------------------------------"
            else:
                cabintype2 = "Business"
                if alltd:
                    for tdtext in alltd:
                        #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                        fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                        bfare_class.append(fare_class)

        deptdetail = '@'.join(departdetails)
        arivedetail = '@'.join(arrivedetails)
        planetext = '@'.join(planedetails)
        efare_class_text = '@'.join(efare_class)
        bfare_class_text = '@'.join(bfare_class)
        ffare_class_text = '@'.join(ffare_class)
        #print "bfare_class_text",bfare_class_text
        #print "ffare_class_text",ffare_class_text
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno, searchid, stime, stp, lyover, sourcestn, destinationstn, test1, arivalformat1, duration, str(fare1), str(economytax), str(fare2), str(businesstax), str(fare3), str(firsttax), cabintype1.strip(), cabintype2.strip(), cabintype3, "delta", deptdetail, arivedetail, planetext, operatedbytext,efare_class_text,bfare_class_text,ffare_class_text))
        db.commit()
        #transaction.commit()
        print "data inserted"


    
    display.stop()
    driver.quit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
    db.commit()
    #transaction.commit()
    return searchkey

def etihad(source, destcode, searchdate, searchkey,scabin):
    #return searchkey
    #dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    #date = dt.strftime('%d/%m/%Y')
    date = searchdate
    print "final date", date
   
    db = MySQLdb.connect(host="localhost",   
                     user="root",          
                      passwd="1jyT382PWzYP",        
                      db="pex")
    db.set_character_set('utf8')
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
    
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver = webdriver.Chrome()
    '''
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 550)'''
    driver.get(url)
    time.sleep(3)
    try:
    	WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "frm_2012158061206151234")))
    except:
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag"))
        db.commit()
        #transaction.commit()
        print "etihad flag inserted"
        display.stop()
        driver.quit()
        return searchkey
    time.sleep(2)
    origin = driver.find_element_by_id("frm_2012158061206151234")
    origin.click()
    time.sleep(3)
    origin.send_keys(str(source))
    time.sleep(1)
    origin.send_keys(Keys.TAB)
    to = driver.find_element_by_id("frm_20121580612061235")
    time.sleep(2)
    to.send_keys(str(destcode))
    time.sleep(2)
    to.send_keys(Keys.TAB)
    
    oneway = driver.find_element_by_id("frm_oneWayFlight")
    oneway.click()
    #driver.execute_script("arguments[0].click();", oneway)
    
    search_cabin1 = driver.find_element_by_id(search_cabin)
    search_cabin1.click()
    #driver.execute_script("arguments[0].click();", search_cabin1)
    
    ddate = driver.find_element_by_id("frm_2012158061206151238")
    ddate.clear()
    ddate.send_keys(date)
    ddate.send_keys(Keys.ENTER)
    flightbutton = driver.find_element_by_name("webform")
    flightbutton.send_keys(Keys.ENTER)
    
    time.sleep(4)
    #html_page = driver.page_source
    
    #soup = BeautifulSoup(html_page)
    datatable = ''
    try:
        html_page = driver.page_source
    	soup = BeautifulSoup(html_page)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtcontainer-both")))
        maincontain = soup.find("div", {"id":"dtcontainer-both"})
    	datatable = maincontain.find("tbody")

    except:
        display.stop()
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag"))
        db.commit()
        #transaction.commit()
        print "flag inserted" 
        return searchkey

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
        
        airport = tds.findAll("td")
        flightnoth = tds.findAll("th",{"class":"flightNumber"})
        from_details = tds.find("th", {"class":"departureDateAndCode"})
        from_detail = ''
        if from_details: 
            from_detail = from_details.findAll("span")
        #print from_detail
        if len(from_detail) > 1:
            from_code = from_detail[0].text
            from_time = from_detail[1].text
	    #print "from info", from_code,from_time
        else:
            #display.stop()
            driver.quit()
            print "etihad has no data"
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag"))
            #transaction.commit()
            db.commit()
            print "etihad flag inserted" 
            return searchkey

        #print from_code, from_time
        to_details = tds.find("th", {"class":"arrivalDateAndCode"})
        to_detail = ''
        if to_details:
            to_detail = to_details.findAll("span")
        if len(to_detail) > 1:
            to_code = to_detail[0].text
            to_time = to_detail[1].text
        
        totalduration = tds.find("th",{"class":"totalTripDuration"})
        if totalduration:
            duration =  totalduration.text
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

        if flightnoth:
            fltno = ''
            opt =''
            flightno = flightnoth[0].find("span",{"class":"flight-number"})
            if flightno.find('span',{'id':'otp'}):
                opt = flightno.find('span',{'id':'otp'}).text
            fltno = flightno.text
            fltno = fltno.replace(opt,'')
    	    soup1 = ''
    	    try:
            	flt_link = driver.find_elements_by_xpath("//*[contains(text(), '"+str(fltno)+"')]")
            	driver.execute_script("arguments[0].click();", flt_link[0])
            	time.sleep(0.05)
            	html_page1 = driver.page_source
            	soup1 = BeautifulSoup(html_page1)
    	    except:
        	 	htmlpage = driver.page_source
        		soup1 = BeautifulSoup(htmlpage)
        
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
                tax = chaged_result
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
        #transaction.commit() 
        print "data inserted"
     
    display.stop()
    driver.quit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag"))
    db.commit()
    #transaction.commit()
    print "etihad flag inserted" 

    return searchkey

#print "in delta"
def threadcall():
    #return sys.argv[5]
    threads = []
    p2 = Thread(target=delta, args=(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[5]))
    #p3 = Thread(target=etihad, args=(sys.argv[6],sys.argv[7],sys.argv[3],sys.argv[5],sys.argv[8]))
    #p1.start()
    p2.start()
    threads.append(p2)
    #threads.append(p3)
    for t in threads:
	t.join

if __name__=='__main__':
    threadcall()
    date1 = datetime.datetime.strptime(sys.argv[3], '%m/%d/%Y')
    date = date1.strftime('%d/%m/%Y')
    #delta(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[5])
    etihad(sys.argv[6],sys.argv[7],date,sys.argv[5],sys.argv[8])
