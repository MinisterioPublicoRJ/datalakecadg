import csv
import gzip
from io import BytesIO, StringIO

import xlrd
from api.utils import FILE_ENCODING, is_data_valid, md5reader
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms.utils import ErrorDict


class FileUploadForm(forms.Form):
    nome = forms.CharField(max_length=255, label="Nome")
    method = forms.CharField(max_length=255, label="Método")
    filename = forms.CharField(
        max_length=255, label="Nome do arquivo", required=False
    )
    md5 = forms.CharField(max_length=32, label="Valor MD5", required=False)
    file = forms.FileField(label="Arquivo")

    def __init__(self, disable_md5=False, good_exts=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disable_md5 = disable_md5
        self.md5_ = self.prepare_md5(self.files.get("file"))
        self.good_exts = good_exts or (".csv.gz",)

    def prepare_md5(self, file_):
        return md5reader(file_) if not self.disable_md5 and file_ else ""

    # TODO: Talvez faça sentido criar uma classe sem herdar de forms.Form
    # e chamaar os métods de validação de cada campo.
    # Os métodos _clean_fields e full_clean foram alterados para que a
    # validação pare no primeiro erro
    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if field.disabled:
                value = self.get_initial_for_field(field, name)
            else:
                value = field.widget.value_from_datadict(
                    self.data, self.files, self.add_prefix(name)
                )
            try:
                if isinstance(field, forms.FileField):
                    initial = self.get_initial_for_field(field, name)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except forms.ValidationError as e:
                self.add_error(name, e)
                break

    def full_clean(self):
        """
        Clean all of self.data and populate self._errors and self.cleaned_data.
        """
        self._errors = ErrorDict()
        if not self.is_bound:  # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return

        clean_methods = [
            self._clean_fields,
            self._clean_form,
            self._post_clean,
        ]
        for clean_method in clean_methods:
            clean_method()
            if self._errors:
                break

    @property
    def is_csv(self):
        return self.files["file"].name.endswith(".csv")

    @property
    def is_xlsx(self):
        return self.files["file"].name.endswith(".xlsx")

    @property
    def base_return(self):
        if self.is_bound:
            return {"md5": self.md5_, "error": self._errors}

    @property
    def status_code(self):
        error_types = [error for error in self._errors]
        status = 400
        if not self._errors:
            status = 201
        elif "md5" in error_types or "schema" in error_types:
            status = 400
        elif "filename" in error_types:
            status = 415

        return status

    def clean_md5(self):
        md5 = self.cleaned_data["md5"]
        if not self.disable_md5 and md5 != self.md5_:
            raise forms.ValidationError("valor md5 não confere!")

        return md5

    def clean_filename(self):
        given_filename = self.cleaned_data.get("filename")
        original_filename = self.files["file"].name
        filename = given_filename or original_filename
        if not filename.endswith(
            self.good_exts
        ) or not original_filename.endswith(self.good_exts):
            raise forms.ValidationError(
                "arquivo deve ser {0}!".format(", ".join(self.good_exts))
            )

        return filename

    def compress(self, file_):
        file_.seek(0)
        if isinstance(file_.file, StringIO):
            c_file = BytesIO(file_.read().encode(FILE_ENCODING))
        else:
            c_file = file_.file

        return gzip.compress(c_file.read())

    def convert_to_csv(self, file_):
        wb = xlrd.open_workbook(file_contents=file_.read())
        if len(wb.sheets()) > 1:
            raise forms.ValidationError(
                "Os arquivos devem conter apenas uma aba. Verifique também as abas escondidas"
            )

        sh = wb.sheet_by_index(0)
        output = StringIO()
        writer = csv.writer(output)
        for rownum in range(sh.nrows):
            writer.writerow(sh.row_values(rownum))

        size = output.tell()
        output.seek(0)
        in_memory = InMemoryUploadedFile(
            output,
            name=file_.name,
            content_type="text/csv",
            size=size,
            field_name=file_.field_name,
            charset=file_.charset,
        )
        in_memory.seek(0)
        return in_memory

    def clean(self):
        cleaned_data = super().clean()
        if self.is_xlsx:
            cleaned_data["file"] = self.convert_to_csv(cleaned_data["file"])

        valid_data, status = is_data_valid(
            cleaned_data["nome"], cleaned_data["method"], cleaned_data["file"]
        )
        if not valid_data:
            self._errors["schema"] = self.error_class(
                ["arquivo apresentou estrutura de dados inválida"]
            )
            self._errors["detail_schema"] = status

        if self.is_csv or self.is_xlsx:
            cleaned_data["filename"] = cleaned_data["filename"].replace(
                ".xlsx", ".csv"
            )
            cleaned_data["file"] = self.compress(cleaned_data["file"])
            cleaned_data["filename"] = cleaned_data["filename"] + ".gz"

        return cleaned_data
