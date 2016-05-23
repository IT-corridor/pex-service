#!/usr/bin/env p

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
from datetime import date
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
import customfunction
import socket
import json

def delta(orgn, dest, searchdate, searchkey):
    db = customfunction.dbconnection()
    cursor = db.cursor()
    db.set_character_set('utf8')
    url = "http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
  
    display = Display(visible=0, size=(800, 600))
    display.start()
    '''
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080) '''
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "oneWayBtn")))
        oneway = driver.find_element_by_id('oneWayBtn')
        #oneway.click()
        driver.execute_script("arguments[0].click();", oneway)
        origin = driver.find_element_by_id("originCity")
        origin.clear()
        origin.send_keys(orgn.strip())
        destination = driver.find_element_by_id("destinationCity")
        destination.send_keys(dest.strip())
        ddate = driver.find_element_by_id("departureDate")  
        driver.execute_script("document.getElementById('departureDate').setAttribute('value', '"+str(searchdate)+"')")
        milebtn = driver.find_element_by_id("milesBtn")
        milebtn.click()
        driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
        
    except:
        print "before data page"
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag","flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        display.stop()
        driver.quit()
        return searchkey
    time.sleep(1)
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID, "submitAdvanced")))
        print "no data"
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        display.stop()
        driver.quit()
        return searchkey
    except:
        print "Data found"
    try:
        WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "showAll")))
        print "More than one page"
        driver.execute_script("""
            DWRHandler.currentPage = -1;
            var _shopInputDo=shopInputDo;
            shoppingUtil.scrollWindow("top");
            FilterFunctions.showFilterMsg();
            FlightUtil.emptyResults();
            ResummarizeFlightResultsDWR.pageResults(DWRHandler.currentPage, _shopInputDo.currentSessionCheckSum, delta.airShopping.cacheKey, {
            async: true,
            callback: function(searchResults) {
                if (searchResults != null) {
                    var jsonData = {};
                    jsonData['jsonobj'] = JSON.stringify(searchResults);
                    var cabininfo = document.getElementsByClassName('tblHeadUp')[0].innerHTML;
                    jsonData['cabinTypes'] = cabininfo;
                    localStorage.setItem('deltaData', JSON.stringify(jsonData));
                    var element = document.createElement('div');
                    element.id = "submitAdvanced";
                    element.appendChild(document.createTextNode("text"));
                    document.body.appendChild(element);
                    throw new Error("Results found");
                    if (searchResults.errorFwdURL == null) {
                        jsonResultPopulation(searchResults);
                        paginationPopulation(searchResults);
                        if (shoppingUtil.isIE8()) {
                            if (DWRHandler.currentPage == -1) {
                                ieTimeout = setTimeout("RenderTemplate.renderResult();FilterFunctions.hideFilterMsg();RenderTemplate.adjustHeight();", 200);
                            } else {
                                ieTimeout = setTimeout("RenderTemplate.renderResult();FilterFunctions.hideFilterMsg();RenderTemplate.adjustHeight();", 100);
                            }
                        } else {
                            RenderTemplate.renderResult();
                            FilterFunctions.hideFilterMsg();
                            RenderTemplate.adjustHeight();
                        }
                        if (DWRHandler.currentPage == -1) {
                            $("#showAll").hide();
                            $("#showAll-footer").hide();
                        }
                        contienuedOnload(false);
                        if (searchResults.debugInfo != null && ((typeof(printRequestResponse) !== "undefined") && printRequestResponse == true)) {
                            $("#requestXml").text(searchResults.debugInfo.itaRequest);
                            $("#responceXml").text(searchResults.debugInfo.itaResponse);
                            $("#reqRes").show();
                        }
                    } else {
                        window.location.replace(searchResults.errorFwdURL);
                    }
                } else {
                    FilterFunctions.errorHandling();
                }
                $(".tableHeaderHolderFareBottom.return2Top").show();
            },
            exceptionHandler: FilterFunctions.errorHandling
        });
        
        
        
        """)
    except:
        print "single page"
        driver.execute_script("""
        if(typeof delta.airShopping.defaultSortBy === 'undefined')
        {
            throw new Error("Results found");
        }
        var sortBy = [delta.airShopping.defaultSortBy, false];
        SearchFlightResultsDWR.searchResults(currentSessionCheckSum, sortBy[0], delta.airShopping.numberOfColumnsToRequest, delta.airShopping.cacheKey, {
            async: true,
            timeout: 65000,
            callback: function(searchResults) {
                    var jsonData = {};
                    
                    jsonData['jsonobj'] = JSON.stringify(searchResults);
                    var cabininfo = document.getElementsByClassName('tblHeadUp')[0].innerHTML;
                    jsonData['cabinTypes'] = cabininfo;
                    localStorage.setItem('deltaData', JSON.stringify(jsonData));
                    var element = document.createElement('div');
                    element.id = "submitAdvanced";
                    element.appendChild(document.createTextNode("text"));
                    document.body.appendChild(element);
                    throw new Error("Results found");
                    
                if (searchResults.errorFwdURL == null || searchResults.errorFwdURL == "") {
                    flightResultsObj.isDOMReady(searchResults, action, false);
                    FilterFunctions.hideFilterMsg();
                } else {
                
                    flightResultsObj.isDOMReady(searchResults, false, true);
                }
                if (!action) {
                    Wait.hide();
                    $(".tableHeaderHolderFareBottom").show();
                    $("#nextGenAirShopping .tableHeaderHolder").show();
                }
            },
            errorHandler: function(msg, exc) {
                shoppingUtil.errorHandler(msg, exc);
            },
            exceptionHandler: function(msg, exc) {
                (action) ? FilterFunctions.hideFilterMsg(): "";
                shoppingUtil.exceptionHandler(msg, exc);
            }
        });
        
        """)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "submitAdvanced")))
    except:
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
        driver.quit()
        display.stop()
        return searchkey
    result = driver.execute_script(""" return localStorage.getItem('deltaData'); """)
    deltaObj = json.loads(result)
    searchResult = json.loads(deltaObj['jsonobj'])
    
    cabinhead = "<tr>"+deltaObj['cabinTypes']+"</tr>"
    
    soup = BeautifulSoup(cabinhead,"xml")
    tds = soup.findAll("td")
    pricecol =  soup.findAll("a",{"class":"tblHeadBigtext lnkCabinName"})
    flightData = searchResult["itineraries"]
    values_string = []
    for i in range(0,len(flightData)):
        
        totalFareDetails = flightData[i]['totalFare']
        slicesDetails = flightData[i]['slices']
        departDetail = []
        ariveDetail = []
        flightDetail = []
        operatorDetail = []
        SourceCOde =''
        tripDuration=''
        destinationCode=''
        arivalTime=''
        departTime=''
        flightNo = ''
        for k in range(0,len(slicesDetails)):
            
            tripDuration = slicesDetails[k]['duration']
            SourceCOde = slicesDetails[k]['sliceOrigin']['airportCode']
            destinationCode = slicesDetails[k]['sliceDestination']['airportCode']
            arivalTime = slicesDetails[k]['sliceArrivalTime']
            departTime = slicesDetails[k]['sliceDepartureTime']
            layover = slicesDetails[k]['flights']
            "**************************************** FLIGHT DETAILS ****************************************"
            FlightFlag = 0
            for m in range(0,len(layover)):
                legData = layover[m]['legs']
                for n in range(0,len(legData)):
                    legdetail = legData[n]
                    if legdetail:
                        fromAirport =''
                        destAirport=''
                        "=========================LEG INFO=================================="
                        if 'origin' in legdetail:
                            orgnCode = legdetail['origin']['airportCode']
                            cityname = legdetail['origin']['nearByCities'][0]['name']
                            cityCode = legdetail['origin']['nearByCities'][0]['country']['region']['code']
                            fromAirport = cityname+" "+cityCode+" ("+orgnCode+")"
                             
                        if 'destination' in legdetail:
                            destCode = legdetail['destination']['airportCode']
                            destcityname = legdetail['destination']['nearByCities'][0]['name']
                            destcityCode = legdetail['destination']['nearByCities'][0]['country']['region']['code']
                            destAirport = destcityname+" "+destcityCode+" ("+orgnCode+")"
                        
                        duration = legdetail['duration']
                        #print "airTime",legdetail['airTime']
                        schedDepartureTime = legdetail['schedDepartureTime']
                        schedDepartureDate = legdetail['schedDepartureDate']
                        schedArrivalTime = legdetail['schedArrivalTime']
                        schedArrivalDate = legdetail['schedArrivalDate']
                        '@@@@@@@ departDetails format @@@@@@@'
                        fromDetail = schedDepartureDate+" "+schedDepartureTime+" | from  "+fromAirport
                        departDetail.append(fromDetail)
                        toDetails = schedArrivalDate+" "+schedArrivalTime+" | at "+destAirport
                        ariveDetail.append(toDetails)
                        aircraft = legdetail['aircraft']['shortName']
                        airlineCode = legdetail['marketAirline']['airline']['airlineCode']
                        flightNumber = legdetail['flightNumber']
                        if FlightFlag == 0:
                            flightNo = airlineCode+" "+str(flightNumber)
                        flightFormat = airlineCode+" "+str(flightNumber)+" | "+aircraft+" ("+duration+")"
                        flightDetail.append(flightFormat)
                        operatedby = legdetail['operatingAirline']['airline']['airlineName']
                        operatorDetail.append(operatedby)
                        FlightFlag = FlightFlag+1
        "====================Fare info ================================="
      
        fareFlag = 0
        cabintype1 =''
        cabintype2 = ''
        cabintype3 = ''
        ecofare = 0
        echoTax = 0
        bussfare = 0
        busstax = 0
        firstFare =0
        firsttax =0
        ecofareClass = ''
        bussFareClass = ''
        firstFareClass = ''
        for j in range(0,len(totalFareDetails)):
            cabintype = ''
            miles = 0
            tax = 0
            
            fareCode=[]
            if totalFareDetails[j]['cabinName'] != None:
                fareCodeHolder = totalFareDetails[j]['miscFlightInfos']
                for c in range(0,len(fareCodeHolder)):
                    fareCabin = fareCodeHolder[c]['cabinName']
                    bookingCode = fareCodeHolder[c]['displayBookingCode']
                    fareCode.append(bookingCode)
                    bookingCode = bookingCode+" "+fareCabin
                cabinName = totalFareDetails[j]['cabinName']
                miles = totalFareDetails[j]['totalAwardMiles']
                if ',' in miles:
                    miles = miles.replace(',','')
                taxInt = totalFareDetails[j]['totalPriceLeft']
                taxFloat = totalFareDetails[j]['totalPriceRight']
                tax = float(taxInt)+float(taxFloat)
            if len(pricecol) > 1:
                
                if j == 0:
                    cabintype = "Economy"
                if j == 1 and 'First' not in pricecol[1].text:
                    cabintype = "Business"
                if j == 2 and len(pricecol) > 2 and 'First' not in pricecol[2].text:
                    cabintype = "Business"
            else:
                if len(pricecol) > 0 and len(pricecol) < 2:
                    if 'Main Cabin' in pricecol[0].text:
                        cabintype = "Economy"
                    elif 'First' not in pricecol[0].text:
                        cabintype = 'Business'
            if 'Economy' in cabintype:
                ecofare = miles
                echoTax = tax
                cabintype1 = "Economy"
                if len(fareCode) > 0:
                    ecofareClass = ' Economy@'.join(fareCode)+' Economy'
                    ecofareClass = ecofareClass
            elif 'Business' in cabintype:
                cabintype2 = "Business"
                bussfare = miles
                busstax = tax
                if len(fareCode) > 0:
                    bussFareClass = ' Business@'.join(fareCode)+' Business'
            else:
                cabintype3 = "First"
                firstFare = miles
                firsttax = tax
                if len(fareCode) > 0:
                    firstFareClass = ' First@'.join(fareCode)+' First'
        departdetailtext = '@'.join(departDetail)
        ariveDetailtext = '@'.join(ariveDetail)
        flightDetailtext = '@'.join(flightDetail)
        operatorDetailtext = '@'.join(operatorDetail)
        
        stoppage = ''
        stop = int(len(departDetail) - 1)
        if stop == 0:
            stoppage = "NONSTOP"
        elif stop == 1:
            stoppage = "1 STOP"
        else:
            stoppage = str(stop)+" STOPS"
        arivalTime1 = (datetime.datetime.strptime(arivalTime, '%I:%M%p'))
        arivalTime = arivalTime1.strftime('%H:%M')
        departTime1 = (datetime.datetime.strptime(departTime, '%I:%M%p'))
        departTime = departTime1.strftime('%H:%M')
        values_string.append((flightNo, str(searchkey), stime, stoppage, "test", SourceCOde, destinationCode, departTime, arivalTime, tripDuration, str(ecofare), str(echoTax), str(bussfare), str(busstax), str(firstFare), str(firsttax), cabintype1, cabintype2, cabintype3, "delta", departdetailtext, ariveDetailtext, flightDetailtext, operatorDetailtext,ecofareClass,bussFareClass,firstFareClass))
        if len(values_string) > 50:
            cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
            db.commit()
            values_string =[]
            
    if len(values_string) > 0:
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
        db.commit()
               
    driver.quit()
    display.stop()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    return searchkey
            
            
if __name__=='__main__':
    delta(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[5])
        
