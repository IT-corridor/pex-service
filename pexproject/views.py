#!usr/bin/env python
import os
import sys
import hashlib
import codecs
import datetime
import settings
import time
import MySQLdb
import threading
import requests
import operator
import smtplib
import socket
import re
import base64
import subprocess
import json
import signal
import logging
from random import randint
from bs4 import BeautifulSoup
from mailchimp import Mailchimp
from types import *
from datetime import datetime as dttime
from datetime import timedelta
from multiprocessing import Process
from threading import Thread
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.template import RequestContext, loader
from social_auth.models import UserSocialAuth
#from djnago.conf import settings
from django.shortcuts import get_object_or_404,redirect
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth import login as social_login,authenticate,get_user
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection, transaction
from django.db.models import Q, Count
from django.db.models import Max, Min

from django.utils import timezone
from django.forms.models import model_to_dict

from customfunction import is_scrape_vAUS,is_scrape_aeroflot,is_scrape_virginAmerica,is_scrape_etihad,is_scrape_delta,is_scrape_united,is_scrape_virgin_atlantic,is_scrape_jetblue,is_scrape_aa, is_scrape_s7, is_scrape_airchina
import customfunction
import rewardScraper
from .form import *
from pexproject.models import *
from pexproject.templatetags.customfilter import floatadd, assign

logger = logging.getLogger(__name__)

'''
def error(request):
    Http404("Poll does not exist")
    return  render_to_response('flightsearch/admin/index.html', context_instance=RequestContext(request))
'''

def get_cityname(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        airport = Airports.objects.filter(Q(code__istartswith=q)).order_by('code','cityName')[:20]    
        if len(list(airport)) < 1:
            airport = Airports.objects.filter(Q(cityName__istartswith=q)|Q(name__istartswith=q)).order_by('code','cityName')[:20]
        results = []
        airportcode = []
        for airportdata in airport:
            if airportdata.code not in airportcode:
                airportcode.append(airportdata.code)
                airport_json = {}
                airport_json['id'] = airportdata.airport_id
                airport_json['label'] = airportdata.cityName + ", " + airportdata.name + ", " + airportdata.countryCode + "  (" + airportdata.code + " )"
                airport_json['value'] = airportdata.cityName
                results.append(airport_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def index(request):
    context = {}
    user = User()
    image = ''
    image = GoogleAd.objects.filter(ad_code="index")

    ''' Fetch recent results'''
    searches = []
    recordFromActiveTable = 0
    img_cityName = []
    
    recent_searches = Searchkey.objects.raw("select ps.destination, ps.searchid,ps.destination,ps.destination_city as final_dest,pfs1.maincabin as maincabin,pfs1.maintax from pexproject_searchkey as ps inner join (select pf1.* from pexproject_flightdata as pf1 inner join (select  (min(if(pf.maincabin > 0 ,pf.maincabin,NULL))) as maincabin, searchkeyid from pexproject_flightdata as pf  where pf.origin <> 'flag' and pf.maincabin >0  group by pf.searchkeyid) pfs on pf1.searchkeyid = pfs.searchkeyid and pf1.maincabin = pfs.maincabin order by pf1.scrapetime desc)  as pfs1 on pfs1.searchkeyid = ps.searchid group by destination_city order by ps.scrapetime desc limit 8")
    recent_searches1 = list(recent_searches)
    for s in recent_searches1:
        if s.final_dest:
            img_cityName.append(s.final_dest)
    img_cityName2 = "','".join(img_cityName)
    recordFromActiveTable = len(recent_searches1)
    dataFromAcradeTable = ''
    
    if recordFromActiveTable < 8:
        nextLimit = 8 - recordFromActiveTable 
        dataFromAcradeTable1 = Searchkey.objects.raw("select ps.destination, ps.searchid,ps.destination,ps.destination_city as final_dest,pfs1.maincabin as maincabin,pfs1.maintax from pexproject_searchkey as ps inner join (select pf1.* from arcade_flight_data as pf1 inner join (select  (min(if(pf.maincabin > 0 ,pf.maincabin,NULL))) as maincabin, searchkeyid from arcade_flight_data as pf  where pf.origin <> 'flag' and pf.maincabin >0  group by pf.searchkeyid) pfs on pf1.searchkeyid = pfs.searchkeyid and pf1.maincabin = pfs.maincabin order by pf1.scrapetime desc)  as pfs1 on pfs1.searchkeyid = ps.searchid where ps.destination_city not in ('"+img_cityName2+"') group by destination order by ps.scrapetime desc limit "+str(nextLimit))
        dataFromAcradeTable = list(dataFromAcradeTable1)

    
    if dataFromAcradeTable:
        for city in dataFromAcradeTable:
            img_cityName.append(city.final_dest)
         
    img_cityName1 = "','".join(img_cityName)
    cityobj = CityImages.objects.raw("select city_image_id,image_path,city_name from pexproject_cityimages where city_image_id IN( select max(city_image_id) from pexproject_cityimages where city_name in  ('"+img_cityName1+"') and status= '1' group by city_name ) ")
    cityobj1 = list(cityobj)
    for s in recent_searches1:
        img_path =''
        for data in cityobj1:
            if s.final_dest == data.city_name:
               img_path = data.image_path 
               break
        searches.append({'final_dest':s.final_dest,'maintax':s.maintax,'searchkeyid':s.searchid,'maincabin':s.maincabin,'image_path':img_path})     
    for rcd in dataFromAcradeTable:
        img_path =''
        for data in cityobj1:
            if rcd.final_dest == data.city_name:
               img_path = data.image_path 
               break
        searches.append({'final_dest':rcd.final_dest,'maintax':rcd.maintax,'searchkeyid':rcd.searchid,'maincabin':rcd.maincabin,'image_path':img_path})
    
    if request.is_ajax() and 'pexdeals' in request.REQUEST:
        request.session['pexdeal'] = request.REQUEST['pexdeals']
        mimetype = 'application/json'
        data = "success"
        json.dumps(data)
        return HttpResponse(data, mimetype)
    if request.user.username:
    	username = request.user.username
        if request.user.user_id:
            request.session['userid']= request.user.user_id
    	user1 = User.objects.get(username=username)
        fname=''
        lname=''
        if user1.email:
    	    request.session['username'] =user1.email
        if user1.first_name:
            request.session['first_name'] =user1.first_name
            fname = user1.first_name
        if user1.last_name:
            lname = user1.last_name
    	request.session['password'] = user1.password        
	if 'pexdeal' in request.session:
	
	    subscriber = Mailchimp(customfunction.mailchimp_api_key)
	    subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':username}, merge_vars={'FNAME':fname,'LNAME':lname})
       	   
    return  render_to_response('flightsearch/index.html',{'image':image,'searchObj':searches,'title':"Search Flights on PEX+"}, context_instance=RequestContext(request))

def flights(request):
    context = {}
    mc = ''
    objects = ''
    searches = []
    img_path =''
    img_cityName = []
    recent_searches = Searchkey.objects.raw("select ps.destination, ps.searchid,ps.destination,ps.destination_city as final_dest,pfs1.maincabin as maincabin,pfs1.maintax from pexproject_searchkey as ps inner join (select pf1.* from pexproject_flightdata as pf1 inner join (select  (min(if(pf.maincabin > 0 ,pf.maincabin,NULL))) as maincabin, searchkeyid from pexproject_flightdata as pf  where pf.origin <> 'flag' and pf.maincabin >0  group by pf.searchkeyid) pfs on pf1.searchkeyid = pfs.searchkeyid and pf1.maincabin = pfs.maincabin order by pf1.scrapetime desc)  as pfs1 on pfs1.searchkeyid = ps.searchid group by destination_city order by ps.scrapetime desc limit 8")
    recent_searches1 = list(recent_searches)
    for s in recent_searches1:
        if s.final_dest:
            img_cityName.append(s.final_dest)
    img_cityName2 = "','".join(img_cityName)        
    recordFromActiveTable = len(recent_searches1)
    dataFromAcradeTable = ''
    if recordFromActiveTable < 8:
        nextLimit = 8 - recordFromActiveTable 
        dataFromAcradeTable1 = Searchkey.objects.raw("select ps.destination, ps.searchid,ps.destination,ps.destination_city as final_dest,pfs1.maincabin as maincabin,pfs1.maintax from pexproject_searchkey as ps inner join (select pf1.* from arcade_flight_data as pf1 inner join (select  (min(if(pf.maincabin > 0 ,pf.maincabin,NULL))) as maincabin, searchkeyid from arcade_flight_data as pf  where pf.origin <> 'flag' and pf.maincabin >0  group by pf.searchkeyid) pfs on pf1.searchkeyid = pfs.searchkeyid and pf1.maincabin = pfs.maincabin order by pf1.scrapetime desc)  as pfs1 on pfs1.searchkeyid = ps.searchid where ps.destination_city not in ('"+img_cityName2+"') group by destination order by ps.scrapetime desc limit "+str(nextLimit))
        dataFromAcradeTable = list(dataFromAcradeTable1)

    
    if dataFromAcradeTable:
        for city in dataFromAcradeTable:
            img_cityName.append(city.final_dest)
         
    img_cityName1 = "','".join(img_cityName)
    cityobj = CityImages.objects.raw("select city_image_id,image_path,city_name from pexproject_cityimages where city_image_id IN( select max(city_image_id) from pexproject_cityimages where city_name in  ('"+img_cityName1+"') and status= '1' group by city_name ) ")
    cityobj1 = list(cityobj)
    for s in recent_searches1:
        img_path =''
        for data in cityobj1:
            if s.final_dest == data.city_name:
               img_path = data.image_path 
               break
        searches.append({'final_dest':s.final_dest,'maintax':s.maintax,'searchkeyid':s.searchid,'maincabin':s.maincabin,'image_path':img_path})  
    for rcd in dataFromAcradeTable:
        img_path =''
        for data in cityobj1:
            if rcd.final_dest == data.city_name:
               img_path = data.image_path 
               break
        searches.append({'final_dest':rcd.final_dest,'maintax':rcd.maintax,'searchkeyid':rcd.searchid,'maincabin':rcd.maincabin,'image_path':img_path})
  
    if 'action' in request.GET:
        mc = request.GET.get('action','')
    searchdata = ''
    msg = ''
    returndate = ''
    #@@@@@@@  search Fliter data to prefill in no search found @@@@@@@
    if 'multicitykeys' in request.GET:
        keys = request.GET.get('multicitykeys','')
        allkeys =  keys.split(',')
        objects = Searchkey.objects.filter(searchid__in=allkeys)
        mc = 'mc'
    elif 'keyid' in request.GET:
        keyid = request.GET['keyid']
        searchdata = Searchkey.objects.get(searchid=keyid)
        if 'returnkey' in request.GET:
            returnkey = request.GET['returnkey']
            returndate = Searchkey.objects.values_list('traveldate', flat=True).get(searchid=returnkey)
        msg = "Oops, looks like there aren't any flight results for your filtered search. Try to broaden your search criteria for better results."
    
    return  render_to_response('flightsearch/flights.html',{'mc':mc,'message':msg,'search':searchdata,'searchparams':objects,'searchObj':searches,'returndate':returndate,'title':"Find Cheap Flights and Airline Tickets Using Miles | PEX+"}, context_instance=RequestContext(request))
        
def staticPage(request):
    context = {}
    page = ''
    curr_path = request.get_full_path()
    action = ''
    if 'staticPage/' in curr_path:
        pageName = curr_path.split('staticPage/')
        if len(pageName) > 1:
            if '?' in pageName[1]:
                pageName1 = pageName[1].split('?')
                page= pageName1[0]
            elif '/' in pageName[1]:
                pageName1 = pageName[1].split('/')
                page= pageName1[0]
                if len(pageName1) > 1:
                    action = pageName1[1]
            else:
                page  = pageName[1].strip()
            return  render_to_response('flightsearch/'+page+'.html',{'action':action}, context_instance=RequestContext(request))
        return  render_to_response('flightsearch/Help.html',{'action':action}, context_instance=RequestContext(request))
    return  render_to_response('flightsearch/About.html',{'action':action}, context_instance=RequestContext(request))

def blog(request, title=None):
    context = {}
    curr_path = request.get_full_path()
    if 'blog/' in curr_path:
	blog_title1 = curr_path.split('blog/')
	if len(blog_title1)>1:
	    blog_title = blog_title1[1].strip()
        try:
            blog = Blogs.objects.get(blog_url=blog_title)
            title = blog.blog_title
            return render_to_response('flightsearch/blog_details.html',{'blog':blog}, context_instance=RequestContext(request))
        except:
            return render_to_response('flightsearch/blog_details.html', context_instance=RequestContext(request))
	
    blogs = Blogs.objects.filter(blog_status=1)
    bloglist = []
    top_banner = ''
    for content in blogs:
	blog_title = content.blog_title
	blog_content = content.blog_content
	#blog_url = content.blog_url
	#metakey = content.blog_meta_key
	#meta_desc = content.blog_meta_Description
	#blog_creator = content.blog_creator
	tree = BeautifulSoup(blog_content)
	img_link = ''
	if tree.find('img'):
	    img_link = tree.find('img')['src']
	if content.blog_position == True:
	    top_banner = {"blog_title":content.blog_title,'img_link':img_link,'postedon':content.blog_created_time,'featured_image':content.blog_image_path,'blog_url':content.blog_url,'blogid':content.blog_id}
	else: 
	    bloglist.append({"blog_title":content.blog_title,'img_link':img_link,'postedon':content.blog_created_time,'featured_image':content.blog_image_path,'blog_url':content.blog_url,'blogid':content.blog_id})
	
    
    return  render_to_response('flightsearch/Blog.html',{"blog":bloglist,"top_banner":top_banner}, context_instance=RequestContext(request))

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
                return HttpResponseRedirect('/index?signup_msg='+msg)
                #return render_to_response('flightsearch/index.html',{'signup_msg':msg},context_instance=RequestContext(request))
            password = request.REQUEST['password']
            password1 = hashlib.md5(password).hexdigest()
            airport = request.REQUEST['home_airport']
            first_name = ''
            last_name = ''
            pexdeals = 0
            if 'first_name' in request.POST:
                first_name = request.REQUEST['first_name']
            if 'last_name' in request.POST:
                last_name = request.REQUEST['last_name']
            if 'pexdeals' in request.REQUEST:
                pexdeals = request.REQUEST['pexdeals']

            object = User(username=email,email=email, password=password1,first_name=first_name,last_name=last_name, home_airport=airport,last_login=time,pexdeals=pexdeals)
            object.save()
            if pexdeals == '1':
                subscriber = Mailchimp(customfunction.mailchimp_api_key)
                subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':email}, merge_vars={'FNAME':first_name,'LNAME':last_name})
            request.session['username'] = email
            request.session['homeairpot'] = airport
            request.session['password'] = password1
            if first_name != '':
                request.session['first_name'] = first_name
            if object.user_id:
                request.session['userid'] = object.user_id
                msg = "Thank you, You have been successfully registered."
                emailbody=''
                obj = EmailTemplate.objects.get(email_code='signup')
                email_sub = obj.subject
                emailbody = obj.body
                emailbody = emailbody.replace('[USER_NAME]',first_name)
                emailbody = emailbody.replace('[SITE-LINK]','<a href="http://pexportal.com/">pexportal</a>')
                
                html_content=''
                try:
                    resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
                except:
                    print "something wrong"
                return HttpResponseRedirect('/index?welcome_msg='+msg)
                #return render_to_response('flightsearch/index.html',{'welcome_msg':msg}, context_instance=RequestContext(request))   
        #return render_to_response('flightsearch/index.html', context_instance=RequestContext(request))
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('index'))

def myRewardPoint(request):
    cursor = connection.cursor()
    context = {}
    points = ''
    temp_message = ''
    updatemsg = ''
    resp = ''
    datasource = []
    userid = request.session['userid']
    if 'account' in request.GET:
        cursor.execute("select * from reward_point_credential where user_id="+str(userid))
        user_account = cursor.fetchall()
        threads = []
        for obj in user_account:
            p = Thread(target=customfunction.syncPoints, args=(obj[4],userid,obj[2],obj[5],obj[3]))
            p.start()
            threads.append(p)
        for t in threads:
            t.join()
        updatemsg = "Your account has been updated successfully"     
        
    if 'userid' in request.GET and 'airline' in request.GET:
        pointsource = request.REQUEST['airline']
        cursor.execute("select * from reward_point_credential where user_id="+str(userid)+" and airline = '"+pointsource+"'")
        user = cursor.fetchone()
        resp = customfunction.syncPoints(pointsource,userid,user[2],user[5],user[3])
        if resp == "fail":
            updatemsg = "There is some technical problem, please try after some time"
        else:
            updatemsg = "Your account has been updated successfully"
    if request.is_ajax():
        airline_name = request.REQUEST['acct']
        cursor.execute("delete from reward_point_credential where user_id="+str(userid)+" and airline = '"+airline_name+"'")
        cursor.execute("delete from reward_points where user_id="+str(userid)+" and airlines = '"+airline_name+"'")
        mimetype = 'application/json'
        data = "success"
        json.dumps(data)
    	return HttpResponse(data, mimetype)
    if request.POST:
        username = request.REQUEST['username']
        password = request.REQUEST['password']
        skymiles_number = request.REQUEST['skymiles_number']
        airline = request.REQUEST['airline']
        action = request.REQUEST['action']
        if action == 'update' :
                 
            resp = customfunction.syncPoints(airline,userid,username,skymiles_number,password)
            if resp == "fail":
                updatemsg = "Invalid account credentials"
            else:
                cursor.execute("update reward_point_credential set username='"+username+"', password='"+password+"', skymiles_number="+skymiles_number+" where airline='"+airline+"' and user_id="+str(userid))
                transaction.commit()
                updatemsg = "Your account has been updated successfully"
        else:
            resp = customfunction.syncPoints(airline,userid,username,skymiles_number,password)
            if resp == "fail":
                temp_message = "Invalid Username or Password"  
            if resp == 'success':
                cursor.execute ("INSERT INTO reward_point_credential (user_id,username,password,airline,skymiles_number) VALUES (%s,%s,%s,%s,%s);", (str(userid),username,password,airline,skymiles_number))
                transaction.commit()
        
    cursor.execute("select * from reward_points where user_id="+str(userid))
    points = cursor.fetchall()
    for row in points: 
        datasource.append(row[3])
    return render_to_response('flightsearch/myrewardpoint.html',{'updatemsg':updatemsg,'datasource':datasource,'points':points,'temp_message':temp_message}, context_instance=RequestContext(request))

def manageAccount(request):
    cursor = connection.cursor()
    context = {}
    msg = ''
    password1 =''
    userid = ''
    issocial =''
    newpassword1 = ''
    #member = mailchimp_user.lists.member_info(customfunction.mailchiml_List_ID,{'email_address':'B.jessica822@gmail.com'})
    subscription = ''
    email1 = request.session['username']
    mailchimp_user = Mailchimp(customfunction.mailchimp_api_key)
    m = mailchimp_user.lists.member_info(customfunction.mailchiml_List_ID,[{'email':email1}])['data']
    if len(m) > 0 and 'subscribed' in m[0]['status']:
        subscription = 'subscribed'
    
    user1 = User.objects.get(pk =request.session['userid']) 
    cursor.execute("select provider from social_auth_usersocialauth where user_id ="+str(request.session['userid']))
    social_id = cursor.fetchone()
    if social_id:	
        issocial = 'yes'
    if request.POST:
        if 'home_ariport' in request.POST:
            user1.home_airport = request.POST['home_ariport']
            isupdated  = user1.save()
        if 'home_ariport' not in request.POST:
            user1.first_name = request.POST['first_name']
            user1.middlename = request.POST['middlename']
            user1.last_name = request.POST['last_name']
            user1.gender = request.POST['gender']
            if request.POST['dateofbirth']:
                user1.date_of_birth = request.POST['dateofbirth']
            else:
                user1.date_of_birth = None
            user1.address1 = request.POST['address1']
            user1.address2 = request.POST['address2']
            user1.city = request.POST['city']
            user1.state = request.POST['state']
            user1.zipcode = request.POST['zipcode']
            user1.country = request.POST['country']
            user1.phone = request.POST['phone']
            user1.save() 
    user1 = User.objects.get(pk =request.session['userid'])  
    return render_to_response('flightsearch/manage_account.html',{'message':msg,'user':user1,'issocial':issocial,'subscription':subscription}, context_instance=RequestContext(request))

def mailchimp(request):
    context = {}
    if request.is_ajax():
    	lname=''
    	fname=''
        useremail = request.REQUEST['email']
    	if 'fname' in request.POST:
                fname = request.REQUEST['fname']
    	if 'lname' in request.POST:
                lname = request.REQUEST['lname']
        data = ''
        try:
            subscriber = Mailchimp(customfunction.mailchimp_api_key)
            subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':useremail}, merge_vars={'FNAME':fname,'LNAME':lname})
            data = "Please check you email to PEX+ update"
        except:
            data = useremail + " is an invalid email address"   
        mimetype = 'application/json'
        
        json.dumps(data)
        return HttpResponse(data, mimetype)

def login(request):
    context = {}
    user = User()
    user = authenticate()
    currentpath = ''
    print "user", user
    if user is not None:
        if user.is_active:
            social_login(request,user)	
    if request.method == "POST": 
        username = request.REQUEST['username']
        password = request.REQUEST['password']
        if "curl" in request.POST:
            currentpath = request.REQUEST['curl']
        password1 = hashlib.md5(password).hexdigest()
    	print password1
    	print username
    	try:
            user = User.objects.get(email=username, password=password1)
            if user > 0:
                request.session['username'] = username
                request.session['password'] = password1
                if user.first_name != '':
                    request.session['first_name'] = user.first_name
                if user.home_airport != '':
                    request.session['homeairpot'] = user.home_airport
                request.session['userid'] = user.user_id
                if currentpath:
                    return HttpResponseRedirect(currentpath)
                return HttpResponseRedirect(reverse('index'))
            else:
                msg = "Invalid username or password"
                return HttpResponseRedirect('/index?msg='+msg)
                #return render_to_response('flightsearch/index.html', {'msg':msg}, context_instance=RequestContext(request))
    	except:
    	    msg = "Invalid username or password"
            return HttpResponseRedirect('/index?msg='+msg)
            #return render_to_response('flightsearch/index.html', {'msg':msg}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('index'))

def logout(request):
    context = {} 
    auth_logout(request)
    if 'username' in request.session:
    	del request.session['username']
        del request.session['homeairpot']
    	del request.session['password']  
    return HttpResponseRedirect(reverse('index'))

def forgotPassword(request):
    context = {}
    msg =''   
    if request.POST:
        user_email =  request.POST['email']
        randomcode = randint(100000000000,999999999999)
        usercode =  base64.b64encode(str(randomcode))
        if 'userid' in request.session:
            user = User.objects.get(pk = request.session['userid'])
        else:
            try:
                user = User.objects.get(email=user_email)
            except:
                return HttpResponseRedirect('/index?msg=Invalid username')
                #return render_to_response('flightsearch/index.html', {'msg':"Invalid username"}, context_instance=RequestContext(request))
        text = ''
        print "user",user
        if user > 0:
            #subject = "Manage Your Password"
            obj = EmailTemplate.objects.get(email_code='forgotPassword')
            email_sub = obj.subject
            emailbody = obj.body
            emailbody = emailbody.replace('[USER_NAME]',user_email)
            emailbody = emailbody.replace('[RESET-LINK]','<a href="http://pexportal.com/createPassword?usercode='+usercode+'">Click here</a>')
            resp = customfunction.sendMail('PEX+',user_email,email_sub,emailbody,text)
            if resp == "sent":
                user.usercode = usercode
                currentdatetime = datetime.datetime.now()
                time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
                user.user_code_time = time
                user.save()
                text = "Please check your registered email id to create new password"
            else:
                text = "There is some technical problem. Please try again"
            
    if 'pagetype' in request.POST:
        return HttpResponseRedirect('/index?welcome_msg='+text)
    if request.is_ajax():
        mimetype = 'application/json'
        data = text
        json.dumps(data)
        return HttpResponse(data, mimetype)
        
    else:
        msg = "forgot password"
    return HttpResponseRedirect('/index?fpmsg='+msg) 
def createPassword(request):
    context = {}
    msg = ''
    currentdatetime = datetime.datetime.now()
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    time1 = datetime.datetime.now() - timedelta(hours=2)
    time1 = time1.strftime('%Y-%m-%d %H:%M:%S') 
    code = request.GET.get('usercode','')
    try:
       user = User.objects.get(usercode=code,user_code_time__gte=time1)
    except:
        msg = "Invalid or expired your password management code."     
    if request.POST:
    	code = request.REQUEST['ucode']
    	user1 = User.objects.get(usercode=code)
        if 'new_password' in request.POST:
            newpassword = request.REQUEST['new_password']
            newpassword1 = hashlib.md5(newpassword).hexdigest()
            user1.password=newpassword1
            user1.save()
            msg = "Your password has been reset successfully."
    return render_to_response('flightsearch/create_password.html',{'message':msg},context_instance=RequestContext(request))    
def sendFeedBack(request):
    context = {}
    alert_msg = ''
    if request.POST:
        html_content=''
        body = ''
        topic = ''
        topic = request.REQUEST['topic']
        from_emailid = request.REQUEST['emailid']
        if 'message' in request.POST:
            message = request.REQUEST['message']
            body = body+message
        if 'text' in request.POST:
            text = request.REQUEST['text']
            text = strip_tags(text)
            body = body+'\n'+text
    
        obj = EmailTemplate.objects.get(email_code='feedback')
        email_sub = obj.subject
        emailbody = obj.body
        emailbody = emailbody.replace('[USERNAME]',from_emailid)
        emailbody = emailbody.replace('[FEEDBACK_MESSAGE]',body)
        resp = customfunction.sendMail(from_emailid,'info@pexportal.com',topic,emailbody,html_content)
        if resp == "sent":
            obj1 = EmailTemplate.objects.get(email_code='feedback_reply')
            email_sub1 = obj1.subject
            emailbody1 = obj1.body
            emailbody1 = emailbody1.replace('[USERNAME]',from_emailid)
            customfunction.sendMail('info@pexportal.com',from_emailid,email_sub1,emailbody1,html_content)
            alert_msg = "Thanks for giving us feedback"
        else:
            alert_msg = "There is some technical problem. Please try again"
    return render_to_response('flightsearch/feedback.html',{'alert_msg':alert_msg}, context_instance=RequestContext(request))

def contactUs(request):
    context = {}
    first_name = ''
    last_name = ''
    title = ''
    company = ''
    phone = ''
    email = ''
    websitename = ''
    labeltext = ''
    message = ''
    topic = ''
    contact_msg = ''
    html_content = ''
    if request.POST:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        title = request.POST['title']
        company = request.POST['company']
        message = request.POST['message']
        topic = request.POST['topic']
        labeltext = request.POST['label_text']
        labeltext = strip_tags(labeltext)
        phone = request.POST['phone']
        websitename = request.POST['website']
        email = request.POST['email']
        object = Contactus(first_name=first_name,last_name=last_name,email=email,phone=phone,title=title,company=company,website=websitename,message=message,topic=topic,label_text= labeltext)
        object.save()
        fullname = first_name+" "+last_name
        emailbody = message+"\n\n"+labeltext+" \n\n"+fullname+"\n"+company+"\n"+websitename
        
        resp = customfunction.sendMail(email,'info@pexportal.com',topic,emailbody,html_content)
        if resp == "sent":
            contact_msg = "Your information has been sent successfully"
        else:
            contact_msg = "There is some technical problem. Please try again"    
    return render_to_response('flightsearch/contact_us.html',{'contact_msg':contact_msg}, context_instance=RequestContext(request))  
        
def search(request):
    if request.is_ajax():
        returndate = request.POST['returndate']
        orgnid = request.POST['fromMain']
        destid = request.POST['toMain']
        depart = request.POST['deptdate']
        searchtype = request.POST.get('searchtype', '')
        cabin = request.POST['cabin']

        key_json = _search(returndate, orgnid, destid, depart, searchtype, cabin)
        
        mimetype = 'application/json'
        data = json.dumps(key_json)
        return HttpResponse(data, mimetype)
        
def _search(returndate, orgnid, destid, depart, searchtype, cabin):
    ''' 
    trigger scrapers or return searchkey for cached search
    return searchkeys
    '''
    customfunction.flag = 0
    context = {}
    cursor = connection.cursor()

    dt1 = ''
    searchdate1 = ''
    multiplekey =''
    seperator = ''
    if returndate:
        dt1 = datetime.datetime.strptime(returndate, '%m/%d/%Y')
        date1 = dt1.strftime('%m/%d/%Y')
        searchdate1 = dt1.strftime('%Y-%m-%d')
    ongnidlist=''
    destlist = ''
    departlist =''
    searchkeyid = ''
    returnkey = ''

    ongnidlist =  orgnid.split(',')
    destlist = destid.split(',')
    departlist = depart.split(',')
    for i in range(0,len(departlist)):
        etihadorigin =''
        etihaddest = ''
        orgnid = ongnidlist[i]
        destid = destlist[i]
        depart = departlist[i]
        # todo get onle single row and remove for look for origin and destination
        originobj = Airports.objects.get(airport_id=orgnid)
        destobj = Airports.objects.get(airport_id=destid)
       
        orgn = originobj.cityName + ", " + originobj.cityCode + ", " + originobj.countryCode + "  (" + originobj.code + ")"
        etihadorigin = originobj.cityName
        orgncode = originobj.code
        origin = originobj.cityName + " (" + originobj.code + ")"
        print '@@@@', orgn, origin, '@@@@'

        dest = destobj.cityName + ", " + destobj.cityCode + ", " + destobj.countryCode + "  (" + destobj.code + ")"
        etihaddest = destobj.cityName
        destcode = destobj.code
        destination1 = destobj.cityName + " (" + destobj.code + ")"
        print '####', dest, destination1, '####'
        
        dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
        date = dt.strftime('%m/%d/%Y')
        searchdate = dt.strftime('%Y-%m-%d')        
        print '$$$$', searchdate, '$$$$'
        
        currentdatetime = datetime.datetime.now()
        time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        time1 = datetime.datetime.now() - timedelta(minutes=30)
        time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
        if searchdate1:
            obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)
            returnobj = Searchkey.objects.filter(source=destination1, destination=origin, traveldate=searchdate1, scrapetime__gte=time1)

            if len(returnobj) > 0:
                for retkey in returnobj:
                     returnkey = retkey.searchid
            else:
                searchdata = Searchkey(source=destination1, destination=origin, destination_city=etihadorigin,traveldate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid)
                searchdata.save()
                returnkey = searchdata.searchid
                if is_scrape_jetblue == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/jetblue.py",destcode, orgncode, str(returndate), str(returnkey)])
                if is_scrape_virginAmerica == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virginAmerica.py",destcode, orgncode, str(returndate), str(returnkey)])
                
                if is_scrape_delta == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/delta.py",destcode, orgncode, str(date1), str(returndate), str(returnkey),etihaddest,etihadorigin,cabin])
                if is_scrape_united == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/united.py",destcode, orgncode, str(returndate), str(returnkey)])
                if is_scrape_s7 == 1:
                    customfunction.flag = customfunction.flag+1
                    print '@@@@@ S7 Round trip', destobj.code, originobj.code, str(searchdate1), str(returnkey)                        
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/s7.ru.py",destobj.code, originobj.code, str(searchdate1), str(returnkey)])
                    # subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/s7.ru.py",destobj.cityCode, originobj.cityCode, str(searchdate1), str(returnkey)])
                if is_scrape_aa == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aa.py",destcode, orgncode, str(returndate), str(returnkey)])
                if is_scrape_vAUS == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virgin_australia.py",destcode, orgncode, str(returndate), str(returnkey),cabin])
               
                if is_scrape_etihad == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/etihad.py",etihaddest, etihadorigin, str(date1), str(returnkey),cabin])
            
            ''' Flexible date search scraper for return Date'''
            if returnkey and  'flexibledate' in searchtype:
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/Flex_delta.py",destcode, orgncode, str(returndate), str(returnkey),cabin])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/flex_jetblue.py",destcode, orgncode, str(returndate), str(returnkey)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/flex_virgin_atlantic.py",destcode, orgncode, str(returndate), str(returnkey)])
                    
            '''-------------------------------------'''
        else:
            obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)


        if len(obj) > 0:
            for keyid in obj:
                searchkeyid = keyid.searchid
        else:
            if dt1:
                searchdata = Searchkey(source=origin, destination=destination1,destination_city=etihaddest, traveldate=dt, returndate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid) 
            else:
                searchdata = Searchkey(source=origin, destination=destination1,destination_city=etihaddest, traveldate=dt, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid)
            searchdata.save()
            searchkeyid = searchdata.searchid 
            cursor = connection.cursor()
            ''' Flexible date search scraper for return Date'''
            if searchkeyid and  'flexibledate' in searchtype:
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/Flex_delta.py",orgncode,destcode, str(depart), str(searchkeyid),cabin])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/flex_jetblue.py",orgncode,destcode, str(depart), str(searchkeyid)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/flex_virgin_atlantic.py",orgncode,destcode, str(depart), str(searchkeyid)])
                    
            '''-------------------------------------'''
            customfunction.flag = 0
    #if searchdate1:
    #    customfunction.flag = 2
            if is_scrape_jetblue == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/jetblue.py",orgncode,destcode,str(depart),str(searchkeyid)])
            if is_scrape_virginAmerica == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virginAmerica.py",orgncode,destcode,str(depart),str(searchkeyid)])                
            if is_scrape_delta == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/delta.py",orgncode,destcode,str(date),str(depart),str(searchkeyid),etihadorigin,etihaddest,cabin])
            if is_scrape_united == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/united.py",orgncode,destcode,str(depart),str(searchkeyid)])
            if is_scrape_s7 == 1:
                customfunction.flag = customfunction.flag+1
                # print '@@@@@ S7 One way', originobj.cityCode, destobj.cityCode, str(searchdate), str(searchkeyid)                    
                print '@@@@@ S7 One way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)                    
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/s7.ru.py", originobj.code, destobj.code, str(searchdate), str(searchkeyid)])                    
                # subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/s7.ru.py", originobj.cityCode, destobj.cityCode, str(searchdate), str(searchkeyid)])                    
            if is_scrape_aa == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aa.py",orgncode,destcode,str(depart),str(searchkeyid)])
            if is_scrape_vAUS == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virgin_australia.py",orgncode,destcode,str(depart),str(searchkeyid),cabin])
            if is_scrape_etihad == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/etihad.py",etihadorigin,etihaddest,str(date),str(searchkeyid),cabin])
            if is_scrape_aeroflot == 1:
                if not searchdate1:
                    customfunction.flag = customfunction.flag+1 
                    print '@@@@@ Aeroflot One Way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aeroflot.py", originobj.code, destobj.code, str(searchdate), str(searchkeyid)])
            if is_scrape_airchina == 1:
                if not searchdate1:
                    customfunction.flag = customfunction.flag+1 
                    print '@@@@@ AirChina One Way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/airchina.py", originobj.code, destobj.code, str(searchdate), str(searchkeyid)])
                
        if is_scrape_virgin_atlantic == 1:
            customfunction.flag = customfunction.flag+1
            Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='virgin_atlantic').delete()
            if returnkey:
                Flightdata.objects.filter(searchkeyid=returnkey,datasource='virgin_atlantic').delete()            
            subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virgin.py",orgncode,destcode, str(depart), str(returndate), str(searchkeyid),str(returnkey)])

        if returnkey:
            if is_scrape_aeroflot == 1:
                flight_to = Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='aeroflot')
                flight_from = Flightdata.objects.filter(searchkeyid=returnkey,datasource='aeroflot') 
                if not (flight_to and flight_from):
                    customfunction.flag = customfunction.flag+1
                    Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='aeroflot').delete()
                    Flightdata.objects.filter(searchkeyid=returnkey,datasource='aeroflot').delete()            
                    print '@@@@@ Aeroflot Round Trip', orgncode, destcode, str(searchdate), str(searchkeyid), str(searchdate1), str(returnkey)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aeroflot_rt.py", orgncode, destcode, str(searchdate),str(searchkeyid), str(searchdate1), str(returnkey)])
            if is_scrape_airchina == 1:
                flight_to = Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='airchina')
                flight_from = Flightdata.objects.filter(searchkeyid=returnkey,datasource='airchina') 
                if not (flight_to and flight_from):
                    customfunction.flag = customfunction.flag+1
                    Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='airchina').delete()
                    Flightdata.objects.filter(searchkeyid=returnkey,datasource='airchina').delete()            
                    print '@@@@@ AirChina Round Trip', orgncode, destcode, str(searchdate), str(searchkeyid), str(searchdate1), str(returnkey)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/airchina_rt.py", orgncode, destcode, str(searchdate),str(searchkeyid), str(searchdate1), str(returnkey)])

        if len(departlist) > 0 :
            multiplekey = multiplekey+seperator+str(searchkeyid)
            seperator = ',' 
                    
    key_json = {}
    key_json['departkey'] = multiplekey
    key_json['returnkey'] = returnkey
    key_json['searchtype'] = searchtype    
    return key_json


def get_airport(request):
    
    if request.is_ajax():
        q = request.GET.get('term', '')
        airport = Airports.objects.filter(Q(code__istartswith=q)).order_by('code','cityName')[:20]    
        if len(list(airport)) < 1:
            airport = Airports.objects.filter(Q(cityName__istartswith=q)|Q(name__istartswith=q)).order_by('code','cityName')[:20]
        results = []
        airportcode = []
        for airportdata in airport:
            if airportdata.code not in airportcode:
	            airportcode.append(airportdata.code)
        	    airport_json = {}
	            airport_json['id'] = airportdata.airport_id
        	    airport_json['label'] = airportdata.cityName + ", " + airportdata.name + ", " + airportdata.countryCode + "  (" + airportdata.code + " )"
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
            passenger = request.POST['passenger']
            cabintype = request.POST['cabintype']
            orgn = ','.join(originlist)
            dest = ','.join(destinationlist)
            
        else:
            orgn = request.POST['fromMain'] 
            dest = request.POST['toMain'] 
            depart = request.POST['deptdate']
            passenger = request.POST['passenger']
            cabintype = ''
            if 'cabintype' in request.POST:
                cabintype = request.POST['cabintype']
            roundtripkey = ''
            if 'keyid' in request.POST:
                roundtripkey = request.POST['keyid']
            if 'trip' in request.POST:
                trip = request.POST['trip']
            if 'returndate' in  request.POST:
                retdate = request.POST['returndate']
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

def checkData(request):
    if request.is_ajax():
        cabin = request.POST['cabin']
        allkey = request.POST.get('multicity')
        recordkey = request.POST.get('keyid')
        returnkey = request.POST.get('returnkey')
        
        results = _check_data(recordkey, returnkey, cabin, allkey)
        mimetype = 'application/json'
        data = json.dumps(results)

        return HttpResponse(data, mimetype)    
    
def _check_data(recordkey, returnkey, cabin, allkey):
    '''
    check and return the current status for the search
    '''
    iscomplete =''
    isdatastored = ''
    flagcheck = ''

    if allkey:  # multi city
        multiple_key = allkey.split(',')
        inner_join_on = ''
        recordcheck = ''
        n = 1
        for keys in multiple_key:                
            if n > 1:
                recordcheck = recordcheck+ " inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +str(keys)+"' and p1.datasource = p"+str(n)+".datasource and p"+str(n)+"."+cabin+" > 0"
                inner_join_on = inner_join_on+" inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +str(keys)+"' and p1.datasource = p"+str(n)+".datasource and p"+str(n)+".flighno = 'flag'"
            n = n + 1
        isdatastored = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 "+recordcheck+" where p1.searchkeyid ='"+str(multiple_key[0])+"' and p1."+cabin+" > 0")
        
        flagcheck = Flightdata.objects.raw("select p1.rowid from pexproject_flightdata p1 "+inner_join_on+" where p1.searchkeyid ='"+str(multiple_key[0])+"' and p1.flighno = 'flag'")            
    else:   
        if recordkey:   # for oneway
            time1 = datetime.datetime.now() - timedelta(minutes=30)
            time1 = time1.strftime('%Y-%m-%d %H:%M:%S')

            if returnkey:   # for round trip
                returnfare = "p2." + cabin
                departfare = "p1." + cabin                
                isdatastored = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(returnkey)+" and "+returnfare+" > 0 where p1.searchkeyid="+str(recordkey)+" and "+departfare+" > 0")
                                 
                flagcheck = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(returnkey)+" and p2.flighno = 'flag' where p1.searchkeyid="+str(recordkey)+" and p1.flighno = 'flag'")
            else: 
                try:
                    keystatus = Searchkey.objects.get(searchid=recordkey,scrapetime__gte= time1)
                except:
                    iscomplete = "key_expired"
                                   
                isdatastored = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(recordkey)+" and "+cabin+"> 0")
                
                flagcheck = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(recordkey)+" and flighno = 'flag' ")

    if len(list(isdatastored)) > 0:
        data1 = "stored"
    else:
        data1 = "onprocess"
    # print "flagcheck",len(list(flagcheck))
    # print "customfunction flag", customfunction.flag
    if len(list(flagcheck)) >= customfunction.flag:
        iscomplete = "completed"

    return [data1, iscomplete]

def getFlexResult(request):
    if request.is_ajax():
        searchtype = request.POST['searchtype']
        departkey = request.POST['departkey']
        returnData = ''
        return_eco_saver = []
        return_bus_saver = []
        retMonth = ''
        if 'returnkey' in request.POST:
            returnkey = request.POST['returnkey']
            returnData = FlexibleDateSearch.objects.raw("select * from pexproject_flexibledatesearch where searchkey='"+str(returnkey)+"' and (economyflex = 'saver' or businessflex = 'saver') order by flexdate")
            returnDatalist = list(returnData)
            journeyDate = ''
            for row1 in returnDatalist:
                journeyDate = row1.journey
                journey_month = journeyDate.strftime("%m")
                flex_date = row1.flexdate
                flex_day = flex_date.strftime("%d")
                flex_month = flex_date.strftime("%m")
                if int(flex_month) == int(journey_month):
                    eco_s = row1.economyflex
                    if eco_s  and flex_day not in return_eco_saver:
                        return_eco_saver.append(flex_day)    
                    bus_s = row1.businessflex
                    if bus_s and flex_day not in return_bus_saver:
                        return_bus_saver.append(flex_day) 
            if journeyDate:            
                dateval1 = journeyDate.strftime("%m/%Y")
                year1 = journeyDate.strftime("%Y")
                retMonth = journeyDate.strftime("%-m")
                
        flexData = FlexibleDateSearch.objects.raw("select * from pexproject_flexibledatesearch where searchkey='"+str(departkey)+"' and (economyflex = 'saver' or businessflex = 'saver') order by flexdate")
        flexDataList = list(flexData)
        
        d = ''
        economy_saver = []
        business_saver = []
        month = ''
        for row in flexDataList:
            d = row.journey
            d.strftime("%m/%Y")
            month1 = d.strftime("%m")
            fd = row.flexdate
            fd1 = fd.strftime("%d")
            fd_month = fd.strftime("%m")
            if int(fd_month) == int(month1): 
                eco_s = row.economyflex
                if eco_s  and fd1 not in economy_saver:
                    economy_saver.append(fd1)    
                bus_s = row.businessflex
                
                if bus_s and fd1 not in business_saver:
                    business_saver.append(fd1)
            
        economy = ''
        business = ''
        ret_economy = ''
        ret_business = ''

        if len(economy_saver)>0:
            economy = ','.join(economy_saver)
        if len(business_saver) > 0:
            business = ','.join(business_saver)
        if len(return_eco_saver) > 0:
            ret_economy = ','.join(return_eco_saver)
        if len(return_bus_saver)  > 0 :  
            ret_business = ','.join(return_bus_saver)
        if d:    
            dateval = d.strftime("%m/%Y")
            year = d.strftime("%Y")
            month = d.strftime("%-m")
        
        
        return render_to_response('flightsearch/calendarmatrix.html',{"month":month,"economy":economy,"business":business,"retmonth":retMonth,"returnEco":ret_economy,"returnBusiness":ret_business},context_instance=RequestContext(request))
        

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
    recordkey=''
    pricematrix =''
    pricesources = []
    roundtripkey = ''
    pointlist=''
    minpricemile = 0
    maxpricemile = 0
    fare_class_code = ''

    print '############ GET', request.GET
    print '############ POST', request.POST

    if 'maincabin' in cabinclass:
        fare_class_code = 'eco_fare_code'
    elif 'firstclass' in cabinclass:
        fare_class_code = 'business_fare_code'
    else:
        fare_class_code = 'first_fare_code'
    
    #@@@@ Get Pricematrix list @@@@@@@@@@@@@@@@@@@@
    if request.POST.get('actionfor') == 'prc_matrix':
        getPriceRange = False
        if request.POST.get('valuefor') == 'pricerange':
            getPriceRange = True

        priceRange = ''
        FareCodeFromDatabase = ''
        if 'multicity' in request.GET or 'multicity' in request.POST:
            n = 1
            multicitykey = request.GET.get('multicity', '')
            multicitykey1 = multicitykey.split(',')
            recordkey = multicitykey1[0]
            ecocabin = 'min(if(p1.maincabin > 0,p1.maincabin,NULL))'
            busscabin = 'min(if(p1.firstclass > 0,p1.firstclass,NULL))'
            firstcabin = 'min(if(p1.business > 0,p1.business,NULL))'
            adding = '+'
            inner_join_on=''
            for keys in multicitykey1:
                if n > 1:
                    ecocabin = ecocabin+adding+"min(if(p"+str(n)+".maincabin > 0,p"+str(n)+".maincabin,NULL))"
                    busscabin = busscabin+adding+"min(if(p"+str(n)+".firstclass > 0,p"+str(n)+".firstclass,NULL))"
                    firstcabin = firstcabin+adding+"min(if(p"+str(n)+".business > 0,p"+str(n)+".business,NULL))"
                    inner_join_on = inner_join_on+" inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +keys+"' and p1.datasource = p"+str(n)+".datasource"
                n = n+1
            pricematrix =  Flightdata.objects.raw("select p1.rowid, p1.datasource,"+ecocabin+" as maincabin,"+busscabin+"  as firstclass ,"+firstcabin+" as business  from pexproject_flightdata p1 "+inner_join_on+" where p1.searchkeyid="+str(recordkey)+" group by p1.datasource")      
            '''fetching min max price miles for multicity '''
            min_max_cabin = ''
            if getPriceRange:
                if cabinclass == 'maincabin':
                    min_max_cabin = ecocabin
                elif cabinclass == 'firstclass':
                    min_max_cabin = busscabin
                else:
                    min_max_cabin = firstcabin
                maxpricemile_query = min_max_cabin
                if 'min' in maxpricemile_query:
                    maxpricemile_query = maxpricemile_query.replace('min','max')    
                priceRange =  Flightdata.objects.raw("select p1.rowid, p1.datasource,p1."+fare_class_code+" as fare_code, "+min_max_cabin+" as minpricemile,"+maxpricemile_query+"  as maxpricemile  from pexproject_flightdata p1 "+inner_join_on+" where p1.searchkeyid="+str(recordkey)+" group by fare_code")
                FareCodeFromDatabase =  Flightdata.objects.raw("select p1.rowid,p1."+fare_class_code+" as fare_code from pexproject_flightdata p1 "+inner_join_on+" where p1.searchkeyid="+str(recordkey)+" group by p1.datasource order by minpricemile,maxpricemile")      
       
        elif 'keyid' in  request.GET:
            key = request.GET.get('keyid', '')
            if 'returnkey' in request.GET:
                returnkeyid = request.GET.get('returnkey', '')
                pricematrix = Flightdata.objects.raw("select p1.rowid,p2.rowid, p2.datasource, (min(if(p1.maincabin > 0,p1.maincabin,NULL))+min(if(p2.maincabin > 0,p2.maincabin,NULL))) as maincabin, (min(if(p1.firstclass>0,p1.firstclass,NULL))+min(if(p2.firstclass>0,p2.firstclass,NULL))) as firstclass ,(min(if(p1.business>0,p1.business,NULL))+min(if(p2.business>0,p2.business,NULL))) as business  from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+returnkeyid+" where p1.searchkeyid="+str(key)+" group by p1.datasource")
                ''' fetch minimum maximum price'''
                priceRange = Flightdata.objects.raw("select p1.rowid,p2.rowid, p2.datasource,p1."+fare_class_code+" as fare_code, (min(if(p1."+cabinclass+" > 0,p1."+cabinclass+",NULL))+min(if(p2."+cabinclass+" > 0,p2."+cabinclass+",NULL))) as minpricemile, (max(if(p1."+cabinclass+" > 0,p1."+cabinclass+",NULL))+max(if(p2."+cabinclass+" > 0,p2."+cabinclass+",NULL))) as maxpricemile  from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+returnkeyid+" where p1.searchkeyid="+str(key)+" group by p1.datasource order by minpricemile,maxpricemile")
                FareCodeFromDatabase = Flightdata.objects.raw("select p1.rowid,p2.rowid,p1."+fare_class_code+" as fare_code from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+returnkeyid+" where p1.searchkeyid="+str(key)+" group by fare_code")

            else:
                pricematrix = Flightdata.objects.raw("select rowid, datasource, min(if(maincabin > 0,maincabin,NULL)) as maincabin, min(if(firstclass>0,firstclass,NULL)) as firstclass ,min(if(business>0,business,NULL)) as business  from pexproject_flightdata where searchkeyid="+str(key)+" group by datasource")
                priceRange = Flightdata.objects.raw("select rowid, datasource, min(if("+cabinclass+" > 0,"+cabinclass+",NULL)) as minpricemile, max(if("+cabinclass+" > 0,"+cabinclass+",NULL)) as maxpricemile  from pexproject_flightdata where searchkeyid="+str(key)+" group by datasource order by minpricemile,maxpricemile")
                FareCodeFromDatabase = Flightdata.objects.raw("select rowid, "+fare_class_code+" as fare_code from pexproject_flightdata where searchkeyid="+str(key)+" group by fare_code")
        ''' get min and max price miles '''
        minPriceMile = 500
        maxPriceMile = 0
        fare_code_Array = []

        if getPriceRange:
            FareCodeFromDatabase1 = list(FareCodeFromDatabase)
            for cd in FareCodeFromDatabase1:
                fare_code_string = cd.fare_code
                if fare_code_string != None and fare_code_string != '' and  ',' in fare_code_string:
                    fare_code_string = fare_code_string.split(',')
                    for n in range(0,len(fare_code_string)):
                        if fare_code_string[n] not in fare_code_Array and fare_code_string != '' and fare_code_string[n] != None:
                            fare_code_Array.append(fare_code_string[n])
                else:
                    if fare_code_string != None and fare_code_string != '' and fare_code_string not in fare_code_Array:
                        fare_code_Array.append(fare_code_string)
            priceRange1 = list(priceRange) 
            temp = 0
            for t in priceRange1:
                if temp < t.maxpricemile:
                    temp = t.maxpricemile
                if t.minpricemile != None and (minPriceMile > t.minpricemile or minPriceMile == 500):
                   minPriceMile = t.minpricemile   
            maxPriceMile = temp
            mimetype = 'application/json'
            results = []
            results.append(minPriceMile)
            results.append(maxPriceMile)
            results.append(fare_code_Array)
            data = json.dumps(results)
            return HttpResponse(data, mimetype)

        price_matrix = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
        price_matrix = {item: [None, None, None] for item in price_matrix}

        if pricematrix:
            for item in pricematrix:
                price_matrix[item.datasource] = [item.maincabin, item.firstclass, item.business]

        return render_to_response('flightsearch/pricematrix.html',{'price_matrix': price_matrix}, context_instance=RequestContext(request))

    adimages = GoogleAd.objects.filter(ad_code="result page")
    if request.is_ajax():
        if 'page_no' in request.POST:
            pageno = request.REQUEST['page_no']
        offset = (int(pageno) - 1) * limit
             
    action = ''
    if request.GET.get('keyid', '') :
        searchkey = request.GET.get('keyid', '')
        if request.GET.get('returnkey', ''):
            roundtripkey = request.GET.get('returnkey', '')
        totalrecords1 = ''
        multiple_key = ''
        if request.GET.get('multicity'):
            allkey = request.GET.get('multicity')
            multiple_key = allkey.split(',')
            searchdata1 = Searchkey.objects.filter(searchid__in=multiple_key).order_by('traveldate')
        else:
            searchdata1 = Searchkey.objects.filter(searchid=searchkey)
        searchdata = list(searchdata1)
        if len(searchdata) < 1:
            return HttpResponseRedirect('/index?message=You must enter departure city, destination city and departure date')
            
        for s in searchdata:
            source = s.source
            destination = s.destination
        if ('action' in request.GET and request.GET.get('action', '') == 'return') or 'rowid' in request.POST and request.GET.get('action', '') != 'depart':
            action = request.GET.get('action', '')
            searchkey = request.GET.get('returnkey', '')
            returnkey = request.GET.get('keyid', '')
        if multiple_key == '':
            querylist = querylist + join + " p1.searchkeyid = '"+searchkey+"'"
            join = ' AND '

    print '$$$ (specify only searchkeyid): ', querylist    

    if 'multicity' in request.GET or 'multicity' in request.POST:
        multicitykey = request.GET.get('multicity', '')
        multicitykey1 = multicitykey.split(',')
    if 'stoppage' in request.POST:
        if request.is_ajax():
            list2 = request.POST.getlist('stoppage')
            list2 = list2[0].split(',')
            if '2 STOPS' in list2:
                querylist = querylist + join + "p1.stoppage in ('" + "','".join(list2) + "','3 STOPS','4 STOPS')"
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
                    list2.append('4 STOPS')
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
    codesList = ''
    code_query_string=''                    
    if 'fareCodes' in request.POST:
        codesList = request.POST.getlist('fareCodes') 
        if request.is_ajax():
            codesList = codesList[0].split(',')
        conn = ''
        for code in codesList:
            code_query_string = code_query_string+conn+"p1."+fare_class_code+" like '%%"+code+"%%' "
            conn = ' or '
        querylist = querylist + join +str("("+code_query_string+")")
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
         depttime = request.POST['depaturemin']
         deptformat = (datetime.datetime.strptime(depttime, '%I:%M %p'))
         deptformat1 = deptformat.strftime('%H:%M:%S')
         querylist = querylist + join + " p1.departure >= '" + deptformat1 + "'"
         join = ' AND '
    if 'depaturemax' in request.POST:
        deptmaxtime = request.POST['depaturemax']
        deptmaxformat = (datetime.datetime.strptime(deptmaxtime, '%I:%M %p'))
        deptmaxformat1 = deptmaxformat.strftime('%H:%M:%S')
        querylist = querylist + join + " p1.departure <= '" + deptmaxformat1 + "'"
        join = ' AND '
    if 'arivalmin' in request.POST:
         arivtime = request.POST['arivalmin']
         
         arivformat = (datetime.datetime.strptime(arivtime, '%I:%M %p'))
         arivformat1 = arivformat.strftime('%H:%M:%S')
         querylist = querylist + join + " p1.arival >= '" + arivformat1 + "'"
         join = ' AND '
    if 'arivalmax' in request.POST:
        arivtmaxtime = request.POST['arivalmax']
        arivtmaxformat = (datetime.datetime.strptime(arivtmaxtime, '%I:%M %p'))
        arivtmaxformat1 = arivtmaxformat.strftime('%H:%M:%S')
        querylist = querylist + join + " p1.arival <= '" + arivtmaxformat1 + "'"
        join = ' AND ' 
    action = ''
    if request.GET.get('keyid', '') :
        if cabinclass != '':
            if cabinclass == 'maincabin':
                taxes = "maintax"
            elif cabinclass == 'firstclass':
                taxes = "firsttax"
            elif cabinclass == 'business':
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
                    recordid = request.POST['rowid']
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
                #unitedmin1 = Flightdata.objects.filter(searchkeyid=returnkey, datasource='united', maincabin__gt=0).values('maincabin', 'maintax', 'cabintype1').annotate(Min('maincabin')).order_by('maincabin')
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
        multisearch = []
        n = 1
        m = 0
        multiSearchTitle=''
        if multicitykey1:
            orlDestination=''
            multicitysearch = ''
            commaSeperator=''
            dateString = ''
            dateSeperator = ''
            for row in searchdata:
                originname = re.findall(re.escape("(")+"(.*)"+re.escape(")"),row.source)[0]
                destname = re.findall(re.escape("(")+"(.*)"+re.escape(")"),row.destination)[0]
                if orlDestination  == originname:
                    multiSearchTitle = multiSearchTitle+"-"+destname
                    commaSeperator=''
                    
                else:
                    multiSearchTitle = multiSearchTitle+commaSeperator+originname+"-"+destname
                    commaSeperator = ", "
                orlDestination = destname
                travingDate = row.traveldate.strftime('%-m/%-d')
                dateString = dateString+dateSeperator+travingDate
                dateSeperator = '-'
                multicitysearch = {"source":originname,"destination":destname,"traveldate":row.traveldate}
                
                m = m+1
                multisearch.append(multicitysearch) 
            multiSearchTitle = multiSearchTitle+", "+dateString
            multicity='true' 
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
            adding = '+'
            pricesources =[]
            recordkey = multicitykey1[0]
            pricematrix_query = ''
            setLimit = 10
            if len(multicitykey1) < 3:
                setLimit = 30
            for keys in multicitykey1:
                if n > 1:
                    totalfare = totalfare+"+p"+str(n)+"." + cabinclass
                    totaltax = totaltax+"+p"+str(n)+"."+taxes
                    newidstring =newidstring+sep+"p"+str(n)+".rowid"
                    qry2 = qry2+sep1+'p'+str(n)+'.origin as origin'+str(n)+',p'+str(n)+'.rowid as rowid'+str(n)+', p'+str(n)+'.stoppage as stoppage'+str(n)+', p'+str(n)+'.destination as destination'+str(n)+', p'+str(n)+'.departure as departure'+str(n)+', p'+str(n)+'.arival as arival'+str(n)+', p'+str(n)+'.duration as duration'+str(n)+',p'+str(n)+'.flighno as flighno'+str(n)+', p'+str(n)+'.cabintype1 as cabintype1'+str(n)+',p'+str(n)+'.cabintype2 as cabintype2'+str(n)+',p'+str(n)+'.cabintype3 as cabintype3'+str(n)+', p'+str(n)+'.maincabin as maincabin'+str(n)+', p'+str(n)+'.maintax as maintax'+str(n)+', p'+str(n)+'.firsttax as firsttax'+str(n)+', p'+str(n)+'.businesstax as businesstax'+str(n)+',p'+str(n)+'.departdetails as departdetails'+str(n)+',p'+str(n)+'.arivedetails as arivedetails'+str(n)+', p'+str(n)+'.planedetails as planedetails'+str(n)+',p'+str(n)+'.operatedby as operatedby'+str(n)
                    sep1 = ','
                    if querylist and 'p1' in querylist:
                        querylist = querylist.replace('p1.','')+" and "
                    qry3 = qry3+" inner join (select  * from pexproject_flightdata where "+querylist+" searchkeyid ='"+keys+"' and "+cabinclass+" > '0' order by "+cabinclass+" limit "+str(setLimit)+") as p"+str(n)+" on p1.datasource = p"+str(n)+".datasource"
                    q = ''
                counter = counter+1
                n = n+1
                if 'minPriceMile' in request.POST:
                    minpricemile = request.POST['minPriceMile']
                    querylist = querylist + join + " "+totalfare+" >= '" + minpricemile + "'"
                    join = ' AND '
                if 'maxPriceMile' in request.POST:
                    maxpricemile = request.POST['maxPriceMile']
                    querylist = querylist + join + " "+totalfare+" <= '" + maxpricemile + "'"
                    join = ' AND '
            finalquery = qry1+"CONCAT("+newidstring+") as newid ,"+qry2+ totalfare+" as finalprice "+totaltax+" as totaltaxes from (select  * from pexproject_flightdata where "+querylist+" searchkeyid ='"+str(recordkey)+"' and "+cabinclass+" > '0' order by maincabin limit "+str(setLimit)+") as p1 "+qry3 + " order by finalprice,totaltaxes , departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset)
            record_obj = Flightdata.objects.raw(finalquery)
            record = list(record_obj)
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
                mainlist1 = {"newid":row.newid,"flighno":row.flighno,"datasource":row.datasource,"cabintype1":row.cabintype1,"cabintype2":row.cabintype2,"cabintype3":row.cabintype3,"finalprice":row.finalprice,"totaltaxes":row.totaltaxes,"origin":multirecordlist,"multidetail_list":multidetail_list}
                mainlist.append(mainlist1)
        else:
            if (returnkeyid1 and ('rowid' not in request.GET) and 'rowid' not in request.POST) or len(multicitykey1) > 0:
                mile_condition = ''
                totalfare = "p1." + cabinclass + "+p2." + cabinclass
                if 'minPriceMile' in request.POST:
                    minpricemile = request.POST['minPriceMile']
                    querylist = querylist + join + " "+totalfare+" >= '" + minpricemile + "'"
                    join = ' AND '
                if 'maxPriceMile' in request.POST:
                    maxpricemile = request.POST['maxPriceMile']
                    querylist = querylist + join + " "+totalfare+" <= '" + maxpricemile + "'"
                    join = ' AND '
                returnfare = "p2." + cabinclass
                departfare = "p1." + cabinclass
                totaltax = "p1."+taxes+"+p2."+taxes
                record = Flightdata.objects.raw("select p1.*,CONCAT(p1.rowid,'_',p2.rowid) as newid,p2.origin as origin1,p2.rowid as rowid1, p2.stoppage as stoppage1,p2.flighno as flighno1, p2.cabintype1 as cabintype11,p2.cabintype2 as cabintype21,p2.cabintype3 as cabintype31, p2.destination as destination1, p2.departure as departure1, p2.arival as arival1, p2.duration as duration1, p2.maincabin as maincabin1, p2.maintax as maintax1, p2.firsttax as firsttax1, p2.businesstax as businesstax1,p2.departdetails as departdetails1,p2.arivedetails as arivedetails1, p2.planedetails as planedetails1,p2.operatedby as operatedby1," + totalfare + " as finalprice,  "+totaltax+" as totaltaxes from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ='" + returnkeyid1 + "' and " + returnfare + " > '0'  where  p1.searchkeyid = '" + searchkey + "' and " + departfare + " > 0 and " + querylist + " order by finalprice ,totaltaxes, departure, p2.departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset))
                
            else:
                if 'minPriceMile' in request.POST:
                    minpricemile = request.POST['minPriceMile']
                    querylist = querylist + join + " p1."+cabinclass+" >= '" + minpricemile + "'"
                    join = ' AND '
                if 'maxPriceMile' in request.POST:
                    maxpricemile = request.POST['maxPriceMile']
                    querylist = querylist + join + " p1."+cabinclass+" <= '" + maxpricemile + "'"
                    join = ' AND '
                cabintype = " and " + cabinclass + " > 0"
                querylist = querylist+cabintype
                print '$$$(class filtered): ', querylist
                record = Flightdata.objects.raw("select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice, "+taxes+" as totaltaxes from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset))
                print '$$$ (synthesis): ', "select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice, "+taxes+" as totaltaxes from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset)
            mainlist = list(record)
            
        progress_value = '' 
        if 'progress_value' in request.POST:
            progress_value = request.REQUEST['progress_value']
            
        recordlen = len(multicitykey1)
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        filterkey = {'stoppage':list2,'fareCodes':json.dumps(codesList),'fareCodelength':len(codesList), 'datasource':list1, 'cabin':cabin,'minpricemile':minpricemile,'maxpricemile':maxpricemile}
        if depttime:
            timeinfo = {'maxdept':deptmaxtime, 'mindept':depttime, 'minarival':arivtime, 'maxarival':arivtmaxtime}
        else:
            timeinfo = ''
        if 'share_recordid' in request.GET:
            sharedid = request.GET.get('share_recordid','')
            selectedrow = Flightdata.objects.get(pk=sharedid)
        scraperStatus = ''
        if 'scraperStatus' in request.POST:
            scraperStatus = request.POST['scraperStatus']
        title=''
        comma = ''
        if multiSearchTitle == '' :
            for val in searchdata:
                title_origin = re.findall(re.escape("(")+"(.*)"+re.escape(")"),val.source)[0]
                title_dest = re.findall(re.escape("(")+"(.*)"+re.escape(")"),val.destination)[0]
                if title_origin == title_dest:
                    title = title+comma+ "-"+title_dest
                    comma = ", "
                else:
                    title = title+comma+title_origin+"-"+title_dest
                    comma = ", "
                fromDate = val.traveldate.strftime('%-m/%-d')
                title = title+", "+fromDate
                toDate = ''
                if returndate:
                    toDate = returndate[0].strftime('%-m/%-d')
                    title = title+"-"+toDate
            
        else:
            title = multiSearchTitle
            
        if request.is_ajax():
            print '$$$ (ajax parameter-data, multirecod)', [(item.rowid, item.searchkeyid, item.datasource, item.flighno) for item in mainlist] 
            return render_to_response('flightsearch/search.html', {'action':action,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value, 'multisearch':multisearch, 'data':mainlist,'multirecod':mainlist, 'multicity':multicity, 'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request))
        '''
        #if totalrecords <= 0 and scraperStatus == "complete":
            #return render_to_response('flightsearch/search.html', {'action':action, 'data':record, 'minprice':minprice, 'tax':tax, 'timedata':timeinfo,'progress_value':progress_value, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request))
            #msg = "Sorry, No flight found  from " + source + " To " + destination + ".  Please search for another date or city !"
            ##msg = "Oops, looks like there aren't any flight results for your filtered search. Try to broaden your search criteria for better results."
            if len(searchdata) > 0:
                return  render_to_response('flightsearch/flights.html', {'message':msg, 'search':searchdata[0],'returndate':returndate}, context_instance=RequestContext(request))
            else:
                return HttpResponseRedirect(reverse('index'))
        else:
        '''
        if 'userid' in request.session and  'actionfor' not in request.POST:
            userid = request.session['userid']
            cursor = connection.cursor()
            cursor.execute("select * from reward_points where user_id="+str(userid))
            pointlist = cursor.fetchall()
        
        print '$$$ (render parameter-data, multirecod)', [(item.rowid, item.searchkeyid, item.datasource, item.flighno) for item in mainlist] 
        return render_to_response('flightsearch/searchresult.html', {'title':title,'action':action,'pointlist':pointlist,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value,'multisearch':multisearch,'data':mainlist,'multirecod':mainlist,'multicity':multicity,'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request)) 
        

def share(request):
    context = {}
    if 'selectedid' in request.GET:
        selectedid = request.GET.get('selectedid', '')
        cabin = request.GET.get('cabin', '')
        traveler = request.GET.get('passenger', '')
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

def useralert(request):
    context = {}
    if request.POST and  'userid' in request.session:
	currentDate = datetime.datetime.now().date()
	preDate = currentDate - timedelta(days=1)
	print preDate
        message = ''
        alertuser = UserAlert()
        email = request.session['username']
        alertuser.user_email = email
        alertuser.userid = request.session['userid']
        triptype = request.POST['trip']
        alertuser.source_airportid = request.POST['fromid']
        alertuser.destination_airportid = request.POST['destid']
        alertuser.departdate = request.POST['alt_depardate']
        if 'pricemile' in request.POST and request.POST['pricemile']:
            alertuser.pricemile = request.POST['pricemile']
        if 'alt_returndate' in request.POST and request.POST['alt_returndate']:
            alertuser.returndate = request.POST['alt_returndate']
            print "alt_returndate",request.POST['alt_returndate']
        if 'alt_expire' in request.POST and request.POST['alt_expire']:
            alertuser.expiredate = request.POST['alt_expire']
        else:
            alertuser.expiredate = request.POST['alt_depardate']
        if 'alertday' in request.POST:
            alertday = request.POST.getlist('alertday')
            alertuser.alertday = ','.join(alertday)
        alertuser.sent_alert_date = preDate
        alertuser.save()
        try:
            html_content = ''
            email_sub = "PEX+ miles alert"
            emailbody = "Hello <b>"+email+"</b>,<br><br> you have successfully created a PEX+ flight miles alert.<br><br>Thanks,<br><b> PEX+ Team"
            resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
            message = "you have successfully created Flight miles alert"
        except:
            message = "Something went wrong, Please try again"
        return HttpResponseRedirect('/manageAccount?status='+message)
    return HttpResponseRedirect(reverse('manageAccount'))

def subscribe(request):
    if request.is_ajax:
        email = request.POST['emailid']
        subscriber = Mailchimp(customfunction.mailchimp_api_key)
        subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':email})
    exit()

def multicity(request):
    context = {}
    
    return render_to_response('flightsearch/multicity.html', context_instance=RequestContext(request)) 
        
    
# hotels views  

def hotels(request):
    searches = Search.objects.all().order_by('-frequency')[:8]
    searches = [[item.keyword, item.image, float(item.lowest_price), int(float(item.lowest_points))/1000, item.keyword.split('-')[0]] for item in searches]

    # #for startup
    # if len(searches) < 8:
    #     searches += default_search

    return render(request, 'hotelsearch/hotel_home.html', {'form': HotelSearchForm(), 'searches': searches})

HOTEL_CHAINS = {
    'ihg':  'IHG Rewards Club', 
    'spg':  'Starwood Preferred Guest', 
    'hh':   'Hilton HHonors', 
    'cp':   'Choice Privileges', 
    'cc':   'Club Carlson', 
    'mr':   'Marriott Rewards', 
    'hy':   'Hyatt Gold Passport', 
    'ac':   'Le Club Accor', 
    'wy':   'Wyndham Rewards',
}

def __debug(message):
    '''check the place'''
    try:
        DEV_LOCAL = False
        DEBUG = True
        log_path = 'hotel_place_log' if DEV_LOCAL else '/home/upwork/hotel_place_log'
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
        log_file = open(log_path, 'a') if DEBUG else sys.stdout
        log_file.write(message);
        if DEBUG:
            log_file.close()
    except Exception, e:
        print '### DEBUG error %s' % str(e)

def is_number(s):
    if not s:
        return True
    try:
        float(s)
    except Exception:
        return False
    return True

def is_date(date_text, date_format='%Y-%m-%d'):
    try:
        parsed_date = dttime.strptime(date_text, date_format).date()
    except Exception:
        return False
    return parsed_date >= dttime.today().date()

def is_time(time_text, time_format='%H:%M:%S'):
    try:
        parsed_time = dttime.strptime(time_text, time_format)
    except Exception:
        return False
    return True

def check_validity_hotel_params(request):
    '''
    check validity of params for hotel from the request
    return 
        valid: ['', return_date, origin, destination, depart_date, search_type, flight_class]
        invalid: [error_message]
    '''
    # check the header
    http_accept = request.META['HTTP_ACCEPT']
    content_type = request.META['CONTENT_TYPE']

    # check the body
    params = json.loads(request.body)

    place = params.get('place')
    checkin = params.get('checkin')
    checkout = params.get('checkout')
    price_low = params.get('price_low')
    price_high = params.get('price_high')
    award_low = params.get('award_low')
    award_high = params.get('award_high')
    radius = params.get('radius') or 1000
    chain = params.get('hotel_chain') or HOTEL_CHAINS.keys()

    if http_accept != 'application/json' or content_type != 'application/json':
        return ['Content type  is incorrect']

    if not place:
        return ['Search place should be provided']

    if not (is_date(checkin) and is_date(checkout)):
        return ['Checkin and checkout date should be provided and be in format(2016-07-17)']

    if not (is_number(price_low) and is_number(price_high) and is_number(award_low) and is_number(award_high) and is_number(radius)):
        return  ['Filter parameters should be number']

    filters = {'price_low':price_low, 'price_high':price_high, 'award_low':award_low, 'award_high':award_high, 'radius': float(radius), 'chain': chain }
    return ['', place, checkin, checkout, filters]

@csrf_exempt
def api_search_hotel(request):
    if request.method == 'POST':        
        result = {}

        _token = check_validity_token(request.META.get('HTTP_AUTHORIZATION'), 'hotel')
        error_message = _token[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return HttpResponse(json.dumps(result), 'application/json')

        _params = check_validity_hotel_params(request)
        error_message = _params[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return HttpResponse(json.dumps(result), 'application/json')

        # _result = _search_hotel(place, checkin, checkout, filters)
        _result = _search_hotel(_params[1], _params[2], _params[3], _params[4])

        error_message = _result[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
        else:
            db_hotels, price_matrix, filters = _result[1], _result[2], _result[3]
            result['status'] = 'Success'
            result['price_matrix'] = price_matrix
            # result['filters'] = filters
            result['hotels'] = [model_to_dict(item) for item in db_hotels]

        return HttpResponse(json.dumps(result), 'application/json')
        
def _search_hotel(place, checkin, checkout, filters):
    '''
    search hotels upon arguments
    return list with first parameter as error message
        Format:
            Success: ['', hotels, price_matrix, filters]
            Fail: [error_message]
        Success if error message is empty
    '''
    checkin_date = dttime.strptime(checkin, "%Y-%m-%d").date()
    checkout_date = dttime.strptime(checkout, "%Y-%m-%d").date()

    # check date range
    if checkin_date < dttime.today().date() or checkout_date < dttime.today().date() or checkin_date > checkout_date:
        return ['Checkin date or checkout date is not correct. Please set it properly.']      

    # check last search time
    currentdatetime = timezone.now().replace(tzinfo=None)
    time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    time_60m = timezone.now() - timedelta(minutes=60)

    search = Search.objects.filter(keyword=place)
    db_hotels = None

    if search:
        search = search[0]
        if search.search_time >= time_60m:
            # cached
            db_hotels = Hotel.objects.filter(search=search.id)
        else:
            # need to update search time
            search.search_time = time
            search.save()
    else:
        search = Search.objects.create(keyword=place, search_time=time)        

    if not db_hotels:
        url = 'http://wandr.me/scripts/hustle/pex.ashx?term=%s&i=%s&o=%s' % (place, checkin, checkout)
        __debug( '== url: %s\n\n' % url)
        
        hotels = []    
        try:
            res = requests.get(url=url).json()
            if res['results'] != 'error':
                hotels = res['hotels']
        except Exception, e:
            pass

        if not hotels:
            # delete empty search including spam search
            if not Hotel.objects.filter(search=search):
                search.delete()
            return ['There is no hotel in the place. Please check fields again.']      

        for hotel in hotels:
            _hotel = {}
            _hotel['prop_id'] = hotel['propID']
            _hotel['cash_rate'] = get_value(hotel['cashRate'])
            _hotel['points_rate'] = int(get_value(hotel['pointsRate']))
            _hotel['distance'] = int(get_value(hotel['distance']))
            _hotel['chain'] = hotel['propID'].split('-')[0].strip()
            _hotel['lat'] = hotel['lat']
            _hotel['lon'] = hotel['lon']
            _hotel['brand'] = hotel['brand']
            _hotel['award_cat'] = hotel['awardCat']
            _hotel['name'] = hotel['name']
            _hotel['img'] = hotel['img']
            _hotel['cash_points_rate'] = hotel['cashPointsRate']
            _hotel['url'] = hotel['url']

            db_hotel = Hotel.objects.filter(search=search.id, prop_id=_hotel['prop_id'])
            if db_hotel:
                db_hotel.update(**_hotel)
            else:
                Hotel.objects.create(search=search, **_hotel)

        db_hotels = Hotel.objects.filter(search=search.id)

    # filter the result
    price_lowest = db_hotels.filter(~Q(cash_rate=0.0)).aggregate(Min('cash_rate'))['cash_rate__min']
    price_highest = db_hotels.aggregate(Max('cash_rate'))['cash_rate__max']
    award_lowest = db_hotels.filter(~Q(points_rate=0)).aggregate(Min('points_rate'))['points_rate__min']
    award_highest = db_hotels.aggregate(Max('points_rate'))['points_rate__max']

    search.frequency = search.frequency + 1
    search.image = db_hotels.filter(~Q(img=''))[0].img
    search.lowest_price = price_lowest
    search.lowest_points = award_lowest
    search.save()

    # filter
    tmp = float(filters['price_low'] or price_lowest)
    price_low = max(tmp, price_lowest)
    tmp = float(filters['price_high'] or price_highest)
    price_high = min(tmp, price_highest)
    tmp = float(filters['award_low'] or award_lowest)
    award_low = max(tmp, award_lowest)
    tmp = float(filters['award_high'] or award_highest)
    award_high = min(tmp, award_highest)
    star_rating = filters.get('star_rating', [u'1', u'2', u'3', u'4', u'5'])
    # __debug('## chain: %s\n\n' % str(filters.chain))
    dis_place = place.split('-')[0]

    db_hotels = db_hotels.filter(
        Q(cash_rate__lte=price_high), 
        Q(points_rate__lte=award_high), 
        Q(distance__lte=filters['radius']), 
        Q(chain__in=filters['chain']), 
        Q(cash_rate=0.0)|Q(cash_rate__gte=price_low), 
        Q(points_rate=0.0)|Q(points_rate__gte=award_low))

    r_db_hotels = db_hotels.filter(star_rating=0)
    for star in star_rating:
        low = float(star) - 0.51
        high = float(star) + 0.41
        r_db_hotels = r_db_hotels | db_hotels.filter(star_rating__range=(low,high))
    
    db_hotels = r_db_hotels.order_by('-star_rating', 'cash_rate')
    # get price matrix
    # '-' if none
    price_matrix = {}
    for item in HOTEL_CHAINS:
        price_min = db_hotels.filter(chain__contains=item).filter(~Q(cash_rate=0.0)).aggregate(Min('cash_rate'))['cash_rate__min']
        points_min = db_hotels.filter(chain=item).filter(~Q(points_rate=0)).aggregate(Min('points_rate'))['points_rate__min'] or '-'
        price_matrix[item] = {'cash_rate': price_min, 'points_rate': points_min, 'title': HOTEL_CHAINS[item]}
    # __debug('price_matrix: %s\n\n' % str(price_matrix))

    filters = {'price_low':price_low, 'price_high':price_high, 'award_low':award_low, 'award_high':award_high, 'radius':filters['radius'], 'chain':filters['chain'], 'price_lowest':price_lowest, 'price_highest':price_highest, 'award_lowest':award_lowest, 'award_highest':award_highest, 'dis_place':dis_place, 'star_rating': star_rating}
    # __debug('filters: %s\n' % str(filters))

    return ['', db_hotels, price_matrix, filters]

def search_hotel(request):
    if request.method == 'POST':
        form = HotelSearchForm(request.POST)
        if not form.is_valid():
            return render(request, 'hotelsearch/hotel_result.html', {'hotels': [], 'form': form, 'price_matrix': {}, 'filters': {}})
        place = form.cleaned_data['place']
        checkin = form.cleaned_data['checkin']
        checkout = form.cleaned_data['checkout']
        
        filters = {'price_low':request.POST.get('price_low'), 'price_high':request.POST.get('price_high'), 'award_low':request.POST.get('award_low'), 'award_high':request.POST.get('award_high'), 'radius':int(request.POST.get('radius', 1000)), 'chain':request.POST.getlist('hotel_chain', HOTEL_CHAINS.keys()), 'star_rating': request.POST.getlist('star')}
    else:
        place = request.GET.get('place')
        place = place.split('&')[0]
        __debug( '@@ place from GET original: %s\n' % place )
        place = parse_place(place)
        __debug( '&& place from  GET  parsed: %s\n' % place )
        checkin = request.GET.get('checkin') or dttime.today().strftime('%Y-%m-%d')
        checkout = request.GET.get('checkout') or (dttime.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        form = HotelSearchForm(initial={'place':place, 'checkin': checkin, 'checkout': checkout})
        filters = {'price_low':'', 'price_high':'', 'award_low':'', 'award_high':'', 'radius': 1000, 'chain': HOTEL_CHAINS.keys()}

    result = _search_hotel(place, checkin, checkout, filters)

    error_message = result[0]
    if error_message:
        form.errors['Error: '] = error_message
        return render(request, 'hotelsearch/hotel_result.html', {'hotels': [], 'form': form, 'price_matrix': {}, 'filters': {}})
    else:
        db_hotels, price_matrix, filters = result[1], result[2], result[3]
        return render(request, 'hotelsearch/hotel_result.html', {'hotels': db_hotels, 'form': form, 'price_matrix': price_matrix, 'filters': filters})    

def get_value(str_value):
    '''
    get float value from the string (cash, point)
    return 0 if not digit (add 0 in front of it)

    example: '12,000' '234.21' 'N/A' '185 *' 
    '''
    str_value = re.sub(r"[^0-9.]", "", '0'+str_value)
    return float(str_value)

def parse_place(place):
    '''
    get real place from encoded place string on twitter
    used in GET request
    '''
    replacement = {'%20':' ', '%2C':',', '%28':'(', '%29':')', '_':' ', '0':',', '1':')'}
    for item in replacement:
        place = place.replace(item, replacement[item])
    return place

FLIGHT_CLASS = {
    'economy': 'maincabin',
    'business': 'firstclass',
    'firstclass': 'business'
}

def check_validity_token(token, service):
    '''
    check and validate the token from the request for the service
    return 
        success: ['']
        fail: [error_message]
    '''
    if not token:
        return ['Authorization should be provided.']
    r = re.compile('^Token \w+$')
    if not r.match(token):
        return ['Authorization format is wrong. It should be in the format("Token <token>").']
    token = token.split('Token ')[1]

    token = Token.objects.filter(token=token)
    if not token:
        return ['The token you provided is not correct!']

    token = token[0]

    # check limit
    limit_request = getattr(token, 'limit_%s_search' % service)
    number_request = getattr(token, 'run_%s_search' % service)
    number_request = number_request + 1
    setattr(token, 'run_%s_search' % service, number_request)
    token.save()

    if number_request > limit_request:
        return ['Your license is reached to its limit. Please extend it!']
    # check domain
    return ['']

def check_validity_flight_params(request):
    '''
    check validity of params for flight from the request
    return 
        valid: ['', return_date, origin, destination, depart_date, search_type, flight_class]
        invalid: [error_message]
    '''
    # check the header
    http_accept = request.META['HTTP_ACCEPT']
    content_type = request.META['CONTENT_TYPE']

    # check the body
    params = json.loads(request.body)

    origin = params.get('origin')
    destination = params.get('destination')
    depart_date = params.get('depart_date')
    return_date = params.get('return_date')
    search_type = params.get('search_type', 'exactdate')
    flight_class = params.get('class')
    mile_low = params.get('mile_low') or '0'
    mile_high = params.get('mile_high') or '1000000'
    airlines = params.get('airlines') or ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
    depart_from = params.get('depart_from') or '00:00:00'
    depart_to = params.get('depart_to') or '23:59:59'
    arrival_from = params.get('arrival_from') or '00:00:00'
    arrival_to = params.get('arrival_to') or '23:59:59'

    if http_accept != 'application/json' or content_type != 'application/json':
        return ['Content type  is incorrect']

    if not (origin and destination):
        return ['Flight origin and destination should be provided']

    origin = Airports.objects.filter(Q(code__istartswith=origin)|Q(cityName__istartswith=origin)|Q(name__istartswith=origin))
    destination = Airports.objects.filter(Q(code__istartswith=destination)|Q(cityName__istartswith=destination)|Q(name__istartswith=destination))
    if not (origin and destination):
        return ['Please check flight origin and destination again. There is no such place']

    origin = origin[0].airport_id
    destination = destination[0].airport_id

    if not is_date or not is_date(depart_date, '%m/%d/%Y'):
        return ['Depart date should be provided as valid date and should be in format(07/18/2016)']

    if return_date and not is_date(return_date, '%m/%d/%Y'):
        return ['Return date should be provided as valid date and should be in format(07/18/2016)']

    if return_date:
        _depart_date = dttime.strptime(depart_date, "%m/%d/%Y").date()
        _return_date = dttime.strptime(return_date, "%m/%d/%Y").date()

        # check date range
        if _depart_date > _return_date:
            return ['Depart date or return date is not correct. Please set it properly.']      

    if not(is_time(depart_from) and is_time(depart_to) and is_time(arrival_from) and is_time(arrival_to)):
        return ['Please check filter time for depart and arrival again. They should be in format(13:45:30).']

    if search_type not in ['exactdate', 'flexibledate']:
        return ['search_type should be "exactdate" or "flexibledate"']

    if flight_class not in FLIGHT_CLASS.keys():
        return ['Flight class is not correct. It should be one of economy, business, firstclass.']
    
    flight_class = FLIGHT_CLASS[flight_class]

    return ['', return_date, str(origin), str(destination), depart_date, search_type, flight_class, mile_low, mile_high, airlines, depart_from, depart_to, arrival_from, arrival_to]

@csrf_exempt
def api_search_flight(request):
    if request.method == 'POST':
        delay_threshold = 30
        result = {}

        _token = check_validity_token(request.META.get('HTTP_AUTHORIZATION'), 'flight')
        error_message = _token[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return HttpResponse(json.dumps(result), 'application/json')

        _params = check_validity_flight_params(request)
        error_message = _params[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return HttpResponse(json.dumps(result), 'application/json')

        # get valid parameters
        return_date, origin, destination, depart_date, search_type, flight_class, mile_low, mile_high, airlines, depart_from, depart_to, arrival_from, arrival_to = _params[1], _params[2], _params[3], _params[4], _params[5], _params[6], _params[7], _params[8], _params[9], _params[10], _params[11], _params[12], _params[13]

        keys = _search(return_date, origin, destination, depart_date, search_type, flight_class)
        while(1):
            delay_threshold = delay_threshold - 1
            time.sleep(1)
            # check the status of the scraping
            scrape_status = _check_data(keys['departkey'], keys['returnkey'], flight_class, '')
            if scrape_status[1] == 'completed' or not delay_threshold:
                break

        kwargs = {
            'searchkeyid': keys['departkey'], 
            '{0}__range'.format(flight_class):(mile_low, mile_high),
            'datasource__in': airlines,
            'departure__range': (depart_from, depart_to),
            'arival__range': (arrival_from, arrival_to)
        }

        __debug('## filters for flight api: %s\n' % str(kwargs)) 
        flights = Flightdata.objects.filter(**kwargs)
        flights = [model_to_dict(item, exclude=['rowid', 'scrapetime', 'searchkeyid']) for item in flights]

        for flight in flights:
            for k,v in flight.items():
                flight[k] = str(v)

        result['status'] = 'Success'
        result['filters'] = kwargs#filters
        result['flights'] = flights
        # result['price_matrix'] = price_matrix

        return HttpResponse(json.dumps(result), 'application/json')

# admin views

@login_required(login_url='/Admin/login/')
def city_image(request):
    city_images = CityImages.objects.all()
    return render(request, 'Admin/city_image.html', {'city_images': city_images})

def city_image_delete(request, id):
    if request.is_ajax():        
        CityImages.objects.get(city_image_id=id).delete()
        return HttpResponse('success')
    
@login_required(login_url='/Admin/login/')
def city_image_update(request, id=None):
    city_image = CityImages()
    if id:
        city_image = CityImages.objects.get(city_image_id=id)

    if request.method == 'GET':
        form = CityImageForm(initial=model_to_dict(city_image))
    else:
        form = CityImageForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['image_path']:
                city_image.image_path = form.cleaned_data['image_path']
            city_image.city_name = form.cleaned_data['city_name']
            city_image.status = form.cleaned_data['status']
            city_image.last_updated = dttime.now()
            city_image.save()
            return HttpResponseRedirect('/Admin/city_image/')

    return render(request, 'Admin/city_image_form.html', {'form':form})

@login_required(login_url='/Admin/login/')
def hotel(request):
    hotels = Hotel.objects.all()
    return render(request, 'Admin/hotel.html', {'hotels': hotels})

def hotel_delete(request, id):
    if request.is_ajax():        
        Hotel.objects.get(id=id).delete()
        return HttpResponse('success')

@login_required(login_url='/Admin/login/')    
def hotel_update(request, id=None):
    hotel = Hotel()
    if id:
        hotel = Hotel.objects.get(id=id)

    if request.method == 'GET':
        form = HotelForm(initial=model_to_dict(hotel))
    else:
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel.prop_id = form.cleaned_data['prop_id']
            hotel.name = form.cleaned_data['name']
            hotel.brand = form.cleaned_data['brand']
            hotel.chain = form.cleaned_data['chain']
            hotel.lat = form.cleaned_data['lat']
            hotel.lon = form.cleaned_data['lon']
            hotel.address = form.cleaned_data['address']
            hotel.img = form.cleaned_data['img']
            hotel.url = form.cleaned_data['url']
            hotel.cash_rate = form.cleaned_data['cash_rate']
            hotel.points_rate = form.cleaned_data['points_rate']
            hotel.star_rating = form.cleaned_data['star_rating']
            hotel.save()
            return HttpResponseRedirect('/Admin/hotel/')

    return render(request, 'Admin/hotel_form.html', {'form':form})

@login_required(login_url='/Admin/login/')
def email_template(request):
    email_templates = EmailTemplate.objects.all()
    return render(request, 'Admin/email_template.html', {'email_templates': email_templates})

def email_template_delete(request, id):
    if request.is_ajax():        
        EmailTemplate.objects.get(template_id=id).delete()
        return HttpResponse('success')

@login_required(login_url='/Admin/login/')    
def email_template_update(request, id=None):
    email_template = EmailTemplate()
    if id:
        email_template = EmailTemplate.objects.get(template_id=id)

    if request.method == 'GET':
        form = EmailTemplateForm(initial=model_to_dict(email_template))
    else:
        form = EmailTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            email_template.email_code = form.cleaned_data['email_code']
            email_template.subject = form.cleaned_data['subject']
            email_template.body = form.cleaned_data['body']
            email_template.placeholder = form.cleaned_data['placeholder']
            email_template.save()
            return HttpResponseRedirect('/Admin/email_template/')

    return render(request, 'Admin/email_template_form.html', {'form':form})

@login_required(login_url='/Admin/login/')
def static_page(request):
    static_pages = Pages.objects.all()
    return render(request, 'Admin/static_page.html', {'static_pages': static_pages})

@login_required(login_url='/Admin/login/')
def google_ad(request):
    google_ads = GoogleAd.objects.all()
    return render(request, 'Admin/google_ad.html', {'google_ads': google_ads})

def google_ad_delete(request, id):
    if request.is_ajax():        
        GoogleAd.objects.get(ad_id=id).delete()
        return HttpResponse('success')

@login_required(login_url='/Admin/login/')    
def google_ad_update(request, id=None):
    google_ad = GoogleAd()
    if id:
        google_ad = GoogleAd.objects.get(ad_id=id)

    if request.method == 'GET':
        form = GoogleAdForm(initial=model_to_dict(google_ad))
    else:
        form = GoogleAdForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['image_path']:
                google_ad.image_path = form.cleaned_data['image_path']            
            google_ad.ad_code = form.cleaned_data['ad_code']
            google_ad.google_code = form.cleaned_data['google_code']
            google_ad.save()
            return HttpResponseRedirect('/Admin/google_ad/')

    return render(request, 'Admin/google_ad_form.html', {'form':form})

@login_required(login_url='/Admin/login/')
def customer(request):
    customers = User.objects.all()
    return render(request, 'Admin/customer.html', {'customers': customers})


@login_required(login_url='/Admin/login/')    
def customer_update(request, id=None):
    customer = User()
    if id:
        customer = User.objects.get(user_id=id)

    if request.method == 'GET':
        form = CustomerForm(initial=model_to_dict(customer))
    else:
        password = customer.password
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer.username = form.cleaned_data['username']
            customer.first_name = form.cleaned_data['first_name']
            customer.middlename = form.cleaned_data['middlename']
            customer.last_name = form.cleaned_data['last_name']
            customer.email = form.cleaned_data['email']
            if password != form.cleaned_data['password']:
                password = hashlib.md5(form.cleaned_data['password']).hexdigest()
                customer.password = password
            customer.phone = form.cleaned_data['phone']
            customer.gender = form.cleaned_data['gender']
            customer.date_of_birth = form.cleaned_data['date_of_birth']
            customer.language = form.cleaned_data['language']
            customer.country = form.cleaned_data['country']
            customer.address1 = form.cleaned_data['address1']
            customer.address2 = form.cleaned_data['address2']
            customer.city = form.cleaned_data['city']
            customer.state = form.cleaned_data['state']
            customer.zipcode = form.cleaned_data['zipcode']
            customer.usercode = form.cleaned_data['usercode']
            customer.home_airport = form.cleaned_data['home_airport']
            customer.is_active = form.cleaned_data['is_active']
            customer.level = form.cleaned_data['level']
            if not customer.level:
                customer.level = 0
            customer.save()
            return HttpResponseRedirect('/Admin/customer/')

    return render(request, 'Admin/customer_form.html', {'form':form})

def customer_delete(request, id):
    if request.is_ajax():        
        User.objects.get(user_id=id).delete()
        return HttpResponse('success')

@login_required(login_url='/Admin/login/')
def blog_list(request):
    blog_list = Blogs.objects.all()
    return render(request, 'Admin/blog_list.html', {'blog_list': blog_list})

@login_required(login_url='/Admin/login/')
def blog_list_update(request, id=None):
    blog_list = Blogs()
    if id:
        blog_list = Blogs.objects.get(blog_id=id)

    if request.method == 'GET':
        form = BlogForm(initial=model_to_dict(blog_list))
    else:
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['blog_image_path']:
                blog_list.blog_image_path = form.cleaned_data['blog_image_path']
            blog_list.blog_title = form.cleaned_data['blog_title']
            blog_list.blog_url = form.cleaned_data['blog_url']      # needs to be considered
            blog_list.blog_position = form.cleaned_data['blog_position']
            blog_list.blog_content = form.cleaned_data['blog_content']
            blog_list.blog_meta_key = form.cleaned_data['blog_meta_key']
            blog_list.blog_meta_Description = form.cleaned_data['blog_meta_Description']
            blog_list.blog_creator = 'Waff Jason'   # needs to be modified
            blog_list.blog_status = form.cleaned_data['blog_status']
            if not blog_list.blog_created_time:
                blog_list.blog_created_time = dttime.now()
            blog_list.blog_updated_time = dttime.now()
            blog_list.save()
            return HttpResponseRedirect('/Admin/blog_list/')

    return render(request, 'Admin/blog_list_form.html', {'form':form})

def blog_list_delete(request, id):
    if request.is_ajax():        
        Blogs.objects.get(blog_id=id).delete()
        return HttpResponse('success')

@login_required(login_url='/Admin/login/')
def token(request):
    tokens = Token.objects.all()
    return render(request, 'Admin/token.html', {'tokens': tokens})

@login_required(login_url='/Admin/login/')
def token_update(request, id=None):
    if id:
        token = Token.objects.get(id=id)
        pre_owners = token.owner.username
    else:
        token = Token()
        owners = [item.owner.user_id for item in Token.objects.all()]
        pre_owners = User.objects.filter(is_active=True, level=1).exclude(user_id__in=owners)

    if request.method == 'GET':
        form = TokenForm(initial=model_to_dict(token))
    else:
        form = TokenForm(request.POST, instance=token)
        if form.is_valid():
            token.token = form.cleaned_data['token']
            token.owner = form.cleaned_data['owner']
            token.limit_flight_search = form.cleaned_data['limit_flight_search']
            token.limit_hotel_search = form.cleaned_data['limit_hotel_search']
            token.run_hotel_search = form.cleaned_data['run_hotel_search']
            token.run_flight_search = form.cleaned_data['run_flight_search']
            token.allowed_domain = form.cleaned_data['allowed_domain']
            token.notes = form.cleaned_data['notes']
            token.number_update = token.number_update + 1 
            if not token.id:
                token.created_at = dttime.now()
            token.save()
            return HttpResponseRedirect('/Admin/token/')

    return render(request, 'Admin/token_form.html', {'form':form, 'pre_owners':pre_owners})

def token_delete(request, id):
    if request.is_ajax():        
        Token.objects.get(id=id).delete()
        return HttpResponse('success')

def admin_login(request):
    if request.method == 'GET':
        return render(request, 'Admin/login.html', {})    
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                social_login(request, user)

    return HttpResponseRedirect('/Admin/')

@login_required(login_url='/Admin/login/')
def admin_logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/Admin/')

@login_required(login_url='/Admin/login/')
def Admin(request):
    stat_num_search = [['aeroflot', 736], ['airchina', 183], ['american airlines', 0], ['delta', 29861], ['etihad', 382], ['jetblue', 754], ['s7', 1790], ['united', 154182], ['Virgin America', 332], ['Virgin Australia', 6464], ['virgin_atlantic', 55]]
    pop_searches = [{'source': u'New York (NYC)', 'destination': u'Tel Aviv (TLV)', 'dcount': 149}, {'source': u'New York (NYC)', 'destination': u'Seattle (SEA)', 'dcount': 124}, {'source': u'Los Angeles (LAX)', 'destination': u'Miami (MIA)', 'dcount': 89}, {'source': u'Houston (IAH)', 'destination': u'Ft Lauderdale (FLL)', 'dcount': 82}, {'source': u'Bangkok (BKK)', 'destination': u'Tokyo (NRT)', 'dcount': 79}, {'source': u'Beijing (PEK)', 'destination': u'Moscow (MOW)', 'dcount': 78}, {'source': u'New York (JFK)', 'destination': u'Sydney (SYD)', 'dcount': 76}, {'source': u'Moscow (MOW)', 'destination': u'Beijing (NAY)', 'dcount': 68}, {'source': u'Miami (MIA)', 'destination': u'New York (LGA)', 'dcount': 68}, {'source': u'New York (NYC)', 'destination': u'Los Angeles (LAX)', 'dcount': 65}]

    return render(request, 'Admin/dashboard.html', {
        'stat_num_search': stat_num_search,
        'pop_searches': pop_searches
        })

@csrf_exempt
def airline_info(request):
    air_lines = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
    period = int(request.POST.get('period'))
    fare_class = request.POST.get('fare_class')

    start_time = datetime.datetime.now() - timedelta(days=period)
    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

    stat_num_search = []
    for air_line in air_lines:
        kwargs = {
            'scrapetime__gte':start_time,
            '{0}__gt'.format(fare_class):0,
            'datasource': air_line,
        }
        num_search = len(list(Flightdata.objects.filter(**kwargs)))
        stat_num_search.append([air_line, num_search])

    return HttpResponse(json.dumps(stat_num_search))


@csrf_exempt
def popular_search(request):    
    period = int(request.POST.get('period'))    
    start_time = datetime.datetime.now() - timedelta(days=period)
    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')

    pop_searches = Searchkey.objects.filter(scrapetime__gte=start_time).values('source', 'destination').annotate(dcount=Count('*')).order_by('-dcount')[:10]
    pop_searches = [{'source':item['source'], 'destination':item['destination1'], 'dcount':item['dcount']} for item in pop_searches]
    try:
        return HttpResponse(json.dumps(pop_searches))
    except Exception, e:
        print str(e), '@@@@@@@@'
        
