from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import hashlib


HOTEL_CHAINS = {
    'ihg':  'IHG Rewards Club', 
    'spg':  'Starwood Preferred Guest', 
    'hh':   'Hilton HHonors', 
    'cp':   'Choice Privileges', 
    'cc':   'Club Carlson', 
    'mr':   'Marriott Rewards', 
    'hy':   'Hyatt Gold Passport', 
    'ac':   'Le Club Accor', 
    'wy':   'Wyndham Rewards',
}


HOTEL_AMENITIES =  {
    "VR Game Amenity": {
        "Pokemon Go":  [
            'Pokestop',
            'Gym',
            'Generally High Lure Module Usage']
        },

    "Basic Amenities": {
        "Wifi": [
            "Wireless internet in public areas (Free Public Wifi)", 
            "Free wireless internet (Free Wifi)",
            'High speed internet (Free)',
            'Wireless internet in public areas (Paid Public Wifi)',
            'Paid wireless internet (Paid Wifi)',
            'High speed internet (Paid)'],

        "Free Breakfast": [
            'Complimentary breakfast',
            'Complimentary continental breakfast',
            'Complimentary full american breakfast',
            'Complimentary buffet breakfast'],

        "Free Parking": ['Free parking'],

        "Public or Free Transportation": [
            'Free transportation',
            'Train access',
            'Ferry'],

        "Business Friendly": [
            'Conference facilities',
            'Early check-in',
            'Late check-out available',
            'Desk with electrical outlet',
            'Executive floor',
            'Package/Parcel services',
            'Shoe shine stand',
            'Dry cleaning',
            'Business center',
            'Business services',
            'Office rental',
            'Ironing board'],

        "Accessible": [
            'Bilingual staff',
            'Brailed elevators',
            'Accessible facilities',
            'Ramp access',
            'Translation services',
            'Wheelchair access',
            'Accessible rooms',
            'Hearing impaired services'],

        "Activities": [
            'Casino',
            'Exercise gym',
            'Heated pool',
            'Nightclub',
            'Playground',
            'Pool',
            'Sauna',
            'Shopping mall',
            'Spa',
            'Beauty shop/salon',
            'Snow sports',
            'Tennis court',
            'Water sports',
            'Golf',
            'Horseback riding']},        
            
    'Advanced Amenities': {
        'Internet': [   
            'High speed internet (Free)',
            'Wireless internet in public areas (Public Wifi)',
            'High speed internet (Paid)',
            'Wireless internet in public areas (Paid Wifi)',
            'Internet services',
            'Paid wireless internet',
            'Internet browser On TV',
            'Hotspots'],
        'Dining': [
            'Complimentary breakfast',
            'Complimentary continental breakfast',
            'Complimentary full american breakfast',
            'Complimentary buffet breakfast',
            'Complimentary cocktails',
            'Complimentary in-room coffee or tea',
            'Complimentary coffee in lobby',
            '24-hour coffee shop',
            'All-inclusive meal plan',
            'Halal food available',
            'Kosher food available',
            'Buffet breakfast',
            'Continental breakfast',
            'Full american breakfast',
            'Carryout breakfast',
            'Deluxe continental breakfast',
            'Hot continental breakfast',
            'Hot breakfast',
            'Concierge breakfast',
            "Children's breakfast",
            '24-hour food & beverage kiosk',
            'Social hour',
            'Coffee shop',
            'Coffee lounge',
            'Bar/Lounge',
            'Piano Bar',
            'Cocktail lounge',
            'Restaurant',
            'Sports bar',
            'Beer garden',
            'Coffee/tea',
            'Meal plan available',
            'Grocery store',
            'Dinner delivery service from local restaurant'],
        'Parking': [    
            'Free parking',
            'Valet parking',
            'On-Site parking',
            'Off-Site parking',
            'Parking lot',
            'Parking deck',
            'Street side parking',
            'Accessible parking',
            'Electric car charging stations',
            'Parking fee managed by hotel',
            'Truck parking',
            'Motorcycle parking',
            'Bus parking',
            'Long term parking',
            'Secured parking',
            'Parking - controlled access gates to enter parking area',
            'Limited parking',
            'No parking available',
            'Loading dock'],
        'Transportation': [
            'Free transportation',
            'Free airport shuttle',
            'Limousine service',
            'Train access',
            'Airport shuttle service (Paid)',
            'Shuttle to local businesses',
            'Shuttle to local attractions',
            'Helicopter service',
            'Ferry'],
        'Activities': [ 
            'Casino',
            'Driving range',
            'Exercise gym',
            'Health club',
            'Game room',
            'Heated pool',
            'Indoor pool',
            'Jacuzzi',
            'Jogging track',
            'Live entertainment',
            'Nightclub',
            'Outdoor pool',
            'Playground',
            'Pool',
            'Sauna',
            'Shopping mall',
            'Solarium',
            'Spa',
            'Whirlpool',
            'Beauty shop/salon',
            'Video games',
            'Barber shop',
            'Disco',
            'Racquetball',
            'Snow sports',
            'Tennis court',
            'Water sports',
            'Parlor',
            'Golf',
            'Horseback riding',
            'Snow skiing',
            'Water skiing',
            'Newspaper',
            'Piano'],
    }            
}


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


class Flightdata_b(models.Model):
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


class DestinationTile(models.Model):
    final_dest = models.CharField(max_length=250, primary_key=True)
    searchkeyid = models.IntegerField()
    image_path = models.CharField(max_length=200)
    maintax = models.FloatField()
    maincabin = models.IntegerField()
    modified_at = models.DateTimeField(auto_now=True)


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
    user_ids = models.CharField(max_length=500, blank=True, null=True)
    qpx_unmatch_percent = models.FloatField(default=0)


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
    

class UserAlert(models.Model):
    alertid = models.AutoField(primary_key=True)
    userid = models.IntegerField()
    user_email = models.EmailField(blank=True, null=True)
    pricemile = models.IntegerField()
    source_airportid = models.IntegerField()
    destination_airportid = models.IntegerField()
    from_airport = models.CharField(max_length=100)
    to_airport = models.CharField(max_length=100)
    departdate = models.DateField()
    returndate = models.DateField()
    traveller = models.IntegerField()
    cabin = models.CharField(max_length=512)
    annual_repeat = models.BooleanField(default=False)
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
    

class Search(models.Model):
    keyword = models.CharField(max_length=300)
    frequency = models.IntegerField(default=0)
    image = models.CharField(max_length=300, null=True, blank=True)
    lowest_price = models.CharField(max_length=50, null=True, blank=True)
    lowest_points = models.CharField(max_length=50, null=True, blank=True)
    search_time = models.DateTimeField()
    user_ids = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return self.keyword

    class Meta:
        verbose_name = 'Hotel Search'
        verbose_name_plural = 'Hotel Searches'


class Hotel(models.Model):
    prop_id = models.CharField(max_length=50)
    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=50, null=True, blank=True)
    chain = models.CharField(max_length=10)
    lat = models.CharField(max_length=50, null=True, blank=True)
    lon = models.CharField(max_length=50, null=True, blank=True)
    img = models.CharField(max_length=300, null=True, blank=True)
    url = models.CharField(max_length=300)
    address = models.CharField(max_length=500, null=True, blank=True)
    cash_rate = models.FloatField(default=0.0)
    points_rate = models.IntegerField()
    cash_points_rate = models.CharField(max_length=150)
    award_cat = models.CharField(max_length=30)
    distance = models.IntegerField()
    star_rating = models.FloatField(default=0.0)
    search = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class HotelAmenity(models.Model):
    hotel = models.ForeignKey(Hotel)
    amenity = models.CharField(max_length=100)

    def __unicode__(self):
        return self.hotel.name+" : "+self.amenity 
   

class EmailTemplate(models.Model):
    template_id = models.AutoField(primary_key=True)
    email_code = models.CharField(max_length=100)
    subject = models.CharField(max_length=512)
    body = models.TextField()
    placeholder = models.TextField()


class GoogleAd(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_code = models.CharField(max_length=100)
    image_path = models.FileField(upload_to='static/flightsearch/uploads/', null=True, blank=True)
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
    blog_url = models.CharField(max_length=100, default='pexportl/blog/')
    blog_position = models.BooleanField(default=False)
    blog_content = models.TextField()
    blog_image_path = models.FileField(upload_to='static/flightsearch/uploads/', null=True, blank=True)
    blog_meta_key = models.CharField(max_length=512)
    blog_meta_Description = models.TextField(null=True, blank=True, default='')
    blog_creator = models.CharField(max_length=100)
    blog_created_time = models.DateTimeField()
    blog_updated_time = models.DateTimeField()
    blog_status = models.BooleanField(default=False)


class CityImages(models.Model):
    city_image_id = models.AutoField(primary_key=True)
    image_path = models.FileField(upload_to='static/flightsearch/uploads/', null=True, blank=True)
    city_name = models.CharField(max_length=512)
    status = models.BooleanField(default=False)
    last_updated = models.DateTimeField()

    def __unicode__(self):
        return self.city_name


class BlogImages(models.Model):
    image_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    image_path = models.CharField(max_length=100)
      

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')

        fname = ''
        lname = ''
        if extra_fields.get('profile'):
            profile = extra_fields.get('profile')
            fname = profile.get('first_name', '')
            lname = profile.get('last_name', '')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, first_name=fname, last_name=lname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True,
                                 **extra_fields)


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    middlename = models.CharField(max_length=100,null=True,blank=True)
    gender = models.CharField(max_length=20,null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=100,null=True, blank=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20,null=True, blank=True)
    home_airport = models.CharField(max_length=100,null=True, blank=True)
    address1 = models.CharField(max_length=512,null=True, blank=True)
    address2 = models.CharField(max_length=512,null=True, blank=True)
    city = models.CharField(max_length=512,null=True, blank=True)
    state = models.CharField(max_length=512,null=True, blank=True)
    zipcode = models.CharField(max_length=20,null=True, blank=True)
    usercode = models.CharField(max_length=20,null=True, blank=True)
    user_code_time = models.DateTimeField(null=True, blank=True)
    pexdeals = models.BooleanField(default=False)
    level = models.IntegerField(default=0,null=True, blank=True)
    search_limit = models.IntegerField(default=10)
    search_run = models.IntegerField(default=0)
    wallet_id = models.CharField(max_length=50,null=True, blank=True)
    acct_alaska = models.CharField(max_length=20, blank=True, null=True)
    objects =  UserManager()


class Token(models.Model):
    token = models.CharField(max_length=100, unique=True)
    test_token = models.CharField(max_length=100, blank=True, null=True)
    test_qpx_token = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(User)
    limit_standard = models.IntegerField(default=0)
    limit_hotel_search = models.IntegerField(default=0)
    limit_flight_search = models.IntegerField(default=0)
    run_hotel_search = models.IntegerField(default=0)
    run_flight_search = models.IntegerField(default=0)
    limit_qpx = models.IntegerField(default=0)
    allowed_domain = models.CharField(max_length=150,null=True, blank=True)
    number_update = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)    # refresh date
    notes = models.TextField(null=True, blank=True)
    carry_over = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True)   
    refresh_log = models.TextField(null=True, blank=True) 

    def __unicode__(self):
        # return self.owner.name
        return self.token


class UserBackend(object):
    def authenticate(self, username=None, password=None):
        if not password:
            return None

        password = hashlib.md5(password).hexdigest()
        user = User.objects.filter(username=username, password=password)
        if user:
            return user[0]
        return None

    def get_user(user_id):
        return User.objects.get(user_id=user_id)


class AccessRateLimit(models.Model):    
    cookie_id = models.CharField(primary_key=True, max_length=100)
    user_id = models.IntegerField(default=-1)
    run_flight_search = models.IntegerField(default=0)
    run_hotel_search = models.IntegerField(default=0)

    def __unicode__(self):
        return self.cookie_id


class SearchLimit(models.Model):
    user_class = models.CharField(max_length=50, unique=True)
    limit = models.IntegerField()

    def __unicode__(self):
        return self.user_class


class UserConfig(models.Model):
    owner = models.ForeignKey(User)
    reward_config = models.CharField(max_length='150', default='')
