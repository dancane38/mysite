from django import forms
from .models import VideoFile

class UploadFileForm(forms.ModelForm):
    document = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )

    class Meta:
        model = VideoFile
        fields = ['document','ct_id', 'site_id']

