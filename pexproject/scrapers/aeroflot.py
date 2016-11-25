import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import re
import json
import codecs
import requests
import HTMLParser

DEBUG = True
# DEBUG = False
DEV_LOCAL = False
# DEV_LOCAL = True

if not DEV_LOCAL:
    import customfunction

TAXES = {
    'AE': 'maintax',        # Economy
    'AC': 'firsttax',       # Comfort
    'AB': 'businesstax',    # Business
}

URL = ('https://reservation.aeroflot.ru/SSW2010/7B47/webqtrip.html?'
       'searchType=NORMAL&journeySpan=OW&alternativeLandingPage=1&lang=en&'
       'currency=USD&referrerCode=AFLBOOK&numAdults=1&numChildren=0&'
       'utm_source=&utm_campaign=&utm_medium=&'
       'utm_content=&utm_term=&isAward=1&origin=%s&destination=%s'
       '&departureDate=%s')

FLIGHT_URL = 'https://reservation.aeroflot.ru/SSW2010/7B47/webqtrip.html'

CONTEXTOBJECT = (
    '{"transferObjects":[{"componentType":"cart","actionCode":"checkPrice"'
    ',"queryData":{"componentId":"cart_1","componentType":"cart","actionCo'
    'de":"checkPrice","queryData":null,"requestPartials":["initialized"],"'
    'selectedBasketRefs":[%s]}}]}'
)

DATA = {
    '_eventId_ajax': '',
    'execution': None,
    'ajaxSource': 'true',
    'contextObject': None
}

def get_cookie(driver, name, path):
    cookies = driver.get_cookies()
    for cookie in cookies:
        if (cookie['name'] == name and cookie['path'].strip('/') == path.strip('/')):
            return cookie['value']
    return None

def find_flight_id(flight, flight_type_code):
    selector = 'td[data-fare-family-key="'+flight_type_code+'"]'
    node = flight.select(selector)[0].find("input")        
    return node['id'].replace('flight_both_', '') if node else None

def aeroflot(ocity_code, dcity_code, searchdate, searchkey):
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)  
    url = URL % (ocity_code, dcity_code, searchdate)
    
    driver.get(url)
    execution = driver.current_url[-4:]
    DATA['execution'] = execution

    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    log_path = 'aeroflot_log' if DEV_LOCAL else '/home/upwork/aeroflot_log'
    log_file = open(log_path, 'a') if DEBUG else sys.stdout
    log_file.write('\n\n'+'='*70+'\n\n')    
    log_file.write(url+'\n\n')
    db = customfunction.dbconnection() if not DEV_LOCAL else None

    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    flightinfo = []

    try:
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"lxml")

        radio_id = soup.find('input', id=re.compile('^flight_both_'))['id']
        radio = driver.find_element_by_id(radio_id)

        time.sleep(1)
        radio.click()
        cookies = {
            'JSESSIONID': get_cookie(driver, 'JSESSIONID', '/SSW2010'),
            'WLPCOOKIE': get_cookie(driver, 'WLPCOOKIE', '/SSW2010'),
        }

        maindata = soup.select("#dtcontainer-both tbody tr")

        operatorArray = []
        taxArray=[]

        # log_file.write(str(len(maindata)))
        for flight in maindata:
            ths, tds = flight.select('th'), flight.select('td')
            operatedby = ths[2].select('.carrier-name')[0].string
            operatorArray.append(operatedby)

            maintax = 0
            firsttax = 0
            businesstax = 0
            for flight_type_code, tax_field_name in TAXES.items():
                flight_id = find_flight_id(flight, flight_type_code)
                # log_file.write(str(flight_id)) 
                # log_file.write('\n')
                if flight_id:
                    DATA['contextObject'] = [CONTEXTOBJECT % flight_id]
                    resp = requests.post(
                        FLIGHT_URL,
                        cookies=cookies,
                        data=DATA,
                    )
                    resp_html = resp.json()['content'][0]['partials']['initialized']
                    h= HTMLParser.HTMLParser()
                    resp_html = h.unescape(resp_html)
                    taxsoup = BeautifulSoup(resp_html, 'lxml')
                    # log_file.write(resp_html.encode('utf8')) 
                    # log_file.write('\n\n')

                    tax_amount = taxsoup.find('div', class_='total-top').find_all(
                        'span', class_='prices-amount')
                    
                    if len(tax_amount) > 0:
                        tax_amount = tax_amount[1].text
                    else:
                        tax_amount = 0

                    if 'main' in tax_field_name:
                        maintax = float(tax_amount)
                    elif 'business' in tax_field_name:
                        businesstax = float(tax_amount)
                    elif 'first' in tax_field_name:
                        firsttax = float(tax_amount)

            taxArray.append({"maintax":maintax,"businesstax":businesstax,"firsttax":firsttax})
        # log_file.write(str(taxArray))
        # log_file.write('\n')
        json_text = re.search(r'^\s*var templateData = \s*({.*?})\s*;\s*$', html_page, flags=re.DOTALL | re.MULTILINE).group(1)
        jsonData = json.loads(json_text)
        tempdata = jsonData["rootElement"]["children"][1]["children"][0]["children"][5]["model"]["allItineraryParts"]
        count = 0
        for k in range(0,len(tempdata)):            
            segments = tempdata[k]["segments"]
            rowRecord = tempdata[k]["itineraryPartData"]
            fltno = ''

            origin = rowRecord["departureCode"]
            dest = rowRecord["arrivalCode"]
            departureDate = rowRecord["departureDate"]
            deptDateTime = departureDate.split(" ")

            originDetails = []
            destDetails = []
            flightsDetails =[]
            operatorCarrier = []
            for counter in range (0,len(segments)):
                bookingCode = segments[counter]['bookingClass']
                bookingClassCabin = segments[counter]['allClassOfService']
                segOrigin = segments[counter]["departureCode"]
                segDepartDate = segments[counter]["departureDate"]
                airport_ = customfunction.get_airport_detail(segOrigin) or segOrigin
                segDetailFormat = segDepartDate[:-3]+" | from "+airport_
                originDetails.append(segDetailFormat)
                
                segDest = segments[counter]["arrivalCode"]
                segArive = segments[counter]["arrivalDate"]
                airport_ = customfunction.get_airport_detail(segDest) or segDest
                destdetailFormat = segArive[:-3]+" | at "+airport_
                destDetails.append(destdetailFormat)
                if len(operatorArray) > count:
                    operatorCarrier.append(operatorArray[count])
                    count = count+1    
                
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
                fltFormat = flightNo+" | "+customfunction.AIRCRAFTS[aircraftType[f]]+" ("+fltTimeFormat+")"
                flightsDetails.append(fltFormat)

            originDetailString = '@'.join(originDetails)
            arivedetailtext = '@'.join(destDetails)
            planedetailtext = '@'.join(flightsDetails)
            operatortext = ''
            if len(operatorCarrier) > 0:
                operatortext = '@'.join(operatorCarrier)
            noOfStop = len(departureCodes) - 1
            stoppage = ''
            if noOfStop == 0:
                stoppage = "NONSTOP"
            elif noOfStop == 1:
                stoppage = "1 STOP"
            else:
                stoppage = str(noOfStop)+" STOPS"
            
            allPrices = tempdata[k]["basketsRef"]
            economy = 0
            ecotax = 0
            business = 0
            businesstax = 0
            first = 0
            firsttax = 0
            for key in allPrices:
                farePrices = allPrices[key]["prices"]["moneyElements"] #["priceAlternatives"]
                miles = farePrices[0]["moneyTO"]["amount"]
                if 'AE' in key:     # X economy
                    economy = miles 
                    ecotax = taxArray[k]['maintax']
                elif 'AB' in key:   # F economy
                    business = miles
                    businesstax = taxArray[k]['businesstax']
                elif 'AC' in key:   # O Business
                    first = miles
                    firsttax = taxArray[k]['firsttax']
            if economy or business:
                flightinfo.append(('Flight '+str(fltno), searchkey, stime, stoppage, "test", origin, dest, departtime, arive, tripDuration, str(economy), str(ecotax), str(business),str(businesstax), str(0), str(0), "Economy", "Business", "First", "aeroflot", originDetailString, arivedetailtext, planedetailtext, operatortext, 'X Economy', 'O Business', 'First', 'X', 'O', 'I'))
            if first:
                flightinfo.append(('Flight '+str(fltno), searchkey, stime, stoppage, "test", origin, dest, departtime, arive, tripDuration, str(first), str(firsttax), str(0),str(0), str(0), str(0), "Economy", "Business", "First", "aeroflot", originDetailString, arivedetailtext, planedetailtext, operatortext, 'F Comfort', 'O Business', 'First', 'F', 'O', 'I'))

        log_file.write(str(flightinfo)) 
    except Exception, e:
        log_file.write('Error Message: '+str(e)+'\n')
        log_file.write('Error or No data!\n\n')

    if not DEV_LOCAL:
        cursor = db.cursor()
        cursor.executemany("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", flightinfo)
        db.commit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", searchkey, stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "aeroflot", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()        

    driver.quit()              
    log_file.close()
    return searchkey    

if __name__=='__main__':
    aeroflot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # aeroflot('MOW', 'BJS', '2016-06-25', '265801')
    # aeroflot('IAD', 'BER', '2016-08-04', '5500')
