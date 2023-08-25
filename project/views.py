import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User

from .models import Project
from .forms import NewProjectForm
from company.models import Employee, Company

# Create your views here.


@login_required
def createProject(request):
    """
New project can only be created by employee who has such permission.
Creates project directory in file server as specified in company setup
"""
    # check permissions
    perm = request.user.employee.designation.project_crud_permission
    if not perm:
        messages.info(request, 'You dont have Project Creation Permission')
        return redirect('company:index')

    form = NewProjectForm()
    # exclude project creator employees from member list
    # to avoid unncessary entries
    form.fields['members'].queryset = Employee.objects.exclude(
        designation__project_crud_permission=True)

    if request.method == 'POST':
        form = NewProjectForm(request.POST)
        new_project = form.save(commit=False)
        manager = Employee.objects.get(id=request.user.employee.id)
        new_project.manager = manager
        filestore = Company.objects.all()[0].fileserver_folder
        folder = os.path.join(filestore, form.instance.short_code)
        new_project.project_folder = folder
        os.mkdir(folder)
        new_project.save()
        form.save_m2m()
        new_project.members.add(manager)
        new_project.save()
        messages.info(request, 'New Project is created')
        return redirect('project:project-detail', pk=new_project.id)

    context = {'form': form}
    return render(request, 'project/add-project.html', context)


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = 'project/project-list.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        return Project.objects.filter(members__id=self.request.user.employee.id)


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    template_name = 'project/project-detail.html'
