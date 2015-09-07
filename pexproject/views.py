#!/usr/bin/env python
import os,sys
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
import json
from django.db.models import Q
#from django.template.context_processors import csrf
from datetime import timedelta
import subprocess
#from datetime import datetime,date
import datetime
from subprocess import Popen
import subprocess
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
    context = {}
    if request.method == "POST":
        if 'search' in request.REQUEST:
            querylist =''
            join=''
            economy=''
            list=''
            multicabin=''
            if 'stoppage' in request.POST:
                list = request.POST.getlist('stoppage')
                if len(list)>1:
                    querylist = querylist+join+"stoppage IN ('"+"','".join(list)+"')"
                    join = ' AND '
                else:
                    if(len(list) > 0):
                        querylist = querylist+join+"stoppage = '"+list[0]+"'"
                        join = ' AND '
                print querylist
                
                
            if 'cabintype1' in request.POST:
                economy = request.REQUEST['cabintype1']
                
                if economy != '':
                    querylist = querylist+join+" cabintype1 LIKE '%%"+economy+"%%'" 
            print querylist
            records = Flightdata.objects.raw('select * from pexproject_flightdata where '+querylist)
            
            
              
            '''       
            if 'cabintype2' in request.POST:
                multicabin = request.POST.getlist('cabintype2')
        
            print list,economy,multicabin
                    
            record = Flightdata.objects.filter(Q(stoppage__in=list),Q(cabintype1__contains=economy))
            print record
           
            if 'nonstop' in request.REQUEST:
                nonstop = request.REQUEST['nonstop']
            if 'onestop' in request.REQUEST:
                onestop = request.REQUEST['onestop']
                print "one stop",onestop
            if 'cabintype1' in request.REQUEST:
                econ = request.REQUEST['cabintype1']
            #if 'twostop' in request.REQUEST:
                #twostop = request.REQUEST['twostop']
                #print econ
            if nonstop != '' or onestop != '':
                record = Flightdata.objects.filter(Q(stoppage__in=[nonstop,onestop]),Q(cabintype1__contains=econ))
            else:
                record = Flightdata.objects.filter(cabintype1__contains=econ)
            print record
            '''
            #searchkey = request.GET.get('keyid', '')
            #searchdata = Searchkey.objects.filter(searchid=searchkey)
            searchdata =''
            filerkey =  {'stoppage':list,'economy':economy}
        
            #print filerkey.economy 

            return render_to_response('flightsearch/searchresult.html',{'data':records,'search':searchdata,'filterkey':filerkey},context_instance=RequestContext(request))
            print data
            for key in request.POST.iterkeys():
                if key != "csrfmiddlewaretoken" and key != "buying_slider_min" and key != "search":
                    valuelist = request.POST[key]
                    print key
                    print valuelist
                    record = Flightdata.objects.filter(key=valuelist)
                    print record
                '''
                if key != "csrfmiddlewaretoken" and key != "buying_slider_min" and key != "search":
                    valuelist = request.POST.gietlist(key)
                    print valuelist
                    mstring.extend(['%s="%s"' % (key, val) for val in valuelist])
                    print "---------------"
            
            print querylist
            '''
            
            searchdata =''
            return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata},context_instance=RequestContext(request))
            
    if request.is_ajax():
        context = {}
        orgn = request.REQUEST['fromMain'] 
        dest = request.REQUEST['toMain'] 
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
        date = dt.strftime('%Y/%m/%d')
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
            
            #p1 = Popen(["python", "delta.py"], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
            #stderr = p1.communicate()
            
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
        print len(record)
        return render_to_response('flightsearch/searchresult.html',{'data':record,'search':searchdata},context_instance=RequestContext(request)) 
    
        

	
# Create your views here.
