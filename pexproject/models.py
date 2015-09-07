from django.db import models

class Flightdata(models.Model):
    rowid = models.AutoField(primary_key=True)
    scrapetime = models.DateTimeField()
    searchkeyid = models.IntegerField ()
    flighno = models.CharField(max_length=100)
    stoppage = models.CharField(max_length=100)
    stoppage_station = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure = models.TimeField('Alarm')
    arival = models.TimeField('Alarm')
    duration = models.CharField(max_length=100)
    maincabin = models.CharField(max_length=100)
    firstclass = models.CharField(max_length=100)
    cabintype1 =  models.CharField(max_length=100)
    cabintype2 =  models.CharField(max_length=100)
# Create your models here.
class Flights_wego(models.Model):
    id = models.IntegerField (primary_key=True)
    country_id = models.IntegerField ()
    state_id = models.IntegerField ()
    city_id = models.IntegerField ()
    code = models.CharField(max_length=4)
    type = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    jo_name = models.CharField(max_length=512)
    time_zone = models.CharField(max_length=5)
    latitude = models.CharField(max_length=20)
    logitude = models.CharField(max_length=20)
    
class Searchkey(models.Model):
    searchid = models.AutoField(primary_key=True)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    traveldate = models.DateField(max_length=50)
    scrapetime = models.DateTimeField(max_length=50)
