#!/usr/bin/env python
import os,sys
import hashlib
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q,Count,Min
from datetime import timedelta
import subprocess
from types import *
import datetime
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from pexproject.models import Flightdata,Airports,Searchkey,User
from pexproject.templatetags.customfilter import floatadd,assign
from subprocess import call
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

def flights(request):
    return  render_to_response('flightsearch/flights.html', context_instance=RequestContext(request))
    
def signup(request):
    context = {}
    if request.method == "POST":
        email = request.REQUEST['username']
        user = User.objects.filter(email=email)
        if len(user) > 0:
            msg = "Email is already registered"
            return HttpResponseRedirect(reverse('index'),{'msg':msg,'action':"signup"})
        password = request.REQUEST['password']
        password1 = hashlib.md5(password).hexdigest()
        airport = request.REQUEST['home_airport']
        object = User(email=email,password=password1,home_airport=airport)
        object.save()
        if object.user_id:
            return HttpResponseRedirect(reverse('index'), context_instance=RequestContext(request))   
    return  render_to_response('flightsearch/register.html', context_instance=RequestContext(request))
def login(request):
    context = {}
    if request.method == "POST":  #and not request.session.get('username', None)
        username = request.REQUEST['username']
        password = request.REQUEST['password']
        password1 = hashlib.md5(password).hexdigest()
        user = User.objects.filter(email=username,password=password1)
        if len(user) > 0:
            request.session['username'] = username
            request.session['password'] = password1
            print request.session['username']
            print request.session['password']
            return HttpResponseRedirect(reverse('index'))
        else:
            msg="Invalid username or password"
            return render_to_response('flightsearch/index.html',{'msg':msg},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))

def logout(request):
    context = {}
    request.session['user'] = ''
    request.session['password'] = ''
    return HttpResponseRedirect(reverse('index'))
    #return render_to_response('flightsearch/index.html',context_instance=RequestContext(request))

def search(request):
    context = {}
    if request.is_ajax():
        context = {}
        cursor = connection.cursor()
        returndate = request.REQUEST['returndate']
        dt1 =''
        searchdate1 = ''
        if returndate:
            dt1 = datetime.datetime.strptime(returndate, '%Y/%m/%d')
            date1 = dt1.strftime('%m/%d/%Y')
            searchdate1 = dt1.strftime('%Y-%m-%d')
        triptype =  request.REQUEST['triptype']
        
        orgnid = request.REQUEST['fromMain'] 
        destid = request.REQUEST['toMain']
        
        originobj = Airports.objects.filter(airport_id=orgnid)
        destobj = Airports.objects.filter(airport_id=destid)
        for row in originobj:
            orgn = row.cityName+", "+row.cityCode+", "+row.countryCode +"  ("+row.code+")"
            orgncode = row.code
            origin = row.cityName+" ("+row.code+")"
        for row1 in destobj:
            dest = row1.cityName+", "+row1.cityCode+", "+row1.countryCode +"  ("+row1.code+")"
            destcode = row1.code
            destination1 = row1.cityName+" ("+row1.code+")"
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
            print destination1,origin
            obj = Searchkey.objects.filter(source=origin,destination=destination1,traveldate=searchdate,scrapetime__gte=time1)
            returnobj = Searchkey.objects.filter(source=destination1,destination=origin,traveldate=searchdate1,scrapetime__gte=time1)
            if len(returnobj) > 0:
                for retkey in returnobj:
                     returnkey = retkey.searchid
            else:
                print destination1,origin
                searchdata = Searchkey(source=destination1,destination=origin,traveldate=dt1,scrapetime=time,origin_airport_id=orgnid,destination_airport_id=destid)
                searchdata.save()
                returnkey = searchdata.searchid
                retdeltares = customfunction.delta(destcode,orgncode,date1,returnkey)
                retrecordkey = customfunction.united(dest,orgn,returndate,returnkey)
                
        else:
            print destination1,origin
            obj = Searchkey.objects.filter(source=origin,destination=destination1,traveldate=searchdate,scrapetime__gte=time1)
        if len(obj) > 0:
            for keyid in obj:
                searchkeyid = keyid.searchid
        else:
            if dt1:
                print destination1,origin
                searchdata = Searchkey(source=origin,destination=destination1,traveldate=dt,returndate=dt1,scrapetime=time,origin_airport_id=orgnid,destination_airport_id=destid) 
            else:
                searchdata = Searchkey(source=origin,destination=destination1,traveldate=dt,scrapetime=time,origin_airport_id=orgnid,destination_airport_id=destid)
            searchdata.save()
            searchkeyid = searchdata.searchid 
            cursor = connection.cursor()
            deltares = customfunction.delta(orgncode,destcode,date,searchkeyid)
            recordkey = customfunction.united(orgn,dest,depart,searchkeyid)
            returnkey = ''
            if returndate:
                retunobj = Searchkey.objects.filter(source=destination1,destination=origin,traveldate=searchdate1,scrapetime__gte=time1)
                if len(retunobj) > 0:
                    for keyid in retunobj:
                        returnkey = keyid.searchid
                else:
                    searchdata = Searchkey(source=destination1,destination=origin,traveldate=dt1,scrapetime=time,origin_airport_id=orgnid,destination_airport_id=destid)
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
	            airport_json['value'] = airportdata.cityName+" ("+airportdata.code+")"
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
        print cabintype
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
    taxes = ''
    cabinclass = request.GET.get('cabin', '')
    passenger = request.GET.get('passenger', '')
    cabin.append(cabinclass)
    cabintype=''
    querylist =''
    join=''
    list2=''
    list1=''
    minprice =0
    tax = 0
    selectedrow = ''
    returndate =''
    returndelta=''
    returnkey =''
    deltaminval = 0
    deltatax = 0
    unitedtax = 0
    unitedminval=0
    returnunited=''
    deltacabin = ''
    unitedcabin =''
    deltacabin_name=''
    unitedcabin_name=''
    
    offset = 0
    pageno = 1
    limit = 10
    
    if request.is_ajax():
        pageno = request.REQUEST['page_no']
        offset = (int(pageno) - 1) * limit
    else:
        if request.GET.get('keyid', ''):
            recordkey = request.GET.get('keyid', '')
            totalrecords = Flightdata.objects.filter(searchkeyid=recordkey).count()
        
        
    if 'stoppage' in request.POST:
        if request.is_ajax():
            list2 = request.POST.getlist('stoppage')
            list2 = list2[0].split(',')
            print list2
            if list2[0] != '':
                querylist = querylist+join+"stoppage in ('"+"','".join(list2)+"')"
                join = ' AND '    
        
        else:
            list2 = request.POST.getlist('stoppage')
            if len(list2)>1:
                querylist = querylist+join+"stoppage IN ('"+"','".join(list2)+"')"
                join = ' AND '
            else:
                if(len(list2) > 0):
                    querylist = querylist+join+"stoppage = '"+list2[0]+"'"
                    join = ' AND '    
    if 'airlines' in request.POST:
        if request.is_ajax():
            list1 = request.POST.getlist('airlines')
            list1 = list1[0].split(',')
            if list1[0] != '':
                querylist = querylist+join+"datasource IN ('"+"','".join(list1)+"')"
                join = ' AND '
        else:
            list1 = request.POST.getlist('airlines')
            if len(list1)>1:
                querylist = querylist+join+"datasource IN ('"+"','".join(list1)+"')"
                join = ' AND '
            else:
                if(len(list1) > 0):
                    querylist = querylist+join+"datasource = '"+list1[0]+"'"
                    join = ' AND '
    depttime = datetime.time(0, 0, 0)
    deptmaxtime = datetime.time(0, 0, 0)
    arivtime = datetime.time(0, 0, 0)
    arivtmaxtime = datetime.time(0, 0, 0)
    
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

   
    
    if request.GET.get('keyid', '') :
        searchkey = request.GET.get('keyid', '')
        searchdata = Searchkey.objects.filter(searchid=searchkey)
        for s in searchdata:
            source = s.source
            destination = s.destination
        if ('action' in request.GET and request.GET.get('action', '') == 'return') or 'rowid' in request.POST:
            action = request.GET.get('action', '')
            searchkey = request.GET.get('returnkey', '')
            returnkey = request.GET.get('keyid', '')
        
        querylist = querylist+join+" searchkeyid = "+searchkey
        join = ' AND '
        
        
        action =''
        
        if cabinclass !='':
            if cabinclass == 'maincabin':
                taxes = "maintax"
            elif cabinclass == 'firstclass':
                taxes = "firsttax"
            else:
                if cabinclass == 'business':
                    taxes = "businesstax"
            print "aaya"
            cabintype = " and "+cabinclass+ " > 0"
            querylist = querylist+cabintype
            
        
        
        if 'returnkey' in request.GET or 'returnkey' in request.POST:
            returnkey = request.GET.get('returnkey', '')
           
            action = 'depart'
            returndate = Searchkey.objects.values_list('traveldate', flat=True).filter(searchid=returnkey)
            if 'rowid' in request.GET or 'rowid' in request.POST:
                print "in rowid"
                recordid = request.GET.get('rowid', '')
                if 'rowid' in request.POST:
                    recordid = request.REQUEST['rowid']
                 
                datasources= request.GET.get('datasource','')
                if recordid != "undefined":
                    selectedrow = Flightdata.objects.get(pk=recordid)
                    action = 'return'
                
            else:
                print "ajxa",returnkey 
                #------------------------change code for return trip------------------------------------
                deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='delta',maincabin__gt=0).values('maincabin','maintax','cabintype1').annotate(Min('maincabin')).order_by('maincabin')
                if len(deltamin1) <= 0:
                    deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='delta',firstclass__gt=0).values('firstclass','firsttax','cabintype2').annotate(Min('firstclass')).order_by('firstclass')
                    if len(deltamin1) <= 0:
                        deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='delta',business__gt=0).values('business','businesstax','cabintype3').annotate(Min('business')).order_by('business')
                        if deltamin1:
                            deltamin = deltamin1[0]
                            deltaminval =  deltamin['business']
                            deltatax =  deltamin['businesstax']
                            deltacabin_name=deltamin['cabintype3']
                            
                    else:
                        deltamin = deltamin1[0]
                        deltaminval =  deltamin['firstclass']
                        deltatax =  deltamin['firsttax']
                        deltacabin_name=deltamin['cabintype2']
                else:
                    deltamin = deltamin1[0]
                    deltaminval =  deltamin['maincabin']
                    deltatax =  deltamin['maintax']
                    deltacabin_name=deltamin['cabintype1']   
                returndelta = Flightdata.objects.filter(searchkeyid=returnkey,datasource='delta',maincabin=deltaminval)            
                unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',maincabin__gt=0).values('maincabin','maintax','cabintype1').annotate(Min('maincabin')).order_by('maincabin')
                
                if len(unitedmin1) <= 0 :
                    unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',firstclass__gt=0).values('firstclass','firsttax','cabintype2').annotate(Min('firstclass')).order_by('firstclass')
                    if len(unitedmin1) <= 0:
                        unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',business__gt=0).values('business','businesstax','cabintype3').annotate(Min('business')).order_by('business')
                        if unitedmin1:
                            unitedmin = unitedmin1[0] 
                            unitedminval =  unitedmin['business']
                            unitedtax =  unitedmin['businesstax']
                            unitedcabin_name = unitedmin['cabintype3']
                            returnunited = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',business=unitedminval)
                            
                    else:
                        unitedmin = unitedmin1[0] 
                        unitedminval =  unitedmin['firstclass']
                        unitedtax =  unitedmin['firsttax']
                        unitedcabin_name = unitedmin['cabintype2']
                        returnunited = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',firstclass=unitedminval)
                else:             
                    unitedmin = unitedmin1[0] 
                    unitedminval =  unitedmin['maincabin']
                    unitedtax = unitedmin['maintax']
                    unitedcabin_name = unitedmin['cabintype1']
                    returnunited = Flightdata.objects.filter(searchkeyid=returnkey,datasource='united',maincabin=unitedminval)
         
        print "unitedminval",unitedminval   
        print "deltaminval",deltaminval   
        print "cabin",cabinclass
        unitedorderprice =  cabinclass+"+"+str(unitedminval)
        deltaorderprice = cabinclass+"+"+str(deltaminval)

        record = Flightdata.objects.raw("select * , case when datasource = 'delta' then "+deltaorderprice+"  else "+unitedorderprice+" end as finalprice  from pexproject_flightdata where "+querylist+" order by finalprice ,"+taxes+",departure ASC LIMIT "+str(limit)+" OFFSET "+str(offset))
        print record.query
            #---------------------------------------------------------------------------------------
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        filterkey =  {'stoppage':list2,'datasource':list1,'cabin':cabin} 
        if depttime:
            timeinfo = {'maxdept':deptmaxtime,'mindept':depttime,'minarival':arivtime,'maxarival':arivtmaxtime}
        else:
            timeinfo=''    
        if request.is_ajax():
            return render_to_response('flightsearch/search.html',{'action':action,'data':record,'minprice':minprice,'tax':tax,'timedata':timeinfo,'returndata':returnkey,'search':searchdata,'selectedrow':selectedrow,'filterkey':filterkey,'passenger':passenger,'returndate':returndate,'deltareturn':returndelta,'unitedreturn':returnunited,'deltatax':deltatax,'unitedtax':unitedtax,'unitedminval':unitedminval,'deltaminval':deltaminval,'deltacabin_name':deltacabin_name,'unitedcabin_name':unitedcabin_name},context_instance=RequestContext(request))
        if totalrecords>0:
            return render_to_response('flightsearch/searchresult.html',{'action':action,'data':record,'minprice':minprice,'tax':tax,'timedata':timeinfo,'returndata':returnkey,'search':searchdata,'selectedrow':selectedrow,'filterkey':filterkey,'passenger':passenger,'returndate':returndate,'deltareturn':returndelta,'unitedreturn':returnunited,'deltatax':deltatax,'unitedtax':unitedtax,'unitedminval':unitedminval,'deltaminval':deltaminval,'deltacabin_name':deltacabin_name,'unitedcabin_name':unitedcabin_name},context_instance=RequestContext(request)) 
        else:
            print "no data"
            if request.is_ajax():
                print "ajax no data"
                return render_to_response('flightsearch/search.html',{'action':action,'data':record,'minprice':minprice,'tax':tax,'timedata':timeinfo,'returndata':returnkey,'search':searchdata,'selectedrow':selectedrow,'filterkey':filterkey,'passenger':passenger,'returndate':returndate,'deltareturn':returndelta,'unitedreturn':returnunited,'deltatax':deltatax,'unitedtax':unitedtax,'unitedminval':unitedminval,'deltaminval':deltaminval,'deltacabin_name':deltacabin_name,'unitedcabin_name':unitedcabin_name},context_instance=RequestContext(request))
            msg = "Sorry, No flight found  from "+source+" To "+destination+".  Please search for another date or city !"
            return  render_to_response('flightsearch/flights.html',{'message':msg}, context_instance=RequestContext(request))
            
def share(request):
    context ={}
    if 'selectedid' in request.GET:
        selectedid = request.GET.get('selectedid','')
        cabin =  request.GET.get('cabin','')
        traveler =  request.GET.get('passenger','')
        #record = Flightdata.objects.get(pk=selectedid)
        record = get_object_or_404(Flightdata, pk=selectedid)
        returnrecord = ''
        price = 0
        tax = 0
        returncabin = ''
        if 'returnrowid' in request.GET:
            returnrowid =request.GET.get('returnrowid','')
            returnrecord = Flightdata.objects.get(pk=returnrowid)
            if returnrecord.maincabin > 0:
                price = returnrecord.maincabin
                tax = returnrecord.maintax
                returncabin = returnrecord.cabintype1
            elif returnrecord.firstclass > 0:
                price = returnrecord.firstclass
                tax = returnrecord.firsttax
                returncabin = returnrecord.cabintype2
            else:
                if returnrecord.business > 0:
                    price = returnrecord.business
                    tax = returnrecord.businesstax
                    returncabin = returnrecord.cabintype3
        #print price,tax
        #totalprice = int(traveler) * int(price)
        #totaltax = float(tax)*int(traveler)
        return render_to_response('flightsearch/share.html',{'record':record,'cabin':cabin,'traveler':traveler,'returnrecord':returnrecord,"price":price,"tax":tax,'returncabin':returncabin}, context_instance=RequestContext(request))



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
