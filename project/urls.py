from django.urls import path

from . import views

app_name = 'project'

urlpatterns = [
    path('add-project/', views.createProject, name='add-project'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('<int:pk>', views.ProjectDetailView.as_view(),
         name='project-detail'),
]
