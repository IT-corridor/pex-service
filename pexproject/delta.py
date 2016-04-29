#!/usr/bin/env python 
import os, sys
from subprocess import call
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import _strptime
import MySQLdb
import re
from selenium.webdriver.common.proxy import *
from datetime import date
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from django.db import connection, transaction
import customfunction  
import threading
from threading import Thread
import Queue
from pyvirtualdisplay import Display
import socket
import urllib
#from pexproject import settings




def delta(orgn, dest, searchdate, searchkey):
    #return searchkey
    db = customfunction.dbconnection()
    cursor = db.cursor()
    db.set_character_set('utf8')
    print "searchdate",searchdate
    #cursor = connection.cursor()
    url = "http://www.delta.com/"   
    searchid = str(searchkey)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
  
    display = Display(visible=0, size=(800, 600))
    display.start()
    '''
    chromedriver = "/usr/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080) '''
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(1)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "oneWayBtn")))
        oneway = driver.find_element_by_id('oneWayBtn')
        #oneway.click()
        driver.execute_script("arguments[0].click();", oneway)
        origin = driver.find_element_by_id("originCity")
        origin.clear()
        origin.send_keys(orgn.strip())
        destination = driver.find_element_by_id("destinationCity")
        destination.send_keys(dest.strip())
        ddate = driver.find_element_by_id("departureDate")  
        driver.execute_script("document.getElementById('departureDate').setAttribute('value', '"+str(searchdate)+"')")
        milebtn = driver.find_element_by_id("milesBtn")
        milebtn.click()
        driver.find_element_by_id("findFlightsSubmit").send_keys(Keys.ENTER)
        
    except:
        print "before data page"
        driver.quit()
        return searchkey
    soup = ''
    try:
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
        print "data found"
    except:
        print "exception"
        display.stop()
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag","flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
    	db.commit()
        return searchkey
    
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "showAll")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
        sleep(1)
	
    except:
        print "single page data"
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
    try:
        html_page = driver.page_source
    	soup = BeautifulSoup(html_page,"lxml")
        pricehead = soup.find("tr",{"class":"tblHeadUp"})
    	pricecol = pricehead.findAll("label",{"class":["nextGenHiddenFieldWindow","tblHeadBigtext"]})
    	datatable = soup.findAll("table", {"class":"fareDetails"})
    except:
	display.stop()
        driver.quit()
        cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
        db.commit()
        return searchkey

    
    
    fare_flag = 0
    soup2 = ''
    #try:
    detailids = soup.findAll("div", {"class":"detailLinkHldr"})
    for detlid in detailids:
        detailid = detlid['id']
        detailid_ele = driver.find_element_by_id(detailid)
        driver.execute_script("document.getElementById('"+detailid+"').click()")
        time.sleep(.02)
	time.sleep(0.05)
    	#page = driver.page_source
    	#soup2 = BeautifulSoup(page)
    #except:
        '''
    	print "something wrong"
    	driver.quit()
    	cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
        print "delta flag inserted"
    	db.commit()
        #transaction.commit()
    	return searchkey'''
    n = 0
    
    htmlpage = driver.page_source
    soup2 = BeautifulSoup(htmlpage,"lxml")
    cabin_ele = driver.find_elements_by_xpath("//*[@class='miscCabin']")
    values_string = []
    recordcount = 1
    for content in datatable:
        datatable1 = soup2.findAll("table", {"class":"fareDetails"})
        k = 0
        departdetails = []
        arrivedetails = []
        planedetails = []
        operatedbytext = ''
        efare_class = []
        bfare_class=[]
        ffare_class = []
        
        for cnt in datatable1:
            if cnt.find("div", {"class":"detailsRow" }) and k == n:
                detailblk = cnt.findAll("div", {"class":"detailsRow"})
                for tmp in detailblk:
                    spaninfo = tmp.findAll("p")
                    depart_string = (spaninfo[0].text).replace('DEPARTS', '')
                    if "Opens in a new popup" in depart_string:
                        depart_string = depart_string.replace('Opens in a new popup','')
                    departdetails.append(depart_string)
                    arive_string = (spaninfo[1].text.replace('ARRIVES', ''))
                    if "Opens in a new popup" in arive_string:
                        arive_string = arive_string.replace('Opens in a new popup','')
                    arrivedetails.append(arive_string)
                    flight_duration = spaninfo[2].text.replace('FLIGHT', '')
                    flight_duration1 = flight_duration.split("|")
                    flight_no = flight_duration1[0].strip()
                    plane_duration = flight_duration1[1].strip()
                    extra_string = ''
                    aircraft =''
                    aircraft1 = spaninfo[3].text.replace('PLANE', '')
                    if "-" in aircraft1:
                        aircraft2 = aircraft1.split('-')
                        aircraft = aircraft2[0]
                        if len(aircraft2)>2:
                            aircraft = aircraft+"-"+aircraft2[1]
                    planedetailinfo = flight_no + " | " + aircraft + " (" + plane_duration + ")"
                    planedetails.append(planedetailinfo)
            k = k + 1
        n = n + 1
        business = ''
        tds = content.findAll("td")
        cabinhead = ''
        detailsblock = tds[0]
        
        if  len(pricecol) > 1:
            if tds[1]:
                economy = tds[1]
            if  'Business' in pricecol[1].text or 'First' in pricecol[1].text:
                cabinhead = pricecol[1].text
                if len(tds) > 2:
                    business = tds[2]
            else:
                if len(pricecol) > 2:
                    cabinhead = pricecol[2].text
                    if 'Business' in cabinhead or 'First' in pricecol[2].text:
                        cabinhead = pricecol[2].text
                        if len(tds) > 3:
                             business = tds[3]
                     
        else:
            if len(pricecol) < 2:
                cabinhead = pricecol[0].text
                if 'Business' in cabinhead or 'First' in cabinhead:
                    business = tds[1]
                    economy = ''
                else:
                    if 'Main Cabin' in cabinhead:
                       economy =  tds[1]
                       business = ''
        cabintype2 = ''
        fare2 = 0
        timeblock = detailsblock.findAll("div", {"class":"flightDateTime"})
        operatordiv = detailsblock.find("div", {"class":"summaryMessageWrapper"})
        if operatordiv.find("span",{"class":"odIndex_1"}):
            operator = operatordiv.find("span",{"class":"odIndex_1"}).text
            operatedbytext = operator
        for info in timeblock:
            temp = info.findAll("span")
            depature = temp[0].text
            part = depature[-2:]
            depature1 = depature.replace(part, "")
            depaturetime = depature1 + " " + part
            test = (datetime.datetime.strptime(depaturetime, '%I:%M %p'))
            test1 = test.strftime('%H:%M')
            arival = temp[3].text
            apart = arival[-2:]
            arival = arival.replace(apart, "")
            arivaltime = arival + " " + apart
            arivalformat = (datetime.datetime.strptime(arivaltime, '%I:%M %p'))
            arivalformat1 = arivalformat.strftime('%H:%M')
            duration = temp[4].text
            
        flite_route = detailsblock.findAll("div", {"class":"flightPathWrapper"})
        fltno = detailsblock.find("a", {"class":"helpIcon"}).text
        for route in flite_route:
            if route.find("div", {"class":"nonStopBtn"}):
                stp = "NONSTOP"
                lyover = ""
            else:
                if route.find("div", {"class":"nStopBtn"}):
                    stp = route.find("div", {"class":"nStopBtn"}).text
                    if route.find("div", {"class":"layOver"}):
                        lyover = route.find("div", {"class":"layOver"}).text
                    elif route.find("div", {"class":"originCityVia2Stops"}):
                        multistop = route.findAll("div", {"class":"originCityVia2Stops"})
                        stoplist = []
                        for sp in multistop:
                            stoplist.append(sp.text)
                        lyover = "|".join(stoplist)
                    else:
                        lyover = ''
            sourcestn = (route.find("div", {"class":"originCity"}).text)
            destinationstn = (route.find("div", {"class":"destinationCity"}).text)
        economytax = 0
        businesstax = 0
        fare3 = 0
        firsttax = 0
        cabintype3 = ''
        fare1 = 0 
        cabintype1 = ''
        fare2 = 0 
        cabintype2 = ''
        if economy:
            if economy.findAll("div", {"class":"priceHolder"}):
                fare1 = economy.find("span", {"class":"tblCntBigTxt mileage"}).text
                fare1 = fare1.replace(",", "")
                if economy.find("span", {"class":"tblCntSmallTxt"}):
                    economytax1 = economy.find("span", {"class":"tblCntSmallTxt"}).text
                    ecotax = re.findall("\d+.\d+", economytax1)
                    economytax = ecotax[0]
                if economy.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype1 = economy.find("div", {"class":"frmTxtHldr flightCabinClass"}).text

                    if 'Main Cabin' in cabintype1:
                        cabintype1 = cabintype1.replace('Main Cabin', 'Economy')
                    if 'Multiple Cabins' in cabintype1:
                        #hover_element =  economy.find("div", {"class":"frmTxtHldr flightCabinClass"})
                        #hover_link = hover_element.find("a")['class']
			try:
                            hover = ActionChains(driver).move_to_element(cabin_ele[fare_flag])
                            hover.perform()
			except:
			    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag"))
    			    db.commit()
			    driver.quit()
                            return searchkey
                        time.sleep(.2)
                        html_page2 = driver.page_source
                        soup = BeautifulSoup(html_page2)
                        hover_string = soup.find("tr",{"class","cabinClass_fly_bodyWrap"})
                        alltd = hover_string.findAll("td",{"class":"subheaderMsg"})
                        for tdtext in alltd:
                            #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                            fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                            efare_class.append(fare_class)
			    fare_flag = fare_flag+1                        
                        
                        
                        cabintype1 = cabintype1.replace('Multiple Cabins', 'Economy')
            else:
                fare1 = 0 
                cabintype1 = ''
            
        if business:
            alltd = ''
            if business.findAll("div", {"class":"priceHolder"}):
                fare2 = business.find("span", {"class":"tblCntBigTxt mileage"}).text
                fare2 = fare2.replace(",", "")
                if business.find("span", {"class":"tblCntSmallTxt"}):
                    businesstax1 = business.find("span", {"class":"tblCntSmallTxt"}).text
                    buss_tax = re.findall("\d+.\d+", businesstax1)
                    businesstax = buss_tax[0]  
                       
                if business.findAll("div", {"class":"frmTxtHldr flightCabinClass"}):
                    cabintype2 = business.find("div", {"class":"frmTxtHldr flightCabinClass"}).text
                    #print "cabintype2" ,cabintype2
                    if 'Multiple Cabins' in cabintype2:
                        #print "fare_flag",fare_flag
                        hover = ActionChains(driver).move_to_element(cabin_ele[fare_flag])
                        hover.perform()
                        #get_html  = ele.get_attribute("innerHTML")
                        time.sleep(.5)
                        #time.sleep(.2)
                        html_page2 = driver.page_source
                        soup = BeautifulSoup(html_page2)
                        hover_string = soup.find("tr",{"class","cabinClass_fly_bodyWrap"})
                        alltd = hover_string.findAll("td",{"class":"subheaderMsg"})
                        fare_flag = fare_flag+1
                    
            else:
                fare2 = 0 
                cabintype2 = ''
            
            if 'First' in cabintype2 or ('First' in cabinhead and 'Business' not in cabinhead):
                fare3 = fare2
                fare2 = 0
                cabintype3 = cabintype2
                firsttax = businesstax
                cabintype2 = ''
                if alltd:
                    for tdtext in alltd:
                        #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                        fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                        ffare_class.append(fare_class)
                        #print "--------------------------- ----------------------------------------"
            else:
                cabintype2 = "Business"
                if alltd:
                    for tdtext in alltd:
                        #print "flt no ",tdtext.find("div",{"class":"cabinContainerLeft"}).text
                        fare_class = tdtext.find("div",{"class":"cabinContainerRight"}).text
                        bfare_class.append(fare_class)

        deptdetail = '@'.join(departdetails)
        arivedetail = '@'.join(arrivedetails)
        planetext = '@'.join(planedetails)
        efare_class_text = '@'.join(efare_class)
        bfare_class_text = '@'.join(bfare_class)
        ffare_class_text = '@'.join(ffare_class)
        recordcount = recordcount+1
        values_string.append((fltno, searchid, stime, stp, lyover, sourcestn, destinationstn, test1, arivalformat1, duration, str(fare1), str(economytax), str(fare2), str(businesstax), str(fare3), str(firsttax), cabintype1.strip(), cabintype2.strip(), cabintype3, "delta", deptdetail, arivedetail, planetext, operatedbytext,efare_class_text,bfare_class_text,ffare_class_text))
        if recordcount > 50:
            cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
            db.commit()
            values_string =[]
            recordcount = 1
            print "data inserted"

    if len(values_string) > 0:
        cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
        db.commit()
    
    driver.quit()
    display.stop()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag", "flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "delta", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    #transaction.commit()
    return searchkey


if __name__=='__main__':
    delta(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[5])
    #etihad(sys.argv[6],sys.argv[7],date,sys.argv[5],sys.argv[8])
