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
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.views.decorators.csrf import requires_csrf_token
from pexproject.models import Flightdata, Airports, Searchkey, User,Pages, Contactus,Adminuser,EmailTemplate,GoogleAd
from pexproject.models import Blogs,BlogImages
from pexproject.templatetags.customfilter import floatadd, assign
from social_auth.models import UserSocialAuth
from django.contrib.auth import login as social_login,authenticate,get_user
from django.contrib.auth import logout as auth_logout
import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from random import randint
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
import time
import MySQLdb
import threading
from multiprocessing import Process
import threading
from threading import Thread
from datetime import date
from django.db import connection, transaction
import operator
import customfunction,rewardScraper
import smtplib
from email.mime.text import MIMEText
import socket
from email.mime.multipart import MIMEMultipart
import base64
#from djnago.conf import settings
import subprocess
import json
import signal
import logging
from mailchimp import Mailchimp
logger = logging.getLogger(__name__)


def Admin(request):
    context = {}
    return  render_to_response('flightsearch/admin/index.html', context_instance=RequestContext(request))

def adminlogin(request):
    context = {}
    if request.POST:
        username = request.REQUEST['admin_user']
        password = request.REQUEST['admin_password']
        
        try:
        
            adminuser = Adminuser.objects.get(username=username, password=password)
            
            request.session['admin'] = username
            request.session['admin_name'] = adminuser.name
            return HttpResponseRedirect('dashboard')
            
        except:
            currentpage = "/Admin?message=invalid"
            return HttpResponseRedirect(currentpage)
    else:
        return render_to_response('flightsearch/admin/admin_dashboard.html', context_instance=RequestContext(request))
        
def adminlogout(request):
    context = {}
    if 'admin' in request.session:
        del request.session['admin']  
    return HttpResponseRedirect(reverse('Admin'))

def pages(request):
    pagelist = Pages.objects.filter()
    return render_to_response('flightsearch/admin/pages.html',{'pagelist':pagelist}, context_instance=RequestContext(request))
def manage_page(request):
    if 'pageid' in request.GET:
        page = Pages.objects.get(pk=request.GET.get('pageid',''))
    if request.POST and 'pageid' in request.REQUEST:
        page = Pages()
        #page = Pages.objects.get(pk=request.REQUEST['pageid'])
        page.pageid = request.REQUEST['pageid']
        page.page_name = request.REQUEST['pagename']
        page.page_path = request.REQUEST['pagename']
        page.top_content = request.REQUEST['top_content']
        page.page_text = request.REQUEST['page_content']
        page.placeholder = request.REQUEST['palceholder']
        page.save()
        return HttpResponseRedirect(reverse('pages'))
    return render_to_response('flightsearch/admin/manage_pages.html',{'page':page}, context_instance=RequestContext(request))
def dashboard(request):
    context = {}  
    return  render_to_response('flightsearch/admin/admin_dashboard.html', context_instance=RequestContext(request))
def emailTemplate(request):
    context = {}
    if 'admin' in request.session:
        emailtemplate = EmailTemplate.objects.filter()
        return  render_to_response('flightsearch/admin/email_template.html',{'emaillist':emailtemplate}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('/Admin'))

def adimage(request):
    context = {}
    image_list = GoogleAd.objects.filter()
    return  render_to_response('flightsearch/admin/ad_image.html',{'imagelist':image_list}, context_instance=RequestContext(request))

def manage_adimage(request):
    context = {}
    image_list = GoogleAd.objects.filter()
    image_path_list=[]
    if request.is_ajax():
        i= 0
        for file in request.FILES.getlist('image[]'):
            t = time.time()
            if '.' in str(t):
                t = str(t).replace('.','')
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            img = str(t)+str(file)
            img_fol = '/static/flightsearch/uploads/'
            path = directory+img_fol+img
            print path
            dest = open(path, 'wb+')
            if file.multiple_chunks:
                for c in file.chunks():
                    dest.write(c)
                    dbpath = img
                    image_path_list.append(dbpath)
            #obj = GoogleAd()
            #obj.image_path = img_fol+img
            #obj.save()
            dest.close()
        mimetype = 'application/json'
        data = json.dumps(image_path_list)
        return HttpResponse(data, mimetype)
    if request.POST and not request.is_ajax():
        image_path = request.REQUEST['img_path']
        img_path_arr = image_path.split('|')
        for i in range(0,len(img_path_arr)):
            obj = GoogleAd()
            obj.image_path = img_path_arr[i]
            if 'imageid' in request.REQUEST:
               obj.ad_id =  request.REQUEST['imageid']
            obj.google_code = request.REQUEST['google_code']
            obj.ad_code = request.REQUEST['ad_code']
            obj.save()
        return HttpResponseRedirect(reverse('adimage'))
    if 'action' in request.GET:
        action = request.GET.get('action','')
        if action == 'add' or action == 'edit':
            imageobj=''
            if 'imageid' in request.GET:
                imageobj = GoogleAd.objects.get(pk=request.GET.get('imageid',''))
            return render_to_response('flightsearch/admin/manage_image.html',{'imageobj':imageobj}, context_instance=RequestContext(request))
        else:
            if action == 'delete' and 'imageid' in request.GET:
                GoogleAd.objects.get(pk=request.GET.get('imageid','')).delete()
                return HttpResponseRedirect(reverse('adimage'))
    return  render_to_response('flightsearch/admin/ad_image.html',{'imagelist':image_list}, context_instance=RequestContext(request))

def bloglist(request):
    context = {}
    if 'admin' in request.session:
    	bloglist=''
    	bloglist = Blogs.objects.filter()
    	return render_to_response('flightsearch/admin/bloglist.html',{'bloglist':bloglist}, context_instance=RequestContext(request))
    else:
	return HttpResponseRedirect(reverse('Admin'))

@csrf_exempt
def manageblogImage(request):
    if 'userid' in request.POST:
	print request.REQUEST['userid']
    for file in request.FILES.getlist('upload'):        
        t = time.time()
        if '.' in str(t):
            t = str(t).replace('.','')
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        img = str(t)+str(file)
        img_fol = '/static/flightsearch/uploads/'
        path = directory+img_fol+img
        print path
        dest = open(path, 'wb+')
  	CKEditorFuncNum =''
	print "post",request.GET
	if 'CKEditorFuncNum' in request.GET: 
            CKEditorFuncNum = request.REQUEST['CKEditorFuncNum'];
	
                           
        if file.multiple_chunks:
            dbpath = ''
            for c in file.chunks():
                dest.write(c)
                dbpath = img
                image = BlogImages()
                image.user_id = "1"
		image.image_path = dbpath
		imgpath1 = img_fol+dbpath
		image.save()
	    message = '' ;
          
            #: 'var cke_ob = window.parent.CKEDITOR; for(var ckid in cke_ob.instances) { if(cke_ob.instances[ckid].focusManager.hasFocus) break;} cke_ob.instances[ckid].insertHtml(\'<audio src="'+ $url .'" controls></audio>\', \'unfiltered_html\'); alert("'. $msg .'"); var dialog = cke_ob.dialog.getCurrent();  dialog.hide();';
	    return render_to_response('flightsearch/admin/ajaxresponse.html',{"CKEditorFuncNum":CKEditorFuncNum,"message":message,"imgpath":imgpath1})
	    
            #mimetype = 'application/html'
    
            #return HttpResponse( '<script>'+re +';</script>', mimetype)

    
    
def manageBlog(request):
    context = {}
    if request.POST:
        currentdatetime = datetime.datetime.now()
    	curr_time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
        url_date = currentdatetime.strftime('%m-%Y')
        blog = Blogs()
	
    	if 'blogid' in request.POST:
    	    blog.blog_id = request.POST['blogid']
    	blog.blog_url = request.POST['blog_url']
    	blog.blog_title = request.POST['blog_title']
    	blog.blog_content = request.POST['blog_content']
    	blog.blog_meta_key = request.POST['metakey']
    	blog.blog_meta_Description = request.POST['meta_description']
    	if 'img_path' in request.POST:
    	    blog.blog_image_path = request.REQUEST['img_path']
    	blog.blog_created_time = str(curr_time)
    	if 'admin' in request.session:
    	    blog.blog_creator = request.session['admin_name']
    	if 'status' in request.POST:
    	    blog.blog_status = request.POST['status']
    	if 'position' in request.POST:
    	    blog.blog_position = request.POST['position']
    	    Blogs.objects.filter(blog_created_time__lte = str(curr_time)).update(blog_position=False)
        try:
            blog.save()
    	    page = ''
    	    if "blogid" in request.POST:
                	page = '/Admin/bloglist?msg=Blog Edited Successfully'
    	    else:
    	   	page = '/Admin/bloglist?msg=Blog Added Successfully'
                return HttpResponseRedirect(page)
        except:
            page = '/Admin/bloglist?msg=There is some technical problem'
            return HttpResponseRedirect(page)
    blog = ''
    if 'blogid' in request.GET:       
    	blogid = request.GET.get('blogid','')
    	blog = Blogs.objects.get(pk=blogid)
	if 'action' in request.GET and request.GET.get('action','') == 'delete':
	    blog.delete()
	    page = '/Admin/bloglist?msg=Blog Deleted Successfully'
	    return HttpResponseRedirect(page)
    return  render_to_response('flightsearch/admin/manageblog.html',{'blog':blog}, context_instance=RequestContext(request))



def manageEmailTemplate(request):
    context = {}
    if request.POST:
        subject = request.REQUEST['subject']
        body = request.REQUEST['body']
        placeholder = request.REQUEST['palceholder']
        email = EmailTemplate()
        email.subject = subject
        email.body = body
        email.email_code = request.REQUEST['emailcode']
        email.template_id = request.REQUEST['templateid']
        email.placeholder = placeholder
        try:
            email.save()
            page = '/Admin/emailTemplate?msg=Record Edited Successfully'
            return HttpResponseRedirect(page)
        except:
            page = '/Admin/dashboard?msg=There is some technical problem'
            return HttpResponseRedirect(page)        
    templateid = request.GET.get('templateid','')
    templateobj = EmailTemplate.objects.get(pk=templateid)
    return  render_to_response('flightsearch/admin/manage_email_template.html',{'templateobj':templateobj}, context_instance=RequestContext(request))

def index(request):
    context = {}
    user = User()
    image = ''
    image = GoogleAd.objects.filter(ad_code="index")

    ''' Fetch recent results'''
    searches = []
    recent_searches = Flightdata.objects.raw("select p1.*,p2.searchid,p2.destination as final_dest, (min(if(p1.maincabin > 0,p1.maincabin,NULL))) as maincabin from pexproject_flightdata p1 inner join pexproject_searchkey p2 on p2.searchid = p1.searchkeyid where p1.origin != 'flag' group by final_dest order by p2.searchid desc limit 10 ")
    for s in recent_searches:
    	dest = s.final_dest.split('(')
    	searches.append({'final_dest':dest[0],'maintax':s.maintax,'searchkeyid':s.searchkeyid,'maincabin':s.maincabin})  
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
        if user1.firstname:
            request.session['firstname'] =user1.firstname
            fname = user1.firstname
        if user1.lastname:
            lname = user1.lastname
    	request.session['password'] = user1.password        
	if 'pexdeal' in request.session:
	    #print "in pex deal"
	    subscriber = Mailchimp(customfunction.mailchimp_api_key)
            subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':username}, merge_vars={'FNAME':fname,'LNAME':lname})
       	   
    return  render_to_response('flightsearch/index.html',{'image':image,'searchObj':searches}, context_instance=RequestContext(request))

def flights(request):
    context = {}
    mc = ''
    objects = ''
    searches = []
    recent_searches = Flightdata.objects.raw("select p1.*,p2.searchid,p2.destination as final_dest, (min(if(p1.maincabin > 0,p1.maincabin,NULL))) as maincabin from pexproject_flightdata p1 inner join pexproject_searchkey p2 on p2.searchid = p1.searchkeyid where p1.origin != 'flag' group by p1.datasource order by p2.searchid desc limit 10 ")
    for s in recent_searches:
	dest = s.final_dest.split('(')
	searches.append({'final_dest':dest[0],'maintax':s.maintax,'searchkeyid':s.searchkeyid,'maincabin':s.maincabin})  
    if 'action' in request.GET:
        mc = request.GET.get('action','')
    if 'multicitykeys' in request.GET:
        keys = request.GET.get('multicitykeys','')
        allkeys =  keys.split(',')
        objects = Searchkey.objects.filter(searchid__in=allkeys)
        mc = 'mc'  
    return  render_to_response('flightsearch/flights.html',{'mc':mc,'searchparams':objects,'searchObj':searches}, context_instance=RequestContext(request))
        
def staticPage(request):
    context = {}
    page = ''
    if "action" in request.GET:
    	page = request.GET.get('action','')
        return  render_to_response('flightsearch/'+page+'.html', context_instance=RequestContext(request))

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
                return render_to_response('flightsearch/index.html',{'signup_msg':msg},context_instance=RequestContext(request))
            password = request.REQUEST['password']
            password1 = hashlib.md5(password).hexdigest()
            airport = request.REQUEST['home_airport']
            firstname = ''
            lastname = ''
            pexdeals = 0
            if 'firstname' in request.POST:
                firstname = request.REQUEST['firstname']
            if 'lastname' in request.POST:
                lastname = request.REQUEST['lastname']
            if 'pexdeals' in request.REQUEST:
                pexdeals = request.REQUEST['pexdeals']

            object = User(username=email,email=email, password=password1,firstname=firstname,lastname=lastname, home_airport=airport,last_login=time,pexdeals=pexdeals)
            object.save()
            if pexdeals == '1':
                subscriber = Mailchimp(customfunction.mailchimp_api_key)
                subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':email}, merge_vars={'FNAME':firstname,'LNAME':lastname})
            request.session['username'] = email
            request.session['homeairpot'] = airport
            request.session['password'] = password1
            if firstname != '':
                request.session['firstname'] = firstname
            if object.user_id:
                request.session['userid'] = object.user_id
                msg = "Thank you, You have been successfully registered."
                emailbody=''
                obj = EmailTemplate.objects.get(email_code='signup')
                email_sub = obj.subject
                emailbody = obj.body
                emailbody = emailbody.replace('[USER_NAME]',firstname)
                emailbody = emailbody.replace('[SITE-LINK]','<a href="http://pexportal.com/">pexportal</a>')
                
                html_content=''
                try:
                    resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
                except:
                    print "something wrong"
                return render_to_response('flightsearch/index.html',{'welcome_msg':msg}, context_instance=RequestContext(request))   
        return render_to_response('flightsearch/index.html', context_instance=RequestContext(request))
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
            user1.home_airport = request.REQUEST['home_ariport']
            isupdated  = user1.save()
            print isupdated
        if 'home_ariport' not in request.POST:
            user1.firstname = request.REQUEST['firstname']
            user1.middlename = request.REQUEST['middlename']
            user1.lastname = request.REQUEST['lastname']
            user1.gender = request.REQUEST['gender']
            if request.REQUEST['dateofbirth']:
                user1.date_of_birth = request.REQUEST['dateofbirth']
            else:
                user1.date_of_birth = None
            user1.address1 = request.REQUEST['address1']
            user1.address2 = request.REQUEST['address2']
            user1.city = request.REQUEST['city']
            user1.state = request.REQUEST['state']
            user1.zipcode = request.REQUEST['zipcode']
            user1.country = request.REQUEST['country']
            user1.phone = request.REQUEST['phone']
            user1.save()   
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
            user = User.objects.get(username=username, password=password1)
            if user > 0:
                request.session['username'] = username
                request.session['password'] = password1
                if user.firstname != '':
                    request.session['firstname'] = user.firstname
                if user.home_airport != '':
                    request.session['homeairpot'] = user.home_airport
                request.session['userid'] = user.user_id
                if currentpath:
                    return HttpResponseRedirect(currentpath)
                return HttpResponseRedirect(reverse('index'))
            else:
                msg = "Invalid username or password"
                return render_to_response('flightsearch/index.html', {'msg':msg}, context_instance=RequestContext(request))
    	except:
    	    msg = "Invalid username or password"
            return render_to_response('flightsearch/index.html', {'msg':msg}, context_instance=RequestContext(request))
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
        user_email =  request.REQUEST['email']
        randomcode = randint(100000000000,999999999999)
        usercode =  base64.b64encode(str(randomcode))
        if 'userid' in request.session:
            user = User.objects.get(pk = request.session['userid'])
        else:
            try:
                user = User.objects.get(email=user_email)
            except:
                return render_to_response('flightsearch/index.html', {'msg':"Invalid username"}, context_instance=RequestContext(request))
        text = ''
        if user > 0:
            #subject = "Manage Your Password"
            obj = EmailTemplate.objects.get(email_code='forgotPassword')
            email_sub = obj.subject
            emailbody = obj.body
            emailbody = emailbody.replace('[USER_NAME]',user_email)
            emailbody = emailbody.replace('[RESET-LINK]','<a href="http://pexportal.com/createPassword?usercode='+usercode+'">Click here</a>')
            #html_content = '"To manage Your password  <a href="http://pexportal.com/createPassword?usercode='+usercode+'">Click here</a>'
            resp = customfunction.sendMail('PEX',user_email,email_sub,emailbody,text)
            if resp == "sent":
                user.usercode = usercode
                currentdatetime = datetime.datetime.now()
                time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
                user.user_code_time = time
                user.save()
                text = "Please check your registered email id to create new password"
            else:
                text = "There is some technical problem. Please try again"
	if 'pagetype' in request.REQUEST:	
	    return render(request, 'flightsearch/index.html', {'welcome_msg': text})
	    #return render_to_response('flightsearch/index.html',{'welcome_msg':text}, context_instance=RequestContext(request))
        if request.is_ajax():
            mimetype = 'application/json'
            data = text
            json.dumps(data)
            return HttpResponse(data, mimetype)
        
    else:
        msg = "forgot password"
    return render_to_response('flightsearch/index.html',{'fpmsg':msg},context_instance=RequestContext(request)) 
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
    firstname = ''
    lastname = ''
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
        firstname = request.REQUEST['first_name']
        lastname = request.REQUEST['last_name']
        title = request.REQUEST['title']
        company = request.REQUEST['company']
        message = request.REQUEST['message']
        topic = request.REQUEST['topic']
        labeltext = request.REQUEST['label_text']
        labeltext = strip_tags(labeltext)
        phone = request.REQUEST['phone']
        websitename = request.REQUEST['website']
        email = request.REQUEST['email']
        object = Contactus(first_name=firstname,last_name=lastname,email=email,phone=phone,title=title,company=company,website=websitename,message=message,topic=topic,label_text= labeltext)
        object.save()
        fullname = firstname+" "+lastname
        emailbody = message+"\n\n"+labeltext+" \n\n"+fullname+"\n"+company+"\n"+websitename
        
        resp = customfunction.sendMail(email,'info@pexportal.com',topic,emailbody,html_content)
        if resp == "sent":
            contact_msg = "Your information has been sent successfully"
        else:
            contact_msg = "There is some technical problem. Please try again"    
    return render_to_response('flightsearch/contact_us.html',{'contact_msg':contact_msg}, context_instance=RequestContext(request))  
        
def search(request):
    context = {}
    if request.is_ajax():
        context = {}
        cursor = connection.cursor()
        returndate = request.POST['returndate']
        dt1 = ''
        searchdate1 = ''
        multiplekey =''
        seperator = ''
        if returndate:
            dt1 = datetime.datetime.strptime(returndate, '%Y/%m/%d')
            date1 = dt1.strftime('%m/%d/%Y')
            searchdate1 = dt1.strftime('%Y-%m-%d')
        triptype = request.POST['triptype']
        ongnidlist=''
        destlist = ''
        departlist =''
        searchkeyid = ''
        returnkey = ''
        orgnid = request.POST['fromMain']
        destid = request.POST['toMain']
        depart = request.POST['deptdate']
        cabin = request.POST['cabin']
        #print "cabin",cabin
        ongnidlist =  orgnid.split(',')
        destlist = destid.split(',')
        departlist = depart.split(',')
        for i in range(0,len(departlist)):
            etihadorigin =''
            etihaddest = ''
            orgnid = ongnidlist[i]
            destid = destlist[i]
            depart = departlist[i]
            originobj = Airports.objects.filter(airport_id=orgnid)
            destobj = Airports.objects.filter(airport_id=destid)
            for row in originobj:
                orgn = row.cityName + ", " + row.cityCode + ", " + row.countryCode + "  (" + row.code + ")"
                etihadorigin = row.cityName
                orgncode = row.code
                origin = row.cityName + " (" + row.code + ")"
            for row1 in destobj:
                dest = row1.cityName + ", " + row1.cityCode + ", " + row1.countryCode + "  (" + row1.code + ")"
                etihaddest = row1.cityName
                destcode = row1.code
                destination1 = row1.cityName + " (" + row1.code + ")"
            
            dt = datetime.datetime.strptime(depart, '%Y/%m/%d')
            date = dt.strftime('%m/%d/%Y')
            searchdate = dt.strftime('%Y-%m-%d')        
            currentdatetime = datetime.datetime.now()
            time = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
            time1 = datetime.datetime.now() - timedelta(hours=4)
            time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
            
            
            
            Searchkey.objects.filter(scrapetime__lte=time1)#.delete()
            cursor.execute("insert into arcade_flight_data select * from pexproject_flightdata where scrapetime < '"+str(time1)+"'")
            Flightdata.objects.filter(scrapetime__lte=time1)#.delete()
            transaction.commit()
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
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/jetblue.py",destcode, orgncode, str(returndate), str(returnkey)])
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/delta.py",destcode, orgncode, str(date1), str(returndate), str(returnkey),etihaddest,etihadorigin,cabin])
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/united.py",destcode, orgncode, str(returndate), str(returnkey)])
                    subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aa.py",destcode, orgncode, str(returndate), str(returnkey)])
                   
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
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/jetblue.py",orgncode,destcode,str(depart),str(searchkeyid)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/delta.py",orgncode,destcode,str(date),str(depart),str(searchkeyid),etihadorigin,etihaddest,cabin])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/united.py",orgncode,destcode,str(depart),str(searchkeyid)])
                subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/aa.py",orgncode,destcode,str(depart),str(searchkeyid)])
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
                        subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/jetblue.py",destcode, orgncode, str(returndate), str(returnkey)])
                        subprocess.Popen(["python",settings.BASE_DIR+"/pexproject/delta.py",destcode, orgncode, str(date1), str(returndate), str(returnkey),etihaddest,etihadorigin,cabin])
                        subprocess.Popen(["python",settings.BASE_DIR+"/pexproject/united.py",destcode, orgncode, str(returndate), str(returnkey)])
                        subprocess.Popen(["python",settings.BASE_DIR+"/pexproject/aa.py",destcode, orgncode, str(returndate), str(returnkey)])
                        
            Flightdata.objects.filter(searchkeyid=searchkeyid,datasource='virgin_atlantic').delete()
            if returnkey:
                Flightdata.objects.filter(searchkeyid=returnkey,datasource='virgin_atlantic').delete()            

            #customfunction.virgin_atlantic(orgncode,destcode,depart,returndate,searchkeyid,returnkey)
            subprocess.Popen(["python", settings.BASE_DIR+"/pexproject/virgin.py",orgncode,destcode, str(depart), str(returndate), str(searchkeyid),str(returnkey)])
            if len(departlist) > 0 :
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
    context = {}
    data1 = ''
    iscomplete =''
    totalrecords = 0
    if request.is_ajax():
        
        #cabinclass = request.GET.get('cabin', '')
        #passenger = request.GET.get('passenger', '')
        if 'keyid' in request.POST:
            recordkey = request.POST['keyid']
            cabin = request.POST['cabin']
            if 'returnkey' in request.POST:
                returnkey = request.POST['returnkey']
                returnfare = "p2." + cabin
                departfare = "p1." + cabin
                #pricematrix = Flightdata.objects.raw("select p1.rowid,p2.rowid, p2.datasource, (min(if(p1.maincabin > 0,p1.maincabin,NULL))+min(if(p2.maincabin > 0,p2.maincabin,NULL))) as maincabin, (min(if(p1.firstclass>0,p1.firstclass,NULL))+min(if(p2.firstclass>0,p2.firstclass,NULL))) as firstclass ,(min(if(p1.business>0,p1.business,NULL))+min(if(p2.business>0,p2.business,NULL))) as business  from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+returnkey+" where p1.searchkeyid="+str(recordkey)+" group by p1.datasource")
                totalrecords1 = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(returnkey)+" and "+returnfare+" > 0 where p1.searchkeyid="+str(recordkey)+" and "+departfare+" > 0")
                totalrecords = len(list(totalrecords1))                 
                obj = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(returnkey)+" and p2.flighno = 'flag' where p1.searchkeyid="+str(recordkey)+" and p1.flighno = 'flag'")
                obj1 = len(list(obj))
                if obj1 > 3:
                     iscomplete = "completed"  
            else:
                #pricematrix =  Flightdata.objects.raw("select rowid, datasource, min(if(maincabin > 0,maincabin,NULL)) as maincabin, min(if(firstclass>0,firstclass,NULL)) as firstclass ,min(if(business>0,business,NULL)) as business  from pexproject_flightdata where searchkeyid="+str(recordkey)+" group by datasource")
                totalrecords1 = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(recordkey)+" and "+cabin+"> 0")
                totalrecords = len(list(totalrecords1))
                obj = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(recordkey)+" and flighno = 'flag' ")
                obj1 = len(list(obj))
                if obj1 > 3:
                     iscomplete = "completed"   
            #pricematrix = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(recordkey))
            if totalrecords > 0:
                data1 = "stored"
            else:
                data1 = "onprocess"
            mimetype = 'application/json'
        results = []
        results.append(data1)
        results.append(iscomplete)
        data = json.dumps(results)
        return HttpResponse(data, mimetype)    
        
        
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
    adimages = GoogleAd.objects.filter(ad_code="result page")
    #print "adimages",adimages
    if 'userid' in request.session:
        userid = request.session['userid']
        cursor = connection.cursor()
        cursor.execute("select * from reward_points where user_id="+str(userid))
        pointlist = cursor.fetchall()
    
    if request.is_ajax():
        if 'page_no' in request.POST:
            pageno = request.REQUEST['page_no']
        print "pageno",pageno
        offset = (int(pageno) - 1) * limit
    if pageno == 1:
        if request.GET.get('keyid', ''):
            recordkey = request.GET.get('keyid', '')
            if request.GET.get('returnkey', ''):
                roundtripkey = request.GET.get('returnkey', '')
                pricematrix = Flightdata.objects.raw("select p1.rowid,p2.rowid, p2.datasource, (min(if(p1.maincabin > 0,p1.maincabin,NULL))+min(if(p2.maincabin > 0,p2.maincabin,NULL))) as maincabin, (min(if(p1.firstclass>0,p1.firstclass,NULL))+min(if(p2.firstclass>0,p2.firstclass,NULL))) as firstclass ,(min(if(p1.business>0,p1.business,NULL))+min(if(p2.business>0,p2.business,NULL))) as business  from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+roundtripkey+" where p1.searchkeyid="+str(recordkey)+" group by p1.datasource")
            else:
                pricematrix =  Flightdata.objects.raw("select rowid, datasource, min(if(maincabin > 0,maincabin,NULL)) as maincabin, min(if(firstclass>0,firstclass,NULL)) as firstclass ,min(if(business>0,business,NULL)) as business  from pexproject_flightdata where searchkeyid="+str(recordkey)+" group by datasource")
            for s in pricematrix:
                 pricesources.append(s.datasource)      
    action = ''
    if request.GET.get('keyid', '') :
        searchkey = request.GET.get('keyid', '')
        totalrecords1 = ''
        if roundtripkey:
            return_cabin_fare = "p2." + cabinclass
            depart_cabin_fare = "p1." + cabinclass
            totalrecords1 = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(roundtripkey)+" and "+return_cabin_fare+" > 0 where p1.searchkeyid="+str(searchkey)+" and "+depart_cabin_fare+" > 0")

	    flag_count1 = Flightdata.objects.raw("select p1.* from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(roundtripkey)+" and p2.flighno = 'flag' where p1.searchkeyid="+str(searchkey)+" and p1.flighno = 'flag'")
        else:
            totalrecords1 = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(searchkey)+" and flighno != 'flag' and "+cabinclass+"> 0")
	    flag_count1 = Flightdata.objects.raw("select * from pexproject_flightdata where searchkeyid="+str(searchkey)+" and flighno = 'flag' ")
	#print flag_count1.query
        totalrecords = len(list(totalrecords1))
	flag_count = len(list(flag_count1))
	
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
        multisearch = []
        n = 1
        m = 0
        if multicitykey1:
            multicitysearch = ''
            for row in searchdata:
                originname1 = row.source.split("(")
                originname = originname1[1].replace(')','')
                destname1 = row.destination.split("(")
                destname = (destname1[1]).replace(')','')
                multicitysearch = {"source":originname,"destination":destname,"traveldate":row.traveldate}
                m = m+1
            #print multicitysearch
                multisearch.append(multicitysearch) 
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
            adding = '+'
            ecocabin = 'min(if(p1.maincabin > 0,p1.maincabin,NULL))'
            busscabin = 'min(if(p1.firstclass > 0,p1.firstclass,NULL))'
            firstcabin = 'min(if(p1.business > 0,p1.business,NULL))'
            inner_join_on = ''
            pricesources =[]
            recordkey = multicitykey1[0]
            pricematrix_query = ''
            for keys in multicitykey1:
                
                if n > 1:
                    ecocabin = ecocabin+adding+"min(if(p"+str(n)+".maincabin > 0,p"+str(n)+".maincabin,NULL))"
                    busscabin = busscabin+adding+"min(if(p"+str(n)+".firstclass > 0,p"+str(n)+".firstclass,NULL))"
                    firstcabin = firstcabin+adding+"min(if(p"+str(n)+".business > 0,p"+str(n)+".business,NULL))"
                    totalfare = totalfare+"+p"+str(n)+"." + cabinclass
                    totaltax = totaltax+"+p"+str(n)+"."+taxes
                    newidstring =newidstring+sep+"p"+str(n)+".rowid"
                    qry2 = qry2+sep1+'p'+str(n)+'.origin as origin'+str(n)+',p'+str(n)+'.rowid as rowid'+str(n)+', p'+str(n)+'.stoppage as stoppage'+str(n)+', p'+str(n)+'.destination as destination'+str(n)+', p'+str(n)+'.departure as departure'+str(n)+', p'+str(n)+'.arival as arival'+str(n)+', p'+str(n)+'.duration as duration'+str(n)+',p'+str(n)+'.flighno as flighno'+str(n)+', p'+str(n)+'.cabintype1 as cabintype1'+str(n)+',p'+str(n)+'.cabintype2 as cabintype2'+str(n)+',p'+str(n)+'.cabintype3 as cabintype3'+str(n)+', p'+str(n)+'.maincabin as maincabin'+str(n)+', p'+str(n)+'.maintax as maintax'+str(n)+', p'+str(n)+'.firsttax as firsttax'+str(n)+', p'+str(n)+'.businesstax as businesstax'+str(n)+',p'+str(n)+'.departdetails as departdetails'+str(n)+',p'+str(n)+'.arivedetails as arivedetails'+str(n)+', p'+str(n)+'.planedetails as planedetails'+str(n)+',p'+str(n)+'.operatedby as operatedby'+str(n)
                    sep1 = ','
                    inner_join_on = inner_join_on+" inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +keys+"' and p1.datasource = p"+str(n)+".datasource"
                    qry3 = qry3+"inner join pexproject_flightdata p"+str(n)+" on  p"+str(n)+".searchkeyid ='" +keys+"' and p1.datasource = p"+str(n)+".datasource and p"+str(n)+"."+cabinclass +" > '0'  "
                    q = ''
                counter = counter+1
                n = n+1
            pricematrix =  Flightdata.objects.raw("select p1.rowid, p1.datasource,"+ecocabin+" as maincabin,"+busscabin+"  as firstclass ,"+firstcabin+" as business  from pexproject_flightdata p1 "+inner_join_on+" where p1.searchkeyid="+str(recordkey)+" group by p1.datasource")      
            finalquery = qry1+"CONCAT("+newidstring+") as newid ,"+qry2+ totalfare+" as finalprice "+totaltax+" as totaltaxes from pexproject_flightdata p1 "+qry3+"where " + querylist + " order by finalprice,totaltaxes , departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset)
            record = Flightdata.objects.raw(finalquery)
	    #print pricematrix.query
            for s in pricematrix:
                 pricesources.append(s.datasource)
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
		    #print "totaltaxes",row.totaltaxes                    
                    data = {"origin":org,"destination":dest,"stoppage":stop,"departure":depart,"arival":arival,"duration":duration}
                    multirecordlist[pos]=data
                    multidetail_list[pos] = {"departdetails":dept_detail,"arivedetails":arive_detail,"planedetails":plane_detail,"operatedby":operate_detail}
                    pos=pos+1
                mainlist1 = {"newid":row.newid,"flighno":row.flighno,"datasource":row.datasource,"cabintype1":row.cabintype1,"cabintype2":row.cabintype2,"cabintype3":row.cabintype3,"finalprice":row.finalprice,"totaltaxes":row.totaltaxes,"origin":multirecordlist,"multidetail_list":multidetail_list}
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
                #print taxes
                record = Flightdata.objects.raw("select p1.*,p1.maintax as maintax1, p1.firsttax as firsttax1, p1.businesstax as businesstax1,p1.rowid as newid ,case when datasource = 'delta' then " + deltaorderprice + "  else " + unitedorderprice + " end as finalprice, "+taxes+" as totaltaxes from pexproject_flightdata as p1 where " + querylist + " order by finalprice ," + taxes + ",departure ASC LIMIT " + str(limit) + " OFFSET " + str(offset))
            mainlist = record 
            #print record.quer
        progress_value = '' 
        if 'progress_value' in request.POST:
            progress_value = request.REQUEST['progress_value']
            
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
        if 'actionfor' in request.POST:
            return render_to_response('flightsearch/pricematrix.html',{'pricesources':pricesources, 'pricematrix':pricematrix},context_instance=RequestContext(request))      
        if request.is_ajax() :
            
            return render_to_response('flightsearch/search.html', {'action':action,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value, 'multisearch':multisearch, 'data':mainlist,'multirecod':mainlist, 'multicity':multicity, 'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request))
        if totalrecords <= 0 and flag_count > 3:
	    return render_to_response('flightsearch/search.html', {'action':action, 'data':record, 'minprice':minprice, 'tax':tax, 'timedata':timeinfo,'progress_value':progress_value, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request))
            #msg = "Sorry, No flight found  from " + source + " To " + destination + ".  Please search for another date or city !"
            msg = "Oops, looks like there aren't any flight results for your filtered search. Try to broaden your search criteria for better results."
	    if len(searchdata) > 0:
		return  render_to_response('flightsearch/flights.html', {'message':msg, 'search':searchdata[0],'returndate':returndate}, context_instance=RequestContext(request))
	    else:
		return HttpResponseRedirect(reverse('index'))
	else:
            return render_to_response('flightsearch/searchresult.html', {'action':action,'pointlist':pointlist,'pricesources':pricesources, 'pricematrix':pricematrix,'progress_value':progress_value,'multisearch':multisearch,'data':mainlist,'multirecod':mainlist,'multicity':multicity,'recordlen':range(recordlen),'minprice':minprice, 'tax':tax, 'timedata':timeinfo, 'returndata':returnkey, 'search':searchdata, 'selectedrow':selectedrow, 'filterkey':filterkey, 'passenger':passenger, 'returndate':returndate, 'deltareturn':returndelta, 'unitedreturn':returnunited, 'deltatax':deltatax, 'unitedtax':unitedtax, 'unitedminval':unitedminval, 'deltaminval':deltaminval, 'deltacabin_name':deltacabin_name, 'unitedcabin_name':unitedcabin_name,'adimages':adimages}, context_instance=RequestContext(request)) 
        

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

def subscribe(request):
    if request.is_ajax:
	email = request.POST['emailid']
	subscriber = Mailchimp(customfunction.mailchimp_api_key)
        subscriber.lists.subscribe(customfunction.mailchiml_List_ID, {'email':email})
    exit()

def multicity(request):
    context = {}
    
    return render_to_response('flightsearch/multicity.html', context_instance=RequestContext(request)) 
        
    
            

	
# Create your views here.
