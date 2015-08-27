from django import forms
from django.forms.extras.widgets import SelectDateWidget
#from flightsearch.models import Register
'''
class RegisterForm(forms.ModelForm):
    name=forms.CharField(label="Name")
    username=forms.CharField(label="username")
    password=forms.CharField(label="password", widget=forms.PasswordInput)
    contact=forms.CharField(label="contact")
   # dob=forms.ChoiceField(choices=[(x, x) for x in range(1980, 2010)], required=False)
    
    email=forms.EmailField(label="Email")
    sex = (
           (1,"male"),(2,"female")
        )
    gender=forms.ChoiceField(widget=forms.RadioSelect(), choices=sex)
    photo=forms.ImageField()
    
    class Media:
        css = {
               'all': ('',)
               }

    class Meta:
        model = Register
        fields = ['id','name','username','password','contact','email','subject','gender','photo']
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


