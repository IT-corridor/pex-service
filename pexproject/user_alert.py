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
cursor.execute("select t1.*,t2.airport_id, t2.code,t2.cityName  from  pexproject_useralert t1 inner join pexproject_airports t2 on t1.source_airportid = t2.airport_id or t1.destination_airportid = t2.airport_id where expiredate > '"+str(currentDate)+"' and sent_alert_date < '"+str(currentDate)+"' and (alertday like '%%"+currday+"%%' or alertday='')")
users = cursor.fetchall()
oldid = ''
oldsourceCode = ''
oldsourceCity = ''
olddestinationCode = ''
olddestinationCity = ''
destid = ''
sourceid = ''
'''  send scraper '''
#def scrapers(sourcecode,sourcecity,destcode,destcity,date):
    
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
            print pricemiles
            ''' check search key is exists or not'''
            cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(originid)+"' and destination_airport_id='"+str(destid1)+"' and traveldate='"+str(departdate)+"' and scrapetime > '"+str(time1)+"'") 
            result = cursor.fetchone()
            searchid = ''
            if result == None:
                cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_source,full_dest,dest_city,str(departdate),returndate,str(time),originid,destid1))
                db.commit()
                searchid = cursor.lastrowid
                returnkey = ''
                print "result",result
                print "call scraper"
                united(oldsourceCode, dest_code, departdate1,searchid)
                delta(oldsourceCode, dest_code, departdate1,searchid)
                jetblue(oldsourceCode, dest_code, departdate1,searchid)
                virginAmerica(oldsourceCode, dest_code, departdate1,searchid)
                #virgin_atlantic(oldsourceCode, dest_code, departdate1,returndate1,searchid,returnkey)
                etihad(oldsourceCity, dest_city, departdate1, searchid,"maincabin")
            else:
                searchid = result['searchid']
            if searchid:
                cursor.execute("select min(maincabin) as minprice, datasource from pexproject_flightdata where searchkeyid='"+str(searchid)+"' and maincabin > 0 and maincabin < "+str(pricemiles))
                priceObj = cursor.fetchone()
                print "priceObj", priceObj
                try:
                    email_sub = "PEX+ miles alert"
                    emailbody = "Hello "+email+" you can find flights from "+full_source+" to "+full_dest+" starting from .<br><br>Thanks,<b> PEX+ Team"
                    html_content = ''
                    resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
                except:
                    "somting wrong"
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
            print row['user_email']
            departdate = row['departdate']
            departdate1 = departdate.strftime('%m/%d/%Y')
            returndate1 = ''
            returndate = row['returndate']
            if returndate1:
                returndate1 = returndate.strftime('%m/%d/%Y')
            alertday = row['alertday']
            pricemiles = row['pricemile']
            
            ''' check search key is exists or not'''
            cursor.execute("select searchid from pexproject_searchkey where origin_airport_id='"+str(originid)+"' and destination_airport_id='"+str(destid1)+"' and traveldate='"+str(departdate)+"' and scrapetime > '"+str(time1)+"'") 
            result = cursor.fetchone()
            searchid = ''
            if result == None:
                cursor.execute("insert into pexproject_searchkey (source,destination,destination_city,traveldate,returndate,scrapetime,origin_airport_id,destination_airport_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",(full_source,full_dest,destcity,str(departdate),returndate,str(time),originid,destid1))
                db.commit()
                searchid = cursor.lastrowid
                returnkey = ''
                print "inserted id",searchid
                print "result",result
                print "call scraper"
                united(source_code, olddestinationCode, departdate1,searchid)
                delta(source_code, olddestinationCode, departdate1,searchid)
                jetblue(source_code, olddestinationCode, departdate1,searchid)
                virginAmerica(source_code, olddestinationCode, departdate1,searchid)
                etihad(source_city, destcity, departdate1, searchid,"maincabin")
                #virgin_atlantic(source_code, olddestinationCode, departdate1,returndate1,searchid,returnkey)
            else:
                searchid = result['searchid']
            if searchid:
                cursor.execute("select min(maincabin) as minprice, datasource from pexproject_flightdata where searchkeyid='"+str(searchid)+"' and maincabin > 0 and maincabin < "+str(pricemiles))
                priceObj = cursor.fetchone()
                print "priceObj",priceObj
                try:
                    email_sub = "PEX+ miles alert"
                    emailbody = "Hello "+email+" you can find flights from "+full_source+" to "+full_dest+" starting from .<br><br>Thanks,<b> PEX+ Team"
                    html_content = ''
                    resp = customfunction.sendMail('PEX+',email,email_sub,emailbody,html_content)
                except:
                    "somting wrong"
                    
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

