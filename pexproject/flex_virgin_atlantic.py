import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import MySQLdb
import customfunction
from pyvirtualdisplay import Display

def flex_virgin_atlantic(src,dest,searchdate,searchkey):
    db = customfunction.dbconnection()
    cursor = db.cursor()
    db.set_character_set('utf8')
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    url ="http://www.virgin-atlantic.com/us/en/book-your-travel/book-your-flight/flight-search-calendar.html?departure="+src+"&arrival="+dest+"&departureDate="+str(searchdate)+"&adult=1&classType=10&classTypeReturn=10&findFlights=go&isreturn=no&jsEnabled=true&search_type=redeemMiles&bookingPanelLocation=Undefined"
    driver.get(url)
    
    sdate = datetime.datetime.strptime(searchdate, '%d/%m/%Y')
    storeDate = sdate.strftime("%Y-%m-%d")
    
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    
    html_page = driver.page_source
    pagecontent = BeautifulSoup(html_page,"lxml")

    calenderTable = pagecontent.find("table")
    trdata = calenderTable.findAll("tr")
    values_string = []
    for c in range(0,len(trdata)):
        tdlist = trdata[c].findAll("td",{"class":["available","requested"]})
        #print len(tdlist)
        if len(tdlist)>0:
            for d in range(0,len(tdlist)):
                ecoflex = ''
                bussflex = ''
                flexdate = tdlist[d].find(attrs={"name" : "departureDate"})
                if flexdate : 
                    flexdate = flexdate['value']
                
                    #['value']
                    flexdate2 = datetime.datetime.strptime(flexdate, '%d/%m/%Y')
                    flexdate1 = flexdate2.strftime("%Y-%m-%d")
                    class_list = tdlist[d].find("span",{"class":["availableClasses","availableClasses2","availableClasses3"]})
                    avilableClass = class_list.findAll("span")
                    for cabin in avilableClass:
                        if 'economy' in cabin['class'][0]:
                            ecoflex = "saver"
                        elif 'premEconomy' in cabin['class'][0] or 'upperclass' in cabin['class'][0]:
                            bussflex = "saver"
                            
                    
                    values_string.append((str(stime),str(searchkey),src,dest,str(storeDate),str(flexdate1),ecoflex,bussflex,"virgin_atlantic"))
    
                
    #print values_string        
    print "*********************************************************************************\n\n"
    cursor.executemany ("INSERT INTO pexproject_flexibledatesearch (scrapertime,searchkey,source,destination,journey,flexdate,economyflex,businessflex,datasource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
    db.commit()
    display.stop()
    driver.quit()

if __name__=='__main__':
    
    sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
    orgn = sys.argv[1]
    dest = sys.argv[2]
    searchdate = sys.argv[3]
    date1 = datetime.datetime.strptime(searchdate, '%m/%d/%Y')
    searchdate = date1.strftime("%d/%m/%Y")
    searchid = sys.argv[4]
    flex_virgin_atlantic(orgn,dest,searchdate,searchid)
     
