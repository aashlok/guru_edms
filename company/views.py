import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q


from .models import Company, Designation, Employee
from .forms import (CompanySetupForm, DesignationForm, NewUserForm,
                    NewEmployeeForm)
from document.models import DocumentType, Document, DocumentFile
from project.models import Project


# Create your views here.


def initialSetup(request):
    """
Step 1
View sets up company for the first time.
Create new local admin, not same as django superuser.
Only admin.company can add Designations, DocumentType and Employees
Username is auto generated so no UserCreationForm.
Only set password from input.
Creates specified folder as central file server.
"""
    count = Company.objects.all().count()
    if count == 1:
        messages.info(request, 'Company is already set up, please login')
        return redirect('login')

    if request.method == 'POST':
        form = CompanySetupForm(request.POST)
        newcompany = form.save(commit=False)
        short_code = request.POST.get('short_code')
        fileserver_folder = (request.POST.get('fileserver_folder')
                             + '/' + short_code)
        newcompany.fileserver_folder = fileserver_folder
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:  # TO-DO: use proper validation
            password = password1
        else:
            return HttpResponse('Passwords do not match')

        newuser = User.objects.create(
            first_name='admin',
            last_name=short_code,
            username='admin' + '.' + short_code,
            is_staff=True,
        )

        os.makedirs(fileserver_folder, exist_ok=True)  # TO-DO: try
        newuser.set_password(password)
        newuser.save()
        newcompany.save()
        return redirect('login')

    else:
        form = CompanySetupForm()

    context = {'form': form}
    return render(request, 'company/initial-setup.html', context=context)


@login_required
@staff_member_required
def configuration(request):
    """
View and add basic configuration before commencing usage.
From this page only employees, designations and document types 
can be added or edited.
Shows summary of configuration.
"""
    num_employees = Employee.objects.all().count()
    num_designations = Designation.objects.all().count()
    num_doc_types = DocumentType.objects.all().count()

    context = {
        'num_employees': num_employees,
        'num_designations': num_designations,
        'num_doc_types': num_doc_types
    }
    return render(request, 'company/configuration.html', context=context)


@login_required
@staff_member_required
def designations(request):
    """
Step 3
Adds designation and shows list
Most Designations must be set before adding employees
because designations are essential for access control
Every designation is attached to type of document given
designation can access.
"""
    designation_list = Designation.objects.all()

    if request.method == 'POST':
        form = DesignationForm(request.POST)
        form.save()
        messages.info(request, 'New Designation added successfully')
        return HttpResponseRedirect(request.path_info)
    else:
        form = DesignationForm()

    context = {'form': form, 'designation_list': designation_list}
    return render(request, 'company/designations.html', context)


@login_required
@staff_member_required
def addEmployee(request):
    """
Step 5
Adds django inbuilt User and custom employee in the same page.
Employee primarily holds designation and shared folder info.
Creates employee folder to store local files.
If employee has document crud permission create upload folder.
"""
    if request.method == 'POST':
        user_form = NewUserForm(request.POST)
        employee_form = NewEmployeeForm(request.POST)
        if user_form.is_valid():
            newuser = user_form.save(commit=False)
            newuser.username = (newuser.first_name.lower()
                                + '.' + newuser.last_name.lower())
            newuser.save()
            newemployee = employee_form.save(commit=False)
            newemployee.user = newuser
            newemployee.shared_folder = os.path.join(
                newemployee.shared_folder, (newuser.first_name
                                            + '-' + newuser.last_name)
            )
            os.mkdir(newemployee.shared_folder)  # check errors
            if employee_form.instance.designation.document_crud_permission:
                os.mkdir(os.path.join(newemployee.shared_folder, 'upload'))
            newemployee.save()
            return redirect('company:employees')
    else:
        user_form = NewUserForm()
        employee_form = NewEmployeeForm()

    context = {'user_form': user_form, 'employee_form': employee_form}
    return render(request, 'company/add-employee.html', context)


# @staff_member_required
class EmployeeListView(LoginRequiredMixin, generic.ListView):
    model = Employee
    template_name = 'company/employees.html'


@login_required
def index(request):
    if request.user.is_staff:
        return redirect('company:configuration')

    employee = request.user.employee
    projects = Project.objects.filter(members__id=employee.id)
    issued_files = DocumentFile.objects.filter(
        Q(status='n') | Q(status='i'), document__document_user=employee
    )
    working_files = DocumentFile.objects.filter(
        document__document_user=employee, status='p'
    )

    context = {'projects': projects,
               'issued_files': issued_files,
               'working_files': working_files}
    return render(request, 'index.html', context=context)
