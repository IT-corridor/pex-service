from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
#from django.template.context_processors import csrf
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
#from pyvirtualdisplay import Display
import datetime
from datetime import timedelta
from datetime import datetime,date
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
#from flightsearch.models import Flightdata
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
        print request.REQUEST['fromMain'] 
    #return render(request, 'flightsearch/index.html', {})

        orgn = request.REQUEST['fromMain'] #"Seattle, WA, US (SEA)"
        dest = request.REQUEST['toMain'] #"New York, NY, US (NYC - All Airports)"
        depart = request.REQUEST['deptdate']
        dt = datetime.strptime(depart, '%m/%d/%Y')
        month = dt.strftime('%b')
        currentDay = dt.strftime('%d')
        #print currentDay
        currentdatetime = datetime.now()
        time = currentdatetime.strftime("%Y-%m-%d %H:%M:%S")
        url = "https://www.americanairlines.in/reservation/oneWaySearchAccess.do?promoCode=&netSaaversTripType="
        #display = Display(visible=0, size=(800, 600))
        #display.start()
        driver = webdriver.Firefox()
        #curdate = datetime.date.today() + datetime.timedelta(days=i)
        #date = depart.strftime('%m/%d/%Y')
        driver.get(url)
        driver.implicitly_wait(20)
        origin = driver.find_element_by_id("flightSearchForm.originAirport")
        origin.clear()
        origin.send_keys(orgn) 	
        
        destination = driver.find_element_by_id("flightSearchForm.destinationAirport")
        destination.send_keys(dest)
        
        select = Select(driver.find_element_by_id("flightSearchForm.flightParams.flightDateParams.travelMonth"))
        select.select_by_visible_text(month)
        
        select = Select(driver.find_element_by_id("flightSearchForm.flightParams.flightDateParams.travelDay"))
        select.select_by_visible_text(str(currentDay))
        
        driver.find_element_by_id("flightSearchForm.button.go").send_keys(Keys.ENTER)  #flightCardDetails
        driver.implicitly_wait(30)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "js-matrix-return-lowest")))
        html_page = driver.page_source
        
        soup = BeautifulSoup(html_page)
        allresult = Select(driver.find_element_by_id("resultPerPage-return-lowest"))
        allresult.select_by_visible_text("View All Results")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "js-matrix-return-lowest")))
        html_page1 = driver.page_source
        
        soup1 = BeautifulSoup(html_page1)
        choice1=[]
        choice2=[]
        choice3=[]
        choice4=[]
        choice5=[]
        flightno = []
        fromstation = []
        depttime =[]
        arivaltime=[]
        deststn=[]
        datatds = soup1.findAll("tr",{"class":"segment-first"})
        for content in datatds:
            print "============================================================="
            fareblock = content.findAll("label")
             #.text.strip()
            flag = 0
            for fare in fareblock:
                price = fare.find("div",{"class":"faresort"}).text
    
                '''
                if price != "999999999999999999":
                        prices.append(price)
                else:
                        prices.append("Not available online")
                 '''
               
                if flag == 0:
                    if price != "999999999999999999":
                        choice1.append(price)
                        fare1 = price
                    else:
                        choice1.append("Not available online")
                        fare1 = "Not available online"
                    flag = flag+1
                elif flag == 1:
                    if price != "999999999999999999":
                        fare2 = price
                        choice2.append(price)
                    else:
                        choice2.append("Not available online")
                        fare2 = "Not available online"
                    flag = flag+1
                elif flag == 2:
                    if price != "999999999999999999":
                        fare3 = price
                        choice3.append(price)
                    else:
                        choice3.append("Not available online")
                        fare3 = "Not available online"
                    flag = flag+1
                elif flag == 3:
                    if price != "999999999999999999":
                        fare4 = price
                        choice4.append(price)
                    else:
                        choice4.append("Not available online")
                        fare4 = "Not available online"
                    flag = flag+1
                else:
                    if flag == 4:
                        if price != "999999999999999999":
                            fare4 = price
                            choice5.append(price)
                        else:
                            choice5.append("Not available online")
                            fare5 = "Not available online"
                        flag = flag+1
                
                    
                    
            flite_no = content.find("span",{"class":"aa-flight-number"})
            fno = flite_no.text
            flightno.append(fno)
            departureinfo = content.findAll("td",{"class":"aa-flight-time"})
            deptime = departureinfo[0].find("strong").text
            depttime.append(deptime)
            origin = departureinfo[0].find("span",{"class":"aa-airport-code"}).text
            fromstation.append(origin) 
            #print "Departure Time = "+time
            #print "Origin Station = "+station
            arivtm = departureinfo[1].find("strong").text
            arivaltime.append(arivtm)
            destns = departureinfo[1].find("span",{"class":"aa-airport-code"}).text
            deststn.append(destns)
            
            #queryset = Flightdata(flighno=fno,scrapetime=time,origin=origin,destination=destns,departure=deptime,arival=arivtm,pricecat1=fare1,pricecat2=fare2,pricecat3=fare3,pricecat4=fare4) 
            #queryset.save()
            #print "Arival Time = "+arival_time
            #print "Destination Station = "+destination_station
    
        #data = {"choice1":choice1,"choice2":choice2,"choice3":choice3,"choice4":choice4}
        #print choice1, choice2, choice3, choice4, choice5
        print "================================================" 
        record = zip(flightno, fromstation, depttime,choice1, choice2, choice3, choice4, arivaltime, deststn) 
        #display.stop()
        driver.quit()

    return render_to_response('flightsearch/searchresult.html', {'temp':record})

	
# Create your views here.
