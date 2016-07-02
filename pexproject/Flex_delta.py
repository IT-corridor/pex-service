import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import datetime
from datetime import timedelta
import time
import MySQLdb
import re
import customfunction
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pyvirtualdisplay import Display
import json
 

def flex_delta(src,dest,date,searchkey,cabin):
    db = customfunction.dbconnection()
    cursor = db.cursor()
    db.set_character_set('utf8')
    
    sdate = datetime.datetime.strptime(date, '%m/%d/%Y')
    storeDate = sdate.strftime("%Y-%m-%d")
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    try:
        url = "http://www.delta.com/air-shopping/calendar.action"
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver = webdriver.Chrome()
        driver.get(url)
        flexClass = ''
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "originCity")))
        time.sleep(2)
    
        milebtn = driver.find_element_by_xpath('//div[@class="toggle-container top-toggle"]/label[2]')
        triptype = driver.find_element_by_xpath('//label[@for="oneWay"]')
        triptype.click()
        #exit()
    
        origin = driver.find_element_by_id("originCity")
        origin.clear()
        origin.send_keys(src)
        
        #print "origin attribute",origin.get_attribute('value')
        destination = driver.find_element_by_id("destinationCity")
        destination.clear()
        destination.send_keys(dest)
        ddate = driver.find_element_by_id("departureDateVisible")
        ddate.send_keys(str(date))
        #milebtn.click()
    
        
        cabinclass = driver.find_element_by_id("economy-button")
        #print cabinclass
        driver.execute_script("return arguments[0].click();", cabinclass)
        cabin_element = ''
        if cabin == 'maincabin':
            flexClass = "economyflex"
            cabin_element = driver.find_element_by_id("ui-id-5")
        else:
            cabin_element = driver.find_element_by_id("ui-id-7")
            flexClass = "businessflex"
        print cabin_element
        
        #business = driver.find_element_by_id("ui-id-5")
        time.sleep(1)
        cabin_element.click()
        time.sleep(1)
        driver.execute_script("return arguments[0].click();", milebtn)
        
        
        #driver.execute_script("return arguments[0].click();", business)
        #exit()
        #driver.execute_script("document.getElementById('economy-button').setAttribute('aria-activedescendant', 'ui-id-6')");
        #driver.execute_script("return arguments[0]")
        #aria-activedescendant="ui-id-6"
        #cabinclass.click()
        time.sleep(2)
        #driver.find_element_by_xpath("//select[@id='economy']/option[@value='firstBusiness']").click()
        
        values_string = []
        driver.find_element_by_id("btnCalendar").send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "revenueCalData")))
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"xml")
        cal_table = soup.find("table",{"id":"revenueCalData"})
        dataTr = cal_table.findAll("tr",{"class":"dataRow"})
    
        for n in range(0,len(dataTr)):
            tdData = dataTr[n].findAll("td")
            for m in range(0,len(tdData)):
                dateValue = tdData[m].find("div",{"class":"calCellHeader topBarOdd"})
                content = tdData[m].find("div",{"class":"awardcalCellContent"})
                if content:
                    data = content.text
                    flex = ''
                    source = ''
                    dest1 = ''
                    orgndate2 = ''
                    destdate2 = ''
                    if "NOT AVAILABLE" in data:
                        print "Flight not available"
                    else:
                        destdate = tdData[m]['data-destinationdate']
                        destdate1 = datetime.datetime.strptime(destdate, '%m/%d/%Y')
                        destdate2 = destdate1.strftime("%Y-%m-%d")
                        
                        orgndate = tdData[m]['data-origindate']
                        orgndate1 = datetime.datetime.strptime(orgndate, '%m/%d/%Y')
                        orgndate2 = orgndate1.strftime("%Y-%m-%d")
                        source = tdData[m]['data-origincode']
                        dest1 = tdData[m]['data-destinationcode']
                        if 'LOWEST' in data:
                            flex = 'saver'
                    values_string.append((str(stime),str(searchkey),src,dest,str(storeDate),str(orgndate2),flex,"delta"))
        #print "INSERT INTO pexproject_flexibledatesearch (scrapertime,searchkey,source,destination,journey,flexdate,"+flexClass+") VALUES (%s,%s,%s,%s,%s,%s,%s);", values_string    
        cursor.executemany ("INSERT INTO pexproject_flexibledatesearch (scrapertime,searchkey,source,destination,journey,flexdate,"+flexClass+",datasource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);", values_string)
        db.commit()
    except:
        "something wrong"
    display.stop()
    driver.quit()
                
if __name__=='__main__':
    
    orgn = sys.argv[1]
    dest = sys.argv[2]
    searchdate = sys.argv[3]
    searchid = sys.argv[4]
    cabin = sys.argv[5]
    
    
    flex_delta(orgn,dest,searchdate,searchid,cabin)







