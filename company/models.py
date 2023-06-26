from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Company(models.Model):
    """
Basic configuration of company to store filestore location etc
Only one instance per installation is required.
"""
    name = models.CharField(
        max_length=100,
        help_text='Full company Name, used in page title etc',
        verbose_name='Company Name',
    )
    short_code = models.CharField(
        max_length=10,
        help_text='Company short code to use in file naming',
        verbose_name='Short Code',
    )
    fileserver_ip = models.GenericIPAddressField(
        null=True, blank=True,
        help_text='Local IP address of central file server',
        verbose_name='Server IP',
    )
    fileserver_name = models.CharField(
        max_length=50,
        null=True, blank=True,
        help_text='Computer name of fileserver',
        verbose_name='Server Name'
    )
    fileserver_user = models.CharField(
        max_length=50,
        null=True, blank=True,
        help_text='Username of fileserver computer',
        verbose_name='Server User'
    )
    fileserver_folder = models.CharField(
        max_length=100,
        help_text='Folder on Fileserver where all file are stored',
        verbose_name='Server Folder',
    )


class Designation(models.Model):
    """
Designations of employees in the company.
Designation is allotted access to document depending on their type.
Additionally allotted permissions to Create Update Delete operations.
Must be created before creating employees.
"""
    title = models.CharField(
        max_length=100,
        help_text='Title of Designation',
        verbose_name='Title',
    )
    document_type_permission = models.ManyToManyField(
        to='document.DocumentType',
        help_text='Document Types allowed to this designation',
        verbose_name='Permitted Types',
        related_name='allowed',
    )
    employee_crud_permission = models.BooleanField(
        default=False,
        help_text='Permission required to add, update and delete employee',
        verbose_name='Employee Permission',
    )
    project_crud_permission = models.BooleanField(
        default=False,
        help_text='Permission required to add , update and delete project',
        verbose_name='Project Permission',
    )
    document_crud_permission = models.BooleanField(
        default=False,
        help_text='Permission required to add , update and delete document',
        verbose_name='Document Permission',
    )

    def __str__(self):
        return self.title


class Employee(models.Model):
    """
Employee model on top of django built in User framework
to accomodate extra information relevant to company operation.
Important fields are designation and shared folder.
"""
    user = models.OneToOneField(
        User,
        null=True,
        on_delete=models.RESTRICT,
        help_text='User model Djnago Builtin',
        verbose_name='User',
    )
    designation = models.ForeignKey(
        Designation,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Employee designation',
        verbose_name='Designation',
    )
    date_joined = models.DateField(
        null=True, blank=True,
        help_text='employee join date',
        verbose_name='Join Date',
    )
    date_left = models.DateField(
        null=True, blank=True,
        help_text='employee left date',
        verbose_name='Left Date',
    )
    shared_folder = models.CharField(
        max_length=200,
        null=True, blank=True,
        help_text='Folder path string of employees local shared folder',
        verbose_name='Folder',
    )
    pc_name = models.CharField(
        max_length=50,
        null=True, blank=True,
        help_text='PC name of employee to access file share',
        verbose_name='PC Name',
    )
    local_ip = models.GenericIPAddressField(
        null=True, blank=True,
        help_text='IP address of employee PC to access file share',
        verbose_name='Local IP',
    )
    bio = models.TextField(
        max_length=500,
        null=True, blank=True,
        help_text='Short employee profile to store qualifications, experience etc',
        verbose_name='Bio',
    )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('employee-detail', args=[str(self.id)])
