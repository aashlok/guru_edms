import os

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Company, Designation, Employee
from .forms import CompanySetupForm

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
    form = CompanySetupForm()

    if request.method == 'POST':
        form = CompanySetupForm(request.POST)
        newcompany = form.save(commit=False)
        short_code = request.POST.get('short_code')
        fileserver_folder = (request.POST.get('fileserver_folder')
                             + '.' + short_code)
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:  # TO-DO: use proper validation
            password = password1
        else:
            return HttpResponse('Passwords do not match')

        newuser = User.objects.create(
            username='admin' + '.' + short_code,
            password=password,
            is_staff=True,
        )

        os.makedirs(fileserver_folder, exist_ok=True)  # TO-DO: try
        newuser.save()
        newcompany.save()
        return redirect('configuration')

    else:
        form = CompanySetupForm()
        # return HttpResponse('Error occured in initial setup')

    context = {'form': form}
    return render(request, 'company/initial-setup.html', context=context)


def configuration(request):
    context = {}
    return render(request, 'company/configuration.html', context=context)


@login_required
def index(request):

    context = {}
    return render(request, 'index.html', context=context)
