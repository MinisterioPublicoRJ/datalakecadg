from django import forms

from api.utils import md5reader


class FileUploadForm(forms.Form):
    username = forms.CharField(max_length=255)
    method = forms.CharField(max_length=255)
    filename = forms.CharField(max_length=255)
    sent_md5 = forms.CharField(max_length=32)
    file = forms.FileField()

    def clean_sent_md5(self):
        sent_md5 = self.cleaned_data["sent_md5"]
        file_ = self.files["file"]
        if sent_md5 != md5reader(file_):
            raise forms.ValidationError("valor md5 não confere!")

        return sent_md5
