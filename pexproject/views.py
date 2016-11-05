#!usr/bin/env python
import sys
import hashlib
import codecs
import datetime
import settings
import time
import requests
import re
import base64
import subprocess
import json
import collections

from apiclient.discovery import build
from random import randint
from bs4 import BeautifulSoup
from mailchimp import Mailchimp
from types import *
from datetime import datetime as dttime
from datetime import timedelta
from datetime import date
from multiprocessing import Process

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.template import RequestContext
from django.contrib.auth import login as social_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from django.utils import timezone
from django.db import connection
from django.db import models as aggregator
from django.db.models import Q, Count
from django.db.models import Max, Min
from django.forms.models import model_to_dict

from .scrapers.customfunction import is_scrape_vAUS,is_scrape_aeroflot,is_scrape_virginAmerica,is_scrape_etihad,is_scrape_delta,is_scrape_united,is_scrape_virgin_atlantic,is_scrape_jetblue,is_scrape_aa, is_scrape_s7, is_scrape_airchina
from .scrapers import customfunction
from .scrapers.delta_price import get_delta_price
from .scrapers.config import config as sys_config
from .form import *
from pexproject.models import *


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
    else:
        results = 'fail'
    return JsonResponse(results, safe=False)


def get_countryname(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        file_path = '/var/www/html/python/pex/pexproject/pexproject/data/country_region.json'
        json_text = open(file_path, 'r')
        jsonData = json.loads(json_text.read())
        result = []
        for item in jsonData:
            if q.lower() in item['name'].lower():
                country = {}
                country['label'] = item['name']
                country['value'] = item['name']
                result.append(country)
        json_text.close()
    else:
        result = 'fail'
    return JsonResponse(result, safe=False)


@csrf_exempt
def destination_tiles(request):
    _searches = Searchkey.objects.order_by('-searchid')
    searches = []
    cities = []
    for search in _searches:
        # avoid duplicate cities
        if search.destination_city in cities:
            continue
        cities.append(search.destination_city)
        
        _search = { 'final_dest': search.destination_city, 'searchkeyid': search.searchid, 'image_path': None }
        _tmp = CityImages.objects.filter(city_name=search.destination_city)

        if _tmp:
            _search['image_path'] = _tmp[0].image_path.url
        _tmp = Flightdata.objects.filter(~Q(origin='flag'), ~Q(maincabin=0), Q(searchkeyid=search.searchid) ).order_by('maincabin')
        if not _tmp:
            continue
        _tmp = _tmp[0]
        _search['maintax'] = _tmp.maintax
        _search['maincabin'] = _tmp.maincabin
        searches.append(_search)
        if len(searches) == 8:
            break
            
    return render(request, 'flightsearch/destination_tiles.html', { 'searchObj': searches })


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
    curr_path = request.get_full_path()
    if 'blog/' in curr_path:
        blog_title = curr_path.split('blog/')
        if blog_title[1]:
            blog_title = blog_title[1].strip()
            try:
                blog = Blogs.objects.get(blog_url=blog_title)
                title = blog.blog_title
                return render_to_response('flightsearch/blog_details.html',{'blog':blog}, context_instance=RequestContext(request))
            except:
                return render_to_response('flightsearch/blog_details.html', context_instance=RequestContext(request))

    blogs = Blogs.objects.filter(blog_status=1).order_by('-blog_created_time');
    bloglist = []
    top_banner = ''
    for content in blogs:
        blog_title = content.blog_title
        blog_content = content.blog_content

        tree = BeautifulSoup(blog_content)
        img_link = ''
        if tree.find('img'):
            img_link = tree.find('img')['src']
        if content.blog_position == True:
            top_banner = {"blog_title":content.blog_title,'img_link':img_link,'postedon':content.blog_created_time,'featured_image':content.blog_image_path,'blog_url':content.blog_url,'blogid':content.blog_id}
        else: 
            bloglist.append({"blog_title":content.blog_title,'img_link':img_link,'postedon':content.blog_created_time,'featured_image':content.blog_image_path,'blog_url':content.blog_url,'blogid':content.blog_id})
      
    return  render_to_response('flightsearch/Blog.html',{"blog":bloglist,"top_banner":top_banner}, context_instance=RequestContext(request))


def index(request):
    if request.user.is_authenticated():
        #user = User.objects.get(email=request.user)
        user = User.objects.filter(username=request.user)
        if len(user) > 0:
            user = User.objects.get(username=request.user)
            request.session['username'] = request.user.username
            if user.first_name != '':
                request.session['first_name'] = user.first_name
            if user.home_airport != '':
                request.session['homeairpot'] = user.home_airport
            request.session['userid'] = user.user_id
            request.session['level'] = user.level
        else:
            email=request.user
            password = ''
            password1 = hashlib.md5(password).hexdigest()
            airport = ''
            first_name = ''
            last_name = ''
            pexdeals = 0
            object = User(username=email,email=email, password=password1,first_name=first_name,last_name=last_name, home_airport=airport,pexdeals=pexdeals, last_login=dttime.now())
            object.save()
            user = User.objects.get(username=request.user)
            if len(user) > 0:
                request.session['username'] = request.user.username
                if user.first_name != '':
                    request.session['first_name'] = user.first_name
                if user.home_airport != '':
                    request.session['homeairpot'] = user.home_airport
                request.session['userid'] = user.user_id
                request.session['level'] = user.level

    return render(request, 'flightsearch/home.html')    


def pricing(request):
    return render(request, 'flightsearch/pricing.html')   


def signup(request):
    context = {}
    if 'username' not in request.session:
        if request.method == "POST":
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

            object = User(username=email,email=email, password=password1,first_name=first_name,last_name=last_name, home_airport=airport,pexdeals=pexdeals, last_login=dttime.now())
            object.save()
            if pexdeals == '1':
                subscriber = Mailchimp(sys_config['MAILCHIMP_API_KEY'])
                subscriber.lists.subscribe(sys_config['MAILCHIML_LIST_ID'], {'email':email}, merge_vars={'FNAME':first_name,'LNAME':last_name})
            request.session['username'] = email
            request.session['homeairpot'] = airport
            request.session['password'] = password1
            if first_name != '':
                request.session['first_name'] = first_name
            if object.user_id:
                request.session['userid'] = object.user_id
                request.session['level'] = object.level
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


def manageAccount(request):
    cursor = connection.cursor()
    context = {}
    msg = ''
    password1 =''
    userid = ''
    issocial =''
    newpassword1 = ''
    #member = mailchimp_user.lists.member_info(sys_config['MAILCHIML_LIST_ID'],{'email_address':'B.jessica822@gmail.com'})
    subscription = ''
    email1 = request.session['username']
    mailchimp_user = Mailchimp(sys_config['MAILCHIMP_API_KEY'])
    m = mailchimp_user.lists.member_info(sys_config['MAILCHIML_LIST_ID'],[{'email':email1}])['data']
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
        
        try:
            subscriber = Mailchimp(sys_config['MAILCHIMP_API_KEY'])
            subscriber.lists.subscribe(sys_config['MAILCHIML_LIST_ID'], {'email':useremail}, merge_vars={'FNAME':fname,'LNAME':lname})
            data = "Please check you email to PEX+ update"
        except:
            data = useremail + " is an invalid email address"   
        return JsonResponse(data, safe=False)


def login(request):
    context = {}
    user = User()
    user = authenticate()
    currentpath = ''
    if user is not None:
        if user.is_active:
            social_login(request,user)  
    if request.method == "POST": 
        username = request.REQUEST['username']
        password = request.REQUEST['password']
        if "curl" in request.POST:
            currentpath = request.REQUEST['curl']
        password1 = hashlib.md5(password).hexdigest()
        try:
            user = User.objects.get(email=username, password=password1)
            if user > 0:
                user.last_login=datetime.datetime.now()
                user.save()
#       login(request=request, user=user)
                request.session['username'] = username
                request.session['password'] = password1
                if user.first_name != '':
                    request.session['first_name'] = user.first_name
                if user.home_airport != '':
                    request.session['homeairpot'] = user.home_airport
                request.session['userid'] = user.user_id
                request.session['level'] = user.level

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
                print 'after object'
            except:
                return HttpResponseRedirect('/index?msg=Invalid username')
                #return render_to_response('flightsearch/index.html', {'msg':"Invalid username"}, context_instance=RequestContext(request))
        text = ''
        # print "user",user
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
        return JsonResponse(text, safe=False)       
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
    print time1 
    code = request.GET.get('usercode','')
    print code
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
    
        # send email to pexportal
        obj = EmailTemplate.objects.get(email_code='feedback')
        emailbody = obj.body
        emailbody = emailbody.replace('[USERNAME]',from_emailid)
        emailbody = emailbody.replace('[FEEDBACK_MESSAGE]',body)
        resp = customfunction.sendMail(from_emailid, 'info@pexportal.com', topic, emailbody, html_content)

        if resp == "sent":
            # send email to the customer
            reply_template = EmailTemplate.objects.get(email_code='feedback_reply')
            reply_subject = reply_template.subject
            reply_body = reply_template.body
            reply_body = reply_body.replace('[USERNAME]',from_emailid)
            customfunction.sendMail('info@pexportal.com', from_emailid, reply_subject, reply_body, html_content)
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
    contact_info = ''

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

        contact_info = contact_info + "Email: {}<br>".format(email) if email else contact_info
        contact_info = contact_info + "Phone Number: {}<br>".format(phone) if phone else contact_info
        contact_info = contact_info + "Company: {}<br>".format(company) if company else contact_info
        contact_info = contact_info + "Website: {}<br>".format(websitename) if websitename else contact_info

        fullname = first_name+" "+last_name
        emailbody_ = message+"<br>"+labeltext+"<br>"
        # send email to pexportal
        obj = EmailTemplate.objects.get(email_code='contactus')
        emailbody = obj.body
        emailbody = emailbody.replace('[USERNAME]',fullname)
        emailbody = emailbody.replace('[CONTACT_MESSAGE]',emailbody_)
        emailbody = emailbody.replace('[CONTACT_INFO]',contact_info)

        resp = customfunction.sendMail(email,'info@pexportal.com', topic, emailbody, html_content)

        if resp == "sent":
            # send email to the customer
            reply_template = EmailTemplate.objects.get(email_code='feedback_reply')
            reply_subject = reply_template.subject
            reply_body = reply_template.body
            reply_body = reply_body.replace('[USERNAME]',email)
            customfunction.sendMail('info@pexportal.com', email, reply_subject, reply_body, html_content)            
            contact_msg = "Your information has been sent successfully"
        else:
            contact_msg = "There is some technical problem. Please try again"    
    return render_to_response('flightsearch/contact_us.html',{'contact_msg':contact_msg}, context_instance=RequestContext(request))  
        

@csrf_exempt
def search(request):
    if request.is_ajax():
        # try:
        returndate = request.POST['returndate']
        origin = request.POST['fromMain'].strip()
        destination = request.POST['toMain'].strip()

        auto = re.search(r'^.* \(([A-Z]{3}?)\)$', origin)
        if auto:
            origin = auto.group(1)
        auto = re.search(r'^.* \(([A-Z]{3}?)\)$', destination)
        if auto:
            destination = auto.group(1)

        try:
            orgnid = Airports.objects.filter(code__iexact=origin)[0].airport_id
            destid = Airports.objects.filter(code__iexact=destination)[0].airport_id
        except Exception, e:
            return HttpResponse(11, status=405)

        depart = request.POST['deptdate']
        searchtype = request.POST.get('searchtype', '')
        cabin = request.POST['cabin']

        # check limit
        _ret = check_limit(request, 'flight')
        if _ret: # not success
            return HttpResponse(_ret, status=405)

        key_json = _search(returndate, str(orgnid), str(destid), depart, searchtype, cabin, request)
        return JsonResponse(key_json)

        # except Exception, e:
        #     print str(e), '###########3'
        

def check_limit(request, service):
    """
    check rate limit for searches on ui
    return  0 if ok
            1 if limited and signed up
            2 if limited and not signed up
            3 if limited and paid customer
    """
    cookie_id, user_id = get_ids(request)
    
    if user_id > -1 and int(request.session['level']) > 0:     # paying user
        user = User.objects.get(user_id=user_id)
        if user.search_run >= user.search_limit:
            return 3
        user.search_run = user.search_run + 1

        if user.search_run >= user.search_limit * settings.SEARCH_LIMIT_WARNING_THRESHOLD and (user.search_run - 1) < user.search_limit * settings.SEARCH_LIMIT_WARNING_THRESHOLD:
            send_limit_warning_email(user, service)

        user.save()
    else:
        arl = AccessRateLimit.objects.filter(cookie_id=cookie_id)
        if arl:
            arl = arl[0]
            if user_id < arl.user_id:               # sign in -> sign out
                return 2
            else:
                limit_search = SearchLimit.objects.get(user_class='Logged out Users').limit
                if user_id > 0:
                    limit_search = SearchLimit.objects.get(user_class='Logged in Users').limit

                if user_id > arl.user_id:           # sign in
                    arl.user_id = user_id

                number_request = getattr(arl, 'run_%s_search' % service)

                if number_request >= limit_search:
                    return 1 if 'userid' in request.session else 2
                else:            
                    setattr(arl, 'run_%s_search' % service, number_request+1)
                    arl.save()
        else:   # search for the first time
            arl = AccessRateLimit(cookie_id=cookie_id, user_id=user_id)
            setattr(arl, 'run_%s_search' % service, 1)
            arl.save()


def get_ids(request):
    """
    return id from ip and cookie and user_id if signed in
    """
    user_id = int(request.session['userid']) if 'userid' in request.session else -1
    cookie_id = get_client_ip(request) + '-' + request.COOKIES['_ga']
    return cookie_id, user_id


def _search(returndate, orgnid, destid, depart, searchtype, cabin, request):
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
        # print '@@@@', orgn, origin, '@@@@'

        dest = destobj.cityName + ", " + destobj.cityCode + ", " + destobj.countryCode + "  (" + destobj.code + ")"
        etihaddest = destobj.cityName
        destcode = destobj.code
        destination1 = destobj.cityName + " (" + destobj.code + ")"
        # print '####', dest, destination1, '####'
        
        dt = datetime.datetime.strptime(depart.strip(), '%m/%d/%Y')
        date = dt.strftime('%m/%d/%Y')
        searchdate = dt.strftime('%Y-%m-%d')        
        # print '$$$$', searchdate, '$$$$'
        
        currentdatetime = datetime.datetime.now()
        time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        time1 = datetime.datetime.now() - timedelta(minutes=30)
        time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
        if searchdate1:
            obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)
            returnobj = Searchkey.objects.filter(source=destination1, destination=origin, traveldate=searchdate1, scrapetime__gte=time1)

            if returnobj:
                returnobj = returnobj[0]
                if request.session.get('userid'):
                    returnobj.user_ids = returnobj.user_ids+str(request.session.get('userid'))+','
                    returnobj.save()
                returnkey = returnobj.searchid
            else:
                user_id = ','+str(request.session.get('userid', ''))+','
                searchdata = Searchkey(source=destination1, destination=origin, destination_city=etihadorigin,traveldate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid, user_ids=user_id)
                searchdata.save()
                returnkey = searchdata.searchid
                if is_scrape_jetblue == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/jetblue.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                if is_scrape_virginAmerica == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/virginAmerica.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                
                if is_scrape_delta == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/delta.py",destcode, orgncode, str(date1).strip(), str(returndate).strip(), str(returnkey),etihaddest,etihadorigin,cabin])
                if is_scrape_united == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/united.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                if is_scrape_s7 == 1:
                    customfunction.flag = customfunction.flag+1
                    # print '@@@@@ S7 Round trip', destobj.code, originobj.code, str(searchdate1), str(returnkey)                        
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/s7.ru.py",destobj.code, originobj.code, str(searchdate1).strip(), str(returnkey)])
                    # subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/s7.ru.py",destobj.cityCode, originobj.cityCode, str(searchdate1), str(returnkey)])
                if is_scrape_aa == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/aa.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                if is_scrape_vAUS == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/virgin_australia.py",destcode, orgncode, str(returndate).strip(), str(returnkey),cabin])
               
                if is_scrape_etihad == 1:
                    customfunction.flag = customfunction.flag+1
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/etihad.py",etihaddest, etihadorigin, str(date1).strip(), str(returnkey),cabin])
            
            ''' Flexible date search scraper for return Date'''
            if returnkey and  'flexibledate' in searchtype:
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/Flex_delta.py",destcode, orgncode, str(returndate).strip(), str(returnkey),cabin])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/flex_jetblue.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/flex_virgin_atlantic.py",destcode, orgncode, str(returndate).strip(), str(returnkey)])
                    
            '''-------------------------------------'''
        else:
            obj = Searchkey.objects.filter(source=origin, destination=destination1, traveldate=searchdate, scrapetime__gte=time1)

        if obj:           
            obj = obj[0]
            if request.session.get('userid'):
                obj.user_ids = obj.user_ids+str(request.session.get('userid'))+','
                obj.save()
            searchkeyid = obj.searchid
        else:
            user_id = ','+str(request.session.get('userid', ''))+','
            if dt1:
                searchdata = Searchkey(source=origin, destination=destination1,destination_city=etihaddest, traveldate=dt, returndate=dt1, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid, user_ids=user_id) 
            else:
                searchdata = Searchkey(source=origin, destination=destination1,destination_city=etihaddest, traveldate=dt, scrapetime=time, origin_airport_id=orgnid, destination_airport_id=destid, user_ids=user_id)
            searchdata.save()
            searchkeyid = searchdata.searchid 
            cursor = connection.cursor()
            ''' Flexible date search scraper for return Date'''
            if searchkeyid and  'flexibledate' in searchtype:
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/Flex_delta.py",orgncode,destcode, str(depart).strip(), str(searchkeyid),cabin])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/flex_jetblue.py",orgncode,destcode, str(depart).strip(), str(searchkeyid)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/flex_virgin_atlantic.py",orgncode,destcode, str(depart).strip(), str(searchkeyid)])
                    
            '''-------------------------------------'''
            customfunction.flag = 0
    
            if is_scrape_jetblue == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/jetblue.py",orgncode,destcode,str(depart).strip(),str(searchkeyid)])
            if is_scrape_virginAmerica == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/virginAmerica.py",orgncode,destcode,str(depart).strip(),str(searchkeyid)])                
            if is_scrape_delta == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/delta.py",orgncode,destcode,str(date),str(depart).strip(),str(searchkeyid),etihadorigin,etihaddest,cabin])
            if is_scrape_united == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/united.py",orgncode,destcode,str(depart).strip(),str(searchkeyid)])
            if is_scrape_s7 == 1:
                customfunction.flag = customfunction.flag+1
                # print '@@@@@ S7 One way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)                    
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/s7.ru.py", originobj.code, destobj.code, str(searchdate).strip(), str(searchkeyid)])
            if is_scrape_aa == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/aa.py",orgncode,destcode,str(depart).strip(),str(searchkeyid)])
            if is_scrape_vAUS == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/virgin_australia.py",orgncode,destcode,str(depart).strip(),str(searchkeyid),cabin])
            if is_scrape_etihad == 1:
                customfunction.flag = customfunction.flag+1
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/etihad.py",etihadorigin,etihaddest,str(date).strip(),str(searchkeyid),cabin])
            if is_scrape_aeroflot == 1:
                if not searchdate1:
                    customfunction.flag = customfunction.flag+1 
                    # print '@@@@@ Aeroflot One Way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/aeroflot.py", originobj.code, destobj.code, str(searchdate).strip(), str(searchkeyid)])
            if is_scrape_airchina == 1:
                if not searchdate1:
                    customfunction.flag = customfunction.flag+1 
                    # print '@@@@@ AirChina One Way', originobj.code, destobj.code, str(searchdate), str(searchkeyid)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/airchina.py", originobj.code, destobj.code, str(searchdate).strip(), str(searchkeyid)])
                
        if is_scrape_virgin_atlantic == 1:
            customfunction.flag = customfunction.flag+1
            Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='virgin_atlantic').delete()
            if returnkey:
                Flightdata.objects.filter(searchkeyid=returnkey,datasource='virgin_atlantic').delete()            
            subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/virgin.py",orgncode,destcode, str(depart).strip(), str(returndate).strip(), str(searchkeyid),str(returnkey)])

        if returnkey:
            if is_scrape_aeroflot == 1:
                flight_to = Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='aeroflot')
                flight_from = Flightdata.objects.filter(searchkeyid=returnkey,datasource='aeroflot') 
                if not (flight_to and flight_from):
                    customfunction.flag = customfunction.flag+1
                    Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='aeroflot').delete()
                    Flightdata.objects.filter(searchkeyid=returnkey,datasource='aeroflot').delete()            
                    # print '@@@@@ Aeroflot Round Trip', orgncode, destcode, str(searchdate), str(searchkeyid), str(searchdate1), str(returnkey)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/aeroflot_rt.py", orgncode, destcode, str(searchdate).strip(),str(searchkeyid), str(searchdate1).strip(), str(returnkey)])
            if is_scrape_airchina == 1:
                flight_to = Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='airchina')
                flight_from = Flightdata.objects.filter(searchkeyid=returnkey,datasource='airchina') 
                if not (flight_to and flight_from):
                    customfunction.flag = customfunction.flag+1
                    Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='airchina').delete()
                    Flightdata.objects.filter(searchkeyid=returnkey,datasource='airchina').delete()            
                    # print '@@@@@ AirChina Round Trip', orgncode, destcode, str(searchdate), str(searchkeyid), str(searchdate1), str(returnkey)
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/scrapers/airchina_rt.py", orgncode, destcode, str(searchdate).strip(),str(searchkeyid), str(searchdate1).strip(), str(returnkey)])

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
    else:
        results = 'fail'
    return JsonResponse(results, safe=False)


def checkData(request):
    if request.is_ajax():
        cabin = request.POST['cabin']
        allkey = request.POST.get('multicity')
        recordkey = request.POST.get('keyid')
        returnkey = request.POST.get('returnkey')
        
        results = _check_data(recordkey, returnkey, cabin, allkey)
        return JsonResponse(results, safe=False)
    

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
        

def get_flight_pricematrix(request):
    """
    Get a price matrix after flight search is done.
    According to the parameter, it returns mile range and farecode filters.
    """
    cabinclass = request.POST.get('cabin', '')
    getPriceRange = 'valuefor' in request.POST
    multicitykey = request.POST.get('multicity', '')
    key = request.POST.get('keyid', '')
    returnkeyid = request.POST.get('returnkey', '')

    if 'maincabin' in cabinclass:
        fare_class_code = 'eco_fare_code'
    elif 'firstclass' in cabinclass:
        fare_class_code = 'business_fare_code'
    else:
        fare_class_code = 'first_fare_code'

    if multicitykey:
        n = 1
        multicitykey1 = multicitykey.split(',')
        recordkey = multicitykey1[0]
        ecocabin = 'min(if(p1.maincabin > 0,p1.maincabin,NULL))'
        busscabin = 'min(if(p1.firstclass > 0,p1.firstclass,NULL))'
        firstcabin = 'min(if(p1.business > 0,p1.business,NULL))'
        adding = '+'
        inner_join_on = ''
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
   
    elif key:
        if returnkeyid:
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
        for cd in list(FareCodeFromDatabase):
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

        return JsonResponse([minPriceMile, maxPriceMile, fare_code_Array], safe=False)


    price_matrix = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
    price_matrix = {item: [None, None, None] for item in price_matrix}

    if pricematrix:
        for item in pricematrix:
            price_matrix[item.datasource] = [item.maincabin, item.firstclass, item.business]

    return render_to_response('flightsearch/pricematrix.html',{'price_matrix': price_matrix}, context_instance=RequestContext(request))


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

    if 'maincabin' in cabinclass:
        fare_class_code = 'eco_fare_code'
    elif 'firstclass' in cabinclass:
        fare_class_code = 'business_fare_code'
    else:
        fare_class_code = 'first_fare_code'
    
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
                record = Flightdata.objects.raw("select p1.*,CONCAT(p1.rowid,'_',p2.rowid) as newid,p2.origin as origin1,p2.rowid as rowid1, p2.stoppage as stoppage1,p2.flighno as flighno1, p2.cabintype1 as cabintype11,p2.cabintype2 as cabintype21,p2.cabintype3 as cabintype31, p2.destination as destination1, p2.departure as departure1, p2.arival as arival1, p2.duration as duration1, p2.maincabin as maincabin1, p2.maintax as maintax1, p2.firsttax as firsttax1, p2.businesstax as businesstax1,p2.departdetails as departdetails1,p2.arivedetails as arivedetails1, p2.planedetails as planedetails1,p2.operatedby as operatedby1," + totalfare + " as finalprice,  "+totaltax+" as totaltaxes from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ='" + returnkeyid1 + "' and " + returnfare + " > '0'  where  p1.searchkeyid = '" + searchkey + "' and " + departfare + " > 0 and " + querylist + " order by finalprice ,totaltaxes, departure, p2.departure ASC")
                
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
                # print '$$$(class filtered): ', querylist
                record = Flightdata.objects.raw("select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice, "+taxes+" as totaltaxes from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC")
                # print '$$$ (synthesis): ', "select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice, "+taxes+" as totaltaxes from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset)
            mainlist = list(record)
            # filter aircraft
            mainlist_ = []            
            aircrafts_filter = request.POST.getlist('aircraft')
            if request.is_ajax():
                aircrafts_filter = aircrafts_filter[0].split(',')

            if aircrafts_filter and aircrafts_filter != [u'']:
                print len(mainlist), ':Before filter #@#@#@#@#'
                print aircrafts_filter, '@@@@@@@@@'
                for flight_ in mainlist:
                    aircrafts = get_aircraft_info_(flight_)
                    aircrafts = get_category_aircrafts(aircrafts)
                    for key, val in aircrafts.items():
                        if set(aircrafts_filter) & set(val):
                            mainlist_.append(flight_)
                            print aircrafts, '#######'
                            break
                mainlist = mainlist_
                print len(mainlist), ':AFter filter #@#@#@#@#'
            mainlist = mainlist[offset:offset+limit]

        progress_value = '' 
        if 'progress_value' in request.POST:
            progress_value = request.REQUEST['progress_value']
            
        recordlen = len(multicitykey1)
        timerecord = Flightdata.objects.raw("SELECT rowid,MAX(departure ) as maxdept,min(departure) as mindept,MAX(arival) as maxarival,min(arival) as minarival FROM  `pexproject_flightdata` ")
        filterkey = {'stoppage':list2,'fareCodes':json.dumps(codesList),'fareCodelength':len(codesList), 'datasource':list1, 'cabin':cabin,'minpricemile':minpricemile,'maxpricemile':maxpricemile, 'aircraft': json.dumps(aircrafts_filter)}
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
            return render_to_response('flightsearch/search.html', {'action':action,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value, 'multisearch':multisearch, 'data':mainlist, 'multicity':multicity, 'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request))

        if 'userid' in request.session and  'actionfor' not in request.POST:
            _, flight = get_reward_config(request)
            pointlist = get_pointlist(request, '%', str(tuple(flight+[''])))
        
        return render_to_response('flightsearch/searchresult.html', {'title':title,'action':action,'pointlist':pointlist,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value,'multisearch':multisearch,'data':mainlist,'multicity':multicity,'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request)) 
        

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


def flightAlert(request):
    context = {}
    record = ''
    if request.is_ajax and 'alertid' in request.POST:
        alertid = request.POST['alertid']
        record = UserAlert.objects.get(pk=alertid)
        record_json = {}
        record_json['alertid'] = record.alertid
        record_json['from_airport'] = record.from_airport
        record_json['to_airport'] = record.to_airport
        record_json['source_airportid'] = record.source_airportid
        record_json['destination_airportid'] = record.destination_airportid
        record_json['departdate'] = str(record.departdate)
        record_json['returndate'] = str(record.returndate)
        record_json['maxprice'] = str(record.pricemile)
        record_json['traveller'] = str(record.traveller)
        record_json['cabin'] = str(record.cabin)
        record_json['annual_repeat'] = str(record.annual_repeat)
        return JsonResponse(record_json)

    userid = request.session['userid']
    #print "userid",userid
    alertResult1 = UserAlert.objects.filter(userid=userid)
    alertResult = list(alertResult1)
    #print alertResult        
    return render_to_response('flightsearch/flight_alert.html',{"alertResult":alertResult,"record":record},context_instance=RequestContext(request))


def useralert(request):
    context = {}
    if 'action' in request.GET and request.GET.get('action') == 'delete' and 'alertid' in request.GET:
        alertid = request.GET['alertid']
        UserAlert.objects.get(pk=alertid).delete()
        
    if request.POST and  'userid' in request.session:
        currentDate = datetime.datetime.now().date()
        preDate = currentDate - timedelta(days=1)
        message = ''
        alertuser = UserAlert()
        alertuser.cabin = request.POST['cabintype']
        alertuser.traveller = request.POST['passenger']
        #print request.POST['year_repeat']
        if 'year_repeat'in request.POST:
            alertuser.annual_repeat = request.POST['year_repeat']
        else:
            alertuser.annual_repeat = 0
        email = request.session['username']
        alertuser.user_email = email
        alertuser.userid = request.session['userid']
        triptype = request.POST['trip']
        alertuser.source_airportid = request.POST['fromid']
        alertuser.destination_airportid = request.POST['destid']
        alertuser.departdate = request.POST['alt_depardate']
        alertuser.from_airport = request.POST['from']
        alertuser.to_airport = request.POST['to']
        if 'pricemile' in request.POST and request.POST['pricemile']:
            alertuser.pricemile = request.POST['pricemile']
        if 'alt_returndate' in request.POST and request.POST['alt_returndate']:
            alertuser.returndate = request.POST['alt_returndate']
            # print "alt_returndate",request.POST['alt_returndate']
        if 'alt_expire' in request.POST and request.POST['alt_expire']:
            alertuser.expiredate = request.POST['alt_expire']
        else:
            alertuser.expiredate = request.POST['alt_depardate']
        if 'alertday' in request.POST:
            alertday = request.POST.getlist('alertday')
            alertuser.alertday = ','.join(alertday)
        alertuser.sent_alert_date = preDate
        if 'alertid' in request.POST and request.POST['alertid']:
            alertuser.alertid = request.POST['alertid']
            message = "Flight price alert has been updated successfully"
        else:
            message = "You have successfully created a Flight price alert"
        try:
            alertuser.save()
            
            '''
            html_content = ''
            email_sub = "PEX+ miles alert"
            emailbody = "Hello <b>"+email+"</b>,<br><br> you have successfully created a PEX+ flight miles alert.<br><br>Thanks,<br><b> PEX+ Team"
            resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
           
            '''
        except:
            message = "Something went wrong, Please try again"
        return HttpResponseRedirect('/flightAlert?status='+message)
    return HttpResponseRedirect(reverse('flightAlert'))


def subscribe(request):
    if request.is_ajax:
        email = request.POST['emailid']
        subscriber = Mailchimp(sys_config['MAILCHIMP_API_KEY'])
        subscriber.lists.subscribe(sys_config['MAILCHIML_LIST_ID'], {'email':email})
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

    filters = {'price_low':price_low, 'price_high':price_high, 'award_low':award_low, 'award_high':award_high, 'radius': float(radius), 'chain': chain, 'amenity': [] }
    return ['', place, checkin, checkout, filters]


@csrf_exempt
def api_search_hotel(request):
    if request.method == 'POST':        
        result = {}

        _token = check_validity_token(request.META.get('HTTP_AUTHORIZATION'), 'hotel', request)
        error_message = _token[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return JsonResponse(result)


        _params = check_validity_hotel_params(request)
        error_message = _params[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return JsonResponse(result)


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
            result['hotels'] = db_hotels

        return JsonResponse(result, safe=False)

        

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
            db_hotels = Hotel.objects.filter(search__contains=',%d,'%search.id)
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
            if not Hotel.objects.filter(search__contains=',%d,'%search.id):
                search.delete()
            return ['There is no hotel in the place. Please check fields again.']      

        for hotel in hotels:
            _hotel = {}
            _hotel['prop_id'] = hotel['propID']
            _hotel['cash_rate'] = get_value(hotel['cashRate']) or 1000000
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

            # db_hotel = Hotel.objects.filter(search=search.id, prop_id=_hotel['prop_id'])
            db_hotel = Hotel.objects.filter(prop_id=_hotel['prop_id'])            
            if db_hotel:
                _hotel['search'] = db_hotel[0].search
                if not str(search.id) in _hotel['search'].split(','):
                    _hotel['search'] = _hotel['search']+'%d,'%search.id

                _hotel['name'] = db_hotel[0].name
                if not _hotel['img']:
                    _hotel['img'] = db_hotel[0].img
                if not _hotel['lat']:
                    _hotel['lat'] = db_hotel[0].lat
                if not _hotel['lon']:
                    _hotel['lon'] = db_hotel[0].lon

                db_hotel.update(**_hotel)
            else:
                Hotel.objects.create(search=',%d,'%search.id, **_hotel)

        db_hotels = Hotel.objects.filter(search__contains=',%d,'%search.id)

    # filter the result
    price_lowest = db_hotels.aggregate(Min('cash_rate'))['cash_rate__min']
    price_highest = db_hotels.filter(~Q(cash_rate=1000000)).aggregate(Max('cash_rate'))['cash_rate__max']
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
    tmp = float(filters['award_low'] or award_lowest or 0)
    award_low = max(tmp, award_lowest)
    tmp = float(filters['award_high'] or award_highest)
    award_high = min(tmp, award_highest)
    star_rating = filters.get('star_rating', ['1', '2', '3', '4', '5'])
    star_rating = [item.encode('ascii', 'ignore') for item in star_rating]
    if star_rating == []:
        star_rating = ['1', '2', '3', '4', '5']

    # __debug('## chain: %s\n\n' % str(filters.chain))
    dis_place = place.split('-')[0]

    db_hotels = db_hotels.filter(
        Q(cash_rate__lte=price_high), 
        Q(points_rate__lte=award_high), 
        Q(distance__lte=filters['radius']), 
        Q(chain__in=filters['chain']), 
        Q(cash_rate=0.0)|Q(cash_rate__gte=price_low), 
        Q(points_rate=0.0)|Q(points_rate__gte=award_low))

    # filter by star rating
    r_db_hotels = db_hotels.filter(star_rating=0)
    for star in star_rating:
        low = float(star) - 0.51
        high = float(star) + 0.41
        r_db_hotels = r_db_hotels | db_hotels.filter(star_rating__range=(low,high))
    
    db_hotels = r_db_hotels.order_by('-star_rating', 'cash_rate')

    # filter by amenities
    r_db_hotels = db_hotels.all()

    for hotel in r_db_hotels:
        amenities = HotelAmenity.objects.filter(hotel=hotel)
        amenities = [am.amenity for am in amenities]
        if not set(filters['amenity']).issubset(set(amenities)):
            db_hotels = db_hotels.exclude(id=hotel.id)

    # get price matrix
    # '-' if none
    price_matrix = {}
    for item in HOTEL_CHAINS:
        price_min = db_hotels.filter(chain__contains=item).filter(~Q(cash_rate=0.0)).aggregate(Min('cash_rate'))['cash_rate__min']
        points_min = db_hotels.filter(chain=item).filter(~Q(points_rate=0)).aggregate(Min('points_rate'))['points_rate__min'] or '-'
        price_matrix[item] = {'cash_rate': price_min, 'points_rate': points_min, 'title': HOTEL_CHAINS[item]}
    # __debug('price_matrix: %s\n\n' % str(price_matrix))

    filters = {
        'price_low':price_low, 
        'price_high':price_high, 
        'award_low':award_low, 
        'award_high':award_high, 
        'radius':filters['radius'], 
        'chain':filters['chain'], 
        'amenity':filters['amenity'],
        'price_lowest':price_lowest, 
        'price_highest':price_highest, 
        'award_lowest':award_lowest, 
        'award_highest':award_highest, 
        'dis_place':dis_place, 
        'star_rating': star_rating
    }
    # __debug('filters: %s\n' % str(filters))

    r_db_hotels = []
    for item in db_hotels:
        amenities = HotelAmenity.objects.filter(hotel=item)
        amenities = [am.amenity for am in amenities]
        _item = model_to_dict(item)
        _item['amenity'] = amenities
        r_db_hotels.append(_item)

    return ['', r_db_hotels, price_matrix, filters]


def search_hotel(request):
    _ret = False #check_limit(request, 'hotel')
    if _ret: # not success
        error_message = 'You reached hotel search limit!'
        if _ret == 2:
            error_message += '   Please sign up and get more access!'

        form = HotelSearchForm()
        form.errors['Error: '] = error_message
        return render(request, 'hotelsearch/hotel_result.html', {
            'hotels': [], 
            'form': form, 
            'price_matrix': {}, 
            'chains': HOTEL_CHAINS,
            'amenities': HOTEL_AMENITIES,
            'filters': {}})

    if request.method == 'POST':
        form = HotelSearchForm(request.POST)
        if not form.is_valid():
            return render(request, 'hotelsearch/hotel_result.html', {'hotels': [], 'form': form, 'price_matrix': {}, 'filters': {}})
        place = form.cleaned_data['place']
        checkin = form.cleaned_data['checkin']
        checkout = form.cleaned_data['checkout']
        
        filters = {'price_low':request.POST.get('price_low'), 'price_high':request.POST.get('price_high'), 'award_low':request.POST.get('award_low'), 'award_high':request.POST.get('award_high'), 'radius':int(request.POST.get('radius', 1000)), 'chain':request.POST.getlist('hotel_chain', HOTEL_CHAINS.keys()), 'star_rating': request.POST.getlist('star'), 'amenity': request.POST.getlist('amenity')}
    else:
        place = request.GET.get('place')
        place = place.split('&')[0]
        __debug( '@@ place from GET original: %s\n' % place )
        place = parse_place(place)
        __debug( '&& place from  GET  parsed: %s\n' % place )
        checkin = request.GET.get('checkin') or dttime.today().strftime('%Y-%m-%d')
        checkout = request.GET.get('checkout') or (dttime.today() + timedelta(days=2)).strftime('%Y-%m-%d')
        form = HotelSearchForm(initial={'place':place, 'checkin': checkin, 'checkout': checkout})
        filters = {'price_low':'', 'price_high':'', 'award_low':'', 'award_high':'', 'radius': 1000, 'chain': HOTEL_CHAINS.keys(), 'amenity': []}

    result = _search_hotel(place, checkin, checkout, filters)

    error_message = result[0]
    if error_message:
        form.errors['Error: '] = error_message
        return render(request, 'hotelsearch/hotel_result.html', {
            'hotels': [], 
            'form': form, 
            'price_matrix': {}, 
            'chains': HOTEL_CHAINS,
            'amenities': HOTEL_AMENITIES,
            'filters': {}})
    else:
        pointlist = None
        if 'userid' in request.session:
            hotel, _ = get_reward_config(request)
            pointlist = get_pointlist(request, '%', str(tuple(hotel+[''])))

        db_hotels, price_matrix, filters = result[1], result[2], result[3]

        return render(request, 'hotelsearch/hotel_result.html', {
            'hotels': db_hotels, 
            'form': form, 
            'price_matrix': price_matrix, 
            'chains': HOTEL_CHAINS,
            'amenities': HOTEL_AMENITIES,
            'pointlist': pointlist,
            'filters': filters})    


def get_pointlist(request, kind='%', filter_=None):
    """
    return pointlist for a logged in user
    """
    if 'userid' in request.session:
        userid = request.session['userid']
        cursor = connection.cursor()
        sql = "select airlines, reward_points, status, kind, account_no, expiration_date, household, next_level from reward_points where user_id={} and kind like '{}'".format(userid, kind)
        if filter_:
            sql += " and kind in {}".format(filter_)
        cursor.execute(sql)
        pointlist = cursor.fetchall()
        return pointlist


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
    'economy': ['maincabin', 'maintax'],
    'business': ['firstclass', 'firsttax'],
    'firstclass': ['business', 'businesstax']
}


def check_validity_token(token, service, request):
    '''
    check and validate the token from the request for the service (for limit_search and limit_qpx)
    return 
        success: ['', True/False] (check qpx availability)
        fail: [error_message]
    '''
    if not token:
        return ['Authorization should be provided.']
    r = re.compile('^Token \w+$')
    if not r.match(token):
        return ['Authorization format is wrong. It should be in the format("Token <token>").']
    token = token.split('Token ')[1]

    token_ = Token.objects.filter(token=token)

    if token_:
        token = token_[0]

        # check limit
        limit_request = getattr(token, 'limit_%s_search' % service)
        limit_qpx = getattr(token, 'limit_qpx')
        number_request = getattr(token, 'run_%s_search' % service)
        number_request = number_request + 1
        setattr(token, 'run_%s_search' % service, number_request)
        token.save()

        request.session['userid'] = token.owner.user_id

        # send email notification once
        if number_request >= limit_request * settings.SEARCH_LIMIT_WARNING_THRESHOLD and (number_request - 1) < limit_request * settings.SEARCH_LIMIT_WARNING_THRESHOLD:
            send_limit_warning_email(token.owner, service)

        if number_request > limit_request:
            return ['Your license is reached to its limit. Please extend it!']
        # check domain
        return ['', limit_qpx > number_request, None]

    token_ = Token.objects.filter(test_token=token)

    if token_:
        token = token_[0]
        request.session['userid'] = token.owner.user_id
        return ['', True, token.test_qpx_token]

    return ['The token you provided is not correct!']


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

    origin_ = params.get('origin')
    destination_ = params.get('destination')
    depart_date = params.get('depart_date')
    return_date = params.get('return_date')
    search_type = params.get('search_type', 'exactdate')
    flight_class = params.get('class')
    mile_low = params.get('mile_low') or '1'
    mile_high = params.get('mile_high') or '10000000'
    airlines = params.get('airlines') or ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
    airlines.append('valid_line')
    airlines = [item.encode('ascii', 'ignore') for item in airlines]

    depart_from = params.get('depart_from') or '00:00:00'
    depart_to = params.get('depart_to') or '23:59:59'
    arrival_from = params.get('arrival_from') or '00:00:00'
    arrival_to = params.get('arrival_to') or '23:59:59'

    if http_accept != 'application/json' or content_type != 'application/json':
        return ['Content type  is incorrect']

    if not (origin_ and destination_):
        return ['Flight origin and destination should be provided']

    origin = Airports.objects.filter(code__istartswith=origin_)
    if not origin:
        origin = Airports.objects.filter(cityName__istartswith=origin_)
    if not origin:
        origin = Airports.objects.filter(name__istartswith=origin_)

    destination = Airports.objects.filter(code__istartswith=destination_)
    if not destination:
        destination = Airports.objects.filter(cityName__istartswith=destination_)
    if not destination:
        destination = Airports.objects.filter(name__istartswith=destination_)

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
    
    flight_class = FLIGHT_CLASS[flight_class][0]

    return ['', return_date, str(origin), str(destination), depart_date, search_type, flight_class, mile_low, mile_high, airlines, depart_from, depart_to, arrival_from, arrival_to]


@csrf_exempt
def api_search_flight(request):
    if request.method == 'POST':
        logos = {
            'aeroflot': 'aeroflot.png',
            'airchina': 'airchinaLogo.gif',
            'american airlines': 'aa.jpg',
            'delta': 'deltaLogo.jpg',
            'etihad': 'etihad.jpg',
            'jetblue': 'jetblue.jpg',
            's7': 's7Logo.svg',
            'united': 'unitedLogo.png',
            'Virgin America': 'va.jpg',
            'Virgin Australia': 'VAUS.png',
            'virgin_atlantic': 'virgin.png'        
        }

        result = {}

        _token = check_validity_token(request.META.get('HTTP_AUTHORIZATION'), 'flight', request)
        error_message = _token[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return JsonResponse(result)


        fare_class = json.loads(request.body).get('class')
        _params = check_validity_flight_params(request)
        error_message = _params[0]
        if error_message:
            result['status'] = 'Failed'
            result['message'] = error_message
            return JsonResponse(result)


        # get valid parameters
        return_date, origin, destination, depart_date, search_type, flight_class, mile_low, mile_high, airlines, depart_from, depart_to, arrival_from, arrival_to = _params[1], _params[2], _params[3], _params[4], _params[5], _params[6], _params[7], _params[8], _params[9], _params[10], _params[11], _params[12], _params[13]

        keys = _search(return_date, origin, destination, depart_date, search_type, flight_class, request)        

        delay_threshold = 38 if keys['returnkey'] else 42

        qpx_prices = {}
        # get qpx price
        origin_ = Airports.objects.get(airport_id=origin).code
        destination_ = Airports.objects.get(airport_id=destination).code

        if _token[1]:   # check qpx limit
            price_start_time = datetime.datetime.now()
            carriers, max_stop = get_qpx_filter_carriers(origin, destination)
            qpx_prices = get_qpx_prices(return_date, origin_, destination_, depart_date, _token[2], carriers, max_stop)
            delta_departure_price, delta_return_price = get_delta_price(origin_, destination_, depart_date, return_date)
            print delta_departure_price, delta_return_price, '#######'
            delay_threshold -= (datetime.datetime.now() - price_start_time).seconds

        qpx_unmatch_count = 0

        while(1):
            delay_threshold -= 1
            time.sleep(1)
            # check the status of the scraping
            scrape_status = _check_data(keys['departkey'], keys['returnkey'], flight_class, '')
            if scrape_status[1] == 'completed' or delay_threshold < 0:
                break

        if not keys['returnkey']:
            kwargs = {
                'searchkeyid': keys['departkey'], 
                '{0}__range'.format(flight_class):(mile_low, mile_high),
                'datasource__in': airlines,
                'departure__range': (depart_from, depart_to),
                'arival__range': (arrival_from, arrival_to)
            }

            __debug('## filters for flight api: %s\n' % str(kwargs)) 
            flights_ = Flightdata.objects.filter(**kwargs)
            flights = []
            # convert each property to string for json dump
            for flight in flights_:
                flight_ = model_to_dict(flight, exclude=['rowid', 'scrapetime', 'searchkeyid', 'stoppage_station', 'arivedetails', 'operatedby', 'departdetails', 'planedetails', 'economy_code', 'first_fare_code', 'first_code', 'eco_fare_code', 'arival', 'business_code', 'firsttax', 'maintax', 'businesstax', 'cabintype3', 'cabintype2', 'business', 'maincabin', 'cabintype1', 'firstclass', 'business_fare_code'])
                flight_['arrival'] = flight.arival
                flight_['image'] = 'pexportal.com/static/flightsearch/img/'+logos[flight.datasource]
                price_key = get_qpx_price_key(flight.planedetails).encode('ascii', 'ignore')        
                flight_['price'] = qpx_prices.get(price_key, 'N/A')
                # get delta price
                if flight_['price'] == 'N/A':
                    delta_price = delta_departure_price.get(price_key)
                    if delta_price:
                        flight_['price'] = delta_price.get(fare_class, 'N/A')

                flight_['total_miles'] = getattr(flight, FLIGHT_CLASS[fare_class][0])
                flight_['total_taxes'] = getattr(flight, FLIGHT_CLASS[fare_class][1])

                # compute percentage of match
                if flight_['price'] == 'N/A':
                    qpx_unmatch_count += 1

                for k,v in flight_.items():
                    flight_[k] = str(v)
                flight_['route'] = parse_detail(flight.departdetails, flight.arivedetails, flight.planedetails, flight.operatedby)
                if not flight_['route']:
                    continue

                flights.append(flight_)

        else:
            totalfare = "p1." + FLIGHT_CLASS[fare_class][0] + "+p2." + FLIGHT_CLASS[fare_class][0]
            totaltax = "p1." + FLIGHT_CLASS[fare_class][1] + "+p2." + FLIGHT_CLASS[fare_class][1]
            returnfare = "p2." + FLIGHT_CLASS[fare_class][0]
            departfare = "p1." + FLIGHT_CLASS[fare_class][0]
            querylist = "p1.datasource IN %s AND p1.departure >='%s' AND p1.departure <='%s' AND p2.arival >='%s' AND p2.arival <='%s' AND %s >= %s AND %s <= %s" % (str(tuple(airlines)), depart_from, depart_to, arrival_from, arrival_to, totalfare, mile_low, totalfare, mile_high)

            _flights = Flightdata.objects.raw("select p1.*,p2.origin as return_origin, p2.stoppage as return_stoppage,p2.flighno as return_fligh_no, p2.destination as return_destination, p2.departure as return_departure, p2.arival as return_arrival, p2.duration as return_duration,p2.departdetails as return_departdetails,p2.arivedetails as return_arrivaldetails, p2.planedetails as return_planedetails,p2.operatedby as return_operatedby," + totalfare + " as total_miles,  "+totaltax+" as total_taxes from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ='" + str(keys['returnkey']) + "' and " + returnfare + " > '0'  where  p1.searchkeyid = '" + keys['departkey'] + "' and " + departfare + " > 0 and " + querylist + " order by total_miles ,total_taxes, p1.departure, p2.departure ASC")

            flights = []
            for item in _flights:
                _item = {}
                _item['origin'] = item.origin
                _item['stoppage'] = item.stoppage
                _item['flight_no'] = item.flighno
                _item['destination'] = item.destination
                _item['departure'] = str(item.departure)
                _item['arrival'] = str(item.arival)
                _item['duration'] = item.duration
                _item['image'] = 'pexportal.com/static/flightsearch/img/'+logos[item.datasource]
                _item['depart_routes'] = parse_detail(item.departdetails, item.arivedetails, item.planedetails, item.operatedby)
                if not _item['depart_routes']:
                    continue

                _item['return_origin'] = item.return_origin
                _item['return_stoppage'] = item.return_stoppage
                _item['return_flight_no'] = item.return_fligh_no
                _item['return_destination'] = item.return_destination
                _item['return_departure'] = str(item.return_departure)
                _item['return_arrival'] = str(item.return_arrival)
                _item['return_duration'] = item.return_duration
                _item['return_routes'] = parse_detail(item.return_departdetails, item.return_arrivaldetails, item.return_planedetails, item.return_operatedby)
                if not _item['return_routes']:
                    continue

                _item['datasource'] = item.datasource
                _item['total_miles'] = item.total_miles
                _item['total_taxes'] = item.total_taxes

                price_key_d = get_qpx_price_key(item.planedetails).encode('ascii', 'ignore')
                price_key_r = get_qpx_price_key(item.return_planedetails).encode('ascii', 'ignore')
                _item['price'] = qpx_prices.get(price_key_d+price_key_r, 'N/A')

                # get delta price
                if _item['price'] == 'N/A':
                    delta_price = delta_departure_price.get(price_key_d)
                    if delta_price:
                        print price_key_d, price_key_r, fare_class, '#####'

                        price_d = delta_price.get(fare_class)
                        if price_d:
                            delta_price = delta_return_price.get(price_key_r)
                            if delta_price:
                                price_r = delta_price.get(fare_class)
                                if price_r:
                                    _item['price'] = price_d[:3] + str(float(price_d[3:])+float(price_r[3:]))

                # compute percentage of match
                if _item['price'] == 'N/A':
                    qpx_unmatch_count += 1

                flights.append(_item)

        # save unmatch percent
        if flights:
            searchkey = Searchkey.objects.get(searchid=keys['departkey'])
            searchkey.qpx_unmatch_percent = qpx_unmatch_count * 1.0 / len(flights)
            searchkey.save()

        result['status'] = 'Success'
        result['flights'] = flights
        return JsonResponse(result, safe=False)

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
        amenities = HotelAmenity.objects.filter(hotel=hotel)
        amenities = [item.amenity for item in amenities]
    else:
        amenities = request.POST.getlist('amenity')
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

            # update hotel amenities
            HotelAmenity.objects.filter(hotel=hotel).delete()
            for item in amenities:
                HotelAmenity.objects.create(hotel=hotel, amenity=item)

            return HttpResponseRedirect('/Admin/hotel/')

    return render(request, 'Admin/hotel_form.html', {
        'form':form,
        'amenities':HOTEL_AMENITIES,
        'old_amenities':amenities
    })


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
def customer_list(request):
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
            customer.search_limit = form.cleaned_data['search_limit']
            customer.search_run = form.cleaned_data['search_run']            
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
            blog_list.blog_url = blog_list.blog_title.lower().replace(' ', '-').replace('+', '').replace('(', '').replace(')', '')
            blog_list.blog_position = form.cleaned_data['blog_position']
            blog_list.blog_content = form.cleaned_data['blog_content']
            blog_list.blog_meta_key = form.cleaned_data['blog_meta_key']
            blog_list.blog_meta_Description = form.cleaned_data['blog_meta_Description']
            blog_list.blog_creator = form.cleaned_data['blog_creator']
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
            token.test_token = form.cleaned_data['test_token']
            token.test_qpx_token = form.cleaned_data['test_qpx_token']
            token.owner = form.cleaned_data['owner']
            token.limit_flight_search = form.cleaned_data['limit_flight_search']
            token.limit_qpx = form.cleaned_data['limit_qpx']
            token.limit_hotel_search = form.cleaned_data['limit_hotel_search']
            token.run_hotel_search = form.cleaned_data['run_hotel_search']
            token.run_flight_search = form.cleaned_data['run_flight_search']
            token.allowed_domain = form.cleaned_data['allowed_domain']
            token.notes = form.cleaned_data['notes']
            token.number_update = token.number_update + 1 
            token.created_at = dttime.now().date()
            token.save()
            return HttpResponseRedirect('/Admin/token/')

    return render(request, 'Admin/token_form.html', {'form':form, 'pre_owners':pre_owners})


def token_delete(request, id):
    if request.is_ajax():        
        Token.objects.get(id=id).delete()
        return HttpResponse('success')


@login_required(login_url='/Admin/login/')
def searchlimit(request):
    searchlimits = SearchLimit.objects.all()
    return render(request, 'Admin/searchlimit.html', {'searchlimits': searchlimits})


@login_required(login_url='/Admin/login/')
def searchlimit_update(request, id=None):
    searchlimit = SearchLimit.objects.get(id=id)

    if request.method == 'GET':
        form = SearchLimitForm(initial=model_to_dict(searchlimit))
    else:
        form = SearchLimitForm(request.POST, instance=searchlimit)
        if form.is_valid():
            searchlimit.user_class = form.cleaned_data['user_class']
            searchlimit.limit = form.cleaned_data['limit']
            searchlimit.save()
            return HttpResponseRedirect('/Admin/searchlimit/')

    return render(request, 'Admin/searchlimit_form.html', {'form':form})


def admin_login(request):
    if request.method == 'GET':
        return render(request, 'Admin/login.html', {})    
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff and user.level == 3:
                social_login(request, user)

    return HttpResponseRedirect('/Admin/')


@login_required(login_url='/Admin/login/')
def admin_logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/Admin/')


@login_required(login_url='/Admin/login/')
def Admin(request):
    air_lines = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']    
    stat_num_search = _airline_info(request.user, 3650, 'maincabin', 'all airports', 'all airports')

    pop_searches = _popular_search(3650)
    stat_price_history = _price_history(request.user, '2016-04-05', '2026-04-05', 'aeroflot', 'New York (JFK)', 'Moscow (MOW)', 'Avg') 
    user_search_history = get_search_history()
    search_on_country = get_search_country()

    return render(request, 'Admin/dashboard.html', {
        'stat_num_search': stat_num_search,
        'pop_searches': pop_searches,
        'air_lines': air_lines,
        'num_users': len(list(User.objects.all())),
        'total_searches': len(list(Searchkey.objects.all())) * 3,
        'user_search_history':user_search_history,
        'search_on_country':search_on_country,
        'stat_price_history': stat_price_history,
        'stat_price_history_period': [[], []],
    })


def get_search_history():
    result = []
    for user in User.objects.all().order_by('username'):
        searches = Searchkey.objects.filter(user_ids__contains=','+str(user.user_id)+',').order_by('-scrapetime')
        if not searches:
            continue
        searches = [(search.source+' -> '+search.destination, search.scrapetime.strftime('%Y-%m-%d %H:%M:%S')) for search in searches]
        result.append([user.username, searches])

    # for Non-Members
    searches = Searchkey.objects.exclude(user_ids__regex=r'[0-9]+').order_by('-scrapetime')[:100]        
    searches = [(search.source+' -> '+search.destination, search.scrapetime.strftime('%Y-%m-%d %H:%M:%S')) for search in searches]
    result.append(['Non-Member', searches])

    return result


def get_search_country():
    searches = Searchkey.objects.filter(user_ids__regex=r'[0-9]+')
    user_dict = {}
    for search in searches:
        user_ids = search.user_ids.split(',')
        for user_id in user_ids:
            if user_id:
                if user_id in user_dict:
                    user_dict[user_id] = user_dict[user_id] + 1
                else:
                    user_dict[user_id] = 1

    country_dict = {}
    for key, val in user_dict.items():
        country = User.objects.get(user_id=key).country or 'Unknown'

        country = country.strip()
        country = 'USA' if country == 'United States' else country

        if country in country_dict:
            country_dict[country] += val
        else:
            country_dict[country] = val

    return country_dict


@csrf_exempt
def airline_info(request):
    period = int(request.POST.get('period'))
    fare_class = request.POST.get('fare_class')
    _from = request.POST.get('_from')
    _to = request.POST.get('_to')
    stat_num_search = _airline_info(request.user, period, fare_class, _from, _to)
    return HttpResponse(json.dumps(stat_num_search))


def _airline_info(user, period, fare_class, _from, _to):
    stat_num_search = []

    try:
        air_lines = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
        start_time = datetime.datetime.now() - timedelta(days=period)

        searches = Searchkey.objects.filter(scrapetime__gte=start_time)
        if user.level != 3:
            searches = searches.filter(user_ids__contains=','+str(user.user_id)+',')

        if _from.lower() == 'all airports':
            if _to.lower() != 'all airports':
                searches = searches.filter(destination=_to)
        elif _to.lower() == 'all airports':
            searches = searches.filter(source=_from)

        searches = [item.searchid for item in searches]
        for air_line in air_lines:
            kwargs = {
                '{0}__gt'.format(fare_class):0,
                'datasource': air_line,
                'searchkeyid__in': searches,
            }
            stat_num_search.append(Flightdata.objects.filter(**kwargs).count())
    except Exception, e:
        print str(e)

    return stat_num_search


@csrf_exempt
def popular_search(request):    
    period = int(request.POST.get('period'))    
    pop_searches = _popular_search(period)
    return HttpResponse(json.dumps(pop_searches))
        

def _popular_search(period):        
    start_time = datetime.datetime.now() - timedelta(days=period)
    pop_searches = Searchkey.objects.filter(scrapetime__gte=start_time).values('source', 'destination').annotate(dcount=Count('*')).order_by('-dcount')[:10]
    return [{'source':item['source'], 'destination':item['destination'], 'dcount':item['dcount']} for item in pop_searches]


@csrf_exempt
def price_history(request):    
    _from = request.POST.get('_from')
    _to = request.POST.get('_to') 
    airline = request.POST.get('airline')
    r_from = request.POST.get('r_from')
    r_to = request.POST.get('r_to') 
    aggregation = request.POST.get('aggregation')

    result = _price_history(request.user, _from, _to, airline, r_from, r_to, aggregation)
    return HttpResponse(json.dumps(result))


@csrf_exempt
def _price_history(user, _from, _to, airline, r_from, r_to, aggregation):    
    searchkeys = Searchkey.objects.filter(traveldate__range=(_from, _to), source=r_from, destination=r_to).values('traveldate').annotate(Min('searchid'), Min('scrapetime')).order_by('traveldate')
    if user.level != 3:
        searchkeys = searchkeys.filter(user_ids__contains=','+str(user.user_id)+',')

    result = {'economy': [], 'business': [], 'firstclass':[]}
    result_tax = {'economy': [], 'business': [], 'firstclass':[]}

    for searchkey in searchkeys:
        label = time.mktime(searchkey['traveldate'].timetuple()) * 1000
        flights = Flightdata.objects.filter(searchkeyid=searchkey['searchid__min'], datasource=airline)
        reducer = getattr(aggregator, aggregation)
        for key, val in FLIGHT_CLASS.items():
            field = val[0]
            res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
            if res[field]:
                result[key].append([float(label), float(res[field])])
            field = val[1]
            res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
            if res[field]:
                result_tax[key].append([float(label), float(res[field])])

    result = [{'label':'Economy', 'data':result['economy']}, {'label':'Business', 'data':result['business']}, {'label':'First', 'data':result['firstclass']}]
    result_tax = [{'label':'Economy', 'data':result_tax['economy']}, {'label':'Business', 'data':result_tax['business']}, {'label':'First', 'data':result_tax['firstclass']}]
    return [result,result_tax]


@csrf_exempt
def price_history_period(request):    
    _from = request.POST.get('_from')
    _to = request.POST.get('_to') 
    airline = request.POST.get('airline')
    r_from = request.POST.get('r_from')
    r_to = request.POST.get('r_to') 
    aggregation = request.POST.get('aggregation')
    period = int(request.POST.get('period'))

    # print _from, _to, airline, r_from, r_to, period, aggregation, '@@@@@@@'
    result = _price_history_period(request.user, _from, _to, airline, r_from, r_to, aggregation, period)
    return HttpResponse(json.dumps(result))


def _price_history_period(user, _from, _to, airline, r_from, r_to, aggregation, period):    
    searchkeys = Searchkey.objects.filter(traveldate=_from, source=r_from, destination=r_to).order_by('scrapetime')
    if user.level != 3:
        searchkeys = searchkeys.filter(user_ids__contains=','+str(user.user_id)+',')

    if _to:
        searchkeys = searchkeys.filter(returndate=_to).order_by('scrapetime')

    r_searchkeys = []

    # check the time before travel
    for item in searchkeys:
        if (item.scrapetime + timedelta(days=period)).date() >= item.traveldate:
            r_searchkeys.append(item)

    result = {'economy': [], 'business': [], 'firstclass':[]}
    result_tax = {'economy': [], 'business': [], 'firstclass':[]}

    traveldate = None
    for searchkey in r_searchkeys:
        label = time.mktime(searchkey.scrapetime.timetuple()) * 1000
        flights = Flightdata.objects.filter(searchkeyid=searchkey.searchid, datasource=airline).exclude(origin='flag')
        reducer = getattr(aggregator, aggregation)

        for key, val in FLIGHT_CLASS.items():
            field = val[0]
            res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
            if res[field]:
                result[key].append([float(label), float(res[field])])
            field = val[1]
            res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
            if res[field]:
                result_tax[key].append([float(label), float(res[field])])

    result = [{'label':'Economy', 'data':result['economy']}, {'label':'Business', 'data':result['business']}, {'label':'First', 'data':result['firstclass']}]
    result_tax = [{'label':'Economy', 'data':result_tax['economy']}, {'label':'Business', 'data':result_tax['business']}, {'label':'First', 'data':result_tax['firstclass']}]
    return [result,result_tax]


@csrf_exempt
def price_history_num(request):    
    _from = request.POST.get('_from')
    _to = request.POST.get('_to') 
    airline = request.POST.get('airline')
    r_from = request.POST.get('r_from')
    r_to = request.POST.get('r_to') 
    aggregation = request.POST.get('aggregation')

    result = _price_history_num(request.user, _from, _to, airline, r_from, r_to, aggregation)
    return HttpResponse(json.dumps(result))


def _price_history_num(user, _from, _to, airline, r_from, r_to, aggregation):    
    result = {'economy': [], 'business': [], 'firstclass':[]}
    result_tax = {'economy': [], 'business': [], 'firstclass':[]}
    ticks = []

    try:
        searchkeys = Searchkey.objects.filter(traveldate=_from, source=r_from, destination=r_to).order_by('scrapetime')
        if user.level != 3:
            searchkeys = searchkeys.filter(user_ids__contains=','+str(user.user_id)+',')

        if _to:
            searchkeys = searchkeys.filter(returndate=_to).order_by('scrapetime')

        r_searchkeys = []

        # check the time before travel
        for item in searchkeys:
            if item.scrapetime.date() == dttime.now().date():
                r_searchkeys.append(item)

        if len(r_searchkeys) > 1:
            idx = 0
            for searchkey in r_searchkeys:
                flights = Flightdata.objects.filter(searchkeyid=searchkey.searchid, datasource=airline).exclude(origin='flag')
                reducer = getattr(aggregator, aggregation)
                if not flights:
                    continue
                idx = idx + 1
                ticks.append([idx, idx])
                for key, val in FLIGHT_CLASS.items():
                    field = val[0]
                    res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
                    if res[field]:
                        result[key].append([idx, float(res[field])])
                    field = val[1]
                    res = flights.filter(**{'{0}__gt'.format(field):0}).aggregate(**{field:reducer(field)})
                    if res[field]:
                        result_tax[key].append([idx, float(res[field])])

            result = [{'label':'Economy', 'data':result['economy']}, {'label':'Business', 'data':result['business']}, {'label':'First', 'data':result['firstclass']}]
            result_tax = [{'label':'Economy', 'data':result_tax['economy']}, {'label':'Business', 'data':result_tax['business']}, {'label':'First', 'data':result_tax['firstclass']}]
    except Exception, e:
        print str(e), 'Error: ###############3'

    return [result, result_tax, ticks]


@csrf_exempt
def signup_activity(request):
    result = []
    try:
        _from = request.POST.get('_from')
        _to = request.POST.get('_to') 
        users = User.objects.filter(date_joined__range=(_from, _to)).order_by('-date_joined')
        result = [[user.username, user.date_joined.strftime('%Y-%m-%d %H:%M:%S')] for user in users]
    except Exception, e:
        print str(e), '######'
    return HttpResponse(json.dumps(result))


@login_required(login_url='/customer/login/')
def customer(request):    
    air_lines = ['aeroflot', 'airchina', 'american airlines', 'delta', 'etihad', 'jetblue', 's7', 'united', 'Virgin America', 'Virgin Australia', 'virgin_atlantic']
    stat_num_search = _airline_info(request.user, 3650, 'maincabin', 'all airports', 'all airports')
    stat_price_history = _price_history(request.user, '2016-04-05', '2026-04-05', 'aeroflot', 'New York (JFK)', 'Moscow (MOW)', 'Avg') 
    user_search_history = get_customer_search_history(user_id=request.user.user_id)

    return render(request, 'customer/dashboard.html', {
        'stat_num_search': stat_num_search,
        'air_lines': air_lines,
        'stat_price_history': stat_price_history,
        'user_search_history':user_search_history,
    })


@login_required(login_url='/customer/login/')
def customer_logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/customer/')


def customer_login(request):
    if request.method == 'GET':
        return render(request, 'customer/login.html', {})    
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active and user.level == 1:
                social_login(request, user)

    return HttpResponseRedirect('/customer/')


def get_customer_search_history(user_id, period=3650, r_from=None, r_to=None, category=None):
    start_time = datetime.datetime.now() - timedelta(days=period)
    searches = Searchkey.objects.filter(user_ids__contains=','+str(user_id)+',',scrapetime__gte=start_time).order_by('-scrapetime')

    if r_from:
        searches = searches.filter(source=r_from)
    if r_to:
        searches = searches.filter(destination=r_to)
    if category == 'rt':
        searches = searches.exclude(returndate=None)

    result = []
    for item in searches:
        search = {'source':item.source, 'destination':item.destination}
        search['scrapetime'] = item.scrapetime.strftime('%Y-%m-%d %H:%M:%S')
        search['traveldate'] = str(item.traveldate)
        search['returndate'] = ''
        if item.returndate:
            search['returndate'] = str(item.returndate)
        search['num_result'] = Flightdata.objects.filter(searchkeyid=item.searchid).exclude(origin='flag').count()
        result.append(search)

    return result


@csrf_exempt
def user_search(request):
    r_from = request.POST.get('r_from')
    r_to = request.POST.get('r_to') 
    category = request.POST.get('category')
    period = int(request.POST.get('period'))
    
    result = get_customer_search_history(user_id=request.user.user_id, period=period, r_from=r_from, r_to=r_to, category=category)
    return HttpResponse(json.dumps(result))


def get_qpx_prices(return_date, origin, destination, depart_date, developerKey, carriers, max_stop):    
    developerKey = developerKey or settings.QPX_KEY

    date = datetime.datetime.strptime(depart_date, '%m/%d/%Y')
    date = date.strftime('%Y-%m-%d')

    slice_item = {
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                }
    if carriers:
        slice_item["permittedCarrier"] = list(carriers)
        slice_item["maxStops"] = max_stop

    slice_ = [slice_item]

    if return_date:
        date = datetime.datetime.strptime(return_date, '%m/%d/%Y')
        date = date.strftime('%Y-%m-%d')
        slice_item_r = {
                        "origin": destination,
                        "destination": origin,
                        "date": date,
                    }
        if carriers:
            slice_item_r["permittedCarrier"] = list(carriers)
            slice_item_r["maxStops"] = max_stop

        slice_.append(slice_item_r)

    service = build('qpxExpress', 'v1', developerKey=developerKey)

    body = {
      "request": {
        "passengers": {
          "adultCount": 1,
          "infantInLapCount": 0,
          "infantInSeatCount": 0,
          "childCount": 0,
          "seniorCount": 0
        },
        "solutions": 500,
        "refundable": False
      }
    }
    body['request']['slice'] = slice_

    qpx_prices = {}

    try:
        response = service.trips().search(body=body).execute()

        for flight in response['trips']['tripOption']:
            saleTotal = flight['saleTotal']
            route = ''
            for slice_ in flight['slice']:
                for segment in slice_['segment']:
                    carrier = segment['flight']['carrier']
                    number = segment['flight']['number']
                    route = route + carrier + number + '@'
                route = route + '--'
            qpx_prices[route] = saleTotal
    except Exception, e:
        qpx_prices['error'] = 'Daily limit is reached!'

    return qpx_prices


def get_qpx_price_key(planedetails):
    """
    get key string for qpx_prices
    e.g) EY 487 | 789 (11h 30m)@EY 19 | 388 (8h 5m)
    """
    flights = planedetails.split('@')
    key_ = ''

    for flight in flights:
        carrier = flight.split('|')[0].replace(' ', '')
        key_ = key_ + carrier+ '@'
    return key_ + '--'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_limit_warning_email(user, service, usage=75):
    emailbody = 'You\'ve used {}% of your PEX Points for <b>{}</b> searches.<br> To avoid any disruptions to your flight search experience, please contact the administrator to purchase more PEX Points.<br><br><br>The PEX+ Team'.format(usage, service)
    try:
        resp = customfunction.sendMail('PEX+', user.email, 'Limit Notification', emailbody,'')
    except:
        print "something wrong"


def parse_detail(depart_details, arrival_details, plane_details, operated_by):
    depart_details = depart_details.split('@')
    arrival_details = arrival_details.split('@')
    plane_details = plane_details.split('@')
    operated_by = operated_by.split('@')

    flights = []
    try:
        for i in range(len(depart_details)):
            dd = depart_details[i].split(' | from ')
            ad = arrival_details[i].split(' | at ')
            pd = plane_details[i].split(' (')
            dd0 = dd[0].split(' ')
            dd1 = dd[1].split(' / ')
            dd11 = dd1[1].split(' (')

            ad0 = ad[0].split(' ')
            ad1 = ad[1].split(' / ')
            ad11 = ad1[1].split(' (')

            flight_ = {
                'departDate': dd0[0],
                'departTime': dd0[1],
                'departAirport': dd1[0],
                'departCity': dd11[0],
                'departAirportCode': dd11[1][:-1],

                'arriveDate': ad0[0],
                'arriveTime': ad0[1],
                'arriveAirport': ad1[0],
                'arriveCity': ad11[0],
                'arriveAirportCode': ad11[1][:-1],

                'flight': pd[0],
                'duration': pd[1][:-1] 
            }

            flights.append(flight_)
        return flights
    except Exception, e:
        print 'Parsing Error'
        print depart_details, arrival_details, plane_details, operated_by


def get_qpx_filter_carriers(orgnid, destid):
    searches = Searchkey.objects.filter(origin_airport_id=orgnid, destination_airport_id=destid).order_by('-scrapetime')
    carriers = [] 
    max_stop = 0
    for search in searches:
        flights = Flightdata.objects.filter(Q(searchkeyid=search.searchid), ~Q(origin='flag'))
        if flights:
            for flight in flights:
                if max_stop < len(flight.planedetails.split('@')):
                    max_stop = len(flight.planedetails.split('@'))
                carriers += [item[:2] for item in flight.planedetails.split('@')]
            return set(carriers), min(2, max_stop-1)
    return None, None


def rewardpoints(request):
    """
    get information from awardwallet
    and render awardwallet page
    """
    if not 'userid' in request.session:
        return HttpResponseRedirect('/index')

    wallet_token = settings.WALLET_TOKEN
    user = User.objects.get(pk=request.session['userid'])
    wallet_id = request.GET.get('userId')

    if wallet_id:
        user.wallet_id = wallet_id
        user.save()
    wallet_id = user.wallet_id

    accounts = []

    if wallet_id:
        url = 'https://business.awardwallet.com/api/export/v1/connectedUser/{}'.format(wallet_id)
        header = { "X-Authentication": wallet_token }
        res = requests.get(url=url, headers=header)
        res_json = res.json()
        cursor = connection.cursor()
        # delete previous reward records
        cursor.execute("delete from reward_points where user_id={}".format(user.user_id))

        for account_ in res_json['accounts']:
            account = {}
            account['airline'] = account_['displayName']
            account['balance'] = account_['balanceRaw']
            account['accountId'] = account_['accountId']
            account['kind'] = account_['kind'][:-1]
            account['expireDate'] = account_.get('expirationDate', '')[:10]
            account['status'] = '' 
            account['next_level'] = '' 
            account['household'] = 0

            if 'properties' in account_:
                for property_ in account_['properties']:
                    if property_['name'] in ['Level', 'Status']:
                        account['status'] = property_['value']
                    elif property_['name'] == 'Household miles':
                        account['household'] = int(property_['value'].replace(',', ''))
                    elif property_['name'] == 'Next Elite Level':
                        account['next_level'] = property_['value']

            accounts.append(account)

            # update database
            display_name = account['airline'].split('(')[0]
            cursor.execute ("INSERT INTO reward_points (user_id, reward_points, airlines, kind, status, account_no, expiration_date, household, next_level) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);", (str(user.user_id),str(account['balance']), display_name, account['kind'], account['status'], account['accountId'], account['expireDate'], str(account['household']), account['next_level'] ))

    hotel, flight = get_reward_config(request)

    return render(request, 'flightsearch/rewardpoints.html', { 
        'accounts': accounts, 
        'wallet_id': wallet_id,
        'hotel': hotel,
        'flight': flight 
    })


def get_reward_config(request):
    """
    get award page configuration
    """
    user = User.objects.get(pk=request.session['userid'])
    config = UserConfig.objects.filter(owner=user)
    if config:
        reward_config = config[0].reward_config.encode('ascii', 'ignore').split('@')
        hotel = reward_config[0].split(';')
        flight = reward_config[1].split(';')
    else:
        hotel = ['Airline', 'Hotel', 'Credit Card']
        flight = ['Airline', 'Hotel', 'Credit Card']
    return hotel, flight


def choose_kind(request):
    """
    filter the programs by kind
    """
    kind = request.GET.get('kind')
    pointlist = get_pointlist(request, kind)
    return render(request, 'flightsearch/rewardpoints_table.html', { 'accounts': pointlist, 'kind':kind })


def modify_config(request):
    """
    modify the configuration for award points display for each page for the user
    """
    userid = request.session['userid']
    hotel_config = request.GET.getlist('hotel')
    flight_config =  request.GET.getlist('flight')
    reward_config = ';'.join(hotel_config)+'@'+';'.join(flight_config)

    config = UserConfig.objects.filter(owner_id=userid)
    if config:
        config = config[0]
        config.reward_config = reward_config
        config.save()
    else:
        config = UserConfig.objects.create(owner_id=userid, reward_config=reward_config)

    return HttpResponse('ok')


def get_history(request):
    """
    get transaction history from awardwallet or db cache with accountID, date range filter
    """
    userid = request.session['userid']
    accountId = request.GET.get('accountId')
    date_from = request.GET.get('from', '01/01/1900')
    date_to = request.GET.get('to', '01/01/2900')

    try:
        date_from = datetime.datetime.strptime(date_from.strip(), '%m/%d/%Y').date()
        date_to = datetime.datetime.strptime(date_to.strip(), '%m/%d/%Y').date()
    except Exception, e:
        date_from = datetime.date(1900, 1,1)
        date_to = datetime.date(2900, 1,1)

    cursor = connection.cursor()
    sql = "select history from reward_points where user_id={} and account_no='{}'".format(userid, accountId)
    cursor.execute(sql)
    history = cursor.fetchone()

    if history[0]:
        history = json.loads(history[0])
    else:
        url = 'https://business.awardwallet.com/api/export/v1/account/{}'.format(accountId)
        header = { "X-Authentication": settings.WALLET_TOKEN }
        res = requests.get(url=url, headers=header)        
        history = res.json()['account']
        if 'history' in history:
            history = history['history']
        else:
            history = []
        cursor.execute ("UPDATE reward_points set history='{}' where user_id={} and account_no='{}';".format(json.dumps(history), userid, accountId))

    r_history = []
    for history_ in history:
        for item in history_['fields']:
            if 'code' in item and item['code'] == 'PostingDate':
                post_date = item['value']
                post_date = datetime.datetime.strptime(post_date.strip(), '%m/%d/%y').date()
                if date_from <= post_date <= date_to:
                    r_history.append(history_)
                break

    # filter by date
    return render(request, 'flightsearch/show_history_dialog.html', { 'history': r_history })    


def get_aircraft_category(request):
    """
    Get a category of aircrafts after flight search is done.
    It is callef from ajax.
    """
    cabinclass = request.POST.get('cabin', '')
    multicitykey = request.POST.get('multicity', '')
    key = request.POST.get('keyid', '')
    returnkeyid = request.POST.get('returnkey', '')
    aircraft = request.POST.get('aircraft', '[]')[1:-1]
    aircraft = aircraft.replace('&quot;', '').split(', ')

    if multicitykey:
        print multicitykey, '%%%%%%%%%%%%%'
    else:
        # if returnkeyid:
        #     pass
        # else:
        fd = Flightdata.objects.filter(~Q(origin='flag'), Q(searchkeyid=int(key)))
        aircrafts = get_aircraft_info(fd)
        cate_aircrafts = get_category_aircrafts(aircrafts)
        return render(request, 'flightsearch/aircraft_category.html', {'aircraft_category': cate_aircrafts, 'aircraft': aircraft})

    return HttpResponse('')


def get_aircraft_info(flights):
    """
    Get a set of aircraft information (aircraft, plane type)
    It returns a set of aircraft info.
    """
    ac = set([])
    for fd_item in flights:
        ac = ac | get_aircraft_info_(fd_item)
    return ac


def get_aircraft_info_(flight):
    """
    Get a set of aircraft information (aircraft, plane type) for a flight
    It returns a set of aircraft info.
    """
    ac = []
    for fdd in flight.planedetails.split('@'):
        fda = re.search(r'^.*\| (.*?) \(.*$', fdd)
        if fda:
            ac.append(fda.group(1).strip())
    return set(ac)


def get_category_aircrafts(aircrafts):
    """
    Get the category of aircrafts from aircrafts info
    It returns a dictionary of aircraft: plane types
    """
    specialties = ['McDonnell Douglas ']

    cate_aircrafts = {}
    for aircraft in aircrafts:
        ai = aircraft.find(' ')
        if ai < 0: # just in case
            continue
        key = aircraft[:ai]
        val = aircraft[ai+1:]

        for item in specialties:
            if aircraft.startswith(item):
                key = item
                val = aircraft[len(item):]

        if key in cate_aircrafts:
            cate_aircrafts[key].add(val)
        else:
            cate_aircrafts[key] = set([val])

    for key, val in cate_aircrafts.items():
        cate_aircrafts[key] = sorted(val)

    return collections.OrderedDict(sorted(cate_aircrafts.items()))
