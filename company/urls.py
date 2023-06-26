from django.urls import path

from . import views

app_name = 'company'

urlpatterns = [
    path('', views.index, name='index'),
    path('initial-setup/', views.initialSetup, name='initial-setup'),
    path('configuration/', views.configuration, name='configuration'),
]
