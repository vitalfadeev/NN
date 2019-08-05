from django import forms
from batch.models import Batch
from django.contrib.auth.models import User


class SendForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ('Project_Name', 'Project_FileSourcePathName', 'Project_Description', 'Project_IsPublic')
