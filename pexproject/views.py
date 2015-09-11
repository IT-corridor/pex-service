#!/usr/bin/env python
import os,sys
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q
from datetime import timedelta
import subprocess
from types import *
import datetime

from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from pexproject.models import Flightdata,Airports,Searchkey
from subprocess import call
#import MySQLdb
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from datetime import timedelta
import time
from datetime import date
from django.db import connection,transaction
import operator


#from pyvirtualdisplay import Display
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import customfunction

from pexproject.form import LoginForm

def index(request):
    
    return  render_to_response('flightsearch/index.html', context_instance=RequestContext(request))


def login(request):
    form = LoginForm
    return render_to_response('flightsearch/login.html',{'LoginForm': form})

def search(request):
    context = {}
    if request.method == "POST":
        if 'search' in request.REQUEST:
            querylist =''
            join=''
            economy=''
            list=''
            multicabin=''
            businesslist=''
            
            if 'stoppage' in request.POST:
                list = request.POST.getlist('stoppage')
                if len(list)>1:
                    querylist = querylist+join+"stoppage IN ('"+"','".join(list)+"')"
                    join = ' AND '
                else:
                    if(len(list) > 0):
                        querylist = querylist+join+"stoppage = '"+list[0]+"'"
                        join = ' AND '
                
            if 'cabintype2' in request.POST:
                businesslist = request.POST.getlist('cabintype2')
                if len(businesslist)>1:
                    querylist = querylist+join+" cabintype2 LIKE ('%"+"%','%".join(businesslist)+"%')"
                    join = ' AND '
                else:
                    if(len(businesslist) > 0):
                        print "aaya"
                        querylist = querylist+join+" cabintype2 LIKE '"+businesslist[0]+"%%'"
                        join = ' AND ' 
               
                
            if 'cabintype1' in request.POST:
                economy = request.REQUEST['cabintype1']
                
                if economy != '':
                    querylist = querylist+join+" cabintype1 LIKE '%%"+economy+"%%'" 
                    join = ' AND '
            if 'searchkeyval' in request.POST:
                searchkey = request.REQUEST['searchkeyval']
                querylist = querylist+join+" searchkeyid = "+searchkey
                join = ' AND '
            if 'depaturemin' in request.POST:
                 depttime = request.REQUEST['depaturemin']
                 deptformat = (datetime.datetime.strptime(depttime,'%I:%M %p'))
                 deptformat1 = deptformat.strftime('%H:%M:%S')
                 querylist = querylist+join+" departure >= '"+deptformat1+"'"
                 join = ' AND '
            if 'depaturemax' in request.POST:
                deptmaxtime = request.REQUEST['depaturemax']
                #print deptmaxtime
                deptmaxformat = (datetime.datetime.strptime(deptmaxtime,'%I:%M %p'))
                deptmaxformat1 = deptmaxformat.strftime('%H:%M:%S')
                querylist = querylist+join+" departure <= '"+deptmaxformat1+"'"
                join = ' AND '
            if 'arivalmin' in request.POST:
                 arivtime = request.REQUEST['arivalmin']
                 arivformat = (datetime.datetime.strptime(arivtime,'%I:%M %p'))
                 arivformat1 = arivformat.strftime('%H:%M:%S')
                 querylist = querylist+join+" arival >= '"+arivformat1+"'"
                 join = ' AND '
            if 'arivalmax' in request.POST:
                arivtmaxtime = request.REQUEST['arivalmax']
                #print deptmaxtime
                arivtmaxformat = (datetime.datetime.strptime(arivtmaxtime,'%I:%M %p'))
                arivtmaxformat1 = arivtmaxformat.strftime('%H:%M:%S')
                querylist = querylist+join+" arival <= '"+arivtmaxformat1+"'"
                join = ' AND '
            
            records = Flightdata.objects.raw('select * from pexproject_flightdata where '+querylist+' order by departure ASC')
            searchdata = Searchkey.objects.filter(searchid=searchkey)
            timeinfo = {'maxdept':deptmaxtime,'mindept':depttime,'minarival':arivtime,'maxarival':arivtmaxtime}#Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` where "+querylist+" order by departure ASC")
            filerkey =  {'stoppage':list,'economy':economy, 'deptmin':depttime,'deptmax': deptmaxtime, 'business':businesslist}
            return render_to_response('flightsearch/searchresult.html',{'data':records,'search':searchdata,'filterkey':filerkey,'timedata':timeinfo},context_instance=RequestContext(request))
            
    if request.is_ajax():
        context = {}
        cursor = connection.cursor()
        orgn = request.REQUEST['fromMain'] 
        dest = request.REQUEST['toMain'] 
        orgncode = orgn.partition('(')[-1].rpartition(')')[0]
        destcode = dest.partition('(')[-1].rpartition(')')[0]
        print orgncode,destcode
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
        date = dt.strftime('%Y/%m/%d')
        unitedres = customfunction.united(orgn,dest,date)

        searchdate = dt.strftime('%Y-%m-%d')        
        currentdatetime = datetime.datetime.now()
        time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        time1 = datetime.datetime.now()- timedelta(hours=4)
        time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
        searchkeyid=''
        obj = Searchkey.objects.filter(source=orgn,destination=dest,traveldate=searchdate,scrapetime__gte=time1)
        if len(obj) > 0:
            for keyid in obj:
                seachkeyid = keyid.searchid
                print seachkeyid
                mimetype = 'application/json'
                
                return HttpResponse(seachkeyid, mimetype)
        else:
            searchdata = Searchkey(source=orgn,destination=dest,traveldate=dt,scrapetime=time) 
            searchdata.save()
            searchkeyid = searchdata.searchid 
            cursor = connection.cursor()
            
            url ="http://www.delta.com/"

            
            curdate = datetime.date.today() + datetime.timedelta(days=1)
            #date = date
            #orgn = request.REQUEST['fromMain'] 
            #dest = request.REQUEST['deptdate']
            searchid = str(searchkeyid)
            currentdatetime = datetime.datetime.now()
            time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
            #display = Display(visible=0, size=(800, 600))
            #display.start()
            driver = webdriver.Firefox()
            driver.implicitly_wait(40)
            
            driver.get(url)
            oneway = driver.find_element_by_id("oneWayBtn")
            driver.execute_script("arguments[0].click();", oneway)
            
            origin = driver.find_element_by_id("originCity")
            origin.clear()
            origin.send_keys(orgncode.strip())
            destination = driver.find_element_by_id("destinationCity")
            destination.send_keys(destcode.strip())
            
            
            driver.find_element_by_id("departureDate").click()
            driver.find_elements_by_css_selector("td[data-date='"+date+"']")[0].click()
            
            driver.find_element_by_id("milesBtn").click()
            driver.find_element_by_id("findFlightsSubmit").click()
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
            except:
                driver.quit()
                mimetype = 'application/json'
                return HttpResponse(searchkeyid, mimetype)
            
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "showAll-footer")))
                driver.find_element_by_link_text('Show All').click()
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_20")))
            except:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "fareRowContainer_0")))
            #driver.implicitly_wait(10)
            html_page = driver.page_source
            soup = BeautifulSoup(html_page)
            datatable = soup.findAll("table",{"class":"fareDetails"})
            
            for content in datatable:
                tds = content.findAll("td")
                detailsblock = tds[0]
                economy = tds[1]
                if len(tds) > 2:
                    business = tds[2]
                else:
                    business = ''

                cabintype2 =''
                fare2 = ''
                timeblock = detailsblock.findAll("div",{"class":"flightDateTime"})
                for info in timeblock:
                    temp = info.findAll("span")
                    depature = temp[0].text
                    part = depature[-2:]
                    depature1 = depature.replace(part, "")
                    depaturetime = depature1+" "+part
                    print depaturetime
                    test = (datetime.datetime.strptime(depaturetime,'%I:%M %p'))
                    test1 = test.strftime('%H:%M')
                    print test1
                    #depttime.append(test1)
                    arival = temp[3].text
                    apart =  arival[-2:]
                    arival = arival.replace(apart, "")
                    arivaltime = arival+" "+apart
                    #arivaltimelist.append(arivaltime)
                    arivalformat = (datetime.datetime.strptime(arivaltime,'%I:%M %p'))
                    arivalformat1 = arivalformat.strftime('%H:%M')
                    duration = temp[4].text
                    
                flite_route = detailsblock.findAll("div",{"class":"flightPathWrapper"})
                fltno = detailsblock.find("a",{"class":"helpIcon"}).text
                #flightno.append(fltno)
                print 
                for route in flite_route:
                    if route.find("div",{"class":"nonStopBtn"}):
                        stp = "NONSTOP"
                        #stop.append(stp)
                        lyover = ""
                        #layover.append(lyover)
                        #print "nonstop"
                    else:
                        if route.find("div",{"class":"nStopBtn"}):
                            stp = route.find("div",{"class":"nStopBtn"}).text
                            #stop.append(stp)
                            #print route.find("div",{"class":"nStopBtn"}).text
                            if route.find("div",{"class":"layOver"}):
                                lyover = route.find("div",{"class":"layOver"}).find("span").text
                            else:
                                lyover=''
                            #print route.find("div",{"class":"layOver"}).find("span").text
                            #print route.find("div",{"class":"layovertoolTip"}).text
                            #layover.append(lyover)
                    sourcestn = (route.find("div",{"class":"originCity"}).text)
                    #fromstation.append(sourcestn)
                    destinationstn = (route.find("div",{"class":"destinationCity"}).text)
                    #deststn.append(destinationstn)
                print "-------------------- Economy--------------------------------------------------"
                if economy.findAll("div",{"class":"priceHolder"}):
                    fare1 = economy.find("div",{"class":"priceHolder"}).text
                    print fare1
                    #lenght = len(fareblock)
                    #print fareblock[0].text
                    if economy.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                        cabintype1 = economy.find("div",{"class":"frmTxtHldr flightCabinClass"}).text
                else:
                    fare1 = economy.find("span",{"class":"ntAvail"}).text
                    cabintype1 =''
                    print fare1
                    
                print "-------------------- Business --------------------------------------------------"
                if business:

                    if business.findAll("div",{"class":"priceHolder"}):
                        fare2 = business.find("div",{"class":"priceHolder"}).text
                        print fare2
                        #lenght = len(fareblock)
                        #print fareblock[0].text
                        if business.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                            cabintype2 = business.find("div",{"class":"frmTxtHldr flightCabinClass"}).text
                            
                    else:
                        fare2 = business.find("span",{"class":"ntAvail"}).text
                        cabintype2 = ''
                        print fare2

                print "last line"
                #queryset = Flightdata(flighno=fltno,searchkeyid=searchid,scrapetime=time,stoppage=stp,stoppage_station=lyover, origin=sourcestn,destination=destinationstn,departure=depature,arival=arival,maincabin=fare1,firstclass=fare2,cabintype1=cabintype1.strip(),cabintype2=cabintype2.strip()) 
                cursor.execute ("INSERT INTO pexproject_flightdata (flighno,searchkeyid,scrapetime,stoppage,stoppage_station,origin,destination,departure,arival,duration,maincabin,firstclass,cabintype1,cabintype2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (fltno,searchid,time,stp,lyover,sourcestn,destinationstn,test1,arivalformat1,duration,fare1,fare2,cabintype1.strip(),cabintype2.strip()))
                transaction.commit()
                print "data inserted"
                #queryset.save()

            driver.quit()
            mimetype = 'application/json'
            return HttpResponse(searchkeyid, mimetype)
            
    
    
            #return render_to_response('flightsearch/searchresult.html', {'temp':record, 'searchdate':date, 'sname':sourcename,'dname':destname},context_instance=RequestContext(request))
        

def get_airport(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        airport = Airports.objects.filter(cityName__icontains = q )[:20]
        results = []
        for airportdata in airport:
            airport_json = {}
            airport_json['id'] = airportdata.airport_id
            airport_json['label'] = airportdata.cityName+", "+airportdata.cityCode+", "+airportdata.countryCode +"  ("+airportdata.code+" )"
            airport_json['value'] = airportdata.cityName+", "+airportdata.cityCode+", "+airportdata.countryCode +"  ("+airportdata.code+" )"
            results.append(airport_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def searchLoading(request):
    context = {}
    if request.method == "POST":
        orgn = request.REQUEST['fromMain'] 
        dest = request.REQUEST['toMain'] 
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
        date = dt.strftime('%Y/%m/%d')     
        data ={}
        
        return render_to_response('flightsearch/searchloading.html', {'searchdate':date, 'sname':orgn,'dname':dest},context_instance=RequestContext(request))
    else:
        return render_to_response('flightsearch/index.html')
    
def getsearchresult(request):
    context = {}
    if request.GET.get('keyid', ''):
        searchkey = request.GET.get('keyid', '')
        record = Flightdata.objects.filter(searchkeyid=searchkey)
        searchdata = Searchkey.objects.filter(searchid=searchkey)
        for s in searchdata:
            source = s.source
            destination = s.destination
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        
        for row in timerecord:
            
            timeinfo = {'maxdept':row.maxdept,'mindept':row.mindept,'minarival':row.minarival,'maxarival':row.maxarival}
        
        if len(record)>0: 
            return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata,'timedata':timeinfo},context_instance=RequestContext(request)) 
        else:

            msg = "Sorry, NO flight found  from "+source+" To "+destination+".  Please search for another date or city !"

            return  render_to_response('flightsearch/index.html',{'message':msg}, context_instance=RequestContext(request))
            
        

	
# Create your views here.
