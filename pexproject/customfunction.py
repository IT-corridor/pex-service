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
    date_format = dt.strftime('%a, %b %-d')
    print date_format
    currentdatetime = datetime.datetime.now()
    searchkey = searchkey
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f="+origin+"&t="+destination+"&d="+date+"&tt=1&at=1&sc=7&px=1&taxng=1&idx=1"
    #url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f="+origin+"&t="+dest+"&d=2015-10-31&r=2015-11-10&at=1&sc=0,0&px="+str(px)+"&taxng=1&idx=1"
    #url = "https://www.united.com/ual/en/us/?root=1"
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    driver.get(url)
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
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
    except:
    	
    	print driver.current_url
        display.stop
        driver.quit()
        return searchkey
    time.sleep(3)
    html_page = driver.page_source
    soup = BeautifulSoup(html_page)
    #datablock = soup.find("section",{"id":"fl-results"})
    pages =[]
    searchid=searchkey
    page = soup.findAll("a",{"class":"page-link"})
    for p in page:
       if (p.text).isdigit():
          pages.append(p.text)
    print pages
    def scrapepage(searchkey,soup):
        soup = soup
        
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
        datadiv = soup.findAll("div",{"class":"flight-block"})
        
        for row in datadiv:
            stoppage = row.find("div",{"class":"flight-connection-container"}).text
            
            if '1' in stoppage:
                stoppage = '1 STOP'
            elif '2' in stoppage:
                stoppage = '2 STOPS'
            elif '3' in stoppage:
                stoppage = '3 STOPS'
            else :
                if stoppage.strip() == 'Nonstop':
                    stoppage = 'NONSTOP'
            
            source1 = row.find("div",{"class":"flight-station flight-station-origin"}).text
            source2 = source1.split('(')
            source3 = (source2 [1].replace(')','')).split('-')
            source = source3[0].strip()
            #print source1
            destination1 = row.find("div",{"class":"flight-station flight-station-destination"}).text
            destination2 = destination1.split('(')
            destination3 = (destination2[1].replace(')','')).split('-')
            Destination = destination3[0].strip()
            #print destination1
            departdlist = []
            arivelist= []
            planelist= []
            operatedby=[]
            
            departtime = row.find("div",{"class":"flight-time flight-time-depart"}).text
            dateduration =''
            dateinfo=''
            if row.find("div",{"class":"date-duration"}):
                dateinfo = row.findAll("div",{"class":"date-duration"})
                dateduration = dateinfo[0].text
            #print dateduration
            depttime  = departtime.replace(dateduration,'').strip()
            #print depttime
            test = (datetime.datetime.strptime(depttime,'%I:%M %p'))
            test1 = test.strftime('%H:%M')
            #print test1
            
            arivetime = row.find("div",{"class":"flight-time flight-time-arrive"}).text
            arivedate = ''
            if row.find("div",{"class":"date-duration"}) and dateinfo[1]:
                arivedate = dateinfo[1].text
            #print arivedate
            arivaltime = arivetime.replace(arivedate,'').strip()
            if '.' in arivaltime:
                arivaltime = arivaltime.replace('.','')
            arivetime1 = (datetime.datetime.strptime(arivaltime,'%I:%M %p'))
            arivetime2 = arivetime1.strftime('%H:%M')
            #print "arivetime",arivetime2
            
            totaltime = row.find("a",{"class":"flight-duration otp-tooltip-trigger"}).text
            if 'total' in totaltime:
                totaltime = totaltime.replace('total','')
            flightno = row.find("div",{"class":"segment-flight-number"}).text
            planetype = row.find("div",{"class":"segment-aircraft-type"}).text
            
            detaillink = row.find("a",{"class":"toggle-flight-block-details ui-tabs-anchor"})['href']
            test = driver.find_element_by_xpath("//a[@href='"+detaillink+"']")
            dtlid = detaillink.replace('#','').strip()
            driver.execute_script("arguments[0].click();", test);
            time.sleep(1)
            html_page1 = driver.page_source
            soup2 = BeautifulSoup(html_page1)
            departuretime = ''
            desttime = ''
            flight_duration= ''
            flight_number = ''
            arival_date = ''
            departure_date =''
            if soup2.find("div",{"id":dtlid}):
                 detailsinfo = soup2.find("div",{"id":dtlid})
                 infoblock = detailsinfo.findAll("div",{"class":"segment-details-left"})
                 for info in infoblock:
                     origindest1 = info.find("div",{"class":"segment-orig-dest"}).text
                     origindest2 = origindest1.split(' to ')
                     depart = origindest2[0]
                     dest = origindest2[1]
                     if info.find('ul',{"class":"advisories-messages"}):
                         uls = info.find('ul',{"class":"advisories-messages"})
                         lis = uls.findAll("li")
                         if len(lis) > 1:
                              ddate = lis[0].text
                              ardate = lis[1].text 
                              if ':' in ddate and ':' in ardate:
                                  ddate = ddate.split(':')
                                  departure_date = ddate[1]
                                  ardate = ardate.split(':')
                                  arival_date = ardate[1]
                     if info.find("div",{"class":"segment-times"}):
                         timesegmt = info.find("div",{"class":"segment-times"}).text
                         timesegmt1 = timesegmt.split('-')
                         departuretime = timesegmt1[0]
                         timesegmt2 = timesegmt1[1].split('(')
                         desttime = timesegmt2[0]
                         flight_duration = timesegmt2[1].replace(')','')
                     if departuretime:
                         departtext = departuretime+" from "+depart
                         if departure_date:
                             departtext = departure_date+" | "+departuretime+" from "+depart
                         else:
                             departtext = date_format+" | "+departuretime+" from "+depart
                             
                     else:
                         departtext = date_format+" | "+departtime+" from "+depart
                     if desttime:
                         dest_text = desttime+" at "+dest
                         if arival_date:
                            dest_text = arival_date+" | "+desttime+" at "+dest
                         else:
                             dest_text = date_format+" | "+desttime+" at "+dest
                              
                     else:
                         dest_text = date_format+" | "+arivetime+" at "+dest
                     departdlist.append(departtext)
                     arivelist.append(dest_text)
                     flight_number = info.find("div",{"class":"segment-flight-equipment"}).text
                     if flight_duration:
                         plane_text = flight_number+" ("+flight_duration+")"
                         planelist.append(plane_text)
                     else:
                         planelist.append(flight_number)
                     
                     operateby = info.find("div",{"class":"segment-operator"})
                     if operateby:
                         operateby = operateby.text
                         operatedby.append(operateby)
            
            priceblock = row.findAll("div",{"class":"flight-block-fares-container"})
            
            for prc in priceblock:
                if prc.find("div",{"class":"fare-option bg-economy"}):
                    cabintype1 = "Economy"
                    eco = prc.find("div",{"class":"fare-option bg-economy"})
                    #print "economy"
                    economy = eco.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in economy:
                        economy = (economy.replace('k','')).replace("miles",'')
                        fare1 = float(economy) * int('1000')
                    
                    econtax = eco.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in econtax:
                        maintax = econtax.replace('+$','')
                    
                else:
                    print "economy not available"
                    
                if prc.find("div",{"class":"fare-option bg-business"}):
                    cabintype2 = 'Business'
                    buss = prc.find("div",{"class":"fare-option bg-business"})
                    #print "business"
                    business = buss.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in business:
                        business = (business.replace('k','')).replace("miles",'')
                        fare2 = float(business) * int('1000')
                    
                    busstax = buss.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in busstax:
                        businesstax = busstax.replace('+$','')
                    #print "busstax",businesstax
                    
                else:
                    print "business not available"
        
                if prc.find("div",{"class":"fare-option bg-first"}):
                    cabintype3 = 'First'
                    first1 = prc.find("div",{"class":"fare-option bg-first"})
                    
                    first = first1.find("div",{"class":"pp-base-price price-point"}).text
                    if "k" in first:
                        first = (first.replace('k','')).replace("miles",'')
                        fare3 = float(first) * int('1000')
                    
                    firsttax = first1.find("div",{"class":"pp-additional-fare price-point"}).text
                    if "+$" in firsttax:
                        firsttax = firsttax.replace('+$','')
                    
                else:
                    print "first not available"
    
            departdetails='@'.join(departdlist)
            arivedetails='@'.join(arivelist)
            planedetails='@'.join(planelist)
            
            #print "operatedby",operatedby
            
            if len(operatedby)>0:
                operatedbytext='@'.join(operatedby)
            
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (flightno,str(searchid),stime,stoppage,"test",source,Destination,test1,arivetime2,totaltime,str(fare1),str(maintax),str(fare2),str(businesstax),str(fare3),str(firsttax),cabintype1,cabintype2,cabintype3,"united",departdetails,arivedetails,planedetails,operatedbytext))
            transaction.commit()
            print "row inserted"
    scrapepage(searchkey,soup)
    for i in range(0,len(pages)):
        link = driver.find_element_by_link_text(pages[i])
        print link
        link.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product_MIN-ECONOMY-SURP-OR-DISP")))
        time.sleep(2)
        html_page1 = driver.page_source
        soup = BeautifulSoup(html_page1)
        scrapepage(searchkey,soup)
    display.stop
    driver.quit()
    return searchid

	#call(["pgrep chrome | xargs kill"])	
def delta(orgn,dest,searchdate,searchkey):
    cursor = connection.cursor()
    url ="http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    print orgn, dest
    try:
    	display = Display(visible=0, size=(800, 600))
    	display.start()
    	chromedriver = "/usr/bin/chromedriver"
    	os.environ["webdriver.chrome.driver"] = chromedriver
    	chrome_options = Options()
    	#chrome_options = webdriver.ChromeOptions()
    	#chrome_options.add_argument('--enable-alternative-services')
       	driver = webdriver.Chrome(chromedriver)
    	driver.implicitly_wait(40)
    	driver.get(url)
        time.sleep(1)
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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "_fareDisplayContainer_tmplHolder")))
    except:
        print "exception"
        display.stop()
        driver.quit()
        return searchkey
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "showAll")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
    except:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
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
                    flight_duration = spaninfo[2].text.replace('FLIGHT','')
                    flight_duration1 = flight_duration.split("|")
                    flight_no = flight_duration1[0].strip()
                    plane_duration = flight_duration1[1].strip()
                    aircraft1 = spaninfo[3].text.replace('PLANE','')
                    aircraft = aircraft1.replace('- View SeatsOpens in a new window','')
                    planedetailinfo = flight_no+" | "+aircraft+" ("+plane_duration+")"
                    planedetails.append(planedetailinfo)
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
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,searchid,stime,stp,lyover,sourcestn,destinationstn,test1,arivalformat1,duration,str(fare1),str(economytax),str(fare2),str(businesstax),str(fare3),str(firsttax),cabintype1.strip(),cabintype2.strip(),cabintype3,"delta",deptdetail,arivedetail,planetext,operatedbytext))
        transaction.commit()
        print "data inserted"


    
    display.stop()
    driver.quit()
    return searchkey

    
