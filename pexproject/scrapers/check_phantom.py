import os, sys
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import codecs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
import time
from django.db import connection, transaction
import datetime
from datetime import timedelta
from selenium.webdriver.support.ui import Select
import re
from pyvirtualdisplay import Display

# url = "https://www.aa.com/reservation/awardFlightSearchAccess.do"
# url = 'https://book.jetblue.com/shop/search/#/'
# url = 'http://www.virgin-atlantic.com/gb/en/book-your-travel/book-your-flight/flight-search-results.html?departure=LON&arrival=LAX&adult=1&departureDate=17/10/16&search_type=redeemMiles&classType=10&classTypeReturn=10&bookingPanelLocation=Undefined&isreturn=no' 
url = "http://www.delta.com/"   

start_time = datetime.datetime.now()

driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true','--ssl-protocol=any'])
driver.set_window_size(1120, 1080)  
driver.get(url)
html_page = driver.page_source
sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

print "PhantomJS: {} +++++++++++".format((datetime.datetime.now() - start_time).seconds)
print html_page

driver.quit()
