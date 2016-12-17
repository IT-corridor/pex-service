import os
from os import sys, path
import datetime
from datetime import timedelta

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pexproject.settings")

from pexproject.models import Flightdata, Flightdata_b, DestinationTile
from pexproject.scrapers import customfunction
from django.db.models import Q

d_tiles = DestinationTile.objects.all().order_by('-modified_at')[:8]
d_tiles = [item.searchkeyid for item in d_tiles]

time_30 = datetime.datetime.now() - timedelta(minutes=30)
del_fdata = Flightdata.objects.filter(~Q(searchkeyid__in=d_tiles), scrapetime__lte=time_30)

del_fdata_id = tuple([item.rowid for item in del_fdata] + [''])

db = customfunction.dbconnection()
cursor = db.cursor()
db.set_character_set('utf8')
print "insert into pexproject_flightdata_b select * from pexproject_flightdata where rowid in {}".format(str(del_fdata_id))
cursor.execute("insert into pexproject_flightdata_b select * from pexproject_flightdata where rowid in {}".format(str(del_fdata_id)))

cursor.execute("DELETE from pexproject_flightdata where rowid in {}".format(str(del_fdata_id)))
db.commit()
