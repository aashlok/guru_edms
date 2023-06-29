from django.urls import path

from . import views

app_name = 'document'

urlpatterns = [
    path('document-types/', views.documentTypes, name='document-types'),
]
