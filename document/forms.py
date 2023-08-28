from django import forms
from django.forms import ModelForm

from .models import DocumentType, Document, DocumentFile


class DocumentTypeForm(ModelForm):
    class Meta:
        model = DocumentType
        fields = ['label', 'short_code', 'extension']


class NewDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['label', 'document_type', 'document_user', 'information']


class NewDocumentFileForm(ModelForm):
    local_files = forms.RadioSelect(choices=[])

    class Meta:
        model = DocumentFile
        fields = ['due_date', 'task_comment']


class DocumentFileRevisionForm(forms.Form):
    revision_note = forms.CharField(label="Revision Note", max_length=200)
