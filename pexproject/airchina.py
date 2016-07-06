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

SET_LANG_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxChangeLang_amrshop.action?request_locale=en_US'
SEARCH_URL = 'http://ebooking.airchina.com.cn/AMRWeb/shopping/search/searchFlight_amrshop.action?shopRequest.adultTravelers=1&shopRequest.orgCity1=%s&shopRequest.dstCity1=%s&shopRequest.takeoffdate1=%s&shopRequest.queryTripType=OW&shopRequest.carrierAirline=CA'
DETAIL_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxGetAirInfo_flightsummary.action?airTypeNo=%s&cabin=I&takeOffDate=%s&segment=%s'
PRICE_URL = 'http://ebooking.airchina.com.cn/AMRWeb/ajaxPriceOW_selection.action'
AJAX_DATA = '{"flightIndex":"%d","cabin":"%s"}'
AIR_LINES = ['CA', 'SC', 'TV', 'ZH', 'NX']


def get_cookie(driver, name, path):
    cookies = driver.get_cookies()
    for cookie in cookies:
        if (cookie['name'] == name and cookie['path'].strip('/') == path.strip('/')):
            return cookie['value']
    return None

def get_tax(log_file, cookies, index, cabin):
    resp = requests.post(
        PRICE_URL,
        cookies=cookies,
        data={'param': AJAX_DATA % (index, cabin)}
    )
    # time.sleep(2)
    # log_file.write(resp.text.encode('utf8')+'\n\n\n')
    soup = BeautifulSoup(resp.text,"lxml")

    if soup.select('div.errorBlock'):
        return 0

    tables = soup.select('table')
    tax = tables[2].td.text
    tax = re.search('\+ ([\d.]+)RMB', tax).group(1)
    return float(tax) * 0.1519355


def airchina(ocity_code, dcity_code, searchdate, searchkey):
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    url = SEARCH_URL % (ocity_code, dcity_code, searchdate)

    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    log_path = 'airchina_log' if DEV_LOCAL else '/home/upwork/airchina_log'
    log_file = open(log_path, 'a') if DEBUG else sys.stdout
    log_file.write('\n\n'+'='*70+'\n\n')    
    log_file.write(url+'\n\n')

    driver = webdriver.Chrome(chromedriver)
    db = customfunction.dbconnection() if not DEV_LOCAL else None
    flightinfo = []
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        driver.get(SET_LANG_URL)
        driver.get(url)        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "idTbl_OutboundAirList")))
        
        cookies = {
            'JSESSIONID': get_cookie(driver, 'JSESSIONID', '/AMRWeb'),
            'BIGipServerAMR_web': get_cookie(driver, 'BIGipServerAMR_web', '/'),
        }

        html_page = driver.page_source
        # log_file.write(html_page.encode('utf8'))
        soup = BeautifulSoup(html_page,"lxml")
        maindata = soup.select('#idTbl_OutboundAirList tbody tr')

        index = -1
        
        for flight in maindata:
            index = index + 1
            tds = flight.select('td')
            flightno = tds[0].string
            departure = tds[1].strong.string
            arrival = tds[2].strong.string
            origin_dest = tds[3].string.split('-')
            origin = origin_dest[0]
            destination = origin_dest[1]

            url = DETAIL_URL % (flightno, searchdate, origin+destination)
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
            departinfo = departinfo_time + ' | from ' + departinfo_airport

            arrivalinfo_airport = get_neat_string(trs[0].select('td')[1].div.select('span')[0].string)
            arrivalinfo_time = get_neat_string(trs[0].select('td')[1].div.select('span')[1].text)        
            arrivalinfo_time = datetime.datetime.strptime(arrivalinfo_time, ' %a, %d %b %Y %H:%M ')
            arrivalinfo_time = arrivalinfo_time.strftime('%Y/%m/%d %H:%M')
            arrivalinfo = arrivalinfo_time + ' at ' + arrivalinfo_airport

            planeinfo = get_clean_string(trs[1].td.div.string)
            planeinfo = '%s | %s (%s)' % (flightno, planeinfo, duration)

            firstmile = tds[5].font
            firstmile = firstmile.label.string if firstmile else 0
            firsttax = get_tax(log_file, cookies, index, 'O') if firstmile else 0

            businessmile = tds[6].font
            businessmile = businessmile.label.string if businessmile else 0
            businesstax = get_tax(log_file, cookies, index, 'I') if businessmile else 0

            economymile = tds[7].font
            economymile = economymile.label.string if economymile else 0
            economytax = get_tax(log_file, cookies, index, 'X') if economymile else 0

            stoppage = "NONSTOP"
            flightinfo.append(('Flight '+flightno, str(searchkey), stime, stoppage, "test", origin, destination, departure+':00', arrival+':00', duration, economymile, economytax, businessmile, businesstax, firstmile, firsttax,"Economy", "Business", "First", "airchina", departinfo, arrivalinfo, planeinfo, operatedby,'X Economy','I Business','O First','X','I','O'))
        log_file.write(str(flightinfo)+'\n')

    except Exception, e:
        log_file.write('Error/No data Message: '+str(e)+'\n')


    if not DEV_LOCAL:
        cursor = db.cursor()
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", flightinfo)     
        db.commit()        
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", searchkey, stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "airchina", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()        

    display.stop()
    driver.quit()              
    log_file.close()
    return searchkey    

def get_clean_string(string):
    return re.sub(r"\s+", "", string, flags=re.UNICODE)

def get_neat_string(string):
    return re.sub(r"\s+", " ", string, flags=re.UNICODE)

if __name__=='__main__':
    airchina(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    # airchina('PEK', 'LAX', '2016-06-28', '265801')
    # airchina('JFK', 'MOW', '2016-07-18', '265801')
