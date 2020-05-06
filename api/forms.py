from django import forms


class FileUploadForm(forms.Form):
    username = forms.CharField(max_length=255)
    method = forms.CharField(max_length=255)
    filename = forms.CharField(max_length=255)
    sent_md5 = forms.CharField(max_length=32)
    file = forms.FileField()
