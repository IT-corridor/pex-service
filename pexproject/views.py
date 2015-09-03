#!/usr/bin/env python
import os,sys
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q
#from django.template.context_processors import csrf
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from datetime import timedelta
#from datetime import datetime,date
import datetime
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from pexproject.models import Flightdata,Flights_wego,Searchkey
from subprocess import call
#import MySQLdb

#from test1.models import Register
from pexproject.form import LoginForm

def index(request):
    
    return  render_to_response('flightsearch/index.html', context_instance=RequestContext(request))
'''
def register(request):
    form = RegisterForm     
    if request.method == 'POST':
        form = RegisterForm(request.POST,request.FILES)        
        if form.is_valid():
          
            form.save()
            return render_to_response('flightsearch/index.html',{'RegisterForm': form} )
        else:
         return render_to_response('flightsearch/register.html',{'RegisterForm': form}  )
    else:
        return   render_to_response('flightsearch/register.html',{'RegisterForm': form})
'''
def login(request):
    form = LoginForm
    return render_to_response('flightsearch/login.html',{'LoginForm': form})

def search(request):
    #db = MySQLdb.connect(user='root', db='pex', passwd='root', host='localhost')
    #cursor = db.cursor()
    context = {}
    if request.method == "POST":
        if 'search' in request.REQUEST:
            mstring = []
            onestop = ''
            nonstop = ''
            econ = ''
            if 'nonstop' in request.REQUEST:
                nonstop = request.REQUEST['nonstop']
            if 'onestop' in request.REQUEST:
                onestop = request.REQUEST['onestop']
                print "one stop",onestop
            if 'cabintype1' in request.REQUEST:
                econ = request.REQUEST['cabintype1']
                #print econ
            record = Flightdata.objects.filter(Q(cabintype1__contains=econ),Q(stoppage__in=[nonstop,onestop]))
            print record
            #searchkey = request.GET.get('keyid', '')
            #searchdata = Searchkey.objects.filter(searchid=searchkey)
            searchdata =''
            filerkey = {nonstop:nonstop,onestop:onestop,econ:"Main Cabin"}

            return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata,'filterkey':filerkey},context_instance=RequestContext(request))
            print data
            exit()
            for key in request.POST.iterkeys():
                if key != "csrfmiddlewaretoken" and key != "buying_slider_min" and key != "search":
                    valuelist = request.POST[key]
                    print key
                    print valuelist
                    record = Flightdata.objects.filter(key=valuelist)
                    print record
                    #mstring.extend(['%s="%s"' % (key, valuelist)])
                    #print record
                '''
                if key != "csrfmiddlewaretoken" and key != "buying_slider_min" and key != "search":
                    valuelist = request.POST.getlist(key)
                    print valuelist
                    mstring.extend(['%s="%s"' % (key, val) for val in valuelist])
                    print "---------------"
            
            print querylist
            '''
            querylist = ','.join(mstring)
            print querylist
            #record = Flightdata.objects.filter(querylist)
            #print querylist
            #print ("select * from pexproject_flightdata where "+query)
            #cursor.execute("select * from pexproject_flightdata where "+query)
            #record = cursor.fetchall()
            searchdata =''
            record = Flightdata.objects.filter(stoppage="NONSTOP")
            print record.query
            return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata},context_instance=RequestContext(request))
            
    if request.is_ajax():
        context = {}
        orgn = request.REQUEST['fromMain'] #"Seattle, WA, US (SEA)"
        dest = request.REQUEST['toMain'] #"New York, NY, US (NYC - All Airports)"
        depart = request.REQUEST['deptdate']
        #print orgn,depart
        dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
        date = dt.strftime('%Y/%m/%d')
        searchdate = dt.strftime('%Y-%m-%d')        
        currentdatetime = datetime.datetime.now()
        time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        time1 = datetime.datetime.now()- timedelta(hours=4)
        time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
        print time1
        if time > time1:
            print time,time1
       
        searchkeyid=''
        obj = Searchkey.objects.filter(source=orgn,destination=dest,traveldate=searchdate,scrapetime__gte=time1)
        print len(obj)
        if len(obj) > 0:
            print "if block"
            for keyid in obj:
                seachkeyid = keyid.searchid
                print seachkeyid
                mimetype = 'application/json'
                
                return HttpResponse(seachkeyid, mimetype)
        else:
            print "else"
            searchdata = Searchkey(source=orgn,destination=dest,traveldate=dt,scrapetime=time) 
            searchdata.save()
            searchkeyid = searchdata.searchid 
            print searchkeyid
            call(["python", "delta.py",orgn,dest,date,str(searchkeyid)])
            mimetype = 'application/json'
            return HttpResponse(searchkeyid, mimetype)
            
    
    
            #return render_to_response('flightsearch/searchresult.html', {'temp':record, 'searchdate':date, 'sname':sourcename,'dname':destname},context_instance=RequestContext(request))
        

def get_airport(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        airports = Flights_wego.objects.filter(name__icontains = q )[:20]
        results = []
        for airportdata in airports:
            airport_json = {}
            airport_json['id'] = airportdata.id
            airport_json['label'] = airportdata.name+" ("+airportdata.code+" )"
            airport_json['value'] = airportdata.code
            results.append(airport_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def searchLoading(request):
    context = {}
    if request.method == "POST":
        orgn = request.REQUEST['fromMain'] #"Seattle, WA, US (SEA)"
        dest = request.REQUEST['toMain'] #"New York, NY, US (NYC - All Airports)"
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
        print len(record)
        return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata},context_instance=RequestContext(request)) 
    
        

	
# Create your views here.
