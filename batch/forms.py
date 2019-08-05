from django import forms
from batch.models import Batch
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SendForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ('Project_Name', 'Project_FileSourcePathName', 'Project_Description', 'Project_IsPublic')
