#!/usr/bin/env python
import os, sys
import selenium
import datetime
import time
import re
import urllib
import codecs

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from datetime import date

DEBUG = False
DEBUG = True
DEV_LOCAL = False
# DEV_LOCAL = True

if DEV_LOCAL:
    import pdb

if not DEV_LOCAL:
    import customfunction


def get_airport_code(airport):
    airport = airport.split(' (')
    return airport[1][:3]


def storeFlag(searchkey,stime):
    db = customfunction.dbconnection()
    cursor = db.cursor()
    cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby,economy_code,business_code,first_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", ("flag", str(searchkey), stime, "flag", "test", "flag", "flag","flag", "0","0", "0","0", "0", "0", "flag", "flag", "flag", "virgin_atlantic", "flag", "flag", "flag", "flag", "flag", "flag", "flag"))
    db.commit()
    

def virgin_atlantic(origin, dest, searchdate,returndate, searchkey,returnkey):
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
    driver.set_window_size(1120, 1080)
    # sys.stdout=codecs.getwriter('utf-8')(sys.stdout)
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    # try:
    if not DEV_LOCAL:
        db = customfunction.dbconnection()
        cursor = db.cursor()
    dt = datetime.datetime.strptime(searchdate.strip(), '%m/%d/%Y')
    date = dt.strftime('%d/%m/%Y')
    if returndate != 'None' and returndate:
        dt1 = datetime.datetime.strptime(returndate, '%m/%d/%Y')
        retdate = dt1.strftime('%d/%m/%Y') 
    if returndate != 'None' and returndate:
        url = "http://www.virgin-atlantic.com/us/en/book-your-travel/book-your-flight/flight-search-results.html?departure="+origin+"&arrival="+dest+"&adult=1&departureDate="+str(date)+"&search_type=redeemMiles&classType=10&classTypeReturn=10&bookingPanelLocation=Undefined&isreturn=yes&returnDate="+str(retdate)
    else:
        url = "http://www.virgin-atlantic.com/us/en/book-your-travel/book-your-flight/flight-search-results.html?departure="+origin+"&arrival="+dest+"&adult=1&departureDate="+str(date)+"&search_type=redeemMiles&classType=10&classTypeReturn=10&bookingPanelLocation=BookYourFlight&isreturn=no"

    # print url, '@@@@@@@@@@@@@22'    

    driver.get(url)
    time.sleep(2)
    html_page = driver.page_source

    soup = BeautifulSoup(html_page,"lxml")
    # except:
    #     print "before data page"
    #     print "searchkey",searchkey
    #     print "returnkey",returnkey
    #     if not DEV_LOCAL:
    #         storeFlag(searchkey,stime)
    #         if returnkey:
    #             storeFlag(returnkey,stime)
    #             print "return key stored"
    #     driver.quit()
    #     return

    def virgindata(tbody,keyid):
        recordcount = 1
        value_string = []
        try :
            if tbody.findAll("tr",{"class":"directRoute "}):
                trbody = tbody.findAll("tr",{"class":"directRoute "})
            else:
                if tbody.findAll("tr",{"class":"indirectRoute "}):
                    trbody = tbody.findAll("tr",{"class":"indirectRoute "})
        except:
            return keyid
        for row in trbody:
            econo = 0
            econotax = 0
            business = 0
            busstax = 0
            first = 0
            firsttax = 0  
            stp = ''
            lyover= ''
            details = row.find("td",{"class":"flightSearchDetails"})    # error
            economy = ''
            #============= price block ================================================================
            if row.find("td",{"class":"cellOption economy  hasLowestCostMessage"}):
                economy = row.find("td",{"class":"cellOption economy  hasLowestCostMessage"})
            if economy == '' and row.find("td",{"class":"cellOption economy "}):
                economy = row.find("td",{"class":"cellOption economy "})
            if economy:
                "--------------economy--------------------------------"
                economy_price = economy.find("span",{"class":"price"})
                econprice1 = economy_price.text
                
                econprice = re.findall("\d+.\d+", econprice1)
                if len(econprice) > 0:
                    econo = econprice[0]
                    if ',' in econo:
                        econo = econo.replace(',','')
                if len(econprice) > 1:
                    if "USD" not in econprice1:
                        cprice = 0
                        if ',' in econprice[1]:
                            cprice = econprice[1].replace(',','')
                        else:
                            cprice = econprice[1]
                        currency_symbol = (re.findall("[a-zA-Z]+", econprice1))
                        currencychange = urllib.urlopen("https://www.exchangerate-api.com/%s/%s/%f?k=e002a7b64cabe2535b57f764"%(currency_symbol[1],"USD",float(cprice)))
                        chaged_result = currencychange.read()
                        econotax = chaged_result
                    else:
                        econotax = econprice[1]
            pre_economy =''
            if row.find("td",{"class":"cellOption premEconomy "}):
                pre_economy = row.find("td",{"class":"cellOption premEconomy "})
            if pre_economy == '' and row.find("td",{"class":"cellOption premEconomy  hasLowestCostMessage"}):
                pre_economy = row.find("td",{"class":"cellOption premEconomy  hasLowestCostMessage"})
            if pre_economy:
                "--------------pre economy--------------------------------"
                pre_economy_price = pre_economy.find("span",{"class":"price"})
                pre_economy = pre_economy_price.text
                #print pre_economy
                pre_econo_price = re.findall("\d+.\d+", pre_economy)
                if len(pre_econo_price) > 0:
                    business = pre_econo_price[0]
                    if ',' in business:
                        business = business.replace(',','')
                if len(pre_econo_price) > 1:
                    if "USD" not in pre_economy:
                        eprice = 0
                        if ',' in pre_econo_price[1]:
                            eprice = pre_econo_price[1].replace(',','')
                        else:
                            eprice = pre_econo_price[1]
                        currency_symbol = (re.findall("[a-zA-Z]+", pre_economy))
                        currencychange = urllib.urlopen("https://www.exchangerate-api.com/%s/%s/%f?k=e002a7b64cabe2535b57f764"%(currency_symbol[1],"USD",float(eprice)))
                        chaged_result = currencychange.read()
                        busstax = chaged_result
                    else:
                        busstax = pre_econo_price[1]
                    #print "pre_econotax",busstax
            upper_class = ''
            if row.find("td",{"class":"cellOption upperclass  last"}):
                "--------------upper class--------------------------------"
                upper_class = row.find("td",{"class":"cellOption upperclass  last"})
            else:
                if row.find("td",{"class":"cellOption upperclass  last hasLowestCostMessage"}):
                    upper_class = row.find("td",{"class":"cellOption upperclass  last hasLowestCostMessage"})
            if upper_class:
                upper_class_price = upper_class.find("span",{"class":"price"})
                upperclass_price = upper_class_price.text
                upperprice = re.findall("\d+.\d+", upperclass_price)
                if len(upperprice) > 0:
                    first = upperprice[0]
                    if ',' in first:
                        first = first.replace(',','')
                if len(upperprice) > 1:
                    if "USD" not in upperclass_price:
                        uprice = 0
                        if ',' in upperprice[1]:
                            uprice = upperprice[1].replace(',','')
                        else:
                            uprice = upperprice[1]
                        currency_symbol = (re.findall("[a-zA-Z]+", upperclass_price))
                        currencychange = urllib.urlopen("https://www.exchangerate-api.com/%s/%s/%f?k=e002a7b64cabe2535b57f764"%(currency_symbol[1],"USD",float(uprice)))
                        chaged_result = currencychange.read()
                        firsttax = chaged_result
                    else:
                        firsttax = upperprice[1]
                    
            #============================= end price block =========================================================
            sourcestn = ''
            destinationstn=''
            depttime= ''
            arivaltime=''
            total_duration = ''
            heading = details.find("ul")
            depart = heading.find("li",{"class":"depart"})
            departinfo = depart.findAll("p")
            if len(departinfo) > 0:
                depttime = departinfo[0].text
                departfrom1 = departinfo[1].text
                if 'from' in departfrom1:
                    departfrom = (departfrom1.replace('from','')).strip()
                    if '(' in departfrom:
                        departfrom1 = departfrom.split('(')
                        sourcestn = departfrom1[1].replace(')','')
            arive = heading.find("li",{"class":"arrive"})
            ariveinfo = arive.findAll("p")
            if len(ariveinfo) > 0:
                arivaltime = ariveinfo[0].text
                if '+' in arivaltime:
                    arivaltimesplit = arivaltime.split('+')
                    arivaltime = arivaltimesplit[0]
                ariveat1 = ariveinfo[1].text
                if 'at' in ariveat1:
                    ariveat = (ariveat1.replace('at','')).strip()
                    if '(' in ariveat:
                        ariveat2 = ariveat.split('(')
                        destinationstn = ariveat2[1].replace(')','')
            stop = heading.find("li",{"class":"stops"})
            durations = heading.find("li",{"class":"duration"})
            stoppage = stop.text
            if '0' in stoppage:
                stp = "NONSTOP"
            elif '1' in stoppage:
                stp = "1 STOP"
            elif '2' in stoppage:
                stp = "2 STOPS"
            else:
                if '3' in stoppage:
                    stp = "3 STOPS"
            total_duration = (durations.text).strip()
            if 'Duration' in total_duration:
                total_duration = (total_duration.replace('Duration','')).strip()
            '''
            #print "total_duration",total_duration
            operator = details.find("dl",{"class":"operator"})
            operatedby = (operator.find("dd").text).strip()
            print "operatedby",operatedby
            '''
            #===============================details block====================================================
            details_block = details.find("div",{"class":"tooltip"})
            details_tr = details_block.findAll("tr")
            counter = 0
            departdlist = []
            arivelist = []
            planelist = []
            operatedby = []
            departdetails = ''
            arivedetails = ''
            planedetails = ''
            operatedbytext = ''
            while (counter < len(details_tr)):
                #print "counter",counter
                from_to = details_tr[counter].find("td",{"class":"flightDetails"})
                operator = from_to.find("span",{"class":"operator"}).text
                operatedby.append(operator)
                #print "operator",operator
                from_to1 = from_to.find("span",{"class":"flightFromTo"}).text
                departing_from = ''
                ariving_at = ''
                departing_date =''
                detaildetptime = ''
                detailarivetime = ''
                deptextraday = ''
                ariveextraday = ''
                if 'to' in from_to1:
                    from_to1 = from_to1.split('to')
                    departing_from = from_to1[0]
                    if '\n' in departing_from:
                        departing_from1 = departing_from.split("\n")
                        departing_from = departing_from1[0].strip()+" "+departing_from1[1].strip()
                    #print "departing_from",departing_from
                    ariving_at = from_to1[1]
                    if '\n' in ariving_at:
                        ariving_at1 = ariving_at.split("\n")
                        ariving_at = ariving_at1[0].strip()+" "+ariving_at1[1].strip()
                    #print "ariving_at",ariving_at
                departing_date = from_to.find("span",{"class":"fullDate"}).text
                if 'Departing' in departing_date:
                    departing_date = (departing_date.replace('Departing','')).strip()
                counter = counter+1 
                departtime = details_tr[counter].find("td",{"class":"departs"})
                fl_dept_time = departtime.find("span",{"class":"flightDeparts"})
                detaildetptime = fl_dept_time.text
                if departtime.find("span",{"class":"extraDays"}):
                    extradeptdate = departtime.find("span",{"class":"extraDays"})
                    deptextraday = extradeptdate.text
                    nod = re.findall("\d+.\d+", deptextraday)
                    #print "nod",nod
                    if "+1" in deptextraday:
                        deptextraday = "+1 day"
                    elif "+2" in deptextraday:
                        deptextraday = "+2 day"
                    else:
                        if "+3" in deptextraday:
                            deptextraday = "+3 day"
                arivetime = details_tr[counter].find("td",{"class":"arrives"})
                fl_arive_time = arivetime.find("span",{"class":"flightArrives"})
                detailarivetime = fl_arive_time.text
                if arivetime.find("span",{"class":"extraDays"}):
                    extra_ariveday = arivetime.find("span",{"class":"extraDays"})
                    ariveextraday = extra_ariveday.text
                    
                duration = details_tr[counter].find("td",{"class":"duration"})
                fl_duration1 = duration.find("span",{"class":"flightDuration"})
                fl_duration = (fl_duration1.text).strip()
                fl_flightno =''
                planeno = ''
                flight_no = details_tr[1].find("td",{"class":"number"})
                fl_flightno1 = flight_no.find("span",{"class":"flightNumber"})
                planeno = (''.join(fl_flightno1.find('br').next_siblings))
                fl_flightno = (fl_flightno1.text).replace(planeno,'')

                departinfo_time = departing_date+" "+detaildetptime
                departinfo_time = datetime.datetime.strptime(departinfo_time, '%A %d %B %Y %H:%M')
                departinfo_time = departinfo_time.strftime('%Y/%m/%d %H:%M')

                airport_ = customfunction.get_airport_detail(get_airport_code(departing_from)) or departing_from
                deptdetail = departinfo_time+" | from "+airport_
                departdlist.append(deptdetail)

                departinfo_time = departing_date+" "+detailarivetime
                departinfo_time = datetime.datetime.strptime(departinfo_time, '%A %d %B %Y %H:%M')
                departinfo_time = departinfo_time.strftime('%Y/%m/%d %H:%M')

                airport_ = customfunction.get_airport_detail(get_airport_code(ariving_at)) or ariving_at
                arivedetail = departinfo_time+" | at "+airport_                
                arivelist.append(arivedetail)
                planetext = fl_flightno+" | "+planeno+" ("+fl_duration+")" 
                planelist.append(planetext)
                counter = counter+1
            departdetails = '@'.join(departdlist)
            arivedetails = '@'.join(arivelist)
            planedetails = ('@'.join(planelist)).strip()
            operatedbytext = '@'.join(operatedby)  
            
            value_string.append((fl_flightno, str(keyid), stime, stp, lyover, sourcestn, destinationstn, depttime, arivaltime,total_duration, str(econo), str(econotax), str(business), str(busstax), str(first), str(firsttax),"Economy","Business","First", "virgin_atlantic", departdetails, arivedetails, planedetails, operatedbytext))
            recordcount = recordcount+1
            if recordcount > 50:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",value_string )
                db.commit()
                value_string = []
                recordcount = 1
        if len(value_string) > 0:
            if not DEV_LOCAL:
                cursor.executemany ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,maintax,firstclass,firsttax,business,businesstax,cabintype1,cabintype2,cabintype3,datasource,departdetails,arivedetails,planedetails,operatedby) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",value_string )
                db.commit()
            # print value_string
        #driver.quit()
            
    tbody = soup.findAll("tbody",{"class":"flightStatusTbody"})
    if searchkey:
        if len(tbody) > 0:
            virgindata(tbody[0],searchkey)
        if not DEV_LOCAL:    
            storeFlag(searchkey,stime)
    if returnkey:
        if len(tbody)> 1 :
            virgindata(tbody[1],returnkey)
        if not DEV_LOCAL:    
            storeFlag(returnkey,stime)
    driver.quit()
    return searchkey


if __name__=='__main__':
    virgin_atlantic(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    # if DEV_LOCAL:
    #     pdb.set_trace()    
    # virgin_atlantic('LON', 'LAX', '10/18/2016', '', '1231', '')