from django import forms

from api.utils import is_data_valid, md5reader


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

    def clean_filename(self):
        filename = self.cleaned_data["filename"]
        if not filename.endswith(".gz") and not self.files[
            "file"
        ].name.endswith(".gz"):
            raise forms.ValidationError("arquivo deve ser GZIP!")

        return filename

    def clean(self):
        cleaned_data = super().clean()
        valid_data, status = is_data_valid(
            cleaned_data["username"],
            cleaned_data["method"],
            self.files["file"]
        )
        if not valid_data:
            self._errors["schema"] = self.error_class(
                ["arquivo apresentou estrutura de dados inválida"]
            )

        return cleaned_data
