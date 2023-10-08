from django.urls import path

from . import views

app_name = 'document'

urlpatterns = [
    path('document-types/', views.documentTypes,
         name='document-types'),
    path('<int:pk>/create-document/', views.createDocument,
         name='create-document'),
    path('document-detail/<int:pk>', views.DocumentDetailView.as_view(),
         name='document-detail'),
    path('<int:pk>/add-document-file/', views.addDocumentFile,
         name='add-document-file'),
    path('document-file-detail/<int:pk>', views.DocumentFileDetailView.as_view(),
         name='document-file-detail'),
    path('fetch-document-file/<int:pk>', views.fetchDocumentFile,
         name='fetch-document-file'),
    path('revise-document-file/<int:pk>', views.reviseDocumentFile,
         name='revise-document-file'),
    path('approve-document-file/<int:pk>', views.approveDocumentFile,
         name='approve-document-file'),
    path('allot-document-file/<int:pk>', views.allotDocumentFile,
         name='allot-document-file'),
    path('document-browser', views.documentBrowser,
         name='document-browser'),
]
