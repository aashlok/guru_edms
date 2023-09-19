from django.db import models
from django.urls import reverse


# Create your models here.


class Project(models.Model):
    """
Define Project with
manager who creates new project and oversees its activity,
team who has access to projects documents,
location of central document storage
"""
    name = models.CharField(
        max_length=200,
        help_text='Full project name',
        verbose_name='Name',
    )
    short_code = models.CharField(
        max_length=4,
        help_text='Short project code to use in file naming',
        verbose_name='Code',
    )
    start_date = models.DateField(
        auto_now_add=True,
        null=True, blank=True,
        help_text='Start date of Project',
        verbose_name='Start Date',
    )
    end_date = models.DateField(
        null=True, blank=True,
        help_text='End date of Project',
        verbose_name='End Date',
    )
    avtive_status = models.BooleanField(
        default=True,
        help_text='Project active status',
        verbose_name='Active',
    )
    manager = models.ForeignKey(
        to='company.Employee',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text='Project Manager, who creates and manages team and activity',
        verbose_name='Manager',
    )
    members = models.ManyToManyField(
        to='company.Employee',
        related_name='team',
        help_text='Employees added to project team, manager is default member',
        verbose_name='Team',
    )
    description = models.TextField(
        max_length=500,
        null=True, blank=True,
        help_text='Short Project Description and or Information',
        verbose_name='Description',
    )
    project_folder = models.CharField(
        max_length=200,
        null=True, blank=True,
        help_text='Project Folder where all project files are centrally stored',
        verbose_name='Folder',
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project:project-detail', args=[str(self.id)])
