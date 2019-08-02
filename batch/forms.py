from django import forms
from batch.models import Batch


class SendForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ('Project_Name', 'Project_FileSourcePathName', 'Project_Description', 'Project_IsPublic')
