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

url = "https://www.aa.com/reservation/awardFlightSearchAccess.do"
display = Display(visible=0, size=(800, 600))
display.start()
driver = webdriver.Chrome()
driver.get(url)
html_page = driver.page_source
sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

print html_page
display.stop()
driver.quit()
