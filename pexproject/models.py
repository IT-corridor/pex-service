from django.db import models

class Flightdata(models.Model):
    rowid = models.AutoField(primary_key=True)
    scrapetime = models.DateTimeField()
    flighno = models.CharField(max_length=100)
    stoppage = models.CharField(max_length=100)
    stoppage_station = models.CharField(max_length=100)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    arival = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    maincabin = models.CharField(max_length=100)
    firstclass = models.CharField(max_length=100)
    cabintype1 =  models.CharField(max_length=100)
    cabintype2 =  models.CharField(max_length=100)
# Create your models here.
