#!/usr/bin/env python 
import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mechanize
import urllib
import time
import MySQLdb
from django.db import connection, transaction
import datetime
from datetime import timedelta
from selenium.webdriver.support.ui import Select
import re
from pyvirtualdisplay import Display

def scrapeFlight(page_contents,searchid):
    '''
    db = MySQLdb.connect(host="localhost",  
                     user="root",          
                      passwd="1jyT382PWzYP",       
                      db="pex")
    cursor = db.cursor()
    '''
    cursor = connection.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    flightcontainer = page_contents.findAll("div",{"class":"aa_flightListContainer"})
    for flights in flightcontainer:
        flightinfo = flights.findAll("div",{"class":"ca_flightSlice"})
        stop =  int(len(flightinfo))-1    
        flag = stop
        pricemile = 0
        flightno = ''
        departcode= ''
        departtime= ''
        dest_time = ''
        dest_code = ''
        aircraft = ''
        totaltime= ''
        cabin_name = ''
        stoppage = ''
        departdetail = []
        arivedetail = []
        flightdetail = []
        operatedby = []
        for detail in flightinfo:
            miles = (detail.find("div",{"class":"aa_flightList_col-1"}).text).strip()
            if miles != '':
                if 'K' in miles:
                    miles = miles.replace('K','')
                    if '.' in miles:
                        miles = miles.replace('.','')
                        pricemile = int(miles) * 100
                    else:
                        pricemile = int(miles) * 1000
            
            #print "flight_num",flight_num
            
            departinfo = detail.find("div",{"class":"aa_flightList_col-3"})
            origin_time = departinfo.find("strong").text
            #print "origin_time",origin_time
            origin_code = departinfo.find("span").text
            #print "origin_code",origin_code
            origin_full_name = departinfo.find("span")['title']
            origin_full_name1 = origin_full_name.split(",")
            origin_info = origin_time+" from "+origin_full_name1[0]
            departdetail.append(origin_info)
            
            ariveinfo = detail.find("div",{"class":"aa_flightList_col-4"})
            dest_time = ariveinfo.find("strong").text
            #print "dest_time",dest_time
            dest_code = ariveinfo.find("span").text
            #print "dest_code",dest_code
            dest_full_name = ariveinfo.find("span")['title']
            dest_full_name1 = dest_full_name.split(",")
            dest_info =  dest_time+" at "+dest_full_name1[0]
            arivedetail.append(dest_info)
            
            flight_num_div = detail.find("div",{"class":"aa_flightList_col-2"})
            flight_num =  flight_num_div.find("p")
            flight_num = flight_num.text
            table = detail.find("table")
            caption = table.find("caption").text
            if 'Operated by' in caption:
                caption = caption.replace('Operated by','').strip()
            operatedby.append(caption)
            detailtable = detail.find("tbody")
            trblock = detailtable.findAll("tr")
            aircraft = trblock[1].find("td").text

            if "Link opens in a new window" in aircraft:
                aircraft = aircraft.replace("Link opens in a new window","").strip()
            flightinfo = flight_num+" | "+aircraft
            flightdetail.append(flightinfo)
            
            extrainfo = trblock[2].findAll("td")
            cabin_name=''
            totaltime=''
            if len(extrainfo) > 1:
                totaltime = (extrainfo[0].text).strip()
                cabin_name = extrainfo[1].text
            else:
                if len(extrainfo) > 0:
                    cabin_name = extrainfo[0].text
            if totaltime != '':
                totaltime = totaltime
                cabin_name = cabin_name
            if flag > 0:
                flightno = flight_num
                departcode = origin_code
                departtime = origin_time
                flag = 0
            else:
                if stop < 1:
                    flightno = flight_num
                    departcode = origin_code
                    departtime = origin_time
                    
        if stop < 1:
            stoppage = 'NONSTOP'
        elif stop > 1:
            stoppage = str(stop)+' STOPS'
        else:
            stoppage = str(stop)+' STOP'
        maincabin = 0
        business = 0
        first = 0
        cabintype1 = ''
        cabintype2 = ''
        cabintype3 = ''
        flightno = "Flight "+str(flightno)
        departtime2 = (datetime.datetime.strptime(departtime, '%I:%M %p'))
        departtime1 = departtime2.strftime('%H:%M')
        dest_time2 = (datetime.datetime.strptime(dest_time, '%I:%M %p'))
        dest_time1 = dest_time2.strftime('%H:%M')
        if ':' in totaltime:
            totaltime1 = totaltime.split(':')
            totaltime = totaltime1[1]
        if 'Cabin:' in cabin_name:
            cabin_name = cabin_name.replace('Cabin:','').strip()
        if 'Economy' in cabin_name:
            maincabin = pricemile
            cabintype1 = cabin_name
        elif 'First' in cabin_name:
            first = pricemile
            cabintype3 = cabin_name
        else:
            if 'Business' in cabin_name:
                business = pricemile
                cabintype2 = cabin_name
        departdetails = '@'.join(departdetail)
        arivedetails = '@'.join(arivedetail)
        planedetails = '@'.join(flightdetail)
        operatedbytext='@'.join(operatedby)
        economy_fare_class = ''
        business_fare_class = ''
        fisrt_fare_class = ''
        #print "****************************************************************************************************"
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (flightno, str(searchid), stime, stoppage, "test", departcode, dest_code, departtime1, dest_time1, totaltime, str(maincabin),"0.0", str(business),"0.0", str(first),"0.0", cabintype1, cabintype2, cabintype3, "american airlines", departdetails, arivedetails, planedetails, operatedbytext,economy_fare_class,business_fare_class,fisrt_fare_class))
        db.commit()
        #transaction.commit()
        print "row inserted"
        
if __name__=='__main__':
    
    searchid = sys.argv[4]
    
    
    
    dt = datetime.datetime.strptime(sys.argv[3], '%Y/%m/%d')
    date = dt.strftime('%m/%d/%Y')
    selectdate = dt.strftime('X%m-X%d-%Y').replace('X0','X').replace('X','')
    month = dt.strftime("%b")
    day = dt.strftime("X%d").replace('X0','X').replace('X','')
    year = dt.strftime("%Y")

    print month,day,year
    url = "https://www.aa.com/reservation/awardFlightSearchAccess.do"
    
    display = Display(visible=0, size=(800, 600))
    display.start()
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    
    #driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)
    origin  = driver.find_element_by_id("awardFlightSearchForm.originAirport")
    origin.clear()
    origin.send_keys(sys.argv[1]) 
    destination = driver.find_element_by_id("awardFlightSearchForm.destinationAirport")

    destination.send_keys(sys.argv[2])


    # oneway  = driver.find_element_by_id("flightSearchForm.tripType.oneWay")
    oneway = driver.find_element_by_id("awardFlightSearchForm.tripType.oneWay")
    driver.execute_script("arguments[0].click();", oneway);

    exactdate = driver.find_element_by_id("awardFlightSearchForm.datesFlexible.false")
    driver.execute_script("arguments[0].click();", exactdate);



    select_month = Select(driver.find_element_by_id("awardFlightSearchForm.flightParams.flightDateParams.travelMonth"))
    select_month.select_by_visible_text(month)

    select_date = Select(driver.find_element_by_id("awardFlightSearchForm.flightParams.flightDateParams.travelDay"))
    #select_date.select_by_visible_text(str(day))
    for optn in select_date.options:
        val = optn.get_attribute('value')
        if val == day:
            optn.click()
            break
    #option = select_date.find_element_by_xpath('.//option[contains(@value, "'+str(day)+'")]')
    #option.click()

    submit = driver.find_element_by_id("awardFlightSearchForm.button.go")
    submit.click()

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "selectedPanel")))
    except:
        print "No flights found on american airlines"
        display.stop()
        driver.quit()
        return searchid
        
        
    time.sleep(2)
    html_page = driver.page_source
    pagecontent = BeautifulSoup(html_page)
    datadiv = pagecontent.find("div",{"id":"selectedPanel"})

    cabindiv = pagecontent.find("div",{"class","aa_awardsListBox"})
    cabinblock = cabindiv.find("ul")
    cabinlist = cabinblock.findAll("a")

    for link in cabinlist:
        is_available = link.text
        
        if "NotAvailable" not in is_available:
            cabin = link['href']
            cabin_ele = driver.find_element_by_xpath("//a[@href='" +cabin+ "']")
            driver.execute_script("arguments[0].click();", cabin_ele)
            time.sleep(2)
            html_page = driver.page_source
            pagecontent = BeautifulSoup(html_page)
            flightblock = pagecontent.find("div",{"id":"flightListBox"})
            data_container = flightblock.find("div",{"id":"flightListContainer"})
            flightcontainer = data_container.findAll("div",{"class":"aa_flightListContainer"})
            pagging = pagecontent.find("div",{"class":"aa_pageInation"})
            paginf_ul = pagging.find("ul",{"id":"pgNt"})
            paginglist = paginf_ul.findAll("a")
            scrapeFlight(data_container,searchid)
            if len(flightcontainer) > 9:
                for page_link in paginglist:
                    link_text = page_link.text
                    pageObj = driver.find_element_by_link_text(link_text)

                    pageObj.click()
                    time.sleep(1)
                    html_page1 = driver.page_source
                    html = BeautifulSoup(html_page)
                    data_container = html.find("div",{"id":"flightListContainer"})
                    scrapeFlight(data_container,searchid)
                    #print "++++++++++++++++++"+link_text+"+++++++++++++++++++++++++++++++++++"
                page1_Obj = driver.find_element_by_link_text("Page 1")
                print "page1_Obj", page1_Obj
                driver.execute_script("arguments[0].click();", page1_Obj);
                
    driver.quit()
    display.stop()
    return searchid