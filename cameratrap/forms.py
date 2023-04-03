from django import forms
from .models import VideoFile

class UploadFileForm(forms.ModelForm):
    document = forms.FileField()

    class Meta:
        model = VideoFile
        fields = ['document','ct_id', 'site_id']

