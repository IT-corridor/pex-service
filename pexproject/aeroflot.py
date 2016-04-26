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
import os,sys

db = MySQLdb.connect(host="localhost",  
                     user="root",           
                      passwd="1jyT382PWzYP",        
                      db="pex")  
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

#searchkeyid =''
class AeroflotSpider(scrapy.Spider):
    name = 'aeroflot'
    searchkeyid = ''    
    def __init__(self,*args, **kwargs):
        super(AeroflotSpider, self).__init__(*args, **kwargs)
       
        self.origin = kwargs.get('origin')
        self.destination =kwargs.get('destination')
        self.date = '2016-05-03' #date #kwargs.get('date')
        self.start_urls = [URL % (self.origin, self.destination, self.date)]
        self.searchkeyid = kwargs.get('searchid')
	print "searchkeyid",self.searchkeyid
    def init_cookies(self, response):
        print "init cookies"
        radio_id = response.xpath(
            '//input[contains(@id, "flight_both_")]/@id').extract_first()

        display = pyvirtualdisplay.Display(visible=0, size=(800, 600))
        display.start()
        driver = selenium.webdriver.Chrome()
        driver.get(self.start_urls[0])
        execution = driver.current_url[-4:]
        radio = driver.find_element_by_id(radio_id)
        time.sleep(1)
        radio.click()
        cookies = {
            'JSESSIONID': get_cookie(driver, 'JSESSIONID', '/SSW2010'),
            'WLPCOOKIE': get_cookie(driver, 'WLPCOOKIE', '/SSW2010'),
        }
        DATA['execution'] = execution
        return cookies

    def parse(self, response):
	print "searchkeyid",self.searchkeyid
        error_msgs = ('No Flights Available', 'No award available')
        for m in error_msgs:
            if m in response.body:
                print m
                return

        now = datetime.datetime.now()
        cookies = self.init_cookies(response)
        flightinfo = []
        
        for i, row in enumerate(response.css('#dtcontainer-both tbody tr')):
            maincabin = 0
            firstclass = 0
            business = 0
            ths, tds = row.css('th'), row.css('td')
            span = ths[2].css('.flight-number-and-direction')

            flightno = [get_text_from_cell(a) for a in span.css('a')]
            flightno = flightno[0]
            stoppage = get_text_from_cell(ths[2].css('.stops'))
            stoppage_station = [get_text_from_cell(e).split('to')[-1].strip()
                                for e in span][:-1]
            departure = get_text_from_cell(ths[0])
            departure = departure.split(' ')[1]
            arrival = get_text_from_cell(ths[1])
            arrival = arrival.split(' ')[1]
            duration = get_text_from_cell(ths[3])
            maincabin1 = get_text_from_cell(tds[0].css('.prices-amount'))
            if maincabin1:
                maincabin = int(maincabin1)
            firstclass1 = get_text_from_cell(tds[1].css('.prices-amount'))
            if firstclass1:
                firstclass = int(firstclass1)
            business1 = get_text_from_cell(tds[2].css('.prices-amount'))
            if business1:
                business = int(business1)
            arrivedetails = '%s at %s' % (arrival, self.destination)
            departdetails = '%s from %s' % (departure, self.origin)
            operatedby = [get_text_from_cell(cn)
                          for cn in ths[2].css('.carrier-name')]
            operatedby =operatedby[0]

            flight = {
                'scrapetime': now,
                'flightno': flightno,
                'searchkeyid':2,
                'stoppage': stoppage,
                'stoppage_station': stoppage_station,
                'origin': self.origin,
                'destination': self.destination,
                'departure': departure,
                'arrival': arrival,
                'duration': duration,
                'maincabin': maincabin,
                'firstclass': firstclass,
                'business': business,
                'datasource': self.name,
                'arrivedetails': arrivedetails,
                'departdetails': departdetails,
                'operatedby': operatedby,
            }
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
                    #flight[tax_field_name] = tax_amount
                
            #yield flight
            #cursor.execute("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (str(flightno),'2',str(now),stoppage,"test",self.origin,self.destination,str(departure),str(arrival),duration,str(maincabin),str(maintax),str(business),str(businesstax),str(firstclass),str(firsttax),'Economy','Business','First','aeroflot',departdetails,arrivedetails,flightno,operatedby))

            flightinfo.append((str(flightno),str(self.searchkeyid),str(now),stoppage,"test",self.origin,self.destination,str(departure),str(arrival),duration,str(maincabin),str(maintax),str(business),str(businesstax),str(firstclass),str(firsttax),'Economy','Business','First','aeroflot',departdetails,arrivedetails,flightno,operatedby))
        #print flightinfo
        cursor.executemany("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", flightinfo)
        print "final row inserted"
        db.commit()
        
        
