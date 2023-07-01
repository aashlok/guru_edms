from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Company, Employee, Designation


class CompanySetupForm(ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(),
        label='Password for admin.company',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(),
        label='Retype Password',
    )

    class Meta:
        model = Company
        fields = ['name', 'short_code', 'fileserver_folder']


class DesignationForm(ModelForm):
    class Meta:
        model = Designation
        fields = ['title', 'document_type_permission',
                  'employee_crud_permission',
                  'project_crud_permission',
                  'document_crud_permission']


class NewUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password1', 'password2']


class NewEmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['designation', 'shared_folder']
