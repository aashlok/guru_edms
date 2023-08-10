from django.urls import path

from . import views

app_name = 'document'

urlpatterns = [
    path('document-types/', views.documentTypes, name='document-types'),
    path('create-document/', views.createDocument, name='create-document'),
    path('add-document-file/', views.addDocumentFile,
         name='add-document-file'),
    path('revise-document-file/', views.reviseDocumentFile,
         name='revise-document-file'),
]
