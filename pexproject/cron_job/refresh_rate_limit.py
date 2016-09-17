from ..scrapers import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("delete from pexproject_accessratelimit;")
db.commit()
