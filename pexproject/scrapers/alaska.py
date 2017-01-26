# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
import time
import re
import codecs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

DEV_LOCAL = False
# DEV_LOCAL = True

if not DEV_LOCAL:
    import customfunction
else:
    import pdb

partners = {'Alaska': 'AS', 'Air France': 'AF', 'American': 'AA', 'Delta': 'DL'
    , 'British Airways': 'BA', 'Emirates': 'EK', 'Ravn Alaska': '7H'
    , 'Icelandair': 'FI', 'Fiji Airways': 'FJ', 'Qantas': 'QF'
    , 'Hainan Airlines': 'HU', 'KLM': 'KL', 'Korean Air': 'KE', 'PenAir': 'KS'}


def get_miles_taxes(tds):
    main_mile, main_tax = 0, 0
    business_mile, business_tax = 0, 0
    first_mile, first_tax = 0, 0

    for td in tds:        
        if 'empty' in td['class']:
            continue

        try:
            tmp = td.select('.Price')[0].text.split('+')
            # print tmp, '@@@@@@@@@2'
            tmp_mile, tmp_tax = tmp[0], tmp[1]
            tmp_mile = int(float(tmp_mile.replace('k', ''))*1000)

            tmp_tax = tmp_tax.replace('$', '').strip()
        except Exception, e:
            continue

        if 'coach-fare' in td['class'] and (main_mile == 0 or float(main_mile) > float(tmp_mile)):
            main_mile, main_tax = tmp_mile, tmp_tax
        elif 'business-fare' in td['class'] and (business_mile == 0 or float(business_mile) > float(tmp_mile)):
            business_mile, business_tax = tmp_mile, tmp_tax
        elif 'first-fare' in td['class'] and (first_mile == 0 or float(first_mile) > float(tmp_mile)):
            first_mile, first_tax = tmp_mile, tmp_tax
            
    return main_mile, main_tax, business_mile, business_tax, first_mile, first_tax


def alaska(ocity_code, dcity_code, searchdate, searchkey):
    sss = datetime.datetime.now()
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true',
                                               '--ssl-protocol=any',
                                               '--load-images=false'],
                                 service_log_path='/tmp/ghostdriver.log')

    driver.set_window_size(1120, 1080)  

    # driver = webdriver.Firefox()

    url = "https://www.alaskaair.com"   

    def storeFlag(searchkey,stime):
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag","flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "alaska", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        db.commit()

    sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

    db = customfunction.dbconnection() if not DEV_LOCAL else None
    flightinfo = []
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        driver.get(url)        

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "oneWay")))
        oneway = driver.find_element_by_id('oneWay')
        oneway.click()
        if oneway.get_attribute('value') == 'false':
            driver.execute_script("arguments[0].click();", oneway)
        # print '########', oneway.get_attribute('value')
        # driver.execute_script("document.getElementById('oneWay').setAttribute('checked', 'checked')")
        milebtn = driver.find_element_by_id("awardReservation")
        driver.execute_script("document.getElementById('awardReservation').setAttribute('checked', 'checked')")
        origin = driver.find_element_by_id("fromCity1")
        origin.clear()
        origin.send_keys(ocity_code.strip())
        destination = driver.find_element_by_id("toCity1")
        destination.clear()
        destination.send_keys(dcity_code.strip())
        flight_date = driver.find_element_by_id("departureDate1")
        flight_date.clear()
        flight_date.send_keys(str(searchdate))

        if oneway.get_attribute('value') == 'false':
            driver.execute_script("arguments[0].click();", oneway)

        # driver.execute_script("document.getElementById('departureDate1').setAttribute('value', '"+str(searchdate)+"')")
        driver.find_element_by_id("findFlights").send_keys(Keys.ENTER)

    except:
        print "before data page"
        if not DEV_LOCAL:
            storeFlag(searchkey,stime)

        driver.quit()        
        return searchkey

    try:
        driver.save_screenshot('/root/out_enter.png');
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "ContinueButton")))

        html_page = driver.page_source

        if DEV_LOCAL:
            log_file = open('/root/1.html', 'w')
            # log_file.write(html_page.encode('utf8'))
        # print html_page
        # return
        soup = BeautifulSoup(html_page,"lxml")
        flights = soup.find(id='MatrixTable0').find_all(role='listitem')
        # print len(flights), '########3'
        for flight in flights:
            tds = flight.select('td.FlightCell')

            maindata = tds[0].select('.OptionDetails')[0]
            SegmentContainer = maindata.select('.SegmentContainer')

            flightno, origin, destination, departure = [], [], [], []
            arrival, planeinfo, duration, operatedby = [], [], [], []
            departure_t, arrival_t = [], []

            for sc_ in SegmentContainer:
                detail_line = sc_.select('.DetailsLine')

                flightno_ = get_clean_string(detail_line[0].select('.DetailsFlightNumber')[0].text)

                for s_t_k, s_t_v in partners.items():
                    if s_t_k in flightno_:
                        flightno_ = flightno_.replace(s_t_k, s_t_v)
                        operatedby_ = 'Operated By '+s_t_k
                        break

                origin_ = get_clean_string(detail_line[0].select('.DetailsStation')[0].text)
                departure_ = get_clean_string(detail_line[0].select('.DetailsTime span')[-1].text) + ' ' + searchdate[-2:]
                # print departure_, '@@@@@@@@'
                # formatting date
                departure_ = datetime.datetime.strptime(departure_, '%I:%M%p, %a, %b %d %y')
                departure_t_ = departure_.strftime('%H:%M:%S')
                departure_ = departure_.strftime('%Y/%m/%d %H:%M')

                destination_ = get_clean_string(detail_line[-1].select('.DetailsStation')[0].text)
                arrival_ = get_clean_string(detail_line[-1].select('.DetailsTime span')[-1].text) + ' ' + searchdate[-2:]
                # print flightno_, arrival_, '@@@@@@@2'
                arrival_ = datetime.datetime.strptime(arrival_, '%I:%M%p, %a, %b %d %y')
                arrival_t_ = arrival_.strftime('%H:%M:%S')
                arrival_ = arrival_.strftime('%Y/%m/%d %H:%M')

                DetailsSmall = sc_.select('.DetailsSmall')
                planeinfo_ = get_clean_string(DetailsSmall[0].select('ul li')[0].text).replace('Aircraft: ', '')
                duration_ = get_clean_string(DetailsSmall[1].select('ul li')[0].text).replace('Duration: ', '').replace('hours', 'h ').replace('minutes', 'm')

                flightno.append(flightno_)
                if not DEV_LOCAL:
                    origin_ = customfunction.get_airport_detail(customfunction.get_airport_code(origin_)) or origin_
                departure.append(departure_+' | from '+origin_)
                departure_t.append(departure_t_)
                
                if not DEV_LOCAL:
                    destination_ = customfunction.get_airport_detail(customfunction.get_airport_code(destination_)) or destination_
                arrival.append(arrival_+' | at '+destination_)
                arrival_t.append(arrival_t_)

                if not DEV_LOCAL:
                    planeinfo_ = customfunction.AIRCRAFTS.get(planeinfo_, planeinfo_)
                    
                planeinfo.append("{} | {} ({})".format(flightno_, planeinfo_, duration_))
                duration.append(duration_)
                operatedby.append(operatedby_)

            stop = int(flight['stops'])
            if stop == 0:
                stoppage = "NONSTOP"
            elif stop == 1:
                stoppage = "1 STOP"
            else:
                stoppage = str(stop)+" STOPS"

            total_duration = get_clean_string(maindata.select('.smallText.rightaligned.DetailsSmall')[0].text).replace('Total duration: ', '').replace('hours', 'h').replace('minutes', 'm')

                        
            main_mile, main_tax, business_mile, business_tax, first_mile, first_tax = get_miles_taxes(flight.select('td.matrix-cell'))
            
            departinfo = '@'.join(departure)
            arrivalinfo = '@'.join(arrival)
            planeinfo = '@'.join(planeinfo)
            operatedby = '@'.join(operatedby)
            flightinfo.append((flightno[0], str(searchkey), stime, stoppage, "test", flight['orig'], flight['dest'], departure_t[0], arrival_t[-1], total_duration, main_mile, main_tax, business_mile, business_tax, first_mile, first_tax,"Economy", "Business", "First", "alaska", departinfo, arrivalinfo, planeinfo, operatedby,'','','','','',''))

            if DEV_LOCAL:
                print (flightno[0], str(searchkey), stime, stoppage, "test", flight['orig'], flight['dest'], departure_t[0], arrival_t[-1], total_duration, main_mile, main_tax, business_mile, business_tax, first_mile, first_tax,"Economy", "Business", "First", "alaska", departinfo, arrivalinfo, planeinfo, operatedby,'','','','','','')

    except Exception, e:
        # raise               
        print 'Something is wrong'


    if not DEV_LOCAL:
        cursor = db.cursor()
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code,eco_fare_code,business_fare_code,first_fare_code) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", flightinfo)     
        db.commit()        

        storeFlag(searchkey,stime)

    driver.quit()              
    print '\t#### alaska time elapsed: {}'.format(datetime.datetime.now()-sss)
    return searchkey    

def get_clean_string(string):
    return string.replace('\n', '').replace('\r', '').replace('\t', '').strip()

def get_neat_string(string):
    return re.sub(r"\s+", " ", string, flags=re.UNICODE)

if __name__=='__main__':
    alaska(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print '\t@@@@ alaska finished'
    # pdb.set_trace()        
    # alaska('sfo', 'lax', '12/27/16', '265801')
    # alaska('lax', 'kef', '7/24/17', '265801')
