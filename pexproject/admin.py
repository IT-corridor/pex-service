from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models import User

class ClientAdmin(UserAdmin):
    fieldsets = None
    fields = ['username', 'password', 'is_active', 'is_staff', 'is_superuser', 
              'first_name', 'middlename', 'last_name', 'email', 'groups', 
              'gender', 'date_of_birth', 'language', 'country', 'phone', 
              'home_airport', 'address1', 'address2', 'city', 'state',
              'zipcode', 'usercode', 'user_code_time', 'pexdeals', 'level',
              'search_limit', 'search_run']

admin.site.register(User, ClientAdmin)
