#!/usr/bin/env python
import os,sys
from subprocess import call
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import MySQLdb
from selenium.webdriver.common.proxy import *
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.db import connection,transaction
from pyvirtualdisplay import Display
import socket
import urllib

def united(origin,destination,searchdate,searchkey):
    cursor = connection.cursor()
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%Y-%m-%d')
    currentdatetime = datetime.datetime.now()
    searchkey = searchkey
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f="+origin+"&t="+destination+"&d="+date+"&tt=1&at=1&sc=7&px=1&taxng=1&idx=1"
    #url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f="+origin+"&t="+dest+"&d=2015-10-31&r=2015-11-10&at=1&sc=0,0&px="+str(px)+"&taxng=1&idx=1"
    #url = "https://www.united.com/ual/en/us/?root=1"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(20)
    change = driver.find_element_by_link_text("Change").click()
    try:
        print "test"
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        print "test1"
        alert = driver.switch_to_alert()
        print "test1"
        alert.accept()

    except:
        print "no alert to accept"
    driver.implicitly_wait(20)
    try:  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
    except:
        display.stop
        driver.quit()
        return searchkey
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    datablock = soup.find("section",{"id":"fl-results"})
    pages =[]
    searchid=searchkey
    page = soup.findAll("a",{"class":"page-link"})
    for p in page:
       if (p.text).isdigit():
          pages.append(p.text)
    print pages
    def scrapepage(searchkey):
        print "aaya"
        fare1 = 0
        fare2 = 0
        fare3 = 0
        maintax = 0
        businesstax =0
        firsttax = 0
        cabintype1 = ''
        cabintype2 = ''
        cabintype3 = ''
        flightno =''
        stoppage =''
        searchid = searchkey
        source=''
        Destination = ''
        arivetime2 = ''
        departdetails=''
        arivedetails=''
        planedetails=''
        departtime =''
        test1 = ''
        operatedbytext =''
        totaltime =''
        #firsttax = 0
        datadiv = soup.findAll("div",{"class":"flight-block flight-block-fares  "})
        print len(datadiv)
        for row in datadiv:
            departdlist = []
            arivelist= []
            planelist= []
            operatedby=[]
            detailblock = row.findAll("div",{"class":"segment"})
            for datainfo in detailblock:
                fromto = datainfo.find("div",{"class":"segment-market"})['oldtitle']
                if 'to<br ></div>' in fromto:
                    fromto1 = fromto.split('to<br ></div>')
                    fromairport = fromto1[0]
                    departdlist.append(fromairport)
                    toairport = fromto1[1]
                    arivelist.append(toairport)
                fltno = datainfo.find("div",{"class":"segment-flight-number"}).text
                aircraft = datainfo.find("div",{"class":"segment-aircraft-type"}).text
                fltcraft = fltno +" | "+aircraft
                planelist.append(fltcraft)
                operateby = datainfo.find("div",{"class":"segment-operator"})
                if operateby:
                    operateby = operateby.text
                    operatedby.append(operateby)
            stopinfo = row.findAll("div",{"class":"segment-market"})
            for info in stopinfo:
                print info.text
            
            departtime = row.find("div",{"class":"flight-time flight-time-depart"}).text
            dateduration =''
            dateinfo=''
            if row.find("div",{"class":"date-duration"}):
                dateinfo = row.findAll("div",{"class":"date-duration"})
                dateduration = dateinfo[0].text
            print dateduration
            depttime  = departtime.replace(dateduration,'').strip()
            print depttime
            test = (datetime.datetime.strptime(depttime,'%I:%M %p'))
            test1 = test.strftime('%H:%M')
            print test1
            
            arivetime = row.find("div",{"class":"flight-time flight-time-arrive"}).text
            arivedate = ''
            if row.find("div",{"class":"date-duration"}) and dateinfo[1]:
                arivedate = dateinfo[1].text
            print arivedate
            arivaltime = arivetime.replace(arivedate,'').strip()
            arivetime1 = (datetime.datetime.strptime(arivaltime,'%I:%M %p'))
            arivetime2 = arivetime1.strftime('%H:%M')
            print "arivetime",arivetime2
            source1 = row.find("div",{"class":"flight-station flight-station-origin"}).text
            source2 = source1.split('(')
            source3 = (source2 [1].replace(')','')).split('-')
            source = source3[0].strip()
            
            destination1 = row.find("div",{"class":"flight-station flight-station-destination"}).text
            destination2 = destination1.split('(')
            destination3 = (destination2[1].replace(')','')).split('-')
            Destination = destination3[0].strip()
            stoppage = row.find("div",{"class":"flight-connection-container"}).text
            print "stoppage"
            if '1' in stoppage:
                stoppage = '1 STOP'
            elif '2' in stoppage:
                stoppage = '2 STOPS'
            else :
                if stoppage.strip() == 'Nonstop':
                    stoppage = 'NONSTOP'
            print "stoppage",stoppage
            totaltime = row.find("a",{"class":"flight-duration otp-tooltip-trigger"}).text
            if 'total' in totaltime:
                totaltime = totaltime.replace('total','')
            flightno = row.find("div",{"class":"segment-flight-number"}).text
            planetype = row.find("div",{"class":"segment-aircraft-type"}).text
            
            
            priceblock = row.findAll("div",{"class":"flight-block-fares-container"})
            
            for prc in priceblock:
                if prc.find("div",{"class":"fare-option bg-economy"}):
                    cabintype1 = "Economy"
                    eco = prc.find("div",{"class":"fare-option bg-economy"})
                    print "economy"
                    economy = eco.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in economy:
                        economy = (economy.replace('k','')).replace("miles",'')
                        fare1 = float(economy) * int('1000')
                    print fare1
                    econtax = eco.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in econtax:
                        maintax = econtax.replace('+$','')
                    print "econtax",maintax
                else:
                    print "economy not available"
                    
                if prc.find("div",{"class":"fare-option bg-business"}):
                    cabintype2 = 'Business'
                    buss = prc.find("div",{"class":"fare-option bg-business"})
                    print "business"
                    business = buss.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in business:
                        business = (business.replace('k','')).replace("miles",'')
                        fare2 = float(business) * int('1000')
                    print fare2
                    busstax = buss.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in busstax:
                        businesstax = busstax.replace('+$','')
                    print "busstax",businesstax
                    
                else:
                    print "business not available"
        
                if prc.find("div",{"class":"fare-option bg-first"}):
                    cabintype3 = 'First'
                    first1 = prc.find("div",{"class":"fare-option bg-first"})
                    print "first"
                    first = first1.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in first:
                        first = (first.replace('k','')).replace("miles",'')
                        fare3 = float(first) * int('1000')
                    print fare3
                    firsttax = first1.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in firsttax:
                        firsttax = firsttax.replace('+$','')
                    print "firsttax",firsttax
                else:
                    print "first not available"
    
            departdetails='@'.join(departdlist)
            arivedetails='@'.join(arivelist)
            planedetails='@'.join(planelist)
            
            print "operatedby",operatedby
            
            if len(operatedby)>0:
                operatedbytext='@'.join(operatedby)
            
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (flightno,str(searchid),time,stoppage,"test",source,Destination,test1,arivetime2,totaltime,str(fare1),str(maintax),str(fare2),str(businesstax),str(fare3),str(firsttax),cabintype1,cabintype2,cabintype3,"united",departdetails,arivedetails,planedetails,operatedbytext))
            transaction.commit()
            print "row inserted"
    for i in range(0,len(pages)):
        link = driver.find_element_by_link_text(pages[i])
        print link
        link.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
        driver.implicitly_wait(5)
        html_page1 = driver.page_source
        soup = BeautifulSoup(html_page1)
        scrapepage(searchkey)
    display.stop
    driver.quit()
    return searchid

	#call(["pgrep chrome | xargs kill"])	
def delta(orgn,dest,searchdate,searchkey):
    cursor = connection.cursor()
    url ="http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    print orgn, dest
    try:
    	display = Display(visible=0, size=(800, 600))
    	display.start()
    	chromedriver = "/usr/bin/chromedriver"
    	os.environ["webdriver.chrome.driver"] = chromedriver
    	chrome_options = Options()
    	#chrome_options = webdriver.ChromeOptions()
    	#chrome_options.add_argument('--enable-alternative-services')
    	print "option"
       	driver = webdriver.Chrome(chromedriver)
        print "oneway"
    	driver.implicitly_wait(40)
    	driver.get(url)
    	oneway = driver.find_element_by_id('oneWayBtn')
    	driver.execute_script("arguments[0].click();", oneway)
    	
    	origin = driver.find_element_by_id("originCity")
    	origin.clear()
    	origin.send_keys(orgn.strip())
    	destination = driver.find_element_by_id("destinationCity")
    	destination.send_keys(dest.strip())
    
    	ddate = driver.find_element_by_id("departureDate")#.click()
    	ddate.send_keys(str(searchdate))
    	'''
    	if returndate:
        	returndate = driver.find_element_by_id("returnDate")#.click()
        	returndate.send_keys(date1)
    	'''
    	#driver.find_element_by_id("departureDate").click()
    	#driver.find_elements_by_css_selector("td[data-date='"+date+"']")[0].click()
    
    	driver.find_element_by_id("milesBtn").send_keys(Keys.ENTER)
    	driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
	    
    except:
        display.stop
    	driver.quit()
    	return searchkey
	
    try:
        print "test1"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "_fareDisplayContainer_tmplHolder")))
    except:
        print "exception"
        display.stop()
        driver.quit()
        return searchkey
    
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "showAll")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
    except:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    datatable = soup.findAll("table",{"class":"fareDetails"})
    n=0
    for content in datatable:
        detailid = content.find("div",{"class":"detailLinkHldr"})['id']
        driver.execute_script("document.getElementById('"+detailid+"').click()")
        driver.implicitly_wait(2)
        page = driver.page_source
        soup2 = BeautifulSoup(page)
        datatable1 = soup2.findAll("table",{"class":"fareDetails"})
        k=0
        departdetails=[]
        arrivedetails=[]
        planedetails=[]
        operatedbytext=''
        for cnt in datatable1:
            if cnt.find("div",{"class":"detailsRow" }) and k==n:
                detailblk = cnt.findAll("div",{"class":"detailsRow"})
                for tmp in detailblk:
                    print "----------------------------------"
                    spaninfo =  tmp.findAll("p")
                    departdetails.append((spaninfo[0].text).replace('DEPARTS',''))
                    arrivedetails.append(spaninfo[1].text.replace('ARRIVES',''))
                    planedetails.append(spaninfo[2].text.replace('FLIGHT',''))
            k=k+1
        n=n+1
        tds = content.findAll("td")
        detailsblock = tds[0]
        economy = tds[1]
        if len(tds) > 2:
            business = tds[2]
        else:
            business = ''

        cabintype2 =''
        fare2 = 0
        timeblock = detailsblock.findAll("div",{"class":"flightDateTime"})
        for info in timeblock:
            temp = info.findAll("span")
            depature = temp[0].text
            part = depature[-2:]
            depature1 = depature.replace(part, "")
            depaturetime = depature1+" "+part
            print depaturetime
            test = (datetime.datetime.strptime(depaturetime,'%I:%M %p'))
            test1 = test.strftime('%H:%M')
            print test1
            arival = temp[3].text
            apart =  arival[-2:]
            arival = arival.replace(apart, "")
            arivaltime = arival+" "+apart
            arivalformat = (datetime.datetime.strptime(arivaltime,'%I:%M %p'))
            arivalformat1 = arivalformat.strftime('%H:%M')
            duration = temp[4].text
            
        flite_route = detailsblock.findAll("div",{"class":"flightPathWrapper"})
        fltno = detailsblock.find("a",{"class":"helpIcon"}).text
        print 
        for route in flite_route:
            if route.find("div",{"class":"nonStopBtn"}):
                stp = "NONSTOP"
                lyover = ""
                #print "nonstop"
            else:
                if route.find("div",{"class":"nStopBtn"}):
                    stp = route.find("div",{"class":"nStopBtn"}).text
                    #print route.find("div",{"class":"nStopBtn"}).text
                    if route.find("div",{"class":"layOver"}):
                        lyover = route.find("div",{"class":"layOver"}).text
                    elif route.find("div",{"class":"originCityVia2Stops"}):
                        multistop = route.findAll("div",{"class":"originCityVia2Stops"})
                        stoplist =[]
                        for sp in multistop:
                            stoplist.append(sp.text)
                        lyover="|".join(stoplist)
                    else:
                        lyover=''
                    #print route.find("div",{"class":"layOver"}).find("span").text
                    #print route.find("div",{"class":"layovertoolTip"}).text
                    #layover.append(lyover)
            sourcestn = (route.find("div",{"class":"originCity"}).text)
            destinationstn = (route.find("div",{"class":"destinationCity"}).text)
        print "-------------------- Economy--------------------------------------------------"
        economytax = 0
        businesstax = 0
        fare3 =0
        firsttax = 0
        cabintype3 =''
        if economy.findAll("div",{"class":"priceHolder"}):
            fare1 = economy.find("span",{"class":"tblCntBigTxt mileage"}).text
            fare1 = fare1.replace(",","")
            if economy.find("span",{"class":"tblCntSmallTxt"}):
                economytax = economy.find("span",{"class":"tblCntSmallTxt"}).text
                economytax = economytax.split('$')
                economytax = economytax[1].strip()
            print economytax
            #lenght = len(fareblock)
            #print fareblock[0].text
            if economy.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                cabintype1 = economy.find("div",{"class":"frmTxtHldr flightCabinClass"}).text
                if 'Main Cabin' in cabintype1:
                    cabintype1 = cabintype1.replace('Main Cabin','Economy')
                if 'Multiple Cabins' in cabintype1:
                    cabintype1 = cabintype1.replace('Multiple Cabins','Economy')
        else:
            fare1 = 0 #economy.find("span",{"class":"ntAvail"}).text
            cabintype1 =''
            
        print "-------------------- Business --------------------------------------------------"
        if business:

            if business.findAll("div",{"class":"priceHolder"}):
                fare2 = business.find("span",{"class":"tblCntBigTxt mileage"}).text
                fare2 = fare2.replace(",","")
                if business.find("span",{"class":"tblCntSmallTxt"}):
                    businesstax = business.find("span",{"class":"tblCntSmallTxt"}).text
                    businesstax = businesstax.split('$')
                    businesstax = businesstax[1].strip()
                print businesstax
                #lenght = len(fareblock)
                #print fareblock[0].text
                if business.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                    cabintype2 = business.find("div",{"class":"frmTxtHldr flightCabinClass"}).text
                    
            else:
                fare2 = 0 #business.find("span",{"class":"ntAvail"}).text
                cabintype2 = ''
            if 'First' in cabintype2:
                fare3 = fare2
                fare2 = 0
                cabintype3 = cabintype2
                firsttax = businesstax
                cabintype2 =''
            else:
                cabintype2 = "Business"

        deptdetail = '@'.join(departdetails)
        arivedetail = '@'.join(arrivedetails)
        planetext = '@'.join(planedetails)
        #print 'arivedetail',arrivedetails
        #print 'plane', planedetails
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,searchid,time,stp,lyover,sourcestn,destinationstn,test1,arivalformat1,duration,str(fare1),str(economytax),str(fare2),str(businesstax),str(fare3),str(firsttax),cabintype1.strip(),cabintype2.strip(),cabintype3,"delta",deptdetail,arivedetail,planetext,operatedbytext))
        transaction.commit()
        print "data inserted"


    
    display.stop()
    driver.quit()
    return searchkey

    
