from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import MySQLdb
import datetime
from django.db import connection, transaction
from pyvirtualdisplay import Display

def deltaPoints(username,password,userid):
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor = connection.cursor()
    url ="https://www.delta.com/custlogin/loginPage.action"
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)
    user = driver.find_element_by_id("usernm_LoginPage")
    user.clear()
    user.send_keys(username)
    passwd = driver.find_element_by_id("pwd_LoginPage")
    passwd.send_keys(password)
    driver.find_element_by_id("submit1_LoginPage").send_keys(Keys.ENTER)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "custlogin_name"))) 
        
        driver.implicitly_wait(40)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"lxml")
   
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "sky-miles")))
    except:
        display.stop
        driver.quit()
        return "fail"
    totalmiles = soup.find("span",{"id":"sky-miles"}).text
    
    print totalmiles
    cursor.execute("select * from reward_points where user_id="+str(userid)+" and airlines='delta'")
    object = cursor.fetchone()
    if object:
        cursor.execute("update reward_points set reward_points="+str(totalmiles)+",update_time='"+str(stime)+"' where airlines='delta' and user_id="+str(userid))
    else:
        cursor.execute ("INSERT INTO reward_points (user_id,reward_points,airlines,update_time) VALUES (%s,%s,%s,%s);", (str(userid),str(totalmiles),"delta",str(stime)))
    transaction.commit()
    display.stop()                                                                                                                                  
    driver.quit()
    return "success"

def unitedPoints(usernumber,password,userid):
    cursor = connection.cursor()
    display = Display(visible=0, size=(800, 600))
    display.start()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "https://www.united.com/web/en-US/apps/account/account.aspx"
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        username = driver.find_element_by_id("ctl00_ContentInfo_SignIn_onepass_txtField")
        username.clear()
        username.send_keys(usernumber)
        passwrd = driver.find_element_by_id("ctl00_ContentInfo_SignIn_password_txtPassword")
        passwrd.send_keys(password)
        driver.find_element_by_id("ctl00_ContentInfo_SignInSecure").send_keys(Keys.ENTER)
    
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ctl00_ContentInfo_AccountSummary_pnlSummaryNew"))) 
    except:
        display.stop()                                                                                                                                  
        driver.quit()
        return "fail"
    driver.implicitly_wait(40)
    html_page = driver.page_source
    soup = BeautifulSoup(html_page,"lxml")
    profilediv = soup.find("div",{"id":"ctl00_ContentInfo_AccountSummary_pnlSummaryNew"})
    mileage = profilediv.find("span",{"id":"ctl00_ContentInfo_AccountSummary_lblMileageBalanceNew"})
    point = mileage.text
    print point
    cursor.execute("select * from reward_points where user_id="+str(userid)+" and airlines='united'")
    object = cursor.fetchone()
    if object:
        cursor.execute("update reward_points set reward_points="+str(point)+",update_time='"+str(stime)+"' where airlines='united' and user_id="+str(userid))
    else:
        cursor.execute ("INSERT INTO reward_points (user_id,reward_points,airlines,update_time) VALUES (%s,%s,%s,%s);", (str(userid),str(point),"united",str(stime)))
    transaction.commit()
    display.stop()                                                                                                                                  
    driver.quit()
    return "success"
    
def virginPoints(username,password,userid):
    cursor = connection.cursor()
    currentdatetime = datetime.datetime.now()
    stime = currentdatetime.strftime('%Y-%m-%d %H:%M:%S')
    url = "http://www.virgin-atlantic.com/us/en.html"
    display = Display(visible=0, size=(800, 600))
    display.start()
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        user = driver.find_element_by_id("login_uname")
        driver.execute_script("document.getElementById('login_uname').setAttribute('value', '"+username+"')");
        driver.execute_script("document.getElementById('login_pwd').setAttribute('value', '"+password+"')");
        
        submit = driver.find_element_by_class_name("primaryAction")
        driver.execute_script("arguments[0].click();", submit);
        
        driver.implicitly_wait(40)
        html_page = driver.page_source
        soup = BeautifulSoup(html_page,"lxml")
        
        mileage = soup.find("td",{"class":"mileageValue"})
        point = (mileage.text).strip()
        cursor.execute("select * from reward_points where user_id="+str(userid)+" and airlines='virgin'")
        object = cursor.fetchone()
        if object:
            cursor.execute("update reward_points set reward_points="+str(point)+",update_time='"+str(stime)+"' where airlines='virgin' and user_id="+str(userid))
        else:
            cursor.execute ("INSERT INTO reward_points (user_id,reward_points,airlines,update_time) VALUES (%s,%s,%s,%s);", (str(userid),str(point),"virgin",str(stime)))
        transaction.commit()
    except:
        display.stop()                                                                                                                                  
        driver.quit()
        return "fail"
    display.stop()                                                                                                                                  
    driver.quit()
    return "success"

       
        
    
