# This scraper scrapes the Aeroflot website for fligth data. It accepts
# three parameters on the command line (origin airport, destination airport
# and date of travel), and outputs the result in a .json file.
#
# Dependencies: BeautifulSoup, requests, Selenium, Scrapy
#
# To invoke the scraper, simply type:
# scrapy runspider aeroflot.py -a origin=MOW -a destination=JFK -a date=2016-04-22 -o aeroflot.json -t json

from bs4 import BeautifulSoup
import datetime
import pyvirtualdisplay
import requests
import selenium.webdriver
import scrapy
import time
import MySQLdb
import re,json
import customfunction

db = customfunction.dbconnection() 
cursor = db.cursor()

TAXES = {
    'AE': 'maintax',
    'AC': 'firsttax',
    'AB': 'businesstax',
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
    'execution': None,
    'contextObject': None
}


def clean(s):
    return s.replace('\n', '').replace('\r', '').strip()


def get_text_from_cell(th):
    return (' '.join([clean(e.extract())
                      for e in th.xpath('.//text()')])).strip()


def get_cookie(driver, name, path):
    cookies = driver.get_cookies()
    for cookie in cookies:
        if (cookie['name'] == name and
           cookie['path'].strip('/') == path.strip('/')):
            return cookie['value']
    return None


def find_flight_id(row, flight_type_code):
    try:
        return row.xpath(
            './/td[@fare-family-key="%s"]' % flight_type_code).css(
            'input').xpath('./@id').extract_first().replace('flight_both_', '')
    except AttributeError:
        return None


class AeroflotSpider(scrapy.Spider):
    name = 'aeroflot'
    searchkeyid = ''
    def __init__(self, *args, **kwargs):
        super(AeroflotSpider, self).__init__(*args, **kwargs)
        self.origin = kwargs.get('origin')
        self.destination = kwargs.get('destination')
        self.date = kwargs.get('date')
        self.start_urls = [URL % (self.origin, self.destination, self.date)]
        self.searchkeyid = kwargs.get('searchid')
        print "searchkeyid",self.searchkeyid
    def init_cookies(self, response):
        radio_id = response.xpath(
            '//input[contains(@id, "flight_both_")]/@id').extract_first()
        
        display = pyvirtualdisplay.Display(visible=0, size=(800, 600))
        display.start()
        driver = selenium.webdriver.Chrome()
        driver.get(self.start_urls[0])
        execution = driver.current_url[-4:]
        try:
            radio = driver.find_element_by_id(radio_id)
        except:
            now = datetime.datetime.now()
            cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(self.searchkeyid), str(now), "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "aeroflot", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
            db.commit()
            return
        time.sleep(1)
        radio.click()
        cookies = {
            'JSESSIONID': get_cookie(driver, 'JSESSIONID', '/SSW2010'),
            'WLPCOOKIE': get_cookie(driver, 'WLPCOOKIE', '/SSW2010'),
        }
        DATA['execution'] = execution
        return cookies

    def parse(self, response):
        error_msgs = ('No Flights Available', 'No award available')
	now = datetime.datetime.now()
        for m in error_msgs:
            if m in response.body:
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(self.searchkeyid), str(now), "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "aeroflot", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
                db.commit()
                return

        
        cookies = self.init_cookies(response)
        flightinfo = []
        operatorArray = []
        priceArray=[]
        taxArray=[]
        priceList = {}
        taxList = {}
        pricecounter = 0
        for i, row in enumerate(response.css('#dtcontainer-both tbody tr')):
            ths, tds = row.css('th'), row.css('td')
            
            span = ths[2].css('.flight-number-and-direction')
            
            for cn in ths[2].css('.carrier-name'):
                operatedby = get_text_from_cell(cn)
                operatorArray.append(operatedby)
            maincabin = 0
            firstclass = 0
            business = 0
            maincabin1 = get_text_from_cell(tds[0].css('.prices-amount'))
            if maincabin1:
                maincabin = int(maincabin1)
            firstclass1 = get_text_from_cell(tds[1].css('.prices-amount'))
            if firstclass1:
                firstclass = int(firstclass1)
            business1 = get_text_from_cell(tds[2].css('.prices-amount'))
            if business1:
                business = int(business1)
                
            priceList[pricecounter]={"maincabin":maincabin,"firstclass":firstclass,"business":business}
            priceArray.append(priceList)
            maintax = 0
            firsttax = 0
            businesstax = 0
            for flight_type_code, tax_field_name in TAXES.items():
                flight_id = find_flight_id(row, flight_type_code)
                if flight_id:
                    DATA['contextObject'] = [CONTEXTOBJECT % flight_id]
                    resp = requests.post(
                        FLIGHT_URL,
                        cookies=cookies,
                        data=DATA,
                    )
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    tax_amount = soup.find('div', class_='total-top').find_all(
                        'span', class_='prices-amount')#[1].text
                    if len(tax_amount) > 0:
                        tax_amount = tax_amount[1].text
                    else:
                        tax_amount = 0
                    print "tax_amount",tax_amount
                    print "tax_field_name",tax_field_name
                    if 'main' in tax_field_name:
                        maintax = float(tax_amount)
                    elif 'business' in tax_field_name:
                        businesstax = float(tax_amount)
                    elif tax_field_name != '':
                        firsttax = float(tax_amount)
            taxList[pricecounter]={"maintax":maintax,"businesstax":businesstax,"firsttax":firsttax}
            pricecounter =pricecounter+1
            taxArray.append(taxList)
            
        print "taxArray",len(taxArray)
        print "priceArray",len(priceArray)
        json_text = re.search(r'^\s*var templateData = \s*({.*?})\s*;\s*$',response.body, flags=re.DOTALL | re.MULTILINE).group(1)
        jsonData = json.loads(json_text)
        tempdata = jsonData["rootElement"]["children"][1]["children"][0]["children"][5]["model"]["allItineraryParts"]
        operatorDetails = []
        count = 0
        for k in range(0,len(tempdata)):
            
            segments = tempdata[k]["segments"]
            #print segments
            rowRecord = tempdata[k]["itineraryPartData"]
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
            flightsDetails =[]
            operatorCarrier = []
            for counter in range (0,len(segments)):
                bookingCode = segments[counter]['bookingClass']
                bookingClassCabin = segments[counter]['allClassOfService']
                #print bookingCode,bookingClassCabin
                segOrigin = segments[counter]["departureCode"]
                segDepartDate = segments[counter]["departureDate"]
                segDetailFormat = segDepartDate+" | from "+segOrigin
                originDetails.append(segDetailFormat)
                
                segDest = segments[counter]["arrivalCode"]
                segArive = segments[counter]["arrivalDate"]
                destdetailFormat = segArive+" | at "+segDest
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
            print "tripDuration",tripDuration
            departureCodes = rowRecord["departureCodes"]
            #arrivalCodes = rowRecord["arrivalCodes"]
            operatingCarrier = rowRecord["operatingCarrier"]
            print "operatingCarrier",operatingCarrier
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
                taxes = farePrices[0]["moneyTO"]["originalAmount"]["amount"]
                if 'AE' in key:
                    economy = miles
                    ecotax = taxes
                elif 'AB' in key:
                    business = miles
                    businesstax = taxes
                elif 'AC' in key:
                    first = miles
                    firsttax = taxes
            
            flightinfo.append((str(fltno), str(self.searchkeyid), str(now), stoppage, "test", origin, dest, departtime, arive, tripDuration, str(economy), str(ecotax), str(business),str(businesstax), str(first), str(firsttax), "Economy", "Business", "First", "aeroflot", originDetailString, arivedetailtext, planedetailtext, operatortext))
            #flightinfo.append((str(flightno),str(self.searchkeyid),str(now),stoppage,"test",self.origin,self.destination,str(departure),str(arrival),duration,str(maincabin),str(maintax),str(business),str(businesstax),str(firstclass),str(firsttax),'Economy','Business','First','aeroflot',departdetails,arrivedetails,flightno,operatedby))
        #print flightinfo
        cursor.executemany("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", flightinfo)
        print "final row inserted"
        db.commit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(self.searchkeyid), str(now), "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "aeroflot", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit() 
