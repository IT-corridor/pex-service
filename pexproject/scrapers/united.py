#!/usr/bin/env python 
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import time
import re
import json
import codecs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEV_LOCAL = False

if not DEV_LOCAL:
    import customfunction

def get_airport_code(airport):
    airport = airport.split(' (')
    return airport[1][:3]


def united(origin, destination, searchdate, searchkey):
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    date = dt.strftime('%Y-%m-%d')
    date_format = dt.strftime('%a, %b %-d')
    payload_date = dt.strftime('%d, %b %Y')    
   
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    searchkey = searchkey

    if not DEV_LOCAL:
        db = customfunction.dbconnection()
        cursor = db.cursor()

    url = "https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f=" + origin + "&t=" + destination + "&d=" + date + "&tt=1&at=1&sc=7&px=1&taxng=1&idx=1"
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)  

    try:
        driver.get(url)
        time.sleep(2)
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
                    
                    if(json_response.hasOwnProperty("status") && json_response["status"] == "success" && json_response.hasOwnProperty("data"))
                    {
                        var tripdata = json_response["data"]
                        if(tripdata["Trips"])
                        {
                            var element = document.createElement('div');
                            element.id = "interceptedResponse";
                            element.appendChild(document.createTextNode(""));
                            document.body.appendChild(element);
                            element.appendChild(document.createTextNode(self.responseText));
                            count = count+1;
                        }                       
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
        })(XMLHttpRequest);
        UA.Booking.FlightSearch.init();    
        """)

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "interceptedResponse")))
        html_page = driver.page_source
        
        soup = BeautifulSoup(html_page,"lxml")
        maindata = soup.findAll("div",{"id":"interceptedResponse"})
        # print maindata
        # return
        json_string = maindata[0].text
        jsonOb = json.loads(json_string)
        
        ''' Flex calender data '''
        try:
            flex_value = []
            calenderData = jsonOb["data"]["Calendar"]["Months"]
            for i in range(0,len(calenderData)):
                flexcalender = calenderData[i]['Weeks']
                for j in range(0,len(flexcalender)):
                    calweeks = flexcalender[j]
                    for row in calweeks:
                        Month = calweeks["Month"]
                        
                        caldays = calweeks["Days"]
                        for d in range(0,len(caldays)):
                            Month  = caldays[d]["Month"]
                            ecosaver,busssaver,firstsaver = '','',''
                            
                            if Month > 0:
                                cabinOption = caldays[d]["ProductClass"]
                                
                                if cabinOption == '':
                                    "--------------- Standard Award may be available -----------------"
                                elif 'cabin-option-one' in cabinOption and 'cabin-option-two' not in cabinOption:
                                    ecosaver = "saver"
                                    "------------- Economy ------------------------------"
                                elif 'cabin-option-two' in cabinOption and 'cabin-option-one' not in cabinOption:
                                    busssaver = "saver"
                                    "------------- premium cabin-------------------------"
                                else:
                                    "--------------- Economy & premium cabin--------------------------"
                                    ecosaver = "saver"
                                    busssaver = "saver"
                                    
                                travelDate = dt.strftime('%Y-%m-%d')
                                Year  = caldays[d]["Year"]
                                DateValue = caldays[d]["DateValue"]
                                fulldate = str(Year)+"/"+str(Month)+"/"+str(DateValue)
                                flexdate = datetime.datetime.strptime(fulldate, '%Y/%m/%d')
                                flexdate1 = flexdate.strftime('%Y-%m-%d')
                                '''
                                print "PromoProductClass ", caldays[d]["PromoProductClass"]
                                print "Cheapest ", caldays[d]["Cheapest"]
                                #print "ProductClass ", caldays[d]["ProductClass"]
                                print "DayNotInThisMonth ", caldays[d]["DayNotInThisMonth"]
                                
                                print "Display ", caldays[d]["Display"] 
                                '''
                                flex_value.append((str(stime),str(searchkey),origin,destination,str(travelDate),str(flexdate1),ecosaver,busssaver,"united"))

            if not DEV_LOCAL:                                
                cursor.executemany ("INSERT INTO pexproject_flexibledatesearch (scrapertime,searchkey,source,destination,journey,flexdate,economyflex,businessflex,datasource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);", flex_value)
                #print cursor._last_executed
                db.commit()
            else:
                print flex_value
        except:
            'no calender data'
            
            
        ''' End flex calender '''
            
            
        flightDetails = jsonOb["data"]["Trips"][0]["Flights"]
    except:
        print "No data Found"
        driver.quit()
        if not DEV_LOCAL:
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "united", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
            db.commit()
        return searchkey
    
    comma = ''
    values_string = []
    totalrecords = len(flightDetails)
    recordcount = 1
    for i in range(0,len(flightDetails)):        
        source = flightDetails[i]["Origin"]
        depttime = flightDetails[i]["DepartTimeFormat"]
        test = (datetime.datetime.strptime(depttime, '%I:%M %p'))
        test1 = test.strftime('%H:%M')
                
        lastdestination =  flightDetails[i]["LastDestination"]['Code']
        lastdesttime = flightDetails[i]["LastDestination"]['TimeFormatted']
        if '.' in lastdesttime:
            lastdesttime = lastdesttime.replace('.','')
        arivetime1 = (datetime.datetime.strptime(lastdesttime, '%I:%M %p'))
        arivetime = arivetime1.strftime('%H:%M')

        stoppage = flightDetails[i]["StopsandConnections"]
        if stoppage == 0:
            stoppage = "NONSTOP"
        elif stoppage == 1:
            stoppage = "1 STOP"
        else:
            stoppage = str(stoppage)+" STOPS"
        Flightno =flightDetails[i]["FlightNumber"]
        flightcode = flightDetails[i]["OperatingCarrier"]
        Flightno = "Flight "+flightcode+" "+str(Flightno)
        TravelMinutes = flightDetails[i]["TravelMinutes"]
        MaxLayoverTime = flightDetails[i]["MaxLayoverTime"]
        TravelMinutes = TravelMinutes
        firstFlighthour = int(TravelMinutes)/60
        firstFlightminute = int(TravelMinutes) % 60
        firstFlightDuration = str(firstFlighthour)+"h "+str(firstFlightminute)+"m"
        MaxLayoverTime = MaxLayoverTime
        firstFlightTotalTime = TravelMinutes
        TravelMinutesTotal = flightDetails[i]["TravelMinutesTotal"]
        travelhour = int(TravelMinutesTotal)/60
        travelminute = int(TravelMinutesTotal) % 60
        totaltime = str(travelhour)+"h "+str(travelminute)+"m"
        connection =  jsonOb["data"]["Trips"][0]["Flights"][i]["Connections"]
        lastFlightTravelDuration = ''
        if connection:
            lastFlightTravelTime = connection[0]["TravelMinutes"]
            lastFlightTravelhour = lastFlightTravelTime/60
            lastFlightTravelminute = lastFlightTravelTime % 60
            lastFlightTravelDuration = str(lastFlightTravelhour)+"h "+str(lastFlightTravelminute)+"m"
        
        DepartDateFormat = flightDetails[i]["DepartDateFormat"]
        #print "**************Destination*****************/n"
        #print "DestinationDescription", flightDetails[i]["DestinationDescription"]
        DestinationDateTime = flightDetails[i]["DestinationDateTime"]
        lastdestdatetime =  flightDetails[i]["LastDestinationDateTime"]
        #print "******** Extra Info *******************\n"
        
        FlightSegmentJson = flightDetails[i]["FlightSegmentJson"]
        segmentJsonObj = json.loads(FlightSegmentJson)
        #print "segmentJsonObj",segmentJsonObj
        departdetails = []
        arivaildetails = []
        flightdeatails = []
        operator = []
        for k in range(0,len(segmentJsonObj)):
            #print "Origin", segmentJsonObj[k]["Origin"]
            FlightNumber = segmentJsonObj[k]["FlightNumber"]
            FlightDate = segmentJsonObj[k]["FlightDate"]
            OriginDescription = segmentJsonObj[k]["OriginDescription"]
            OperatingCarrierCode = segmentJsonObj[k]["OperatingCarrierCode"]

            departinfo_time = datetime.datetime.strptime(FlightDate, '%m/%d/%Y %H:%M')
            FlightDate = departinfo_time.strftime('%Y/%m/%d %H:%M')

            airport_ = customfunction.get_airport_detail(get_airport_code(OriginDescription)) or OriginDescription
            deptdetail = FlightDate+" | from "+airport_
            departdetails.append(deptdetail)
            stopstation = segmentJsonObj[k]["Stops"]
            if stopstation != None:
                stopnJsonobj = stopstation
                
                if len(stopnJsonobj) > 0:

                    for l in range(0,len(stopnJsonobj)):
                        stopOrigin = stopnJsonobj[l]["OriginDescription"]
                        stopFlightDate = stopnJsonobj[l]["FlightDate"]
                        stopFlightDate = datetime.datetime.strptime(stopFlightDate, '%m/%d/%Y %H:%M')
                        stopFlightDate = stopFlightDate.strftime('%Y/%m/%d %H:%M')

                        airport_ = customfunction.get_airport_detail(get_airport_code(stopOrigin)) or stopOrigin
                        stopOriginDetails = stopFlightDate+" | from "+airport_
                        departdetails.append(stopOriginDetails)
                        # # what is it, Pradeep?
                        # stopOriginDetails = stopFlightDate+" | at "+airport_
                        # arivaildetails.append(stopOriginDetails)
                        stopDestination = stopnJsonobj[l]["DestinationDescription"]
                        if stopnJsonobj[l]["Destination"].strip() == lastdestination.strip():
                            lastdestdatetime = datetime.datetime.strptime(lastdestdatetime, '%m/%d/%Y %H:%M')
                            lastdestdatetime = lastdestdatetime.strftime('%Y/%m/%d %H:%M')     
                            airport_ = customfunction.get_airport_detail(get_airport_code(stopDestination)) or stopDestination                       
                            destdetail = lastdestdatetime+" | at "+airport_
                            arivaildetails.append(destdetail)
                        else:
                            DestinationDateTime = datetime.datetime.strptime(DestinationDateTime, '%m/%d/%Y %H:%M')
                            DestinationDateTime = DestinationDateTime.strftime('%Y/%m/%d %H:%M')                            
                            airport_ = customfunction.get_airport_detail(get_airport_code(stopDestination)) or stopDestination
                            fullAriveinfo = DestinationDateTime+" | at "+airport_
                            arivaildetails.append(fullAriveinfo)
                        stopOperator = stopnJsonobj[l]["OperatingCarrierDescription"]
                        if stopOperator != None:
                            operator.append(stopOperator)
                        else:
                            stopOperator = segmentJsonObj[k]["MarketingCarrierDescription"]
                            if stopOperator != None:
                                operator.append(stopOperator)
                        stopFlightNumber = stopnJsonobj[l]["FlightNumber"]
                        stopOperatingCarrierCode = stopnJsonobj[l]["OperatingCarrierCode"]
                        stopflightDetail = stopOperatingCarrierCode+" "+stopFlightNumber
                        stopEquipmentDescription = stopnJsonobj[l]["EquipmentDescription"]
                        # --- NORM ---
                        if stopEquipmentDescription.startswith('Canadair Regional Jet'):
                            stopEquipmentDescription = stopEquipmentDescription.replace('Canadair Regional Jet', 'Bombardier CRJ')
                        elif stopEquipmentDescription[:3] in ['CS1', '32B', '359']:
                            stopEquipmentDescription = customfunction.AIRCRAFTS[stopEquipmentDescription[:3]] + stopEquipmentDescription[3:]

                        stopflightDetail = stopflightDetail+" | "+stopEquipmentDescription
                        flightdeatails.append(stopflightDetail)
            else:
                DestinationDescription = segmentJsonObj[k]["DestinationDescription"]
                if segmentJsonObj[k]["Destination"].strip() == lastdestination.strip():
                    lastdestdatetime = datetime.datetime.strptime(lastdestdatetime, '%m/%d/%Y %H:%M')
                    lastdestdatetime = lastdestdatetime.strftime('%Y/%m/%d %H:%M')         
                    airport_ = customfunction.get_airport_detail(get_airport_code(DestinationDescription)) or DestinationDescription           
                    destdetail = lastdestdatetime+" | at "+airport_
                else:
                    try:
                        DestinationDateTime = datetime.datetime.strptime(DestinationDateTime, '%m/%d/%Y %H:%M')
                        DestinationDateTime = DestinationDateTime.strftime('%Y/%m/%d %H:%M')
                    except Exception, e:
                        pass
                    airport_ = customfunction.get_airport_detail(get_airport_code(DestinationDescription)) or DestinationDescription
                    destdetail = DestinationDateTime+" | at "+airport_
                arivaildetails.append(destdetail)
                
            operatedby = segmentJsonObj[k]["OperatingCarrierDescription"]
            if operatedby != None:
                operator.append(operatedby)
            else:
                operatedby = segmentJsonObj[k]["MarketingCarrierDescription"]
                if operatedby != None:
                    operator.append(operatedby)
            
            EquipmentDescription = segmentJsonObj[k]["EquipmentDescription"]

            # --- NORM ---
            if EquipmentDescription.startswith('Canadair Regional Jet'):
                EquipmentDescription = EquipmentDescription.replace('Canadair Regional Jet', 'Bombardier CRJ')
            elif EquipmentDescription in ['CS1', '32B', '359']:
                EquipmentDescription = customfunction.AIRCRAFTS[EquipmentDescription]

            if source.strip() == segmentJsonObj[k]["Origin"].strip():                
                filghtFormat = OperatingCarrierCode+" "+FlightNumber+" | "+EquipmentDescription+" ("+firstFlightDuration+")"
            else:
                filghtFormat = OperatingCarrierCode+" "+FlightNumber+" | "+EquipmentDescription+" ("+lastFlightTravelDuration+")"
            flightdeatails.append(filghtFormat)
        
        economy = 0
        ecoTax = 0
        business = 0
        businessTax = 0
        first = 0
        firstTax = 0
        ecoFareClassCode = []
        busFareClassCode = []
        firtFareClassCode = []
        ecoFareCode = ''
        businessFareCode =''
        firstFareCode = ''
        eco_code = []
        bus_code = []
        first_code = []
        eco_fare_code = ''
        bus_fare_code = ''
        first_fare_code = ''
        for j in range(0, len(flightDetails[i]["Products"])):
            productstype = flightDetails[i]["Products"][j]["DataSourceLabelStyle"]
            pricesMiles = flightDetails[i]["Products"][j]["Prices"]
            tax = 0
            TaxAndFees = flightDetails[i]["Products"][j]["TaxAndFees"]
            if TaxAndFees:
                tax = TaxAndFees["Amount"]
            miles = 0
            if pricesMiles:
                miles = flightDetails[i]["Products"][j]["Prices"][0]["Amount"]
            Description = flightDetails[i]["Products"][j]["Description"]
            BookingCode = flightDetails[i]["Products"][j]["BookingCode"]
            ProductTypeDescription = flightDetails[i]["Products"][j]["ProductTypeDescription"]
            if ProductTypeDescription:
                BookingCode = BookingCode+" "+ProductTypeDescription
            if 'Economy' in productstype and economy == 0  :
                economy = miles
                ecoTax = tax
                ecoFareCode = BookingCode
                ecoFareClassCode.append(BookingCode)
                if flightDetails[i]["Products"][j]["BookingCode"]:
                    eco_code.append(flightDetails[i]["Products"][j]["BookingCode"])
                
            elif 'Business' in productstype and business == 0 and miles:
                business = miles
                businessTax = tax
                businessFareCode = BookingCode
                busFareClassCode.append(BookingCode)
                if flightDetails[i]["Products"][j]["BookingCode"]:
                    bus_code.append(flightDetails[i]["Products"][j]["BookingCode"])
                
            elif 'First' in productstype and first == 0 and miles:
                first = miles
                firstTax = tax
                firstFareCode = BookingCode
                firtFareClassCode.append(BookingCode)
                if flightDetails[i]["Products"][j]["BookingCode"]:
                    first_code.append(flightDetails[i]["Products"][j]["BookingCode"])
        if connection:
            connectingFarecode = connection[0]["Products"]
            for m in range(0,len(connectingFarecode)):
                connectingDescription = connectingFarecode[m]["Description"]
                connectingProductstype = connectingFarecode[m]["DataSourceLabelStyle"]
                connectingBookingCode = connectingFarecode[m]["BookingCode"]
                productdesc = connectingFarecode[m]["ProductTypeDescription"]
                if productdesc:
                    connectingBookingCode = connectingBookingCode+" "+productdesc
                if connectingProductstype and 'Economy' in connectingProductstype:
                    ecoFareClassCode.append(connectingBookingCode)
                    if connectingFarecode[m]["BookingCode"]:
                        eco_code.append(connectingFarecode[m]["BookingCode"])
                elif connectingProductstype and 'Business' in connectingProductstype:
                    busFareClassCode.append(connectingBookingCode)
                    if connectingFarecode[m]["BookingCode"]:
                        bus_code.append(connectingFarecode[m]["BookingCode"])
                elif connectingProductstype and 'First' in connectingProductstype:
                    firtFareClassCode.append(connectingBookingCode)
                    if connectingFarecode[m]["BookingCode"]:
                        first_code.append(connectingFarecode[m]["BookingCode"])
        if len(ecoFareClassCode) > 0:
            ecoFareCode = '@'.join(ecoFareClassCode)
        if len(busFareClassCode) > 0:
            businessFareCode = '@'.join(busFareClassCode)
        if len(firtFareClassCode) > 0:
           firstFareCode = '@'.join(firtFareClassCode)
        if len(eco_code) > 0:
            eco_fare_code = ','.join(eco_code)
        if len(bus_code) > 0:
            bus_fare_code = ','.join(bus_code)
        if len(first_code) > 0:
            first_fare_code = ','.join(first_code)
        departdetailsText = '@'.join(departdetails) 
        arivedetailsText = '@'.join(arivaildetails) 
        planedetails = '@'.join(flightdeatails)
        operatedbytext = ''
        if len(operator) > 0: 
            operatedbytext = '@'.join(operator)
    
        recordcount = recordcount+1        
        values_string.append((Flightno, str(searchkey), stime, stoppage, "test", source, lastdestination, test1, arivetime, totaltime, str(economy), str(ecoTax), str(business), str(businessTax), str(first), str(firstTax),"Economy", "Business", "First", "united", departdetailsText, arivedetailsText, planedetails, operatedbytext,ecoFareCode,businessFareCode,firstFareCode,eco_fare_code,bus_fare_code,first_fare_code))
        if recordcount > 50 or i == (totalrecords)-1 and len(values_string)>0:
            if not DEV_LOCAL:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", values_string)
                db.commit()
            else:
                print values_string
            values_string =[]
            recordcount = 1
        
    if not DEV_LOCAL:
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "united", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()
    driver.quit()              
    return searchkey              
        

if __name__=='__main__':
    # print "in united"
    united(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    # united('las','iad','12/21/2016',1111)
