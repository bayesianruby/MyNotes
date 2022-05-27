from django import forms
from django.db.models import fields
from django.forms import ModelForm
from django.db import models
from .models import Image
from .models import Text
from .models import Subject
from .models import UserProfile

from djrichtextfield.widgets import RichTextWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('university','year')


class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Image
        fields = ('image',)


class TextForm(forms.ModelForm):
    """Form for the text model"""
    teacher = forms.CharField(required=False)
    class Meta:
        model = Text 
        fields = ('pdf','richtext','title','subject','teacher')
    def __init__(self, user, *args, **kwargs):   
        super(TextForm, self).__init__(*args, **kwargs)
        user_profile= UserProfile.objects.filter(user=user)[0]
        subjects = user_profile.subjects.all()
        self.fields['subject'].queryset = subjects
        #self.fields['subject'].queryset = Subject.objects.filter(user="Tom")



class PdfForm(forms.ModelForm):
    """Form for the text model"""
    class Meta:
        model = Text 
        fields = ('pdf','title','subject')
        





    # def add_value(self,valeur):
    #     SELF.your_name = forms.CharField(label='Your name', max_length=100 ,initial=valeur,widget=RichTextWidget())
    