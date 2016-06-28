#!/usr/bin/env python
import os, sys
import MySQLdb
import datetime
from datetime import timedelta
import customfunction
from united import united
from delta import delta
from jetblue import jetblue
from virginAmerica import virginAmerica
from virgin import virgin_atlantic
from etihad import etihad
import thread

db = customfunction.dbconnection()
cursor = db.cursor(MySQLdb.cursors.DictCursor)
db.set_character_set('utf8')
time = datetime.datetime.now()
time1 = datetime.datetime.now() - timedelta(minutes=30)
time1 = time1.strftime('%Y-%m-%d %H:%M:%S')

currentDate = datetime.datetime.now().date()
currday = currentDate.strftime("%A")
cursor.execute("select t1.*,t2.airport_id, t2.code,t2.cityName  from  pexproject_useralert t1 inner join pexproject_airports t2 on t1.source_airportid = t2.airport_id or t1.destination_airportid = t2.airport_id where expiredate >= '"+str(currentDate)+"' and sent_alert_date < '"+str(currentDate)+"' and (alertday like '%%"+currday+"%%' or alertday='')")
users = cursor.fetchall()
oldid = ''
oldsourceCode = ''
oldsourceCity = ''
olddestinationCode = ''
olddestinationCity = ''
destid = ''
sourceid = ''

def callScraper(source_code, olddestinationCode, departdate1,searchid,source_city,destcity):
    #print source_code, olddestinationCode, departdate1,searchid
    united(source_code, olddestinationCode, departdate1,searchid)
    delta(source_code, olddestinationCode, departdate1,searchid)
    jetblue(source_code, olddestinationCode, departdate1,searchid)
    virginAmerica(source_code, olddestinationCode, departdate1,searchid)
    etihad(source_city, destcity, departdate1, searchid,"maincabin")
    virgin_atlantic(source_code, olddestinationCode, departdate1,returndate1,searchid,returnkey)
    
def sendAlertEmail(searchid,returnkey,pricemiles,full_source,full_dest,usermail,deptdate,retdate):
    retstr = ''
    triptype=''
    if returnkey:
        cursor.execute("select (min(p1.maincabin)+min(p2.maincabin)) as minprice from pexproject_flightdata p1 inner join pexproject_flightdata p2 on p1.datasource = p2.datasource and p2.searchkeyid ="+str(returnkey)+" and p2.maincabin > 0 where p1.searchkeyid="+str(searchid)+" and p1.maincabin > 0 group by p1.datasource order by minprice")   
        retstr = ' - '+str(retdate)
        triptype = "Round-Trip"
    else:    
        cursor.execute("select min(maincabin) as minprice, datasource from pexproject_flightdata where searchkeyid='"+str(searchid)+"' and maincabin > 0 and maincabin < "+str(pricemiles))
        triptype = "One-Way"
        
    #print cursor._last_executed
    priceObj = cursor.fetchone()
    
    ''' Send alert mail  '''
    if priceObj and priceObj['minprice'] <= pricemiles and priceObj['minprice'] != None:
        try:
            price = priceObj['minprice']
            email_sub = "PEX+ Flight Alert: We found a matching flight"
            emailbody = "<img src='/var/www/html/python/pex/pexproject/pexproject/static/flightsearch/img/logo.jpg' alt='Creating Email Magic' width='100' height='100' style='display: block;' /> <br><br> Hello <b>"+usermail+"</b>,<br><br> We've found flights that meets your search for:<br><br>"+full_source+" - "+full_dest+"<br>"+deptdate+retstr+" for "+triptype+".<br><br> Get more details by searching on <a href='http://pexportal.com/'>pexportal.com</a><br><br>Best Regards,<br><b>The PEX+ Team"
            #print emailbody
            html_content = ''
            resp = customfunction.sendMail('PEX+',usermail,email_sub,emailbody,html_content)
        except:
            print "somting wrong"

    
for row in users:
    print "**************************************************"
    if oldid == row['alertid']:
        if oldsourceCode:
            originid = sourceid
            destid1 = row['airport_id']
            dest_code = row['code']  
            dest_city = row['cityName']
            full_dest = dest_city+" ("+dest_code+")"
            full_source = oldsourceCity+" ("+oldsourceCode+")"
            usermail = row['user_email']
            departdate = row['departdate']
            departdate1 = departdate.strftime('%m/%d/%Y')
            returndate =  row['returndate']
            returndate1 = ''
            if returndate:
                returndate1 = returndate.strftime('%m/%d/%Y')
            alertday =  row['alertday']
            pricemiles = row['pricemile']
            
            ''' check search key is exists or not'''
            cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(originid)+"' and destination_airport_id='"+str(destid1)+"' and traveldate='"+str(departdate)+"' and scrapetime > '"+str(time1)+"'") 
            result = cursor.fetchone()
            searchid = ''
            returnkey = ''
            
            if result == None:
                cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_source,full_dest,dest_city,str(departdate),returndate,str(time),originid,destid1))
                db.commit()
                searchid = cursor.lastrowid
                callScraper(oldsourceCode, dest_code, departdate1,searchid,oldsourceCity,dest_city)
                
            else:
                searchid = result['searchid']
                
            ''' if roundTrip '''
            if returndate:
                cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(destid1)+"' and destination_airport_id='"+str(originid)+"' and traveldate='"+str(returndate)+"' and scrapetime > '"+str(time1)+"'") 
                returnresult = cursor.fetchone()
                if returnresult == None:
                    returndate3 = ''
                    cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_dest,full_source,oldsourceCity,str(returndate),returndate3,str(time),destid1,originid))
                    db.commit()
                    returnkey = cursor.lastrowid
                    callScraper(dest_code, oldsourceCode, returndate1,returnkey,dest_city,oldsourceCity)
                else:
                    returnkey = returnresult['searchid']
                    
            if searchid:
                sendAlertEmail(searchid,returnkey,pricemiles,full_source,full_dest,usermail,departdate1,returndate1)
            cursor.execute("update pexproject_useralert set sent_alert_date='"+str(currentDate)+"' where alertid="+str(row['alertid']))    
            db.commit()
            oldsourceCode = ''
            destid = ''
            
        elif olddestinationCode:
            originid = row['airport_id']
            destid1 = destid
            source_code =row['code']
            source_city = row['cityName']
            full_source = source_city+" ("+source_code+")"
            destcode = olddestinationCode
            destcity = olddestinationCity  
            full_dest = olddestinationCity+" ("+olddestinationCode+")"
            usermail = row['user_email']
            departdate = row['departdate']
            departdate1 = departdate.strftime('%m/%d/%Y')
            returndate1 = ''
            returndate = row['returndate']
            if returndate:
                returndate1 = returndate.strftime('%m/%d/%Y')
            alertday = row['alertday']
            pricemiles = row['pricemile']
            
            ''' check search key is exists or not'''
            cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(originid)+"' and destination_airport_id='"+str(destid1)+"' and traveldate='"+str(departdate)+"' and scrapetime > '"+str(time1)+"'") 
            result = cursor.fetchone()
            searchid = ''
            returnkey = ''
            if result == None:
                cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_source,full_dest,destcity,str(departdate),returndate,str(time),originid,destid1))
                db.commit()
                searchid = cursor.lastrowid
                callScraper(source_code, olddestinationCode, departdate1,searchid,source_city,destcity)
            else:
                searchid = result['searchid']
                
            ''' if RoundTrip '''
              
            if returndate:
                cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(destid1)+"' and destination_airport_id='"+str(originid)+"' and traveldate='"+str(returndate)+"' and scrapetime > '"+str(time1)+"'") 
                returnresult = cursor.fetchone()
                if returnresult == None:
                    returndate3 = ''
                    cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_dest,full_source,source_city,str(returndate),returndate3,str(time),destid1,originid))
                    db.commit()
                    returnkey = cursor.lastrowid
                    print "returndate",returndate      
                    callScraper(olddestinationCode, source_code, returndate1,returnkey,destcity,source_city)
                else:
                    returnkey = returnresult['searchid']
            
            if searchid:
                sendAlertEmail(searchid,returnkey,pricemiles,full_source,full_dest,usermail,departdate1,returndate1)
            cursor.execute("update pexproject_useralert set sent_alert_date='"+str(currentDate)+"' where alertid="+str(row['alertid']))    
            db.commit()
            olddestinationCode = ''
            sourceid = ''
            
    if row['airport_id'] == row['source_airportid']:
        oldsourceCode = row['code']
        oldsourceCity = row['cityName']
        sourceid = row['source_airportid']
    if row['airport_id'] == row['destination_airportid']:
        olddestinationCode = row['code']
        olddestinationCity = row['cityName']
        destid = row['destination_airportid']
    oldid = row['alertid']


