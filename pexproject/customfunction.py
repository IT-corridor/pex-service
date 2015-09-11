from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
import datetime
from datetime import timedelta
import time
import MySQLdb
from datetime import date
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.db import connection,transaction
from pyvirtualdisplay import Display
import socket
import urllib

def united(origin,destination,searchdate):
    cursor = connection.cursor()
    
    url = "http://www.united.com/web/en-US/default.aspx?root=1"
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Firefox()
    
    curdate = datetime.date.today() + datetime.timedelta(days=1)
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%m/%d/%Y')
    currentdatetime = datetime.datetime.now()
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    time1 = datetime.datetime.now()- timedelta(hours=4)
    time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
    #searchkeyid=''
    print date
    driver.get(url)
    driver.implicitly_wait(20)
    oneway = driver.find_element_by_id("ctl00_ContentInfo_Booking1_rdoSearchType2")
    driver.execute_script("arguments[0].click();", oneway)
    
    
    #driver.find_elements_by_css_selector("input[type='radio'][value='rdoSearchType2']")[0].click()
    
    #test = driver.find_elements_by_css_selector("label[for='ctl00_ContentInfo_Booking1_rdoSearchType2']")[0]
    #test.send_keys(Keys.ENTER)
    inputElement = driver.find_element_by_id("ctl00_ContentInfo_Booking1_Destination_txtDestination")
    inputElement.clear()
    inputElement.send_keys(destination)#"Seattle, WA, US (SEA)")
    
    inputElement1 = driver.find_element_by_id("ctl00_ContentInfo_Booking1_Origin_txtOrigin")
    inputElement1.clear()
    inputElement1.send_keys(origin)   #"New York, NY, US (NYC - All Airports)")
    
    driver.find_element_by_id("ctl00_ContentInfo_Booking1_SearchBy_rdosearchby3").click()
    inputElement2 = driver.find_element_by_id("ctl00_ContentInfo_Booking1_DepDateTime_Depdate_txtDptDate")
    inputElement2.clear()
    inputElement2.send_keys(date)
    
    inputElement2.send_keys(Keys.ENTER)
    
    driver.implicitly_wait(20)
    html_page = driver.page_source
    
    soup = BeautifulSoup(html_page)
    table = soup.findAll("table",{"class":"rewardResults"})
    i= 1
    searchid =1
    dursn =''
    fltn0 =''
    source=''
    Destination = ''
    arivalformat1 = ''
    test1 =''
    
    for trs in table:
        trblock = trs.findAll("tr")
        for tds in trblock:
            tdblock = tds.findAll("td",{"class":"tdRewardPrice"})
            #print tdblock
            tdsegblock = tds.findAll("td",{"class":"tdSegmentBlock"})
            for datablock in tdsegblock:
                contenttr = datablock.findAll("tr")
                for content in contenttr:
                    
                    if content.find("td",{"class":"tdDepart"}):
                        print "==================================================================================="
                        departinfo = content.find("td",{"class":"tdDepart"})
                        info = departinfo.findAll("div")
                        depart = info[1].text
                        depart = depart.replace(".","")
                        #print depart
                        test = (datetime.datetime.strptime(depart,'%I:%M %p'))
                        test1 = test.strftime('%H:%M')
                        print test1
                        #print test1
                        #print "depart Date  : ",info[2].text
                        source = info[3].text
                        print source
                        
                        arivinfo = content.find("td",{"class":"tdArrive"})
                        ainfo = arivinfo.findAll("div")
                        arival = ainfo[1].text
                        arival1 = arival.replace(".","").strip()
                        if '+' in arival1:
                            arival1 = arival1.split("+")
                            arival1 = arival1[0].strip()
                        #print arival1
                        arivalformat = (datetime.datetime.strptime(arival1,'%I:%M %p'))
                        #print arivalformat
                        arivalformat1 = arivalformat.strftime('%H:%M')
                        print arivalformat1 
                        #print "Arive Date  : ",info[2].text
                        Destination = ainfo[3].text
                        print Destination
                      
                        duration = content.find("td",{"class":"tdTrvlTime"})
                        traveltime = duration.findAll("span")
                        for timetext in traveltime:
                            print timetext.text
                        flightdetail = content.find("td",{"class":"tdSegmentDtl"})
                        fltno = flightdetail.find("div").text
                        print fltno
                    #duration = ''
                    #for flno in flightdetail:
                        #print flno.find("div").text
                        '''
                        if duration.find("span",{"class":"PHead"}):
                            print "duration :"
                            totaltime = duration.find("span",{"class":"PHead"}).text
                            print totaltime
                        else:
                            print duration.find("span").text
                        '''
                    #print content.find("td",{"class":"tdSegmentDtl"}).text
            j = 0
            k = 0
            cabin = []
            fare1 = ''
            fare2 = ''
            fare3 = ''
            cabintype1 = ''
            cabintype2 = ''
            cabintype3 = ''
            for mileage in tdblock:
                j = j+1
                k = k+1
                miles = mileage.find("div",{"class":"divMileage"}).text
                if mileage.find("div",{"class":"divTaxBreakdownA"}):
                    extramile = mileage.find("div",{"class":"divTaxBreakdownA"}).text
                    miles = miles+" "+extramile[1].strip()
                else:
                    notavl = mileage.find("div",{"class":"divNA"}).text
                    miles = notavl.strip()
                print miles
                cabin.append(miles)
                if j == 2:
                    cabinval = "|".join(cabin)
                    if k == 2:
                        fare1 = cabinval
                        cabintype1 = "Main Cabin"
                        print fare1,cabintype1
                    elif k == 4:
                        fare2 = cabinval
                        canibtype2 = "Business"
                        print fare2,cabintype2
                    else:
                        if k== 6:
                            fare3 = cabinval
                            cabintype3 = "first two row"
                            print fare3,cabintype3
                    
                        
                    print j
                    j=0
                    cabin =[]
            #cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,origin,destination,departure,arival,duration,maincabin,firstclass,cabintype1,cabintype2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,str(searchid),time,source,Destination,test1,arivalformat1,dursn,fare1,fare2,cabintype1,cabintype2))
            #print cursor.query 
            transaction.commit()
            print "row inserted"
                    
            i = i+1
            
            
            
   
    display.stop()
    driver.quit()
    return i
        
