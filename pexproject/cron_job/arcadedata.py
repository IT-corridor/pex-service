
#!usr/bin/env python
import datetime
from datetime import timedelta

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from scrapers import customfunction 


db = customfunction.dbconnection()
cursor = db.cursor()
db.set_character_set('utf8')

time1 = datetime.datetime.now() - timedelta(minutes=30)
time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
cursor.execute("insert into arcade_flight_data select * from pexproject_flightdata where scrapetime < '"+str(time1)+"'")
cursor.execute("DELETE from pexproject_flightdata where scrapetime < '"+str(time1)+"'")
db.commit()