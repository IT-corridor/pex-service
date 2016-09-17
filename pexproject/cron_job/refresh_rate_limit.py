from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from scrapers import customfunction 

db = customfunction.dbconnection()

cursor = db.cursor()
cursor.execute("delete from pexproject_accessratelimit;")
db.commit()
