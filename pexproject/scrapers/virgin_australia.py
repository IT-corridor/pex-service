#!/usr/bin/env python 
import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import _strptime
import re
import json
import pdb
from selenium.webdriver.common.proxy import *
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display

DEV_LOCAL = False
# DEV_LOCAL = True

if not DEV_LOCAL:
    import customfunction

def virginAustralia(from_airport,to_airport,searchdate,searchid,cabinName,isflag):
    if not DEV_LOCAL:
        db = customfunction.dbconnection()
        cursor = db.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    dateday = dt.strftime('%d')
    datemonth = dt.strftime('%Y%m')
    cabinType = ''
    if cabinName == "maincabin":
        cabinType = "E"
    else:
        cabinType = "B"
    
    url = "http://www.virginaustralia.com/au/en/bookings/flights/make-a-booking/?bookingType=flights&passthru=0&trip_type=0&origin="+from_airport+"&destination="+to_airport+"&travel_class="+cabinType+"&adults=1&children=0&infants=0&date_flexible=0&use_points=1&showPromoCode=1&date_start_day="+str(dateday)+"&date_start_month="+str(datemonth) #+"&date_end_day="+str(dateday)+"&date_end_month="+str(datemonth)
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    
    def storeFlag(searchid,stime,isflag):
        if isflag:   
            if not DEV_LOCAL:
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin Australia", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
                db.commit()
        display.stop()
        driver.quit()
    try:
        driver.get(url)
        # print driver.page_source
        submitbtn = WebDriverWait(driver,5).until(
                    lambda driver :driver.find_element_by_xpath("//*[contains(text(), 'Find Flights')]"))
        driver.execute_script("arguments[0].click();", submitbtn)
        
    except:
        storeFlag(searchid,stime,isflag)
        return
    try:
        # check Invalid Input
        WebDriverWait(driver,2).until(EC.presence_of_element_located((By.ID, "page-dialog")))
        storeFlag(searchid,stime,isflag)
        return
    except:
        print "form submitted"
    try:
        # check No flight data 
        errorValue = WebDriverWait(driver,5).until(
                    lambda driver :driver.find_elements_by_class_name("flightAdvisoryMessages"))
        storeFlag(searchid,stime,isflag)
        return
    except:
        print "data found"
    try:
        # driver.save_screenshot('/root/out_enter.png');
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dtcontainer-0")))
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"xml")
        templatedata = soup.find('script', text=re.compile('var templateData = '))
        # time.sleep(1)
        json_text = re.search(r'^\s*var templateData = \s*({.*?})\s*;\s*$',templatedata.string, flags=re.DOTALL | re.MULTILINE).group(1)
        jsonData = json.loads(json_text)
        tempdata = jsonData["rootElement"]["children"][1]["children"][0]["children"][7]["model"]
    except:
        storeFlag(searchid,stime,isflag)
        return searchid
    i = 1 
    try:
        operatordiv = soup.findAll(True, {'class': re.compile(r'\operating-carrier-wrapper\b')})
       
        # print operatordiv, '@@@@@@@@@2'
        operatorArray = []
        for div in operatordiv:
            #print "========================================================================"
            optrtext =''
            optr = div.find("span",{"class":["carrier-name","operator-meta-data-internal"]})
            if optr:
                optrtext = optr.text
                if '/' in optrtext[0]:
                     optrtext = optrtext.replace('/','')
            operatorArray.append(optrtext)
        maindata = tempdata['dayOffers'][0]["itineraryOffers"]
        
        operatorDetails = []
        value_string = []
        operatorcounter = 0
        for k in range(0,len(maindata)):
            flightsDetails =[]
            segments = maindata[k]["segments"]
            rowRecord = maindata[k]["itineraryPartData"]
            fltno = ''
            #@@@@@@ Depart Details @@@@@@@@@@@@@@@@@
            origin = rowRecord["departureCode"]
            dest = rowRecord["arrivalCode"]
            departureDate = rowRecord["departureDate"]
            deptDateTime = departureDate.split(" ")
            #departdetailFormat = departureDate+" | from "+origin
            #originDetails.append(departdetailFormat)
            #@@@@@@@ Segment info @@@@@@@@@@@@@@@@@
            originDetails = []
            destDetails = []
            operatingCarrier = []
            fareClassCode = []
            eco_fare_code = ''
            bus_fare_code= ''
            sep = ''
            for counter in range (0,len(segments)):
                bookingCode1 = ''
                bookingCode = segments[counter]['bookingClass']
                if cabinType == 'E':
                    eco_fare_code = eco_fare_code+sep+bookingCode
                    sep = ','
                    bookingCode1 = bookingCode+" Economy"
                else:
                    bus_fare_code = bus_fare_code+sep+bookingCode
                    sep = ','
                    bookingCode1 = bookingCode+" Business"
                fareClassCode.append(bookingCode1)
                segOrigin = segments[counter]["departureCode"]
                segDepartDate = segments[counter]["departureDate"]
                if DEV_LOCAL:
                    airport_ = segOrigin
                else:
                    airport_ = customfunction.get_airport_detail(segOrigin) or segOrigin

                segDetailFormat = segDepartDate[:-3]+" | from "+airport_
                originDetails.append(segDetailFormat)
                
                segDest = segments[counter]["arrivalCode"]
                segArive = segments[counter]["arrivalDate"]
                if DEV_LOCAL:
                    airport_ = segDest
                else:
                    airport_ = customfunction.get_airport_detail(segDest) or segDest
                destdetailFormat = segArive[:-3]+" | at "+airport_
                destDetails.append(destdetailFormat)
                if len(operatorArray) >= operatorcounter:
                    operatingCarrier.append(operatorArray[operatorcounter]) 
                    operatorcounter = operatorcounter+1     
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
            #operatingCarrier = rowRecord["operatingCarrier"]
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
                if DEV_LOCAL:
                    fltFormat = flightNo+" | "+aircraftType[f]+" ("+fltTimeFormat+")"
                else:    
                    fltFormat = flightNo+" | "+customfunction.AIRCRAFTS[aircraftType[f]]+" ("+fltTimeFormat+")"
                flightsDetails.append(fltFormat)
            originDetailString = '@'.join(originDetails)
            arivedetailtext = '@'.join(destDetails)
            planedetailtext = '@'.join(flightsDetails)
            ecoFareCode = ''
            busFareCode = ''
            firstFareCode = ''
            if len(fareClassCode)> 0:
                if cabinType == 'E':
                    ecoFareCode = '@'.join(fareClassCode)
                else:
                    busFareCode = '@'.join(fareClassCode)
    
            noOfStop = len(departureCodes) - 1
            stoppage = ''
            if noOfStop == 0:
                stoppage = "NONSTOP"
            elif noOfStop == 1:
                stoppage = "1 STOP"
            else:
                stoppage = str(noOfStop)+" STOPS"
            if len(operatingCarrier) > 0:
                operatortext = '@'.join(operatingCarrier)
            allPrices = maindata[k]["basketsRef"]
            for key in allPrices:
                farePrices = maindata[k]["basketsRef"][key]["prices"]["priceAlternatives"]
                economy = 0
                ecotax = 0
                business = 0
                businesstax = 0
                first = 0
                firsttax = 0
                for m in range(0,len(farePrices)):
                    saverPrice = farePrices[m]["pricesPerCurrency"]
                    taxes = 0
                    miles = 0
                    if "AUD" in saverPrice:
                        taxes = saverPrice["AUD"]["amount"]
                    miles = saverPrice["FFCURRENCY"]["amount"]
                    if cabinType == 'E':
                        economy = miles
                        ecotax = taxes
                    else:
                        business = miles
                        businesstax = taxes
                    value_string.append((str(fltno), str(searchid), stime, stoppage, "test", origin, dest, departtime, arive, tripDuration, str(economy), str(ecotax), str(business),str(businesstax), str(first), str(firsttax), "Economy", "Business", "First", "Virgin Australia", originDetailString, arivedetailtext, planedetailtext, operatortext,ecoFareCode,busFareCode,firstFareCode,eco_fare_code,bus_fare_code))
                    if len(value_string) == 50:
                        if not DEV_LOCAL:
                            cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                            db.commit()
                        else:
                            print value_string
                        value_string=[]
        if len(value_string) > 0:
            if not DEV_LOCAL:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                db.commit()
            else:
                print value_string
        if isflag:   
            if not DEV_LOCAL:
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin Australia", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
                db.commit()
        display.stop()
        driver.quit()
    except:
        raise
        if isflag:   
            if not DEV_LOCAL:
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin Australia", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
                db.commit()
        display.stop()
        driver.quit()
    return searchid


if __name__=='__main__':
    
    flag = True
    nextCabin = ''  
    # pdb.set_trace()        
    virginAustralia(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],flag)
    
    if sys.argv[5] == "maincabin":
        nextCabin = "firstclass"
    else:
        nextCabin = "maincabin"
    flag = False
    virginAustralia(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],nextCabin,flag)
    print '\t@@@@ virgin australia finished'
    
