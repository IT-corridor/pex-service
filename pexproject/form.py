from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from .models import *


class LoginForm(forms.Form):
    name=forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    sid=forms.IntegerField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

    
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
        exclude = ['blog_created_time', 'blog_updated_time', 'blog_url']


class FlightHotelLinkForm(ModelForm):
    class Meta:
        model = FlightHotelLink
        exclude = ['ah_type']


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
        exclude = ['last_login', 'user_code_time', 'date_joined']


class TokenForm(ModelForm):
    class Meta:
        model = Token
        exclude = ['number_update', 'created_at', 'closed_at']


class SearchLimitForm(ModelForm):
    class Meta:
        model = SearchLimit
        exclude = []

