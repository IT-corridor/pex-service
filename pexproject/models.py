from django.conf import settings
#from django.contrib.sessions.models import Session
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

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
    maincabin = models.IntegerField()
    maintax = models.FloatField()
    firstclass = models.IntegerField()
    firsttax = models.FloatField()
    business = models.IntegerField()
    businesstax = models.FloatField()
    cabintype1 =  models.CharField(max_length=100)
    cabintype2 =  models.CharField(max_length=100)
    cabintype3 =  models.CharField(max_length=100)
    datasource =  models.CharField(max_length=20)
    arivedetails = models.TextField()
    departdetails = models.TextField()
    planedetails = models.TextField()
    operatedby = models.TextField()
    
    '''
    def arive_list(self):
        return self.arivedetails.split('@')
    def depart_list(self):
        return self.departdetails.split('@')
    def plane_list(self):
        return self.planedetails.split('@')
    '''

class Airports(models.Model):
    airport_id = models.IntegerField (primary_key=True)
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=255)
    cityCode = models.CharField(max_length=50)
    cityName = models.CharField(max_length=200)
    countryName = models.CharField(max_length=200)
    countryCode = models.CharField(max_length=200)
    timezone = models.CharField(max_length=8)
    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=200)
    numAirports = models.IntegerField()
    city = models.BooleanField(default=True)
       
class Searchkey(models.Model):
    searchid = models.AutoField(primary_key=True)
    source = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    traveldate = models.DateField(max_length=50)
    returndate = models.DateField(null=True)
    scrapetime = models.DateTimeField(max_length=50)
    origin_airport_id = models.IntegerField ()
    destination_airport_id = models.IntegerField ()

class Contactus(models.Model):
    contactid = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    title = models.TextField()
    company = models.CharField(max_length=500)
    website = models.CharField(max_length=500)
    message = models.TextField()
    topic = models.TextField()
    label_text = models.TextField()
    
class UserManager(BaseUserManager):
	def create_user(self, username, email, password=None):
		print username
		print "email=",email
		
        	#if not email:
	         #   raise ValueError('Users must have an email address')
		#return self._create_user(username, email, password)
		
        	user = self.model(
	            email=UserManager.normalize_email(email),
		        username = username
		   
	        )
        	user.set_password(password)
	        user.save(using=self._db)
        	return user

class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(blank=True, null=True)
    #password = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    home_airport = models.CharField(max_length=100)
    address = models.CharField(max_length=512)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']    
    objects =  UserManager()
    def is_authenticated(self):
        return False
