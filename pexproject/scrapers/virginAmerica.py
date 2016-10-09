#!/usr/bin/env python
import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import MySQLdb
import re
from datetime import date
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from django.db import connection, transaction
import customfunction
from pyvirtualdisplay import Display
import json
#import socket

def virginAmerica(from_airport,to_airport,searchdate,searchid):
  
    db = customfunction.dbconnection()
    cursor = db.cursor()
    from_airport = from_airport.strip()
    to_airport = to_airport.strip()
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    date = dt.strftime('%m-%d-%Y')
    searchdate = dt.strftime('%Y%m%d')
    airport = from_airport+"_"+to_airport
    
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.virginamerica.com/book/ow/a1/"+airport+"/"+str(searchdate)
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)
    driver.get(url)
    pageStatus = driver.execute_script('return document.readyState;')
    pageLoadFlag = 0
    while pageLoadFlag < 1:
        pageStatus = driver.execute_script('return document.readyState;')
        if pageStatus == 'complete':
            pageLoadFlag = pageLoadFlag+1
        else:
            time.sleep(1)
    try:
       
       errorMsg = WebDriverWait(driver,4).until(
                    lambda driver :driver.find_element_by_class_name("message"))
       cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
       db.commit()
       driver.quit()
       return
    except:
        print "data found"
    try:
        milesbtn = WebDriverWait(driver,5).until(
                lambda driver :driver.find_elements_by_name("payment_type"))
        driver.execute_script("return arguments[0].click();", milesbtn[1])
        element = WebDriverWait(driver,5).until(
                lambda driver : driver.find_element_by_link_text("Close"))
        element.click()
    except:
        print "something wrong"
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        driver.quit()
        return

    driver.execute_script("""
        (function(XHR) {
        "use strict";
         
        var count = 0;

        var open = XHR.prototype.open;
        var send = XHR.prototype.send;
        XHR.prototype.open = function(method, url, async, user, pass) {
            this._url = url;
            open.call(this, method, url, async, user, pass);
        };
        
        XHR.prototype.send = function(data) {
            var self = this;
            var oldOnReadyStateChange;
            var url = this._url;
            function onReadyStateChange() {
                
                if(self.readyState == 4) {
                   var json_response = JSON.parse(self.responseText);
                   
                    if(json_response && json_response.hasOwnProperty('response')){ 
                        
                            var element = document.createElement('div');
                            element.id = "interceptedResponse";
                            element.appendChild(document.createTextNode(""));
                            document.body.appendChild(element);
                            element.appendChild(document.createTextNode(JSON.stringify(json_response)));
                   } 
                }

                if(oldOnReadyStateChange) {
                    oldOnReadyStateChange();
                }
            }

            /* Set xhr.noIntercept to true to disable the interceptor for a particular call */
            if(!this.noIntercept) {            
                if(this.addEventListener) {
                    this.addEventListener("readystatechange", onReadyStateChange, false);
                } else {
                    oldOnReadyStateChange = this.onreadystatechange; 
                    this.onreadystatechange = onReadyStateChange;
                }
            }

            send.call(this, data);
        }
    }) (XMLHttpRequest);
    """)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "interceptedResponse")))
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"lxml")
        flightData = soup.find("div",{"id":"interceptedResponse"})
    except:
        print "No flights found"
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        return
    try: 
        if flightData:
            jsonOb = json.loads(flightData.text)
            flightList = jsonOb["response"]["departingFlightsInfo"]["flightList"]
            value_string = []
            for key in flightList:
                for n in range(0,len(flightList[key])):
                    flightInfo = flightList[key][n]
                    flightType = flightList[key][n]['flightType']
                    fareList = flightList[key][n]['fareList']
                    economy = 0
                    business = 0
                    first = 0
                    ecotax = 0
                    busstax = 0
                    firsttax = 0
                    ecoFareClass = ''
                    bussFareClass = ''
                    firstFareClass = ''
                    eco_fare_code = ''
                    bus_fare_code = ''
                    first_fare_code = ''
                    for i in fareList:
                        if 'fareBasisCode' in fareList[i]:
                            Taxes = float(fareList[i]['pointsFare']['totalTax'])
                            Miles = int(fareList[i]['pointsFare']['totalPoints'])
                            classOfServiceList = fareList[i]['classOfServiceList']
                            fareCode = []
                            for j in range(0,len(classOfServiceList)):
                                classOfService = classOfServiceList[j]['classOfService']
                                fareCode.append(classOfService)
                            if 'MCS' in i and (0 == business or business > Miles):
                                business = Miles
                                busstax = Taxes
                                bus_fare_code = ','.join(fareCode)
                                bussFareClass = ' Business@'.join(fareCode)+' Business'
                            elif 'MC' in i and (0 == economy or economy > Miles):
                                economy = Miles
                                ecotax = Taxes
                                eco_fare_code = ','.join(fareCode)
                                ecoFareClass = ' Economy@'.join(fareCode)+' Economy'
                            elif 'FIRST' in i and (0 == first or first > Miles):
                                first = Miles
                                firsttax = Taxes
                                first_fare_code = ','.join(fareCode)
                                firstFareClass = ' First@'.join(fareCode)+' First'
                            #print "seatsRemaining",fareList[i]['seatsRemaining']
                            
                    flightDetails =''
                    "++++++++++++++++flightDetails ++++++++++++++++++++++++++++"
                    source = ''
                    dest = ''
                    departureTime=''
                    arivalTime=''
                    flightNo = ''
                    duration = ''
                    ariveArray = []
                    departArray = []
                    flightArray = []
                    
                    if 'NON_STOP' in flightType:
                        flightDetails = flightList[key][n]['flightSegment']
                        
                        "########### Source ####################"
                        
                        source = flightDetails["departure"]
                        departureDateTime = flightDetails["departureDateTime"]
                        
                        
                        dept = departureDateTime.split("T")
                        #print "deptDate",dept[0]
                        departTime = dept[1].split("-")
                        departTimeFormat = (datetime.datetime.strptime(departTime[0], '%H:%M:%S'))
                        departureTime = departTimeFormat.strftime('%H:%M')
                        airport_ = customfunction.get_airport_detail(source) or source
                        departDisplay = dept[0]+" | "+departureTime+" from "+airport_
                        departArray.append(departDisplay)
                
                        "############ Destination ######################"
                        dest = flightDetails["arrival"]
                        arrivalDateTime = flightDetails["arrivalDateTime"]
                        arrival = arrivalDateTime.split("T")
                        
                        ariveTime = arrival[1].split("-")
                        arivalTime = ariveTime[0]
                        ariveTimeFormat = (datetime.datetime.strptime(ariveTime[0], '%H:%M:%S'))
                        arivalTime = ariveTimeFormat.strftime('%H:%M')
                        airport_ = customfunction.get_airport_detail(dest) or dest
                        ariveDisplay = arrival[0]+" | "+arivalTime+" at "+airport_
                        ariveArray.append(ariveDisplay)
                        
                        elapsedTime = flightDetails["elapsedTime"]
                        duration = str((int(elapsedTime)/60))+"h "+str((int(elapsedTime)%60))+"m"
    
                        "########### Flight Details #############################"
                        aircraftType = flightDetails["aircraftType"]
                        flightNo = "VX "+str(flightDetails["flightNum"])
                        flightDisplay = flightNo+" | "+aircraftType+" ("+duration+")"
                        flightArray.append(flightDisplay)
                        
                        classOfService = flightDetails["classOfService"]
                        
                        segNum = flightDetails["segNum"]
                        
                    else:
                        flightDetails = flightList[key][n]['flightList']
                        oldAriveTime = ''
                        tripDuration = 0
                        for k in range(0,len(flightDetails)):
                            
                            flightType = flightDetails[k]['flightType']
                            "########### Source ####################"
                            departure = flightDetails[k]['flightSegment']["departure"]
                            
                            departureDateTime = flightDetails[k]['flightSegment']["departureDateTime"]
                            dept = departureDateTime.split("T")
                            
                            departTime = dept[1].split("-")
                            
                            departTimeFormat = (datetime.datetime.strptime(departTime[0], '%H:%M:%S'))
                            departTimeFormat = departTimeFormat.strftime('%H:%M')
                            
                            airport_ = customfunction.get_airport_detail(departure) or departure
                            departDisplay = dept[0]+" | "+departTimeFormat+" from "+airport_
                            departArray.append(departDisplay)
                            
                            "############ Destination ######################"
                            ariveAt = flightDetails[k]['flightSegment']["arrival"]
                            
                            arrivalDateTime = flightDetails[k]['flightSegment']["arrivalDateTime"]
                            arrival = arrivalDateTime.split("T")
                            ariveTime = arrival[1].split("-")
                            ariveTimeFormat = (datetime.datetime.strptime(ariveTime[0], '%H:%M:%S'))
                            ariveTimeFormat = ariveTimeFormat.strftime('%H:%M')
                            if k == len(flightDetails)-1:
                                dest = ariveAt
                                arivalTime = ariveTimeFormat
                            timedelta = 0
                            if oldAriveTime:
                                waitingTime = datetime.datetime.strptime(departTimeFormat,'%H:%M') - datetime.datetime.strptime(oldAriveTime,'%H:%M')
                                timedelta = (waitingTime.total_seconds())/60  
                            
                            airport_ = customfunction.get_airport_detail(ariveAt) or ariveAt
                            ariveDisplay = str(arrival[0])+" | "+str(ariveTimeFormat)+" at "+airport_
                            ariveArray.append(ariveDisplay)
    
                            "########### Flight Details #############################"
                            flightNum = flightDetails[k]['flightSegment']["flightNum"]
                            if k == 0:
                                source = departure
                                flightNo = "VX "+str(flightNum)
                                departureTime = departTimeFormat
                            classOfService = flightDetails[k]['flightSegment']["classOfService"]
                            elapsedTime = flightDetails[k]['flightSegment']["elapsedTime"]
                            aircraftType = flightDetails[k]['flightSegment']["aircraftType"]
                            flightairTime = str((int(elapsedTime)/60))+"h "+str((int(elapsedTime)%60))+"m"
                            flightDisplay = "VX "+str(flightNum)+" | "+aircraftType+" ("+flightairTime+")"
                            flightArray.append(flightDisplay)
                            
                            tripDuration = tripDuration+timedelta+elapsedTime
                            
                            segNum = flightDetails[k]['flightSegment']["segNum"]
                            oldAriveTime = ariveTimeFormat
                        duration = str((int(tripDuration)/60))+"h "+str((int(tripDuration)%60))+"m"
                    stoppage = ''
                    stop = len(departArray) - 1
                    if stop == 0:
                        stoppage = "NONSTOP"
                    elif stop == 1:
                        stoppage = "1 STOP"
                    else:
                        stoppage = str(stop)+" STOPS"
                        
                    departdetailtext= '@'.join(departArray)
                    arivedetailtext = '@'.join(ariveArray)
                    planedetailtext = '@'.join(flightArray)
                    operatortext = ''
                    
                    value_string.append((str(flightNo), str(searchid), stime, stoppage, "test", source, dest, departureTime, arivalTime, duration, str(economy), str(ecotax), str(business),str(busstax), str(first), str(firsttax), "Economy", "Business", "First", "Virgin America", departdetailtext, arivedetailtext, planedetailtext, operatortext,ecoFareClass,bussFareClass,firstFareClass,eco_fare_code,bus_fare_code,first_fare_code)) 
                    if len(value_string) == 50:
                        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                        db.commit()
                        print "row inserted"
                        value_string =[]
            if len(value_string) > 0:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                db.commit()
                print len(value_string),"row inserted"
    except:
        print "some thing wrong"
    finally:
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        return 

if __name__=='__main__':
    virginAmerica(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    
