from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from scrapers import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("update pexproject_token set limit_hotel_search=0, run_flight_search=0, limit_flight_search=0, run_hotel_search=0, limit_qpx=0 where created_at = CURRENT_DATE - INTERVAL 30 DAY;")
db.commit()
