import MySQLdb
import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("delete pexproject_accessratelimit;")
db.commit()
