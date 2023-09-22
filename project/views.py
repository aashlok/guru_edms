import os

from django.shortcuts import render, redirect
# from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.contrib.auth.models import User

from company.models import Employee, Company
from document.models import Document, DocumentFile
from .models import Project
from .forms import NewProjectForm


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_doc_list = []  # document only list
        doc_file_list = []  # document with last file activity composite list

        if self.request.user.employee.designation.project_crud_permission:
            user_doc_list = self.object.document_set.all()
        else:
            user_doc_list = self.object.document_set.filter(
                document_user=self.request.user.employee.id)

        for doc in user_doc_list:
            last_file = doc.documentfile_set.last()
            doc_last_file = {}  # dictionary for key value access in template
            doc_last_file['id'] = doc.id
            doc_last_file['name'] = doc.label
            doc_last_file['user'] = doc.document_user
            doc_last_file['save'] = doc.save_count
            doc_last_file['file_id'] = last_file.id
            doc_last_file['last_file_name'] = last_file.filename
            doc_last_file['last_file_created'] = last_file.created_date.date()
            doc_last_file['last_file_due'] = last_file.due_date.date()
            doc_last_file['last_file_status'] = last_file.get_status_display
            doc_file_list.append(doc_last_file)

        context['doc_file_list'] = doc_file_list
        return context
