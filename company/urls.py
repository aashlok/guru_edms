from django.urls import path

from . import views

app_name = 'company'

urlpatterns = [
    path('', views.index, name='index'),
    path('initial-setup/', views.initialSetup, name='initial-setup'),
    path('configuration/', views.configuration, name='configuration'),
    path('designations/', views.designations, name='designations'),
    path('employees/', views.EmployeeListView.as_view(), name='employees'),
    path('add-employee/', views.addEmployee, name='add-employee'),
]
