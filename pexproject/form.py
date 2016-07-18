from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from .models import *

#from flightsearch.models import Register
'''
class RegisterForm(forms.ModelForm):
    email=forms.EmailField(label="Email")
    password=forms.CharField(label="password", widget=forms.PasswordInput)
    home_airport = forms.CharField()
'''

class LoginForm(forms.Form):
    name=forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    sid=forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    '''
    def clean_name(self):
        try:
	   cleaned_data = super(LoginForm, self).clean()
           name_val = cleaned_data.get("name")           
	   sid_val = cleaned_data.get("sid")
           
	   if name_val and sid_val and Register.objects.filter(name=name_val):
		obj = Register.objects.get(name=name_val)
	   	if sid_val==obj.id:
                  return 1
	        else:
		  return "0" 
           else: 
	     return name_val
        except:
           return "0"
    '''

    
class HotelSearchForm(forms.Form):
    place = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Where To'}))
    checkin = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Check-in', 'autocomplete':'off'}), label='Check-in')
    checkout = forms.CharField(widget=forms.TextInput(attrs={'required': True, 'class': 'form-control', 'placeholder': 'Check-out', 'autocomplete':'off'}), label='Check-out')

# form for admin
class HotelForm(ModelForm):
  class Meta:
    model = Hotel
    exclude = ['cash_points_rate', 'award_cat', 'search', 'distance']

class CityImageForm(ModelForm):
    class Meta:
        model = CityImages
        fields = ['city_image_id', 'image_path', 'city_name', 'status']

class BlogForm(ModelForm):
  class Meta:
    model = Blogs
    exclude = ['blog_created_time', 'blog_updated_time', 'blog_creator']

class EmailTemplateForm(ModelForm):
  class Meta:
    model = EmailTemplate
    exclude = []

class GoogleAdForm(ModelForm):
  class Meta:
    model = GoogleAd
    exclude = []

class CustomerForm(ModelForm):
  class Meta:
    model = User
    exclude = ['language', 'country', 'phone']

class TokenForm(ModelForm):
  class Meta:
    model = Token
    exclude = []


