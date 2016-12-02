#!/usr/bin/env python
import sys
import json
import datetime
import requests

DEV_LOCAL = False

if not DEV_LOCAL:
    import customfunction

def virginAmerica(from_airport,to_airport,searchdate,searchid, passenger=1):
    if not DEV_LOCAL:  
        db = customfunction.dbconnection()
        cursor = db.cursor()

    from_airport = from_airport.strip().upper()
    to_airport = to_airport.strip().upper()
    dt = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    searchdate = dt.strftime('%Y-%m-%d')
    
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')

    url = 'https://www.virginamerica.com/api/v2/booking/search'
    header = {"Content-Type": "application/json"}
    body = {
        "oneWay":{
            "origin":from_airport,
            "dest":to_airport,
            "departureDate":searchdate,
            "numOfAdults":passenger,
            "bookingType":"POINTS"
        }
    }           

    try: 
        res = requests.post(url=url, headers=header, data=json.dumps(body))
        res_json = res.json()
        flightList = res_json["response"]["departingFlightsInfo"]["flightList"]

        value_string = []
        for key, val in flightList.items():
            for flightInfo in val:
                flightType = flightInfo['flightType']
                fareList = flightInfo['fareList']
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

                for key_, val_ in fareList.items():
                    if 'fareBasisCode' in val_:
                        Taxes = float(val_['pointsFare']['totalTax'])
                        Miles = int(val_['pointsFare']['totalPoints'])

                        fareCode = [item['classOfService'] for item in val_['classOfServiceList']]

                        if 'MCS' in key_ and (0 == business or business > Miles):
                            business = Miles
                            busstax = Taxes
                            bus_fare_code = ','.join(fareCode)
                            bussFareClass = ' Business@'.join(fareCode)+' Business'
                        elif 'MC' in key_ and (0 == economy or economy > Miles):
                            economy = Miles
                            ecotax = Taxes
                            eco_fare_code = ','.join(fareCode)
                            ecoFareClass = ' Economy@'.join(fareCode)+' Economy'
                        elif 'FIRST' in key_ and (0 == first or first > Miles):
                            first = Miles
                            firsttax = Taxes
                            first_fare_code = ','.join(fareCode)
                            firstFareClass = ' First@'.join(fareCode)+' First'
                        #print "seatsRemaining",val_['seatsRemaining']
                        
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
                    flightDetails = flightInfo['flightSegment']
                    
                    "########### Source ####################"
                    
                    source = flightDetails["departure"]
                    departureDateTime = flightDetails["departureDateTime"]
                    
                    
                    dept = departureDateTime.split("T")
                    #print "deptDate",dept[0]
                    departTime = dept[1].split("-")
                    departTimeFormat = (datetime.datetime.strptime(departTime[0], '%H:%M:%S'))
                    departureTime = departTimeFormat.strftime('%H:%M')
                    airport_ = customfunction.get_airport_detail(source) or source
                    departDisplay = dept[0]+" "+departureTime+" | from "+airport_
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
                    ariveDisplay = arrival[0]+" "+arivalTime+" | at "+airport_
                    ariveArray.append(ariveDisplay)
                    
                    elapsedTime = flightDetails["elapsedTime"]
                    duration = str((int(elapsedTime)/60))+"h "+str((int(elapsedTime)%60))+"m"

                    "########### Flight Details #############################"
                    aircraftType = flightDetails["aircraftType"]
                    flightNo = "VX "+str(flightDetails["flightNum"])
                    flightDisplay = flightNo+" | Airbus "+aircraftType+" ("+duration+")"
                    flightArray.append(flightDisplay)
                    
                    classOfService = flightDetails["classOfService"]
                    
                    segNum = flightDetails["segNum"]
                    
                else:
                    flightDetails = flightInfo['flightList']
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
                        departDisplay = dept[0]+" "+departTimeFormat+" | from "+airport_
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
                        ariveDisplay = str(arrival[0])+" "+str(ariveTimeFormat)+" | at "+airport_
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
                        flightDisplay = "VX "+str(flightNum)+" | Airbus "+aircraftType+" ("+flightairTime+")"
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
                    print value_string
                    value_string =[]
        if len(value_string) > 0:
            if not DEV_LOCAL:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", value_string)
                db.commit()
            print len(value_string),"row inserted"
    except:
        print "Something wrong"
    finally:
        if not DEV_LOCAL:
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchid), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "Virgin America", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
            db.commit()

if __name__=='__main__':
    virginAmerica(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    # virginAmerica('hnl','lax','12/27/2016',321321)
