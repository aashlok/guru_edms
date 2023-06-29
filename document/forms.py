from django import forms
from django.forms import ModelForm

from .models import DocumentType


class DocumentTypeForm(ModelForm):
    class Meta:
        model = DocumentType
        fields = ['label', 'short_code', 'extension']
