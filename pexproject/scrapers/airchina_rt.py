import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import re
from pyvirtualdisplay import Display
import codecs
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEBUG = False
DEBUG = True
DEV_LOCAL = False
# DEV_LOCAL = True

if not DEV_LOCAL:
    import customfunction

HOME_URL = 'http://ebooking.airchina.com.cn/AMRWeb/shopping/search/showSearchPage_amrshop.action'
SET_LANG_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxChangeLang_amrshop.action?request_locale=en_US'
SEARCH_URL = 'http://ebooking.airchina.com.cn/AMRWeb/shopping/search/searchFlight_amrshop.action?shopRequest.adultTravelers=1&shopRequest.orgCity1=%s&shopRequest.dstCity1=%s&shopRequest.takeoffdate1=%s&shopRequest.takeoffdate2=%s&shopRequest.queryTripType=RT&shopRequest.carrierAirline=CA'
DETAIL_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxGetAirInfo_flightsummary.action?airTypeNo=%s&cabin=I&takeOffDate=%s&segment=%s'
PRICE_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxPriceRT_selection.action'
AJAX_DATA = '{"flightIndex":"%d","cabin":"%s","flightIndex1":"%d","cabin1":"%s"}'
AIR_LINES = ['CA', 'SC', 'TV', 'ZH', 'NX']

AIRCRAFTS = {
    '321': 'Airbus A321',
    '32A': 'Airbus A32A',
    '330': 'Airbus A330',
    '333': 'Airbus A330-300',
    '33A': 'Airbus A33A',
    '747': 'Boeing 747',
    '772': 'Boeing 777-200ER',
    '773': 'Boeing 777-300'
}

def get_airport_code(airport):
    airport = airport.split(' (')
    return airport[1][:3]


def get_cookie(driver, name, path):
    cookies = driver.get_cookies()
    for cookie in cookies:
        if (cookie['name'] == name and cookie['path'].strip('/') == path.strip('/')):
            return cookie['value']
    return None

def get_mile_tax(log_file, cookies, flight_to_info, flight_from_info, cabin):
    index = {'X':10, 'I':12, 'O':14}

    ii = -1
    for i in range(len(flight_to_info)):
        if flight_to_info[i][index[cabin]]:
            ii = i
            break
    if ii == -1:
        return '0', '0'

    jj = -1
    for j in range(len(flight_from_info)):
        if flight_from_info[j][index[cabin]]:
            jj = j
            break
    if jj == -1:
        return '0', '0'

    resp = requests.post(
        PRICE_URL,
        cookies=cookies,
        data={'param': AJAX_DATA % (ii, cabin, jj, cabin)}
    )
    soup = BeautifulSoup(resp.text,"lxml")

    if soup.select('div.errorBlock'):
        return '0', '0'

    tables = soup.select('table')
    mile = int(tables[1].tr.select('td')[1].span.string) / 2
    tax = tables[2].td.text
    tax = re.search('\+ ([\d.]+)RMB', tax).group(1)
    tax = float(tax) * 0.1519355 / 2
    return str(mile), str(tax)

def airchina(ocity_code, dcity_code, searchdate, searchkey, returndate, returnkey):
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    
    driver = webdriver.Chrome(chromedriver)
    driver.implicitly_wait(1) 

    url = SEARCH_URL % (ocity_code, dcity_code, searchdate, returndate)

    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    log_path = 'airchina_rt_log' if DEV_LOCAL else '/home/upwork/airchina_rt_log'
    log_file = open(log_path, 'a') if DEBUG else sys.stdout
    log_file.write('\n\n'+'='*70+'\n\n')    
    log_file.write(url+'\n\n')
    db = customfunction.dbconnection() if not DEV_LOCAL else None
    flightinfo = []     

    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')

    try:
        driver.get(SET_LANG_URL)
        log_file.write(SET_LANG_URL+'\n')
        driver.get(url)
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "idTbl_OutboundAirList")))
        log_file.write('@@@@@@@@')
        cookies = {
            'JSESSIONID': get_cookie(driver, 'JSESSIONID', '/AMRWeb'),
            'BIGipServerAMR_web': get_cookie(driver, 'BIGipServerAMR_web', '/'),
        }

        html_page = driver.page_source
        # log_file.write(html_page.encode('utf8'))
        soup = BeautifulSoup(html_page,"lxml")

        maindata = soup.select('#idTbl_OutboundAirList tbody tr')
        flight_to_info = get_flight_info(driver, maindata[1:], searchdate, searchkey, stime)
        maindata = soup.select('#idTbl_InboundAirList tbody tr')
        flight_from_info = get_flight_info(driver, maindata[1:], returndate, returnkey, stime)

        log_file.write(str(flight_to_info)+'\n\n')
        log_file.write(str(flight_from_info)+'\n\n')

        firstmile, firsttax = get_mile_tax(log_file, cookies, flight_to_info, flight_from_info, 'O')
        businessmile, businesstax = get_mile_tax(log_file, cookies, flight_to_info, flight_from_info, 'I')
        economymile, economytax = get_mile_tax(log_file, cookies, flight_to_info, flight_from_info, 'X')

        for i in range(len(flight_to_info)):
            flight_to_info[i][15] = firsttax if flight_to_info[i][14] else '0'
            flight_to_info[i][13] = businesstax if flight_to_info[i][12] else '0'
            flight_to_info[i][11] = economytax if flight_to_info[i][10] else '0'
            flight_to_info[i][14] = firstmile if flight_to_info[i][14] else '0'
            flight_to_info[i][12] = businessmile if flight_to_info[i][12] else '0'
            flight_to_info[i][10] = economymile if flight_to_info[i][10] else '0'
            flightinfo.append(tuple(flight_to_info[i]))

        for i in range(len(flight_from_info)):
            flight_from_info[i][15] = firsttax if flight_from_info[i][14] else '0'
            flight_from_info[i][13] = businesstax if flight_from_info[i][12] else '0'
            flight_from_info[i][11] = economytax if flight_from_info[i][10] else '0'
            flight_from_info[i][14] = firstmile if flight_from_info[i][14] else '0'
            flight_from_info[i][12] = businessmile if flight_from_info[i][12] else '0'
            flight_from_info[i][10] = economymile if flight_from_info[i][10] else '0'
            flightinfo.append(tuple(flight_from_info[i]))

        log_file.write(str(flightinfo)+'\n')
    except Exception, e:
        log_file.write('Error/No data Message: '+str(e)+'\n')

    if not DEV_LOCAL:
        cursor = db.cursor()
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", flightinfo)     
        db.commit()        
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "airchina", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()        
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(returnkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "airchina", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()        

    display.stop()
    driver.quit()              
    log_file.close()
    return searchkey    

def get_flight_info(driver, maindata, flightdate, searchkey, stime):
    flightinfo = []
    for flight in maindata:
        tds = flight.select('td')
        flightno = tds[0].string
        departure = tds[1].strong.string
        arrival = tds[2].strong.string
        origin_dest = tds[3].string.split('-')
        origin = origin_dest[0]
        destination = origin_dest[1]

        url = DETAIL_URL % (flightno, flightdate, origin+destination)
        driver.get(url)
        html_page = driver.page_source
        # log_file.write(html_page.encode('utf8'))
        detail_soup = BeautifulSoup(html_page,"lxml")
        tables = detail_soup.select('table')
        trs = tables[0].select('tr')

        operatedby = get_clean_string(trs[0].select('td')[1].div.string)
        duration = get_clean_string(trs[1].select('td')[1].div.string)
        trs = tables[1].select('tr')
        departinfo_airport = get_neat_string(trs[0].select('td')[0].div.select('span')[0].string)
        departinfo_time = get_neat_string(trs[0].select('td')[0].div.select('span')[1].text)
        departinfo_time = datetime.datetime.strptime(departinfo_time, ' %a, %d %b %Y %H:%M ')
        departinfo_time = departinfo_time.strftime('%Y/%m/%d %H:%M')
        airport_ = customfunction.get_airport_detail(get_airport_code(departinfo_airport)) or departinfo_airport
        departinfo = departinfo_time + ' | from ' + airport_

        arrivalinfo_airport = get_neat_string(trs[0].select('td')[1].div.select('span')[0].string)
        arrivalinfo_time = get_neat_string(trs[0].select('td')[1].div.select('span')[1].text)        
        arrivalinfo_time = datetime.datetime.strptime(arrivalinfo_time, ' %a, %d %b %Y %H:%M ')
        arrivalinfo_time = arrivalinfo_time.strftime('%Y/%m/%d %H:%M')
        airport_ = customfunction.get_airport_detail(get_airport_code(arrivalinfo_airport)) or arrivalinfo_airport
        arrivalinfo = arrivalinfo_time + ' at ' + airport_

        planeinfo = get_clean_string(trs[1].td.div.string)
        planeinfo = '%s | %s (%s)' % (flightno, AIRCRAFTS[planeinfo], duration)

        firstmile = tds[5].input
        firstmile = 1 if firstmile else 0
        firsttax = 0

        businessmile = tds[6].input
        businessmile = 1 if businessmile else 0
        businesstax = 0

        economymile = tds[7].input
        economymile = 1 if economymile else 0
        economytax = 0

        stoppage = "NONSTOP"
        flightinfo.append(['Flight '+flightno, searchkey, stime, stoppage, "test", origin, destination, departure+':00', arrival+':00', duration, economymile, economytax, businessmile, businesstax, firstmile, firsttax,"Economy", "Business", "First", "airchina", departinfo, arrivalinfo, planeinfo, operatedby,'X Economy','I Business','O First','X','I','O'])

    return flightinfo

def get_clean_string(string):
    return re.sub(r"\s+", "", string, flags=re.UNICODE)

def get_neat_string(string):
    return re.sub(r"\s+", " ", string, flags=re.UNICODE)

if __name__=='__main__':
    airchina(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    # airchina('PEK', 'LAX', '2016-06-28', 265801, '2016-08-09')
    # airchina('JFK', 'MOW', '2016-07-18', '265801')
