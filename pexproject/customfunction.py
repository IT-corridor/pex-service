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

def united(origin,destination,searchdate,searchkey):
    '''
    db = MySQLdb.connect(host="localhost", 
                     user="pex",           
                      passwd="pex@1234",        
                      db="pex")
    cursor=db.cursor()
    '''
    cursor = connection.cursor()
    url = "http://www.united.com/web/en-US/default.aspx?root=1"
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Firefox()
    dt = datetime.datetime.strptime(searchdate, '%Y/%m/%d')
    date = dt.strftime('%m/%d/%Y')
    #curdate = datetime.date.today() + datetime.timedelta(days=10)
    #date = curdate.strftime('%m/%d/%Y')
    currentdatetime = datetime.datetime.now()
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    #print date
    driver.get(url)
    driver.implicitly_wait(20)
    oneway = driver.find_element_by_id("ctl00_ContentInfo_Booking1_rdoSearchType2")
    driver.execute_script("arguments[0].click();", oneway)


    #driver.find_elements_by_css_selector("input[type='radio'][value='rdoSearchType2']")[0].click()

    #test = driver.find_elements_by_css_selector("label[for='ctl00_ContentInfo_Booking1_rdoSearchType2']")[0]
    #test.send_keys(Keys.ENTER)
    inputElement = driver.find_element_by_id("ctl00_ContentInfo_Booking1_Destination_txtDestination")
    inputElement.clear()
    inputElement.send_keys(destination)

    inputElement1 = driver.find_element_by_id("ctl00_ContentInfo_Booking1_Origin_txtOrigin")
    inputElement1.clear()
    inputElement1.send_keys(origin)

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
    fltno =''
    searchid = searchkey
    fltno =''
    source=''
    Destination = ''
    arivalformat1 = ''
    test1 =''
    for trs in table:
        trblock = trs.findAll("tr")
        for tds in trblock:
            tdsegblock = tds.findAll("td",{"class":"tdSegmentBlock"})
            for datablock in tdsegblock:
                stop = 0
                contenttr = datablock.findAll("tr")
                #========= chnageing on 16/9/2015=============================
                origininfo = contenttr[0]
                if origininfo:
                    if origininfo.find("td",{"class":"tdDepart"}):
                        departinfo = origininfo.find("td",{"class":"tdDepart"})
                        info = departinfo.findAll("div")
                        depart = info[1].text
                        depart = depart.replace(".","")
                        test = (datetime.datetime.strptime(depart,'%I:%M %p'))
                        test1 = test.strftime('%H:%M')
                        #print "depart Date  : ",info[2].text
                        source = info[3].text
                        flightdetail = origininfo.find("td",{"class":"tdSegmentDtl"})
                        fltno = flightdetail.find("div").text
                        print fltno
                        
                    
                
                #========== end===============================================
                
                for content in contenttr:
                    if content.find("td",{"class":"tdDepart"}):
                        stop = stop+1
                        print "==================================================================================="
                        """
                        departinfo = content.find("td",{"class":"tdDepart"})
                        info = departinfo.findAll("div")
                        depart = info[1].text
                        depart = depart.replace(".","")
                        test = (datetime.datetime.strptime(depart,'%I:%M %p'))
                        test1 = test.strftime('%H:%M')
                        #print "depart Date  : ",info[2].text
                        source = info[3].text
                        """
                        arivinfo = content.find("td",{"class":"tdArrive"})
                        ainfo = arivinfo.findAll("div")
                        arival = ainfo[1].text
                        arival1 = arival.replace(".","").strip()
                        if '+' in arival1:
                            arival1 = arival1.split("+")
                            arival1 = arival1[0].strip()
                        arivalformat = (datetime.datetime.strptime(arival1,'%I:%M %p'))
                        arivalformat1 = arivalformat.strftime('%H:%M')
                        Destination = ainfo[3].text
                      
                        duration = content.find("td",{"class":"tdTrvlTime"})
                        if duration.find("span",{"class":"PHead"}):
                            totaltime = duration.find("span",{"class":"PHead"}).text
                            print totaltime
                        traveltime = duration.findAll("span")
                        for timetext in traveltime:
                            print timetext.text
                        """
                        flightdetail = content.find("td",{"class":"tdSegmentDtl"})
                        fltno = flightdetail.find("div").text
                        print fltno
                        """
                    #duration = ''
                    #for flno in flightdetail:
                        #print flno.find("div").text
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
                tdblock = tds.findAll("td",{"class":"tdRewardPrice"})
                for mileage in tdblock:
                    j = j+1
                    k = k+1
                    
                    miles = mileage.find("div",{"class":"divMileage"}).text
                    if mileage.find("div",{"class":"divTaxBreakdownA"}):
                        extramile = mileage.find("div",{"class":"divTaxBreakdownA"}).text
                        extramile = extramile.split("and")
                        miles = miles+" "+extramile[1].strip()
                    else:
                        notavl = mileage.find("div",{"class":"divNA"}).text
                        miles = notavl.strip()
                        
                    if miles != "NotAvailable":
                        cabin.append(miles)
                    else:
                        cabin.append('')
                    #print "K val =",k
                    if j == 2:
                        #cabinval = "|".join(cabin)
                        if k == 2:
                            if cabin[0]:
                                fare1 = cabin[0]
                            else:
                                fare1 = cabin[1]
                            cabintype1 = "Main Cabin"
                            cabin =[]
                            #print cabintype1,fare1
                           
                        if k == 4:
                            if cabin[0]:
                                fare2 = cabin[0]
                            else:
                                fare2 = cabin[1]
                            canibtype2 = "Business"
                            cabin =[]
                            #print cabintype2,fare2
                           
                        if k == 6:
                            if cabin[0]:
                                fare3 = cabin[0]
                            else:
                                fare3 = cabin[1]
                                cabintype3 = "first two row"
                                cabin =[]
                        j=0
                        
                print canibtype2
                if stop-1 < 1:
                    stopage = "NONSTOP"
                elif stop-1 == 1:
                    stopage = "1 STOP"
                else:
                    if stop-1 == 2:
                        stopage = "2 STOPS"
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,firstclass,cabintype1,cabintype2,datasource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,str(searchid),time,stopage,"test",source,Destination,test1,arivalformat1,totaltime,fare1,fare2,cabintype1,canibtype2,"united"))
                #db.commit()
                transaction.commit()
                print "row inserted"
    display.stop
    driver.quit()
    return searchid
    
        
