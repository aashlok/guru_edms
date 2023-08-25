import os
import shutil
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.views import generic

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required


from .models import DocumentType, Document, DocumentFile
from .forms import (DocumentTypeForm, NewDocumentForm, NewDocumentFileForm,
                    DocumentFileRevisionForm)
from company.models import Employee, Designation
from project.models import Project
# Create your views here.


@login_required
@staff_member_required
def documentTypes(request):
    """
Step 2
Adds Document type company uses for daily operations.
Shows list of added Document Type.
These are alloted to designations hence must be set before
designations.
"""
    doc_type_list = DocumentType.objects.all()

    if request.method == 'POST':
        form = DocumentTypeForm(request.POST)
        form.save()
        messages.info(request, 'New Document Type added')
        return HttpResponseRedirect(request.path_info)
    else:
        form = DocumentTypeForm()

    context = {'form': form, 'doc_type_list': doc_type_list}
    return render(request, 'document/document-types.html', context)


@login_required
def createDocument(request, pk):
    """
Only project manager or permitted employee can create document.
Creates new Meta Document record for given project.
Creates folder of document label name inside project folder.
Assigns employee who is expected to work on this document.
"""
    # permission check
    # extra project permission can be checked for further control
    perm = request.user.employee.designation.document_crud_permission
    if not perm:
        messages.info(request, 'You dont have Document Creation Permission')
        return redirect('index')

    form = NewDocumentForm()
    project = Project.objects.get(pk=pk)
    form.fields['document_user'].queryset = project.members.all()

    if request.method == 'POST':
        form = NewDocumentForm(request.POST)
        new_document = form.save(commit=False)
        # remove '-' from name because its used as delimiter
        new_document.label = request.POST.get('label').replace("-", "")
        new_document.project = project
        folder = os.path.join(project.project_folder, form.instance.label)
        os.mkdir(folder)
        new_document.save()
        messages.info(request, 'New document record is created.')
        return redirect('document:document-detail', pk=new_document.id)

    context = {'form': form}
    return render(request, 'document/create-document.html', context)


class DocumentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Document
    template_name = 'document/document-detail.html'


@login_required
def addDocumentFile(request, pk):
    """
Only permitted employee can add new file to project.
Adds actual working file to meta document record.
Generates actual file name using document label, 
project code, document type and revision number.
Copies file from uploader employee's workstation to project 
folder at central file server with new name.
Sets a new file flag.
"""
    # permission check
    perm = request.user.employee.designation.document_crud_permission
    if not perm:
        messages.info(request, 'You dont have Document Creation Permission')
        return redirect('index')

    form = NewDocumentFileForm()
    document = Document.objects.get(pk=pk)
    project = Project.objects.get(pk=document.project.id)
    employee = request.user.employee
    source_folder = os.path.join(employee.shared_folder, 'upload')
    source_files = os.listdir(source_folder)  # check errors
    form.local_files.choices = source_files

    if request.method == 'POST':
        form = NewDocumentFileForm(request.POST)
        new_doc_file = form.save(commit=False)
        new_doc_file.document = document
        selected_name = request.POST.get('local_file')
        file_extension = os.path.splitext(selected_name)[1]
        source_path = os.path.join(source_folder, selected_name)
        # project_code = project.short_code
        # type_code = document.document_type.short_code
        # doc_name = document.label
        new_file_name = (project.short_code + "-"
                         + document.document_type.short_code + "-"
                         + document.label + "-"
                         + "0-0" + file_extension)
        new_doc_file.filename = new_file_name
        new_doc_file.central_folder = os.path.join(project.project_folder,
                                                   document.label)
        destination_path = os.path.join(new_doc_file.central_folder,
                                        new_file_name)
        new_doc_file.status = 'n'
        shutil.copy(source_path, destination_path)  # check errors
        new_doc_file.save()
        messages.info(request, 'File is added to document record')
        return redirect('document:document-file-detail', pk=new_doc_file.id)

    context = {'form': form, 'source_files': source_files}
    return render(request, 'document/add-document-file.html', context)


class DocumentFileDetailView(LoginRequiredMixin, generic.DetailView):
    model = DocumentFile
    template_name = 'document/document-file-detail.html'


@login_required
def fetchDocumentFile(request, pk):
    """
Employee who is assigned to work on file fetches the same to his workstation.
No fetch form is required. Only confirmation page is shown.
Simple copy is made from File Server to employee workstation.
File flag is changed to working status.
"""
    employee = request.user.employee
    source_file = DocumentFile.objects.get(pk=pk)
    source_path = os.path.join(source_file.central_folder,
                               source_file.filename)
    fetch_folder = os.path.join(employee.shared_folder,
                                source_file.document.project.short_code,
                                source_file.document.label)
    fetch_path = os.path.join(fetch_folder, source_file.filename)
    source_file.fetch_folder = fetch_folder
    os.makedirs(os.path.dirname(fetch_folder), exist_ok=True)
    shutil.copy(source_path, fetch_path)
    source_file.status = 'p'
    source_file.access_date = datetime.now()
    source_file.save()
    messages.info(request, 'File is fetched to user workstation')
    return redirect('document:document-file-detail', pk=source_file.id)


def reviseDocumentFile(request, pk):
    """
Only employee who has worked on file can revise the same on completion.
Choice is given to replace or overwrite existing file and mark
as revision or version.
File name is modified with new revision number.
File is copied from employee workstation to central file server.
"""
    form = DocumentFileRevisionForm()

    context = {'form': form}
    return render(request, '', context)
