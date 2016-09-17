import MySQLdb
import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("update pexproject_token set limit_hotel_search=0, run_flight_search=0, limit_flight_search=0, run_hotel_search=0;")
db.commit()
