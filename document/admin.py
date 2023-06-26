from django.contrib import admin

from .models import DocumentType, Document, DocumentFile

# Register your models here.
admin.site.register(DocumentType)
admin.site.register(Document)
admin.site.register(DocumentFile)
