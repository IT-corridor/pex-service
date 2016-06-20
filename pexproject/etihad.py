#!/usr/bin/env python 
import os, sys
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
import json
import customfunction
#from pyvirtualdisplay import Display
import urllib

def etihad(source, destcode, searchdate, searchkey,scabin):
    #return searchkey
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    date = dt.strftime('%d/%m/%Y')
    db = customfunction.dbconnection()
    cursor = db.cursor()
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
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)  
    driver.get(url)
    def storeFlag(searchkey,stime):
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        print "etihad flag inserted"
        driver.quit()
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "frm_2012158061206151234")))
    except:
        storeFlag(searchkey,stime)
        return searchkey

    driver.execute_script('document.getElementById("frm_2012158061206151234").removeAttribute("readonly")')
    oneway = driver.find_element_by_id("frm_oneWayFlight")
    #oneway.click()
    driver.execute_script("return arguments[0].click();", oneway)
    
    search_cabin1 = driver.find_element_by_id(search_cabin)
    #search_cabin1.click()
    driver.execute_script("return arguments[0].click();", search_cabin1)
    
    origin = driver.find_element_by_id("frm_2012158061206151234")
    
    driver.execute_script("return arguments[0].click();", origin)
    #origin.click()
    time.sleep(1)
    origin.send_keys(str(source))
    time.sleep(1)
    origin.send_keys(Keys.TAB)
    flag = 0
    flag1 = 0
    sourceVal = ''
    def setOrigin():
        origin.clear()
        origin.send_keys(str(source))
        time.sleep(1)
        origin.send_keys(Keys.TAB)
    while flag < 1 and flag1 < 2:
        sourceVal = origin.get_attribute("value")   
        if (sourceVal == '' or len(sourceVal) <= len(source)):
            setOrigin()
            flag1 = flag1+1
        else:
            flag = flag+1
    if sourceVal == '':
        storeFlag(searchkey,stime)
        return
    flag = 0
    flag1 = 0
    driver.execute_script('return document.getElementById("frm_20121580612061235").removeAttribute("readonly")')
    to = driver.find_element_by_id("frm_20121580612061235")
    time.sleep(1) 
    to.send_keys(destcode)
    time.sleep(1)
    to.send_keys(Keys.TAB)
    def setDestination():
        to.clear()
        to.send_keys(destcode)
        time.sleep(1)
        to.send_keys(Keys.TAB)
    destcodeVal = ''
    while flag < 1 and flag1 < 2:
        destcodeVal = to.get_attribute("value")
        if (destcodeVal == '' or len(destcodeVal) <= len(destcode)) and flag < 2:
            flag1 = flag1+1
            setDestination()
        else:
            flag = flag+1
    if destcodeVal == '':
        storeFlag(searchkey,stime)
        return
    time.sleep(1)
    ddate = driver.find_element_by_id("frm_2012158061206151238")
    ddate.clear()
    ddate.send_keys(date)
    ddate.send_keys(Keys.TAB)
    flightbutton = driver.find_element_by_name("webform")
    flightbutton.send_keys(Keys.ENTER)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "dtcontainer-both")))
    except:
        storeFlag(searchkey,stime)
        return searchkey
    
    html_page = driver.page_source
    soup = BeautifulSoup(html_page,"lxml")
    operators = soup.findAll("th",{"class":"operatingCarrier"})
    operatorArray = []
    for optr in operators:
        operatorDiv = optr.findAll("p")
        for opname in operatorDiv:
            operatorArray.append(opname.text)
    templatedata = soup.find('script', text=re.compile('var templateData = '))
    time.sleep(1)
    json_text = re.search(r'^\s*var templateData = \s*({.*?})\s*;\s*$',templatedata.string, flags=re.DOTALL | re.MULTILINE).group(1)
    jsonData = json.loads(json_text)
    
    tempdata = jsonData["rootElement"]["children"][1]["children"][0]["children"][4]["model"]["allItineraryParts"]
    
    value_string = []
    opCounter = 0
    for k in range(0,len(tempdata)):
        segments = tempdata[k]["segments"]
        
        rowRecord = tempdata[k]["itineraryPartData"]
        fltno = ''
        #@@@@@@ Depart Details @@@@@@@@@@@@@@@@@
        origin = rowRecord["departureCode"]
        
        dest = rowRecord["arrivalCode"]
       
        departureDate = rowRecord["departureDate"]
        
        deptDateTime = departureDate.split(" ")
        
        #@@@@@@@ Segment info @@@@@@@@@@@@@@@@@
        originDetails = []
        destDetails = []
        flightsDetails =[]
        operatorCarrier = []
        bookingFareCode = []
        
        for counter in range (0,len(segments)):
            bookingFare = ''
            bookingCode = segments[counter]['bookingClass']
            bookingClass = segments[counter]['allClassOfService']
            bookingFare = bookingCode+" "+bookingClass
            bookingFareCode.append(bookingFare)
            segOrigin = segments[counter]["departureCode"]
            segDepartDate = segments[counter]["departureDate"]
            segDetailFormat = segDepartDate+" | from "+segOrigin
            originDetails.append(segDetailFormat)
            
            segDest = segments[counter]["arrivalCode"]
            segArive = segments[counter]["arrivalDate"]
            destdetailFormat = segArive+" | at "+segDest
            destDetails.append(destdetailFormat)
            if len(operatorArray) > opCounter:
                operatorCarrier.append(operatorArray[opCounter])
                opCounter = opCounter+1
            
        deptDate = deptDateTime[0]
        depttime = deptDateTime[1]
        depttime1 = (datetime.datetime.strptime(depttime, '%H:%M:%S'))
        departtime = depttime1.strftime('%H:%M')
      
        
        arrivalDate = rowRecord["arrivalDate"]
        
        
        arrivalDateTime = arrivalDate.split(" ")
        
        arivaldt = arrivalDateTime[0]
        arivalTime = arrivalDateTime[1]
        arivalTime1 = (datetime.datetime.strptime(arivalTime, '%H:%M:%S'))
        arive = arivalTime1.strftime('%H:%M')
       
        
        totalTripDuration = rowRecord["totalTripDuration"]
        
        totalMinte = (int(totalTripDuration)/60000)
        hr = totalMinte/60
        minute = totalMinte % 60
        tripDuration = str(hr)+"h "+str(minute)+"m"
        
        departureCodes = rowRecord["departureCodes"]
        #arrivalCodes = rowRecord["arrivalCodes"]
        operatingCarrier = rowRecord["operatingCarrier"]
        flightDurations = rowRecord["flightDurations"]
        
        flightNumber = rowRecord["flightNumber"]
        airlineCodes = rowRecord["airlineCodes"]
        aircraftType = rowRecord["aircraftType"]
        for f in range(0,len(flightNumber)):
            flightNo = airlineCodes[f]+" "+str(flightNumber[f])
            if f == 0:
                fltno = flightNo
            fltTime = flightDurations[f]
            fltMinuteTime = int(fltTime)/60000
            fltMinuteTimeHour = fltMinuteTime/60
            fltMinuteTime = fltMinuteTime % 60
            fltTimeFormat = str(fltMinuteTimeHour)+"h "+str(fltMinuteTime)+"m"
            fltFormat = flightNo+" | "+aircraftType[f]+" ("+fltTimeFormat+")"
            flightsDetails.append(fltFormat)
        originDetailString = '@'.join(originDetails)
        arivedetailtext = '@'.join(destDetails)
        planedetailtext = '@'.join(flightsDetails)
        operatortext = ''
        bookingFareCodeString = ''
        if len(operatorCarrier) > 0:
            operatortext = '@'.join(operatorCarrier)
        if len(bookingFareCode) > 0:
            bookingFareCodeString = '@'.join(bookingFareCode)
        
        noOfStop = len(departureCodes) - 1
        stoppage = ''
        if noOfStop == 0:
            stoppage = "NONSTOP"
        elif noOfStop == 1:
            stoppage = "1 STOP"
        else:
            stoppage = str(noOfStop)+" STOPS"
      
        allPrices = tempdata[k]["basketsRef"]
        
        economylist = []
        ecotaxlist = []
        businesslist = []
        busstaxlist= []
        firstlist = []
        fisrtaxlist = []
        for key in allPrices:
            farePrices = allPrices[key]["prices"]["priceAlternatives"]
            #print farePrices
            classOfService = allPrices[key]["classOfService"]
            for m in range(0,len(farePrices)):
                saverPrice = farePrices[m]["pricesPerCurrency"]
                for infokey in saverPrice:
                    
                    if infokey == "FFCURRENCY":
                        miles = saverPrice[infokey]["amount"]
                    else:
                        rawTaxes = saverPrice[infokey]["amount"]
                        currencychange = urllib.urlopen("https://www.exchangerate-api.com/%s/%s/%f?k=e002a7b64cabe2535b57f764"%(infokey,"USD",float(rawTaxes)))
                        taxes = currencychange.read()
                    
                
                if "ECONOMY" in classOfService:
                    economylist.append(miles)
                    ecotaxlist.append(taxes)
                elif "BUSINESS" in classOfService:
                    businesslist.append(miles) 
                    busstaxlist.append(taxes)
                elif "FIRST" in classOfService:
                    firstlist.append(miles)
                    fisrtaxlist.append(taxes)
        
        if len(economylist) >= len(businesslist) and len(economylist) >= len(firstlist):
            priceLength = len(economylist)
        elif len(businesslist) >= len(economylist) and len(businesslist) >= len(firstlist):
            priceLength = len(businesslist)
        else:
            priceLength = len(firstlist)
        for c in range(0,priceLength):
            economy = 0
            ecotax = 0
            business = 0
            businesstax = 0
            first = 0
            firsttax = 0
            
            if c < len(economylist):
                economy = economylist[c]
                ecotax = ecotaxlist[c]
            
            if c < len(businesslist):
                business = businesslist[c]
                businesstax = busstaxlist[c]
            
            if c < len(firstlist):
                first = firstlist[c]
                firsttax = fisrtaxlist[c]
            
            value_string.append((str(fltno), str(searchkey), stime, stoppage, "test", origin, dest, departtime, arive, tripDuration, str(economy), str(ecotax), str(business),str(businesstax), str(first), str(firsttax), "Economy", "Business", "First", "etihad", originDetailString, arivedetailtext, planedetailtext, operatortext,bookingFareCodeString,bookingFareCodeString,bookingFareCodeString))
            if len(value_string)> 50:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                db.commit() 
                value_string = []
    if len(value_string) > 0 :
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
        db.commit()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "etihad", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    driver.quit()
    #display.stop()    
    return searchkey
                
        
    
    
if __name__=='__main__':
    etihad(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

