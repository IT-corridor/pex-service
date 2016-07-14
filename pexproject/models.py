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
    eco_fare_code = models.CharField(max_length=50, null=True, blank=True)
    business_fare_code = models.CharField(max_length=50, null=True, blank=True)
    first_fare_code = models.CharField(max_length=50, null=True, blank=True)
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
    destination_city = models.CharField(max_length=512)
    traveldate = models.DateField()
    returndate = models.DateField()
    scrapetime = models.DateTimeField()
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
	if user.password == '' or user.password == None:
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
    level = models.IntegerField(default=0)
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
    name = models.CharField(max_length=100)
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

class Blogs(models.Model):
    blog_id = models.AutoField(primary_key=True)
    blog_title = models.CharField(max_length=512)
    blog_url = models.CharField(max_length=100)
    blog_position = models.BooleanField(default=False)
    blog_content = models.TextField()
    blog_image_path = models.CharField(max_length=512)
    blog_meta_key = models.CharField(max_length=512)
    blog_meta_Description = models.TextField()
    blog_creator = models.CharField(max_length=100)
    blog_created_time = models.DateTimeField()
    blog_updated_time = models.DateTimeField()
    blog_status = models.BooleanField(default=False)

class BlogImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    image_path = models.CharField(max_length=100)
    
class CityImages(models.Model):
    city_image_id = models.AutoField(primary_key=True)
    image_path = models.CharField(max_length=100)
    city_name = models.CharField(max_length=512)
    status = models.BooleanField(default=False)
    last_updated = models.DateTimeField()

class Search(models.Model):
    keyword = models.CharField(max_length=300)
    frequency = models.IntegerField(default=0)
    image = models.CharField(max_length=300, null=True, blank=True)
    lowest_price = models.CharField(max_length=50, null=True, blank=True)
    lowest_points = models.CharField(max_length=50, null=True, blank=True)
    search_time = models.DateTimeField()

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = 'Hotel Search'
        verbose_name_plural = 'Hotel Searches'

class Hotel(models.Model):
    prop_id = models.CharField(max_length=50)
    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=50)
    chain = models.CharField(max_length=10)
    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=50)
    img = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    cash_rate = models.FloatField(default=0.0)
    points_rate = models.IntegerField()
    cash_points_rate = models.CharField(max_length=150)
    award_cat = models.CharField(max_length=30)
    distance = models.IntegerField()
    star_rating = models.FloatField(default=0.0)
    search = models.ForeignKey(Search)

    def __unicode__(self):
        return self.name

class Token(models.Model):
    token = models.CharField(max_length=100)
    owner = models.IntegerField(default=0)
    limit_hotel_search = models.IntegerField(default=0)
    limit_flight_search = models.IntegerField(default=0)
    run_hotel_search = models.IntegerField(default=0)
    run_flight_search = models.IntegerField(default=0)
    allowed_domain = models.CharField(max_length=150)
    number_update = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True)

    def __unicode__(self):
        # return self.owner.name
        return self.token

class UserAlert(models.Model):
    alertid = models.AutoField(primary_key=True)
    userid = models.IntegerField()
    user_email = models.EmailField(blank=True, null=True)
    pricemile = models.IntegerField()
    source_airportid = models.IntegerField()
    destination_airportid = models.IntegerField()
    departdate = models.DateField()
    returndate = models.DateField()
    expiredate = models.DateField()
    alertday = models.CharField(max_length=512)
    sent_alert_date = models.DateField()

class FlexibleDateSearch(models.Model):
    dataid = models.AutoField(primary_key=True)
    scrapertime = models.DateTimeField()
    searchkey = models.IntegerField ()
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    journey = models.DateField()
    flexdate = models.DateField()
    economyflex = models.CharField(max_length=100)
    businessflex = models.CharField(max_length=100)
    firstflex = models.CharField(max_length=100)
    datasource = models.CharField(max_length=50, null=True, blank=True)
    