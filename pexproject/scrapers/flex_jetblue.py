import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import MySQLdb
import customfunction
import json

#mainurl = "http://www.jetblue.com/bestfarefinder/#/"
def flex_blue(origin,dest,date,searchkey):
    db = customfunction.dbconnection()
    cursor = db.cursor()
    db.set_character_set('utf8')
    sdate = datetime.datetime.strptime(date, '%m/%d/%Y')
    storeDate = sdate.strftime("%Y-%m-%d")
    month = sdate.strftime("%B")
    year = sdate.strftime("%Y")
    month = month.upper()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "http://www.jetblue.com/bestfarefinder/CalendarData.aspx?month="+month+"+"+str(year)+"&type=POINTS&direction=outbound&tripType=RT&origin="+origin+"&destination="+dest+"&adult=1&child=0&infant=0"
    ret_url = "http://www.jetblue.com/bestfarefinder/CalendarData.aspx?month="+month+"+"+str(year)+"&type=POINTS&direction=inbound&tripType=RT&origin="+origin+"&destination="+dest+"&adult=1&child=0&infant=0"
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)  
    driver.get(url)

    html_page = driver.page_source
    soup = BeautifulSoup(html_page,"xml")
    values_string = []
    calenderData = soup.find("pre").text
    calJson = json.loads(calenderData)
    mainData = calJson['calendarData']

    lowest = []
    temp = 0
    for i in range(0,len(mainData)):
        price = mainData[i]["amount"]
        date = mainData[i]["date"]
        if i == 0:
            temp = price
        if temp > 0 and price <= temp:
            if price < temp:
                lowest = []
                lowest.append(date)
            else:
                lowest.append(date)
            temp = price
            
    for i in range(0,len(mainData)):
        date = mainData[i]["date"]
        #print date
        flex = ''
        if  date not in lowest:
            flex = ''
        else:
            flex = 'saver'
        values_string.append((str(stime),str(searchkey),origin,dest,str(storeDate),str(date),flex,flex,flex,"jetblue"))
    cursor.executemany ("INSERT INTO pexproject_flexibledatesearch (scrapertime,searchkey,source,destination,journey,flexdate,economyflex,businessflex,firstflex,datasource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
    db.commit()
    driver.quit()

if __name__=='__main__':
    origin = sys.argv[1]
    dest = sys.argv[2]
    date = sys.argv[3]
    searchid = sys.argv[4]
    flex_blue(origin,dest,date,searchid)
    
        
    

