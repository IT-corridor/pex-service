from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
#from django.template.context_processors import csrf
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from pyvirtualdisplay import Display
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
        
        #currentdatetime = datetime.datetime.now()
        #time = currentdatetime.strftime("%Y-%m-%d %H:%M:%S")
        #print time
        
    #return render(request, 'flightsearch/index.html', {})
        fromstation = []
        depttime =[]
        arivaltime=[]
        deststn=[]
        choice1=[]
        choice2=[]
        maincabin=[]
        firstcabin=[]
        stop=[]
        layover=[]
        flightno=[]
        orgn = request.REQUEST['fromMain'] #"Seattle, WA, US (SEA)"
        dest = request.REQUEST['toMain'] #"New York, NY, US (NYC - All Airports)"
        depart = request.REQUEST['deptdate']
        dt = datetime.datetime.strptime(depart, '%m/%d/%Y')
        date = dt.strftime('%Y/%m/%d')
        time = dt.strftime('%Y-%m-%d %H:%M:%S')
        print time
        #records = Flightdata.objects.filter()
        url ="http://www.delta.com/"

        #curdate = datetime.date.today() + datetime.timedelta(days=1)
        #date = curdate.strftime('%Y/%m/%d')
        #print date
        display = Display(visible=0, size=(800, 600))
        display.start()
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
        for content in datatable:
            timeblock = content.findAll("div",{"class":"flightDateTime"})
            for info in timeblock:
                temp = info.findAll("span")
                depature = temp[0].text
                depttime.append(depature)
                arival = temp[3].text
                arivaltime.append(arival)
                #print temp[0].text,temp[1].text,temp[3].text,temp[4].text
                
            flite_route = content.findAll("div",{"class":"flightPathWrapper"})
            fltno = content.find("a",{"class":"helpIcon"}).text
            flightno.append(fltno)
            for route in flite_route:
                if route.find("div",{"class":"nonStopBtn"}):
                    stp = "NONSTOP"
                    stop.append(stp)
                    lyover = ""
                    layover.append(lyover)
                    #print "nonstop"
                else:
                    if route.find("div",{"class":"nStopBtn"}):
                        stp = route.find("div",{"class":"nStopBtn"}).text
                        stop.append(stp)
                        #print route.find("div",{"class":"nStopBtn"}).text
                        lyover = route.find("div",{"class":"layOver"}).find("span").text
                        print route.find("div",{"class":"layOver"}).find("span").text
                        print route.find("div",{"class":"layovertoolTip"}).text
                        layover.append(lyover)
                #print route.find("div",{"class":"originCity"}).text
                sourcestn = route.find("div",{"class":"originCity"}).text
                fromstation.append(sourcestn)
                destinationstn = route.find("div",{"class":"destinationCity"}).text
                deststn.append(destinationstn)
                #print route.find("div",{"class":"destinationCity"}).text
            if content.findAll("div",{"class":"priceHolder"}):
                fareblock = content.findAll("div",{"class":"priceHolder"})
                lenght = len(fareblock)
                #print fareblock[0].text
                fare1 =fareblock[0].text 
                choice1.append(fare1)
                if lenght>1:
                    #print fareblock[1].text
                    fare2 = fareblock[1].text
                    choice2.append(fare2)
            if content.findAll("div",{"class":"frmTxtHldr flightCabinClass"}):
                cabintype = content.findAll("div",{"class":"frmTxtHldr flightCabinClass"})
                clength = len(cabintype)
                cabintype1 = cabintype[0].text
                maincabin.append(cabintype1)
                if clength>1:
                    #print cabintype[1].text
                    cabintype2 = cabintype[1].text
                    firstcabin.append(cabintype2)
            #queryset = Flightdata(flighno=fltno,scrapetime=time,stoppage=stp,stoppage_station=lyover, origin=sourcestn,destination=destinationstn,departure=depature,arival=arival,maincabin=fare1,firstclass=fare2,cabintype1=cabintype1,cabintype2=cabintype2) 
            #queryset.save()
             
        record = zip(flightno,fromstation, stop,layover, depttime,choice1,maincabin, choice2,firstcabin, arivaltime, deststn) 
        display.stop()
        driver.quit()
        

        return render_to_response('flightsearch/searchresult.html', {'temp':record, 'searchdate':date})
    else:
        render_to_response('flightsearch/searchresult.html')
        

	
# Create your views here.
