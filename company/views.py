import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from document.models import DocumentType
from .models import Company, Designation, Employee
from .forms import CompanySetupForm, DesignationForm
# from project.models import Project


# Create your views here.


def initialSetup(request):
    """
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
def index(request):
    if request.user.is_staff:
        return redirect('company:configuration')

    context = {}
    return render(request, 'index.html', context=context)
