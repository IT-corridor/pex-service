from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from scrapers import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("update pexproject_token set limit_hotel_search=0, run_flight_search=0, limit_flight_search=0, run_hotel_search=0, qpx_limit=0;")
db.commit()
