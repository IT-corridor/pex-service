from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from datetime import timedelta
import time
from datetime import date
import datetime
from django.db import connection,transaction

#from pyvirtualdisplay import Display
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pexproject.models import Flightdata,Flights_wego,Searchkey
import sys,os

cursor = connection.cursor()

def is_text_present(text):
    try:
        body = driver.find_element_by_id(text) 
        return 
    except:
        return False
    return text in body.text 

url ="http://www.delta.com/"

curdate = datetime.date.today() + datetime.timedelta(days=1)
date = sys.argv[3]
orgn = sys.argv[1]
dest = sys.argv[2]
searchid = sys.argv[4]
currentdatetime = datetime.datetime.now()
time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
print"======= delta=========="
print sys.argv
print"=======  end delta=========="

fromstation = []
depttime =[]
arivaltimelist=[]
deststn=[]
choice1=[]
choice2=[]
maincabin=[]
firstcabin=[]
stop=[]
layover=[]
flightno=[]

#display = Display(visible=0, size=(800, 600))
#display.start()
driver = webdriver.Firefox()
driver.get(url)
driver.implicitly_wait(40)

oneway = driver.find_element_by_id("oneWayBtn")
driver.execute_script("arguments[0].click();", oneway)

origin = driver.find_element_by_id("originCity")
origin.clear()
origin.send_keys(orgn)
destination = driver.find_element_by_id("destinationCity")
destination.send_keys(dest)


driver.find_element_by_id("departureDate").click()
driver.find_elements_by_css_selector("td[data-date='"+date+"']")[0].click()

driver.find_element_by_id("milesBtn").click()
driver.find_element_by_id("findFlightsSubmit").click()

test = is_text_present("showAll-footer")
if test != 0:
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "showAll-footer")))
    driver.find_element_by_link_text('Show All').click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
else:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
#driver.implicitly_wait(10)
html_page = driver.page_source
soup = BeautifulSoup(html_page)

datatable = soup.findAll("table",{"class":"fareDetails"})

for content in datatable:
    cabintype2 =''
    fare2 = ''
    timeblock = content.findAll("div",{"class":"flightDateTime"})
    for info in timeblock:
        temp = info.findAll("span")
        depature = temp[0].text
        part = depature[-2:]
        depature1 = depature.replace(part, "")
        depaturetime = depature1+" "+part
        test = (datetime.datetime.strptime(depaturetime,'%I:%M %p'))
        test1 = test.strftime('%H:%M')
        print test1
        depttime.append(test1)
        arival = temp[3].text
        apart =  arival[-2:]
        arival = arival.replace(apart, "")
        arivaltime = arival+" "+apart
        arivaltimelist.append(arivaltime)
        arivalformat = (datetime.datetime.strptime(arivaltime,'%I:%M %p'))
        arivalformat1 = arivalformat.strftime('%H:%M')
        duration = temp[4].text
        
    flite_route = content.findAll("div",{"class":"flightPathWrapper"})
    fltno = content.find("a",{"class":"helpIcon"}).text
    flightno.append(fltno)
    
    for route in flite_route:
        if route.find("div",{"class":"nonStopBtn"}):
            stp = "NONSTOP"
            stop.append(stp)
            lyover = ""
            layover.append(lyover)
            #print "nonstop"
        else:
            if route.find("div",{"class":"nStopBtn"}):
                stp = route.find("div",{"class":"nStopBtn"}).text
                stop.append(stp)
                #print route.find("div",{"class":"nStopBtn"}).text
                if route.find("div",{"class":"layOver"}):
                    lyover = route.find("div",{"class":"layOver"}).find("span").text
                else:
                    lyover=''
                #print route.find("div",{"class":"layOver"}).find("span").text
                #print route.find("div",{"class":"layovertoolTip"}).text
                layover.append(lyover)
        sourcestn = (route.find("div",{"class":"originCity"}).text)
        fromstation.append(sourcestn)
        destinationstn = (route.find("div",{"class":"destinationCity"}).text)
        deststn.append(destinationstn)
    if content.findAll("div",{"class":"priceHolder"}):
        fareblock = content.findAll("div",{"class":"priceHolder"})
        lenght = len(fareblock)
        fare1 =(fareblock[0].text)
        choice1.append(fare1)
        if lenght>1:
            fare2 = (fareblock[1].text)
            choice2.append(fare2)
    if content.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
        cabintype = content.findAll("div",{"class":"frmTxtHldr flightCabinClass"})
        clength = len(cabintype)
        cabintype1 = (cabintype[0].text)
        maincabin.append(cabintype1)
        if clength>1:
            cabintype2 = (cabintype[1].text)
            firstcabin.append(cabintype2)
    #queryset = Flightdata(flighno=fltno,searchkeyid=searchid,scrapetime=time,stoppage=stp,stoppage_station=lyover, origin=sourcestn,destination=destinationstn,departure=depature,arival=arival,maincabin=fare1,firstclass=fare2,cabintype1=cabintype1.strip(),cabintype2=cabintype2.strip()) 
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,firstclass,cabintype1,cabintype2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,searchid,time,stp,lyover,sourcestn,destinationstn,test1,arivalformat1,duration,fare1,fare2,cabintype1.strip(),cabintype2.strip()))
    transaction.commit()
    #queryset.save()
#display.stop()
driver.quit()
            
