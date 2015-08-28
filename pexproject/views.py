from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
#from django.template.context_processors import csrf
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
#from pyvirtualdisplay import Display
from datetime import timedelta
#from datetime import datetime,date
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from pexproject.models import Flightdata
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
        
    #return render(request, 'flightsearch/index.html', {})
        fromstation = []
        depttime =[]
        arivaltime=[]
        deststn=[]
        choice1=[]
        choice2=[]
        maincabin=[]
        firstcabin=[]
        
        orgn = request.REQUEST['fromMain'] #"Seattle, WA, US (SEA)"
        dest = request.REQUEST['toMain'] #"New York, NY, US (NYC - All Airports)"
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
        date = dt.strftime('%Y/%m/%d')
        print date
        url ="http://www.delta.com/"

        #curdate = datetime.date.today() + datetime.timedelta(days=1)
        #date = curdate.strftime('%Y/%m/%d')
        #print date
        driver = webdriver.Firefox()
        driver.get(url)
        driver.implicitly_wait(5)
        
        oneway = driver.find_element_by_id("oneWayBtn")
        driver.execute_script("arguments[0].click();", oneway)
        
        origin = driver.find_element_by_id("originCity")
        origin.clear()
        origin.send_keys(orgn)
        destination = driver.find_element_by_id("destinationCity")
        destination.send_keys(dest)
        #destination.send_keys(Keys.ENTER)
        
        driver.find_element_by_id("departureDate").click()
        driver.find_elements_by_css_selector("td[class='available delta-calendar-td'][data-date='"+date+"']")[0].click()
        
        driver.find_element_by_id("milesBtn").click()
        driver.find_element_by_id("findFlightsSubmit").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "showAll-footer")))
        driver.find_element_by_link_text('Show All').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "fareRowContainer_21")))
        driver.implicitly_wait(10)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page)
        
        datatable = soup.findAll("table",{"class":"fareDetails"})
        #print datatable
        i = 1
        for content in datatable:
            print "=============================data row = "+str(i)+"=================================="
            timeblock = content.findAll("div",{"class":"flightDateTime"})
            for info in timeblock:
                temp = info.findAll("span")
                depttime.append(temp[0].text)
                arivaltime.append(temp[3].text)
                #print temp[0].text,temp[1].text,temp[3].text,temp[4].text
                
            flite_route = content.findAll("div",{"class":"flightPathWrapper"})
            for route in flite_route:
                #print route.find("div",{"class":"originCity"}).text
                fromstation.append(route.find("div",{"class":"originCity"}).text)
                deststn.append(route.find("div",{"class":"destinationCity"}).text)
                #print route.find("div",{"class":"destinationCity"}).text
            if content.findAll("div",{"class":"priceHolder"}):
                fareblock = content.findAll("div",{"class":"priceHolder"})
                lenght = len(fareblock)
                #print fareblock[0].text
                choice1.append(fareblock[0].text)
                if lenght>1:
                    #print fareblock[1].text
                    choice2.append(fareblock[1].text)
            if content.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                cabintype = content.findAll("div",{"class":"frmTxtHldr flightCabinClass"})
                clength = len(cabintype)
                #print cabintype[0].text
                maincabin.append(cabintype[0].text)
                if clength>1:
                    #print cabintype[1].text
                    firstcabin.append(cabintype[1].text)
            i = i+1
            #print "Arival Time = "+arival_time
            #print "Destination Station = "+destination_station
    
        #data = {"choice1":choice1,"choice2":choice2,"choice3":choice3,"choice4":choice4}
        #print choice1, choice2, choice3, choice4, choice5
        #print "================================================" 
        record = zip(fromstation, depttime,choice1,maincabin, choice2,firstcabin, arivaltime, deststn) 
         
        driver.quit()

        return render_to_response('flightsearch/searchresult.html', {'temp':record, 'searchdate':date})
    else:
        render_to_response('flightsearch/searchresult.html')
        

	
# Create your views here.
