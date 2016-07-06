import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pyvirtualdisplay import Display
import json
import codecs

DEBUG = False
DEBUG = True
DEV_LOCAL = False
# DEV_LOCAL = True

if not DEV_LOCAL:
    import customfunction

def get_city_s7_code(citycode=None):
    file_path = 'location.json' if DEV_LOCAL else '/var/www/html/python/pex/pexproject/pexproject/location.json'
    json_text = open(file_path, 'r')
    jsonData = json.loads(json_text.read())
    for item in jsonData:
        if item['iata'] == citycode:
            return item['code']
    json_text.close()
    return 'None'

def s7ru(ocity_code, dcity_code, searchdate, searchkey):
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    
    driver = webdriver.Chrome(chromedriver)
    driver.implicitly_wait(1) 
    url = 'http://travelwith.s7.ru/selectExactDateSearchFlights.action?TA=1&CUR=USD&FLC=1&RDMPTN=true&FSC1=1&DD1=%s&DA1=%s&DP1=%s&AA1=%s&AP1=%s&LAN=en' % (searchdate, ocity_code, get_city_s7_code(ocity_code), dcity_code, get_city_s7_code(dcity_code))

    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    log_path = 's7_log' if DEV_LOCAL else '/home/upwork/s7_log'
    log_file = open(log_path, 'a') if DEBUG else sys.stdout
    db = customfunction.dbconnection() if not DEV_LOCAL else None

    log_file.write('\n\n'+'='*70+'\n\n')
    log_file.write(url+'\n\n')

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "exact_outbound_section")))

        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"lxml")
        maindata = soup.find_all("div",{"class": "select-item--multiple"})

        ibe_conversation = soup.find_all("input",{"id": "ibe_conversation"})[0]['value']
        log_file.write(ibe_conversation+'\n\n') 
        for flight in maindata:
            parse_flight(flight, ibe_conversation, driver, log_file, db, searchkey, searchdate)
    except Exception, e:
        log_file.write('Error/No data Message: '+str(e)+'\n')

    if not DEV_LOCAL:
        currentdatetime = datetime.datetime.now()
        stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')

        cursor = db.cursor()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", searchkey, stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "s7", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()        

    display.stop()
    driver.quit()              
    log_file.close()
    return searchkey    

def parse_flight(flight, ibe_conversation, driver, log_file, db, searchkey, searchdate):
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')

    searchdate = datetime.datetime.strptime(searchdate, '%Y-%m-%d')

    departure = flight.find_all("time", {"data-qa": "timeDepartureTotal_flightItemShort"})[0].text
    arrival = flight.find_all("time", {"data-qa": "timeArrivedTotal_flightItemShort"})[0].text
    origin = flight.find_all("span", {"data-qa": "airportDepartureTotal_flightItemShort"})[0].text    
    destination = flight.find_all("span", {"data-qa": "airportArrivedTotal_flightItemShort"})[0].text    
    duration = flight.find_all("div", {"class": "duration"})[0].text    

    e_node = (flight.find_all("div", {"data-qa": "tariff_economy optimum"}) or flight.find_all("div", {"data-qa": "tariff_economy optimum_active"}))[0]
    eo_mile, eo_tax = get_miles_tax(e_node, ibe_conversation, driver)
    e_node = (flight.find_all("div", {"data-qa": "tariff_economy priority"}) or flight.find_all("div", {"data-qa": "tariff_economy priority_active"}))[0]
    ep_mile, ep_tax = get_miles_tax(e_node, ibe_conversation, driver)
    e_node = (flight.find_all("div", {"data-qa": "tariff_business optimum"}) or flight.find_all("div", {"data-qa": "tariff_business optimum_active"}))[0]
    bo_mile, bo_tax = get_miles_tax(e_node, ibe_conversation, driver)
    e_node = (flight.find_all("div", {"data-qa": "tariff_business priority"}) or flight.find_all("div", {"data-qa": "tariff_business priority_active"}))[0]
    bp_mile, bp_tax = get_miles_tax(e_node, ibe_conversation, driver)

    stoppage = -1
    departs = []
    arrives = []
    flights = []
    flightnos = []
    operatedby = []
    flightinfo = []

    for extend_info in flight.find_all("div", {"data-qa": "extended_info"}):
        stoppage += 1
        e_info = extend_info.find_all("div", {"class": "info-flight"})[0]
        e_departure = e_info.find_all("time", {"data-qa": "timeDeparture_flightItem"})[0].text
        departdate = searchdate
        departdatestr = departdate.strftime('%Y/%m/%d')

        e_arrival = e_info.find_all("time", {"data-qa": "timeArrived_flightItem"})[0].text
        next_day = extend_info.find_all("div", {"class": "arrival-time"})[0]
        next_day = next_day.find_all("span", {"data-qa": "nextDayArrived"})
        arrivaldate = searchdate + timedelta(days=1) if next_day else searchdate
        arrivaldatestr = arrivaldate.strftime('%Y/%m/%d')

        e_flightno = e_info.find_all("span", {"data-qa": "number_flightItem"})[0].text
        e_origin = e_info.find_all("li")[0].text
        e_destination = e_info.find_all("li")[1].text
        e_plane1 = e_info.find_all("li")[2].text
        e_plane2 = e_info.find_all("li")[3].text
        e_duration = e_info.find_all("li")[4].text.strip()

        e_origin = re.sub(r"\s+", " ", e_origin, flags=re.UNICODE)
        e_destination = re.sub(r"\s+", " ", e_destination, flags=re.UNICODE)
        e_plane1 = re.sub(r"\s+", " ", e_plane1, flags=re.UNICODE)
        e_plane2 = re.sub(r"\s+", " ", e_plane2, flags=re.UNICODE)

        depart = '%s %s | from %s' % (departdatestr, e_departure, e_origin)
        arrive = '%s %s at %s' % (arrivaldatestr, e_arrival, e_destination)
        flight_ = '%s | %s (%s)' % (e_flightno, e_plane2, e_duration)

        flightnos.append(e_flightno)
        departs.append(depart)
        arrives.append(arrive)
        flights.append(flight_)
        operatedby.append(e_plane1)

    if stoppage == 0:
        stoppage = "NONSTOP"
    elif stoppage == 1:
        stoppage = "1 STOP"
    else:
        stoppage = str(stoppage)+" STOPS"

    departdetailsText = '@'.join(departs)
    arivedetailsText = '@'.join(arrives)
    planedetails = '@'.join(flights)
    operatedbytext = '@'.join(operatedby)

    if eo_mile != '0' or bo_mile != '0':
        flightinfo.append(('Flight '+flightnos[0], str(searchkey), stime, stoppage, "test", origin, destination, departure+':00', arrival+':00', duration, eo_mile, eo_tax, bo_mile, bo_tax, '0', '0',"Economy", "Business", "First", "s7", departdetailsText, arivedetailsText, planedetails, operatedbytext,'Economy Optimum@Economy Optimum@Economy Optimum','Business Optimum@Business Optimum@Business Optimum','Business Priority@Business Priority@Business Priority','X','I','O'))
    if ep_mile != '0' or bp_mile != '0':
        flightinfo.append(('Flight '+flightnos[0], str(searchkey), stime, stoppage, "test", origin, destination, departure+':00', arrival+':00', duration, ep_mile, ep_tax, bp_mile, bp_tax, '0', '0',"Economy", "Business", "First", "s7", departdetailsText, arivedetailsText, planedetails, operatedbytext,'Economy Priority@Economy Priority@Economy Priority','Business Priority@Business Priority@Business Priority','Business Priority@Business Priority@Business Priority','X','I','O'))

    if db:
        cursor = db.cursor()
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", flightinfo)
        db.commit()

    log_file.write(str(flightinfo)+'\n')

def get_miles_tax(node, ibe_conversation, driver):
    mile = node.find_all("span", {"data-qa": "amount"})
    if mile:
        mile = re.sub(r"\s+", "", mile[0].text, flags=re.UNICODE)

        flightRefId = node.find_all("input", {"class": "js-flightRef"})[0]['value']
        fareRefId = node.find_all("input", {"class": "js-fareDetailsRef"})[0]['value']
        ajax_url = 'http://travelwith.s7.ru/ajax/actions/changeOutboundExactDateFlight.action?flightRefId=%s&fareRefId=%s&ibe_conversation=%s' % (flightRefId, fareRefId, ibe_conversation)
        driver.get(ajax_url)
        # time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "lxml")
        tax = soup.find_all("span", {"id": "shopping_cart_total_amount"})
        if tax:
            return mile, tax[0]['data-base-amount']
    return '0', '0'

if __name__=='__main__':
    s7ru(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # s7ru('MOW', 'BJS', '2016-06-27', '265801')
    # s7ru('JFK', 'MOW', '2016-07-18', '265801')
