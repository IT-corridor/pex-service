#!/usr/bin/env python
import os,sys
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q,Count,Min
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

from datetime import timedelta
import time
from datetime import date
from django.db import connection,transaction
import operator

import customfunction

from pexproject.form import LoginForm
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)

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
            list1=''
            multicabin=''
            cabinlist=''
            if 'stoppage' in request.POST:
                list = request.POST.getlist('stoppage')
                if len(list)>1:
                    querylist = querylist+join+"stoppage IN ('"+"','".join(list)+"')"
                    join = ' AND '
                else:
                    if(len(list) > 0):
                        querylist = querylist+join+"stoppage = '"+list[0]+"'"
                        join = ' AND '
            if 'airlines' in request.POST:
                list1 = request.POST.getlist('airlines')
                if len(list1)>1:
                    querylist = querylist+join+"datasource IN ('"+"','".join(list1)+"')"
                    join = ' AND '
                else:
                    if(len(list1) > 0):
                        querylist = querylist+join+"datasource = '"+list1[0]+"'"
                        join = ' AND '
            if 'cabin' in request.POST:
                cabinlist = request.POST.getlist('cabin')
                if len(cabinlist)>1:
                    querylist = querylist+join+"('"+"' != '' or '".join(cabinlist)+"' != '')"
                    
                    join = ' AND '
                else:
                    if(len(cabinlist) > 0):
                        querylist = querylist+join+cabinlist[0]+" != ''"
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
                 
            minprice = request.POST['price']
            tax = request.POST['tax']
            action = request.POST['action']
            passenger = request.REQUEST['passenger']
            returnkey = ''
            selectedrow=''
            if 'returnkey' in request.POST:
                returnkey = request.POST['returnkey']
            if 'rowid' in request.POST:
                recordid = request.REQUEST['rowid']
                selectedrow = Flightdata.objects.get(pk=recordid)
            records = Flightdata.objects.raw('select * from pexproject_flightdata where '+querylist+' order by departure ASC')
            print records.query
            searchdata = Searchkey.objects.filter(searchid=searchkey)
            timeinfo = {'maxdept':deptmaxtime,'mindept':depttime,'minarival':arivtime,'maxarival':arivtmaxtime}#Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` where "+querylist+" order by departure ASC")
            filerkey =  {'stoppage':list,'cabin':cabinlist, 'deptmin':depttime,'deptmax': deptmaxtime,'datasource':list1}
            return render_to_response('flightsearch/searchresult.html',{'returndata':returnkey,'action':action,'minprice':minprice,'tax':tax,'data':records,'search':searchdata,'selectedrow':selectedrow,'filterkey':filerkey,'timedata':timeinfo,'passenger':passenger},context_instance=RequestContext(request))
            
    if request.is_ajax():
        context = {}
        cursor = connection.cursor()
        returndate = request.REQUEST['returndate']
        if request.REQUEST['rndtripkey']:
            roundtrip = 1
        else:
            roundtrip = 0
        dt1 =''
        searchdate1 = ''
        if returndate:
            dt1 = datetime.datetime.strptime(returndate, '%Y/%m/%d')
            date1 = dt1.strftime('%m/%d/%Y')
            searchdate1 = dt1.strftime('%Y-%m-%d')
        triptype =  request.REQUEST['triptype']
        
        orgn = request.REQUEST['fromMain'] 
        dest = request.REQUEST['toMain'] 
        orgncode = orgn.partition('(')[-1].rpartition(')')[0]
        destcode = dest.partition('(')[-1].rpartition(')')[0]
        #print orgncode,destcode
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
        date = dt.strftime('%m/%d/%Y')
        searchdate = dt.strftime('%Y-%m-%d')        
        currentdatetime = datetime.datetime.now()
        time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        time1 = datetime.datetime.now()- timedelta(hours=4)
        time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
        searchkeyid=''
        returnkey =''
        Searchkey.objects.filter(scrapetime__lte=time1).delete()
        Flightdata.objects.filter(scrapetime__lte=time1).delete()
        if searchdate1:
            obj = Searchkey.objects.filter(source=orgn,destination=dest,traveldate=searchdate,scrapetime__gte=time1)
            returnobj = Searchkey.objects.filter(source=dest,destination=orgn,traveldate=searchdate1,scrapetime__gte=time1)
            if len(returnobj) > 0:
                for retkey in returnobj:
                     returnkey = retkey.searchid
            else:
                searchdata = Searchkey(source=dest,destination=orgn,traveldate=dt1,scrapetime=time,isreturnkey=0)
                searchdata.save()
                returnkey = searchdata.searchid
                retdeltares = customfunction.delta(destcode,orgncode,date1,returnkey)
                retrecordkey = customfunction.united(dest,orgn,returndate,returnkey)
                
        else:
            obj = Searchkey.objects.filter(source=orgn,destination=dest,traveldate=searchdate,scrapetime__gte=time1)
        if len(obj) > 0:
            for keyid in obj:
                searchkeyid = keyid.searchid
        else:
            if dt1:
                searchdata = Searchkey(source=orgn,destination=dest,traveldate=dt,returndate=dt1,scrapetime=time) 
            else:
                searchdata = Searchkey(source=orgn,destination=dest,traveldate=dt,scrapetime=time,isreturnkey=roundtrip)
            searchdata.save()
            searchkeyid = searchdata.searchid 
            cursor = connection.cursor()
            deltares = customfunction.delta(orgncode,destcode,date,searchkeyid)
            recordkey = customfunction.united(orgn,dest,depart,searchkeyid)
            returnkey = ''
            if returndate:
                retunobj = Searchkey.objects.filter(source=dest,destination=orgn,traveldate=searchdate1,scrapetime__gte=time1)
                if len(retunobj) > 0:
                    for keyid in retunobj:
                        returnkey = keyid.searchid
                else:
                    searchdata = Searchkey(source=dest,destination=orgn,traveldate=dt1,scrapetime=time,isreturnkey=0)
                    searchdata.save()
                    returnkey = searchdata.searchid
                    retdeltares = customfunction.delta(orgncode,destcode,date,returnkey)
                    retrecordkey = customfunction.united(orgn,dest,depart,returnkey)
                
        mimetype = 'application/json'
        results = []
        results.append(searchkeyid)
        if returnkey:
            results.append(returnkey)
        data = json.dumps(results)
        return HttpResponse(data, mimetype)
        
def get_airport(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        airport = Airports.objects.filter(Q(cityName__istartswith = q ) | Q(code__istartswith = q))[:20]
        #airport.query.group_by = ['code']
        results = []
        airportcode = []
        for airportdata in airport:
            if airportdata.code not in airportcode:
	            airportcode.append(airportdata.code)
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
        passenger = request.REQUEST['passenger']
        cabintype = ''
        if 'cabintype' in request.REQUEST:
            cabintype = request.REQUEST['cabintype']
        roundtripkey = ''
        if 'keyid' in request.REQUEST:
            roundtripkey = request.REQUEST['keyid']
            
        trip = ''
        date1 = ''
        print orgn,dest,roundtripkey,depart
        if 'trip' in request.REQUEST:
            trip = request.REQUEST['trip']
            print trip
        if 'returndate' in  request.REQUEST:
            retdate = request.REQUEST['returndate']
            if retdate:
                returndate = datetime.datetime.strptime(retdate, '%m/%d/%Y')
                date1 = returndate.strftime('%Y/%m/%d') 
        dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
        date = dt.strftime('%Y/%m/%d')
        
        
        return render_to_response('flightsearch/searchloading.html', {'searchdate':date, 'sname':orgn,'dname':dest,'returndate':date1,'triptype':trip,'roundtripkey':roundtripkey,'cabintype':cabintype,'passenger':passenger},context_instance=RequestContext(request))
    else:
        return render_to_response('flightsearch/index.html')
    
def getsearchresult(request):
    
    context = {}
    cabin =[]
    cabinclass = request.GET.get('cabin', '')
    passenger = request.GET.get('passenger', '')
    cabin.append(cabinclass)
    cabintype=''
    if request.GET.get('keyid', '') :
        searchkey = request.GET.get('keyid', '')
        returnkey = request.GET.get('returnkey', '')
        action =''
        if 'action' in request.GET and request.GET.get('action', '') == 'return':
            action = request.GET.get('action', '')
            searchkey = request.GET.get('returnkey', '')
            returnkey = request.GET.get('keyid', '')
        if cabinclass !='':
            cabintype = " and "+cabinclass+ "!=''"
            
        record = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+searchkey+cabintype+" order by maincabin ASC")
        minprice =0
        tax = 0
        selectedrow = ''
        
        if returnkey:
            if action != '':
                minprice = request.GET.get('price', '')
                print minprice,
            else:    
                data = Flightdata.objects.filter(searchkeyid=returnkey,maincabin__gt=0).values('maincabin','maintax').annotate(Min('maincabin'))[:1]
                tax=data[0]['maintax']
                minprice =data[0]['maincabin']
                action = 'depart'
            if 'rowid' in request.GET:
                recordid = request.GET.get('rowid', '')
                selectedrow = Flightdata.objects.get(pk=recordid)
        searchdata = Searchkey.objects.filter(searchid=searchkey)
        for s in searchdata:
            source = s.source
            destination = s.destination
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        filterkey ={'cabin':cabin}
        for row in timerecord:
            
            timeinfo = {'maxdept':row.maxdept,'mindept':row.mindept,'minarival':row.minarival,'maxarival':row.maxarival}
        
        if len(list(record))>0: 
            return render_to_response('flightsearch/searchresult.html',{'action':action,'data':record,'minprice':minprice,'tax':tax,'returndata':returnkey,'search':searchdata,'timedata':timeinfo,'selectedrow':selectedrow,'filterkey':filterkey,'passenger':passenger},context_instance=RequestContext(request)) 
        else:

            msg = "Sorry, No flight found  from "+source+" To "+destination+".  Please search for another date or city !"
            return  render_to_response('flightsearch/index.html',{'message':msg}, context_instance=RequestContext(request))
            
def booking(request):
    context = {}
    if request.method == "POST":
        recordid = request.REQUEST['rowid']
        price = request.REQUEST['price']
        cabin = request.REQUEST['cabinname']
        tax = request.REQUEST['tax']
        passenger = request.REQUEST['passenger']
        selectedrow = Flightdata.objects.get(pk=recordid)
        totalprice = int(passenger) * int(price)
        totaltax = float(tax)*int(passenger)
        print totaltax
        return render_to_response('flightsearch/booking.html',{'selectedrow':selectedrow,'tax':tax,'cabin':cabin,'price':price,'passenger':passenger,'total':totalprice,'totaltax':totaltax},context_instance=RequestContext(request)) 
        
    
            

	
# Create your views here.
