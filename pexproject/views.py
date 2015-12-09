#!/usr/bin/env python
import os, sys
import hashlib
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q, Count, Min
from datetime import timedelta
from social_auth.models import UserSocialAuth
from django.contrib.auth import login
from types import *
import datetime
from django.shortcuts import get_object_or_404,redirect
from django.core.mail import send_mail
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from pexproject.models import Flightdata, Airports, Searchkey, User
from pexproject.templatetags.customfilter import floatadd, assign
from social_auth.models import UserSocialAuth
from django.contrib.auth import login as social_login,authenticate,get_user
from django.contrib.auth import logout as auth_logout
from django.conf import settings
from random import randint
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
import time
import threading
from multiprocessing import Process
from datetime import date
from django.db import connection, transaction
import operator
import customfunction
from pexproject.form import LoginForm
#from django.utils import timezone
#from bson import json_util
import json
import logging
logger = logging.getLogger(__name__)

def index(request):
    context = {}
    user = User()
    if request.user.username:
    	request.session['username'] = request.user.username
    if 'password'  not in request.session:	
    	request.session['password'] = "123456" #request.user.password
    return  render_to_response('flightsearch/index.html', context_instance=RequestContext(request))

def flights(request):
    context = {}
    mc = ''
    if 'action' in request.GET:
        mc = request.GET.get('action','')
        #return  render_to_response('flightsearch/multicity.html', context_instance=RequestContext(request))
    return  render_to_response('flightsearch/flights.html',{'mc':mc}, context_instance=RequestContext(request))
    
def signup(request):
    context = {}
    if 'username' not in request.session:
        if request.method == "POST":
	    currentdatetime = datetime.datetime.now()
            time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
            email = request.REQUEST['username']
            user = User.objects.filter(username=email)
            if len(user) > 0:
                msg = "Email is already registered"
                return render_to_response('flightsearch/index.html', {'signup_msg':msg},context_instance=RequestContext(request))
            password = request.REQUEST['password']
            password1 = hashlib.md5(password).hexdigest()
            airport = request.REQUEST['home_airport']
            object = User(username=email,email=email, password=password1, home_airport=airport,last_login=time)
            object.save()
            request.session['username'] = email
            request.session['password'] = password1
            if object.user_id:
                msg = "Thank you, You have been successfully registered."
                return render_to_response('flightsearch/index.html',{'welcome_msg':msg}, context_instance=RequestContext(request))   
        return  render_to_response('flightsearch/index.html', context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))

def manageAccount(request):
    context = {}
    msg = ''
    email = request.session['username']
    user1 = User.objects.get(username=email)
    if request.POST:
        if 'current_password' in request.POST:
            password = request.REQUEST['current_password']
            password1 = hashlib.md5(password).hexdigest()
            newpassword = request.REQUEST['new_password']
            newpassword1 = hashlib.md5(newpassword).hexdigest()
            user1.password=newpassword1
        else:
            password1 = request.session['password']
        if user1.email :
            home_airport = request.REQUEST['home_airport']
            user1.home_airport = home_airport
            user1.save()
            msg = "Your account has been updated  successfully"
        else:
            msg = "wrong current password" 
    print msg
    return render_to_response('flightsearch/manage_account.html',{'message':msg,'user':user1}, context_instance=RequestContext(request))

def login(request):
    context = {}
    user = User()
    user = authenticate()
    if user is not None:
        if user.is_active:
 		social_login(request,user)
		
    if request.method == "POST":  # and not request.session.get('username', None)
        username = request.REQUEST['username']
        password = request.REQUEST['password']
        password1 = hashlib.md5(password).hexdigest()
        user = User.objects.filter(username=username, password=password1)
        if len(user) > 0:
            request.session['username'] = username
            request.session['password'] = password1
            return HttpResponseRedirect(reverse('index'))
        else:
            msg = "Invalid username or password"
            return render_to_response('flightsearch/index.html', {'msg':msg}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))

def logout(request):
    context = {} 
    auth_logout(request)
    if 'username' in request.session:
    	del  request.session['username'] 
    	del  request.session['password']  
    return HttpResponseRedirect(reverse('index'))

def forgotPassword(request):
    context = {}
    msg =''
    if request.POST:
        user_email =  request.REQUEST['email']
        password = randint(100000,999999)
        password1 = hashlib.md5(str(password)).hexdigest()
        obj = User.objects.get(email=user_email)
        obj.password=password1
        obj.save()
        send_mail('Forgot Your Password', 'Your password has been reset. Please login with your new password '+str(password), 'PEX', ['jk.dhn2010@gmail.com'])
    else:
        msg = "forgot password"
    return render_to_response('flightsearch/index.html',{'fpmsg':msg},context_instance=RequestContext(request)) 

def search(request):
    context = {}
    if request.is_ajax():
        context = {}
        cursor = connection.cursor()
        returndate = request.REQUEST['returndate']
        dt1 = ''
        searchdate1 = ''
        multiplekey =''
        seperator = ''
        #customfunction.etihad()
        
        if returndate:
            dt1 = datetime.datetime.strptime(returndate, '%Y/%m/%d')
            date1 = dt1.strftime('%m/%d/%Y')
            searchdate1 = dt1.strftime('%Y-%m-%d')
        triptype = request.REQUEST['triptype']
        ongnidlist=''
        destlist = ''
        departlist =''
        searchkeyid = ''
        returnkey = ''
        orgnid = request.REQUEST['fromMain']
        destid = request.REQUEST['toMain']
        depart = request.REQUEST['deptdate']
        cabin = request.REQUEST['cabin']
        print "cabin",cabin
        ongnidlist =  orgnid.split(',')
        destlist = destid.split(',')
        departlist = depart.split(',')
        
        for i in range(0,len(departlist)):
            etihadorigin =''
            etihaddest = ''
            orgnid = ongnidlist[i]
            destid = destlist[i]
            depart = departlist[i]
            print "orgnid",orgnid,"destid",destid
            originobj = Airports.objects.filter(airport_id=orgnid)
            destobj = Airports.objects.filter(airport_id=destid)
            for row in originobj:
                orgn = row.cityName + ", " + row.cityCode + ", " + row.countryCode + "  (" + row.code + ")"
                etihadorigin = row.cityName
                print "origin",etihadorigin
                orgncode = row.code
                origin = row.cityName + " (" + row.code + ")"
            for row1 in destobj:
                dest = row1.cityName + ", " + row1.cityCode + ", " + row1.countryCode + "  (" + row1.code + ")"
                etihaddest = row1.cityName
                print "dest",etihaddest
                destcode = row1.code
                destination1 = row1.cityName + " (" + row1.code + ")"
            dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
            date = dt.strftime('%m/%d/%Y')
            searchdate = dt.strftime('%Y-%m-%d')        
            currentdatetime = datetime.datetime.now()
            time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
            time1 = datetime.datetime.now() - timedelta(hours=4)
            time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
            #flag1 = 0
            #flag2 = 0
            Searchkey.objects.filter(scrapetime__lte=time1).delete()
            #Flightdata.objects.filter(scrapetime__lte=time1).delete()
            if searchdate1:
                obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)
                returnobj = Searchkey.objects.filter(source=destination1, destination=origin, traveldate=searchdate1, scrapetime__gte=time1)
                if len(returnobj) > 0:
                    for retkey in returnobj:
                         returnkey = retkey.searchid
                else:
                    searchdata = Searchkey(source=destination1, destination=origin, traveldate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid)
                    searchdata.save()
                    returnkey = searchdata.searchid
                    #flag2 = 1
                    customfunction.etihad(etihaddest,etihadorigin,date1,returnkey,cabin)
                    customfunction.scrape(destcode, orgncode, date1, returndate, returnkey)
            else:
                obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)
            if len(obj) > 0:
                for keyid in obj:
                    searchkeyid = keyid.searchid
            else:
                if dt1:
                    searchdata = Searchkey(source=origin, destination=destination1, traveldate=dt, returndate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid) 
                else:
                    searchdata = Searchkey(source=origin, destination=destination1, traveldate=dt, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid)
                searchdata.save()
                searchkeyid = searchdata.searchid 
                cursor = connection.cursor()
                #flag1 = 1
                customfunction.etihad(etihadorigin,etihaddest,date,searchkeyid,cabin)
                customfunction.scrape(orgncode, destcode, date, depart, searchkeyid)
                returnkey = ''
                if returndate:
                    retunobj = Searchkey.objects.filter(source=destination1, destination=origin, traveldate=searchdate1, scrapetime__gte=time1)
                    if len(retunobj) > 0:
                        for keyid in retunobj:
                            returnkey = keyid.searchid
                    else:
                        searchdata = Searchkey(source=destination1, destination=origin, traveldate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid)
                        searchdata.save()
                        returnkey = searchdata.searchid
                        #flag2 = 1
                        #customfunction.scrape(destcode, orgncode, date1, returndate, returnkey)
                        customfunction.etihad(etihaddest,etihadorigin,date,returnkey,cabin)
                        customfunction.scrape(destcode, orgncode, date, depart, returnkey)
            if len(departlist) >0 :
                multiplekey = multiplekey+seperator+str(searchkeyid)
                seperator = ','             
        mimetype = 'application/json'
        results = []
        results.append(multiplekey)
        if returnkey:
            results.append(returnkey)
        data = json.dumps(results)
        return HttpResponse(data, mimetype)
        
def get_airport(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        airport = Airports.objects.filter(Q(cityName__istartswith=q) | Q(code__istartswith=q))[:20]
        # airport.query.group_by = ['code']
        results = []
        airportcode = []
        for airportdata in airport:
            if airportdata.code not in airportcode:
	            airportcode.append(airportdata.code)
        	    airport_json = {}
	            airport_json['id'] = airportdata.airport_id
        	    airport_json['label'] = airportdata.cityName + ", " + airportdata.cityCode + ", " + airportdata.countryCode + "  (" + airportdata.code + " )"
	            airport_json['value'] = airportdata.cityName + " (" + airportdata.code + ")"
        	    results.append(airport_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def searchLoading(request):
    context = {}
    if request.method == "POST":
        trip = ''
        date=''
        date1 = ''
        datelist= ''
        roundtripkey = ''
        if 'multicy' in request.POST:
            originlist = request.POST.getlist('fromMain')
            destinationlist = request.POST.getlist('toMain')
            datelist = request.POST.getlist('deptdate')
            passenger = request.REQUEST['passenger']
            cabintype = request.REQUEST['cabintype']
            orgn = ','.join(originlist)
            dest = ','.join(destinationlist)
            
        else:
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
            if 'trip' in request.REQUEST:
                trip = request.REQUEST['trip']
            if 'returndate' in  request.REQUEST:
                retdate = request.REQUEST['returndate']
                if retdate:
                    returndate = datetime.datetime.strptime(retdate, '%m/%d/%Y')
                    date1 = returndate.strftime('%Y/%m/%d')
        if len(datelist)>0:
            dates = []
            for dt3 in datelist:
                dt4 = datetime.datetime.strptime(dt3, '%m/%d/%Y')
                date3 = dt4.strftime('%Y/%m/%d')
                dates.append(date3)
                date = ','.join(dates)
        else: 
            dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
            date = dt.strftime('%Y/%m/%d')
        return render_to_response('flightsearch/searchloading.html', {'searchdate':date, 'sname':orgn, 'dname':dest, 'returndate':date1, 'triptype':trip, 'roundtripkey':roundtripkey, 'cabintype':cabintype, 'passenger':passenger}, context_instance=RequestContext(request))
    else:
        return render_to_response('flightsearch/index.html')
    
def getsearchresult(request):
    context = {}
    
    cabin = []
    taxes = ''
    cabinclass = request.GET.get('cabin', '')
    passenger = request.GET.get('passenger', '')
    cabin.append(cabinclass)
    cabintype = ''
    querylist = ''
    join = ''
    list2 = ''
    list1 = ''
    minprice = 0
    tax = 0
    selectedrow = ''
    returndate = ''
    returndelta = ''
    returnkey = ''
    deltaminval = 0
    deltatax = 0
    unitedtax = 0
    unitedminval = 0
    returnunited = ''
    deltacabin = ''
    unitedcabin = ''
    deltacabin_name = ''
    unitedcabin_name = ''
    returnkeyid1 = ''
    offset = 0
    pageno = 1
    limit = 10
    multicitykey1=''
    if request.is_ajax():
        pageno = request.REQUEST['page_no']
        offset = (int(pageno) - 1) * limit
    else:
        if request.GET.get('keyid', ''):
            recordkey = request.GET.get('keyid', '')
            totalrecords = Flightdata.objects.filter(searchkeyid=recordkey).count()
    
    action = ''
    if request.GET.get('keyid', '') :
        searchkey = request.GET.get('keyid', '')
        if request.GET.get('multicity'):
            allkey = request.GET.get('multicity')
            multiple_key = allkey.split(',')
            searchdata = Searchkey.objects.filter(searchid__in=multiple_key)
        else:
            searchdata = Searchkey.objects.filter(searchid=searchkey)
        for s in searchdata:
            source = s.source
            destination = s.destination
        if ('action' in request.GET and request.GET.get('action', '') == 'return') or 'rowid' in request.POST and request.GET.get('action', '') != 'depart':
            action = request.GET.get('action', '')
            searchkey = request.GET.get('returnkey', '')
            returnkey = request.GET.get('keyid', '')
            
        
        querylist = querylist + join + " p1.searchkeyid = '"+searchkey+"'"
        join = ' AND '
    
    
    if 'multicity' in request.GET or 'multicity' in request.POST:
        multicitykey = request.GET.get('multicity', '')
        multicitykey1 = multicitykey.split(',')
    if 'stoppage' in request.POST:
        if request.is_ajax():
            list2 = request.POST.getlist('stoppage')
            list2 = list2[0].split(',')
            if '2 STOPS' in list2:
                querylist = querylist + join + "p1.stoppage in ('" + "','".join(list2) + "','3 STOPS')"
                join = ' AND '
            else: 
                if list2[0] != '':
                    querylist = querylist + join + "p1.stoppage in ('" + "','".join(list2) + "')"
                    join = ' AND ' 
                
                   
        
        else:
            list2 = request.POST.getlist('stoppage')
            if len(list2) > 1:
                if '2 STOPS' in list2:
                    list2.append('3 STOPS')
                querylist = querylist + join + "p1.stoppage IN ('" + "','".join(list2) + "')"
                join = ' AND '
            else:
                if(len(list2) > 0):
                    stops = request.REQUEST['stoppage']
                    if stops == '2 STOPS':
                         querylist = querylist + join + "p1.stoppage NOT IN ('NONSTOP','1 STOP')"
                         join = ' AND '
                    else:
                        querylist = querylist + join + "p1.stoppage = '" + list2[0] + "'"
                        join = ' AND '    
    if 'airlines' in request.POST:
        if request.is_ajax():
            list1 = request.POST.getlist('airlines')
            list1 = list1[0].split(',')
            if list1[0] != '':
                querylist = querylist + join + "p1.datasource IN ('" + "','".join(list1) + "')"
                join = ' AND '
        else:
            list1 = request.POST.getlist('airlines')
            if len(list1) > 1:
                querylist = querylist + join + "p1.datasource IN ('" + "','".join(list1) + "')"
                join = ' AND '
            else:
                if(len(list1) > 0):
                    querylist = querylist + join + "p1.datasource = '" + list1[0] + "'"
                    join = ' AND '
    depttime = datetime.time(0, 0, 0)
    deptmaxtime = datetime.time(0, 0, 0)
    arivtime = datetime.time(0, 0, 0)
    arivtmaxtime = datetime.time(0, 0, 0)
    
    if 'depaturemin' in request.POST:
         depttime = request.REQUEST['depaturemin']
         deptformat = (datetime.datetime.strptime(depttime, '%I:%M %p'))
         deptformat1 = deptformat.strftime('%H:%M:%S')
         querylist = querylist + join + " p1.departure >= '" + deptformat1 + "'"
         join = ' AND '
    if 'depaturemax' in request.POST:
        deptmaxtime = request.REQUEST['depaturemax']
        deptmaxformat = (datetime.datetime.strptime(deptmaxtime, '%I:%M %p'))
        deptmaxformat1 = deptmaxformat.strftime('%H:%M:%S')
        querylist = querylist + join + " p1.departure <= '" + deptmaxformat1 + "'"
        join = ' AND '
    if 'arivalmin' in request.POST:
         arivtime = request.REQUEST['arivalmin']
         arivformat = (datetime.datetime.strptime(arivtime, '%I:%M %p'))
         arivformat1 = arivformat.strftime('%H:%M:%S')
         querylist = querylist + join + " p1.arival >= '" + arivformat1 + "'"
         join = ' AND '
    if 'arivalmax' in request.POST:
        arivtmaxtime = request.REQUEST['arivalmax']
        arivtmaxformat = (datetime.datetime.strptime(arivtmaxtime, '%I:%M %p'))
        arivtmaxformat1 = arivtmaxformat.strftime('%H:%M:%S')
        querylist = querylist + join + " p1.arival <= '" + arivtmaxformat1 + "'"
        join = ' AND ' 

   
    action = ''
    if request.GET.get('keyid', '') :
        '''
        searchkey = request.GET.get('keyid', '')
        if request.GET.get('multicity'):
            allkey = request.GET.get('multicity')
            multiple_key = allkey.split(',')
            searchdata = Searchkey.objects.filter(searchid__in=multiple_key)
        else:
            searchdata = Searchkey.objects.filter(searchid=searchkey)
        for s in searchdata:
            source = s.source
            destination = s.destination
        if ('action' in request.GET and request.GET.get('action', '') == 'return') or 'rowid' in request.POST and request.GET.get('action', '') != 'depart':
            action = request.GET.get('action', '')
            searchkey = request.GET.get('returnkey', '')
            returnkey = request.GET.get('keyid', '')
            
        
        querylist = querylist + join + " p1.searchkeyid = " + searchkey
        join = ' AND '
        
        '''
       
        
        if cabinclass != '':
            if cabinclass == 'maincabin':
                taxes = "maintax"
            elif cabinclass == 'firstclass':
                taxes = "firsttax"
            else:
                if cabinclass == 'business':
                    taxes = "businesstax"
            
            
        
        
        
        if 'returnkey' in request.GET or 'returnkey' in request.POST:
            returnkey = request.GET.get('returnkey', '')
            returnkeyid1 = returnkey
            action = 'depart'
            returndate = Searchkey.objects.values_list('traveldate', flat=True).filter(searchid=returnkey)
            if 'rowid' in request.GET or 'rowid' in request.POST:
                cabintype = ''
                recordid = request.GET.get('rowid', '')
                if 'rowid' in request.POST:
                    recordid = request.REQUEST['rowid']
                 
                datasources = request.GET.get('datasource', '')
                if recordid != "undefined":
                    selectedrow = Flightdata.objects.get(pk=recordid)
                    action = 'return'
                
            else:
                
                #------------------------change code for return trip------------------------------------
                if cabinclass == "maincabin" :
                    deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', maincabin__gt=0).values('maincabin', 'maintax', 'cabintype1').annotate(Min('maincabin')).order_by('maincabin')
                    if len(deltamin1) > 0:
                        deltamin = deltamin1[0]
                        deltaminval = deltamin['maincabin']
                        deltatax = deltamin['maintax']
                        deltacabin_name = deltamin['cabintype1']
                        returndelta = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', maincabin=deltaminval)   
                elif cabinclass == "firstclass" :
                    deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', firstclass__gt=0).values('firstclass', 'firsttax', 'cabintype2').annotate(Min('firstclass')).order_by('firstclass')
                    if len(deltamin1) > 0:
                        deltamin = deltamin1[0]
                        deltaminval = deltamin['firstclass']
                        deltatax = deltamin['firsttax']
                        deltacabin_name = deltamin['cabintype2']
                        returndelta = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', firstclass=deltaminval)
                else:
                    if cabinclass == "business":
                        deltamin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', business__gt=0).values('business', 'businesstax', 'cabintype3').annotate(Min('business')).order_by('business')
                        if len(deltamin1) > 0:
                            deltamin = deltamin1[0]
                            deltaminval = deltamin['business']
                            deltatax = deltamin['businesstax']
                            deltacabin_name = deltamin['cabintype3']
                            returndelta = Flightdata.objects.filter(searchkeyid=returnkey, datasource='delta', business=deltaminval)
                       
                '''
                returndelta = Flightdata.objects.filter(searchkeyid=returnkey,datasource='delta',maincabin=deltaminval)            
                '''
                unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', maincabin__gt=0).values('maincabin', 'maintax', 'cabintype1').annotate(Min('maincabin')).order_by('maincabin')
                if cabinclass == "maincabin" :
                    unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', maincabin__gt=0).values('maincabin', 'maintax', 'cabintype1').annotate(Min('maincabin')).order_by('maincabin')
                    if len(unitedmin1) > 0:
                        unitedmin = unitedmin1[0] 
                        unitedminval = unitedmin['maincabin']
                        unitedtax = unitedmin['maintax']
                        unitedcabin_name = unitedmin['cabintype1']
                        returnunited = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', maincabin=unitedminval)   
                elif cabinclass == "firstclass" :
                    unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', firstclass__gt=0).values('firstclass', 'firsttax', 'cabintype2').annotate(Min('firstclass')).order_by('firstclass')
                    if len(unitedmin1) > 0:
                        unitedmin = unitedmin1[0] 
                        unitedminval = unitedmin['firstclass']
                        unitedtax = unitedmin['firsttax']
                        unitedcabin_name = unitedmin['cabintype2']
                        returnunited = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', firstclass=unitedminval)
                else:
                    if cabinclass == "business":
                        unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', business__gt=0).values('business', 'businesstax', 'cabintype3').annotate(Min('business')).order_by('business')
                        if len(unitedmin1) > 0:
                            unitedmin = unitedmin1[0] 
                            unitedminval = unitedmin['business']
                            unitedtax = unitedmin['businesstax']
                            unitedcabin_name = unitedmin['cabintype3']
                            returnunited = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', business=unitedminval)
                
        
        
        unitedorderprice = cabinclass + "+" + str(unitedminval)
        deltaorderprice = cabinclass + "+" + str(deltaminval)
        
        if 'returnkey' in request.GET and returndelta == '' and ('rowid' not in request.GET) and 'rowid' not in request.POST:
            querylist = querylist + join + "p1.datasource NOT IN ('delta')"
            join = ' AND '
        if 'returnkey' in request.GET and returnunited == '' and ('rowid' not in request.GET) and 'rowid' not in request.POST:
            querylist = querylist + join + "p1.datasource NOT IN ('united')"
            join = ' AND '
        multirecods ={}
        counter =0
        recordlen = 0
        
        mainlist =[]
        multicity = ''
        n = 1
        
        if multicitykey1:
            
            multicity='true' 
            cabintype = " and " + "p1."+cabinclass + " > 0"
            querylist = querylist+cabintype
            replacekey = searchkey
            totalfare = ", p1." + cabinclass
            totaltax = ", p1."+taxes
            departfare = "p1." + cabinclass 
            qry1 = "select p1.*,"
            qry2=''
            qry3=''
            newidstring="p1.rowid"
            sep = ",'_',"
            sep1 = ''
            #print querylist
            #q = "p1.searchkeyid = '"+searchkey+"' AND" 
            #print q
            #querylist = querylist.replace(q,'')
            for keys in multicitykey1:
                if n > 1:
                    totalfare = totalfare+"+p"+str(n)+"." + cabinclass
                    totaltax = totaltax+"+p"+str(n)+"."+taxes
                    newidstring =newidstring+sep+"p"+str(n)+".rowid"
                    qry2 = qry2+sep1+'p'+str(n)+'.origin as origin'+str(n)+',p'+str(n)+'.rowid as rowid'+str(n)+', p'+str(n)+'.stoppage as stoppage'+str(n)+', p'+str(n)+'.destination as destination'+str(n)+', p'+str(n)+'.departure as departure'+str(n)+', p'+str(n)+'.arival as arival'+str(n)+', p'+str(n)+'.duration as duration'+str(n)+',p'+str(n)+'.flighno as flighno'+str(n)+', p'+str(n)+'.cabintype1 as cabintype1'+str(n)+',p'+str(n)+'.cabintype2 as cabintype2'+str(n)+',p'+str(n)+'.cabintype3 as cabintype3'+str(n)+', p'+str(n)+'.maincabin as maincabin'+str(n)+', p'+str(n)+'.maintax as maintax'+str(n)+', p'+str(n)+'.firsttax as firsttax'+str(n)+', p'+str(n)+'.businesstax as businesstax'+str(n)+',p'+str(n)+'.departdetails as departdetails'+str(n)+',p'+str(n)+'.arivedetails as arivedetails'+str(n)+', p'+str(n)+'.planedetails as planedetails'+str(n)+',p'+str(n)+'.operatedby as operatedby'+str(n)
                    sep1 = ','
                    qry3 = qry3+"inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +keys+"' and p1.datasource = p"+str(n)+".datasource and p"+str(n)+"."+cabinclass +" > '0'  "
                    q = ''
                counter = counter+1
                n = n+1
                   
            finalquery = qry1+"CONCAT("+newidstring+") as newid ,"+qry2+ totalfare+" as finalprice "+totaltax+" as totaltax from pexproject_flightdata p1 "+qry3+"where " + querylist + " order by finalprice,totaltax , departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset)
            print finalquery
            record = Flightdata.objects.raw(finalquery)
            for row in record:
                mainlist1=''
                multirecordlist = {}
                multidetail_list = {}
                pos = 0
                multirecordlist[pos] = {"origin":row.origin,"destination":row.destination,"stoppage":row.stoppage,"departure":row.departure,"arival":row.arival,"duration":row.duration}
                multidetail_list[pos] = {"departdetails":row.departdetails,"arivedetails":row.arivedetails,"planedetails":row.planedetails,"operatedby":row.operatedby}
                pos = pos+1
                
                for i in range(2,len(multicitykey1)+1):
                    org = getattr(row, "origin"+str(i))
                    stop = getattr(row, "stoppage"+str(i))
                    dest = getattr(row, "destination"+str(i))
                    depart = getattr(row, "departure"+str(i))
                    arival = getattr(row, "arival"+str(i))
                    duration = getattr(row,"duration"+str(i))
                    dept_detail = getattr(row,"departdetails"+str(i))
                    arive_detail = getattr(row,"arivedetails"+str(i))
                    plane_detail = getattr(row,"planedetails"+str(i))
                    operate_detail = getattr(row,"operatedby"+str(i))
                    
                    data = {"origin":org,"destination":dest,"stoppage":stop,"departure":depart,"arival":arival,"duration":duration}
                    multirecordlist[pos]=data
                    multidetail_list[pos] = {"departdetails":dept_detail,"arivedetails":arive_detail,"planedetails":plane_detail,"operatedby":operate_detail}
                    pos=pos+1
                mainlist1 = {"newid":row.newid,"flighno":row.flighno,"datasource":row.datasource,"cabintype1":row.cabintype1,"cabintype2":row.cabintype2,"cabintype3":row.cabintype3,"finalprice":row.finalprice,"taxes":row.totaltax,"origin":multirecordlist,"multidetail_list":multidetail_list}
                mainlist.append(mainlist1)
        else:
            if (returnkeyid1 and ('rowid' not in request.GET) and 'rowid' not in request.POST) or len(multicitykey1) > 0:
                totalfare = "p1." + cabinclass + "+p2." + cabinclass
                returnfare = "p2." + cabinclass
                departfare = "p1." + cabinclass
                totaltax = "p1."+taxes+"+p2."+taxes
                record = Flightdata.objects.raw("select p1.*,CONCAT(p1.rowid,'_',p2.rowid) as newid,p2.origin as origin1,p2.rowid as rowid1, p2.stoppage as stoppage1,p2.flighno as flighno1, p2.cabintype1 as cabintype11,p2.cabintype2 as cabintype21,p2.cabintype3 as cabintype31, p2.destination as destination1, p2.departure as departure1, p2.arival as arival1, p2.duration as duration1, p2.maincabin as maincabin1, p2.maintax as maintax1, p2.firsttax as firsttax1, p2.businesstax as businesstax1,p2.departdetails as departdetails1,p2.arivedetails as arivedetails1, p2.planedetails as planedetails1,p2.operatedby as operatedby1," + totalfare + " as finalprice,  "+totaltax+" as totaltaxes from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ='" + returnkeyid1 + "' and " + returnfare + " > '0'  where  p1.searchkeyid = '" + searchkey + "' and " + departfare + " > 0 and " + querylist + " order by finalprice ,totaltaxes, departure, p2.departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset))
            
            else:
                cabintype = " and " + cabinclass + " > 0"
                querylist = querylist+cabintype
                record = Flightdata.objects.raw("select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice  from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset))
            mainlist = record  
        recordlen = len(multicitykey1)
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        filterkey = {'stoppage':list2, 'datasource':list1, 'cabin':cabin} 
        if depttime:
            timeinfo = {'maxdept':deptmaxtime, 'mindept':depttime, 'minarival':arivtime, 'maxarival':arivtmaxtime}
        else:
            timeinfo = ''
        if 'share_recordid' in request.GET:
            sharedid = request.GET.get('share_recordid','')
            selectedrow = Flightdata.objects.get(pk=sharedid)
              

        if request.is_ajax():
            return render_to_response('flightsearch/search.html', {'action':action, 'data':mainlist,'multirecod':mainlist, 'multicity':multicity, 'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name}, context_instance=RequestContext(request))
        if totalrecords > 0:
            return render_to_response('flightsearch/searchresult.html', {'action':action,'data':mainlist,'multirecod':mainlist,'multicity':multicity,'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name}, context_instance=RequestContext(request)) 
        else:
            
            if request.is_ajax():
                
                return render_to_response('flightsearch/search.html', {'action':action, 'data':record, 'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name}, context_instance=RequestContext(request))
            #msg = "Sorry, No flight found  from " + source + " To " + destination + ".  Please search for another date or city !"
            msg = "Oops, looks like there aren't any flight results for your filtered search. Try to broaden your search criteria for better results."
            return  render_to_response('flightsearch/flights.html', {'message':msg, 'search':searchdata[0],'returndate':returndate}, context_instance=RequestContext(request))
            
def share(request):
    context = {}
    if 'selectedid' in request.GET:
        selectedid = request.GET.get('selectedid', '')
        cabin = request.GET.get('cabin', '')
        traveler = request.GET.get('passenger', '')
        # record = Flightdata.objects.get(pk=selectedid)
        record = get_object_or_404(Flightdata, pk=selectedid)
        returnrecord = ''
        price = 0
        tax = 0
        returncabin = ''
        if 'returnrowid' in request.GET:
            returnrowid = request.GET.get('returnrowid', '')
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
        return render_to_response('flightsearch/share.html', {'record':record, 'cabin':cabin, 'traveler':traveler, 'returnrecord':returnrecord, "price":price, "tax":tax, 'returncabin':returncabin}, context_instance=RequestContext(request))



def multicity(request):
    context = {}
    
    return render_to_response('flightsearch/multicity.html', context_instance=RequestContext(request)) 
        
    
            

	
# Create your views here.
