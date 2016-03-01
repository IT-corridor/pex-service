from django.conf import settings
#from django.contrib.sessions.models import Session
#from django.contrib.sessions.backends.db import SessionStore
import customfunction
from social_auth.signals import pre_update, socialauth_registered
from social_auth.backends.steam import SteamBackend
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

#class User(AbstractUser):
    #pass

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
    economy_code = models.TextField(blank=True, null=True)
    business_code = models.TextField(blank=True, null=True)
    first_code = models.TextField(blank=True, null=True)
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
    
    def create_user(self, username,email, password=None, **kwargs):
        fname = ''
        lname = ''
        if kwargs['profile']['first_name']:
            fname = kwargs['profile']['first_name']
        if kwargs['profile']['last_name']:
            lname = kwargs['profile']['last_name']
        try:			
		    user = self.model.objects.get(email=email)
        except:
            user = self.model(
                  email=UserManager.normalize_email(email),
		          username = username,
		   	
	            )

        user.firstname = fname
        
        user.lastname = lname
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
    address1 = models.CharField(max_length=512)
    address2 = models.CharField(max_length=512)
    city = models.CharField(max_length=512)
    state = models.CharField(max_length=512)
    zipcode = models.CharField(max_length=20)
    usercode = models.CharField(max_length=20)
    user_code_time = models.DateTimeField()
    pexdeals = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = ['username']    
    objects =  UserManager()
    def is_authenticated(self):
        return False

#class User(AbstractUser):
    #pass
    #objects = UserManager()
    
class EmailTemplate(models.Model):
    template_id = models.AutoField(primary_key=True)
    email_code = models.CharField(max_length=100)
    subject = models.CharField(max_length=512)
    body = models.TextField()
    placeholder = models.TextField()
    
class Adminuser(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
'''    
class GoogleAd(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_code = models.CharField(max_length=100)
    image_path = models.ImageField(upload_to='/static/flightsearch/img', blank=True, null=True)
    google_code = models.CharField(max_length=512)'''
class GoogleAd(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_code = models.CharField(max_length=100)
    image_path = models.CharField(max_length=512)
    google_code = models.CharField(max_length=512)
    

class Pages(models.Model):
    pageid = models.AutoField(primary_key=True)
    page_name=models.CharField(max_length=100)
    page_path=models.CharField(max_length=100)
    top_content=models.TextField()
    page_text=models.TextField()
    placeholder=models.CharField(max_length=512)
 
