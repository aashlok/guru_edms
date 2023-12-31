import os
import shutil
import re
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect  # HttpResponse,
from django.contrib import messages
from django.views import generic

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required

# from company.models import Employee, Designation
from project.models import Project
# from company.models import Employee, Designation
from .models import DocumentType, Document, DocumentFile
from .forms import (DocumentTypeForm, NewDocumentForm, NewDocumentFileForm,
                    DocumentFileRevisionForm, DocumentBrowserForm,
                    DocumentFileAllotForm)


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
        return redirect('company:index')

    form = NewDocumentForm()
    project = Project.objects.get(pk=pk)
    form.fields['document_user'].queryset = project.members.all()

    if request.method == 'POST':
        form = NewDocumentForm(request.POST)
        new_document = form.save(commit=False)
        # remove all special characters
        new_document.label = re.sub('[^a-zA-Z0-9]', '',
                                    request.POST.get('label'))
        new_document.project = project
        folder = os.path.join(project.project_folder, new_document.label)
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
        return redirect('company:index')

    form = NewDocumentFileForm()
    document = Document.objects.get(pk=pk)
    doc_label = document.label
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
        new_doc_file.is_stub = False
        new_doc_file.save()
        messages.info(request, 'File is added to document record')
        return redirect('document:document-file-detail', pk=new_doc_file.id)

    context = {'form': form, 'source_files': source_files,
               'doc_label': doc_label}
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
    source_file.access_date = datetime.now()
    source_file.status = 'p'
    os.makedirs(fetch_folder, exist_ok=True)
    shutil.copy(source_path, fetch_path)  # overwrite protection!
    source_file.save()
    messages.info(request, 'File is fetched to user workstation')
    return redirect('document:document-file-detail', pk=source_file.id)


@login_required
def reviseDocumentFile(request, pk):
    """
Only employee who has worked on file can revise the same on completion.
Choice is given to replace or overwrite existing file and mark
as revision or version.
File name is modified with new revision number.
File is copied from employee workstation to central file server.
"""
    employee = request.user.employee
    old_doc_file = DocumentFile.objects.get(pk=pk)

    # permission check
    if old_doc_file.document.document_user != employee:
        messages.info(request, 'This file is not alloted to you.')
        return redirect('company:index')

    form = DocumentFileRevisionForm()

    if request.method == 'POST':
        form = DocumentFileRevisionForm(request.POST)
        revision_note = request.POST.get('revision_note')
        new_doc_file = DocumentFile(
            document=old_doc_file.document,
            filename=revision_rename(old_doc_file.filename),
            central_folder=old_doc_file.central_folder,
            fetch_folder=old_doc_file.fetch_folder,
            status='r',
            version=old_doc_file.version,
            revision=old_doc_file.revision + 1,
            is_stub=False
        )
        old_doc_file.status = 'z'
        old_doc_file.modified_date = datetime.now()
        new_doc_file.revision_comment = revision_note
        # copy-create new file at workstation
#        shutil.copy(os.path.join
#                    (old_doc_file.fetch_folder, old_doc_file.filename),
#                    os.path.join
#                    (old_doc_file.fetch_folder, new_doc_file.filename))
        # rename instead of copy to avoid redundant file
        os.rename(os.path.join
                  (old_doc_file.fetch_folder, old_doc_file.filename),
                  os.path.join
                  (old_doc_file.fetch_folder, new_doc_file.filename))
        old_doc_file.is_stub = True
        # copy new file to file server
        shutil.copy(os.path.join
                    (new_doc_file.fetch_folder, new_doc_file.filename),
                    os.path.join
                    (new_doc_file.central_folder, new_doc_file.filename))

        old_doc_file.save()
        new_doc_file.save()
        document = Document.objects.get(id=old_doc_file.document.id)
        document.save_count = document.save_count + 1
        document.save()
        messages.info(request, 'File is revised and uploaded to server')
        return redirect('document:document-file-detail', pk=new_doc_file.id)

    context = {'form': form}
    return render(request, 'document/revise-document-file.html', context)


def revision_rename(filename):
    """
Helper function to increment revision number of file after revision.
"""
    basename = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    splitted = basename.split('-')
    ln = len(splitted)
    revision = splitted[ln-1]
    new_revision = int(revision) + 1
    splitted[ln-1] = str(new_revision)
    new_name = '-'.join(splitted)
    at_last = new_name + extension
    return at_last


@login_required
def approveDocumentFile(request, pk):
    """
Only revised document file can be approved with project level permission
Function does not need page of its own.
"""
    perm = request.user.employee.designation.project_crud_permission
    if not perm:
        messages.info(request, 'You dont have Document Approval Permission')
        return redirect('company:index')

    source_file = DocumentFile.objects.get(pk=pk)
    source_file.status = 'a'
    source_file.save()
    messages.info(request, 'File is Approved')
    return redirect('document:document-file-detail', pk=source_file.id)


@login_required
def allotDocumentFile(request, pk):
    """
Revised or approved file can be allotted for more work 
with project level permission
"""
    perm = request.user.employee.designation.project_crud_permission
    if not perm:
        messages.info(request, 'You dont have Document Allottment Permission')
        return redirect('company:index')

    form = DocumentFileAllotForm()
    source_file = DocumentFile.objects.get(pk=pk)
    file_name = source_file.filename

    if request.method == 'POST':
        form = DocumentFileAllotForm(request.POST)
        source_file.status = 'i'
        source_file.due_date = request.POST.get('due_date')
        # source_file.due_date = datetime.combine(request.POST.get('due_date'),
        # datetime.min.time())
        source_file.task_comment = request.POST.get('task_note')
        source_file.save()
        messages.info(request, 'File is Allotted to employee')
        return redirect('document:document-file-detail', pk=source_file.id)

    context = {'form': form, 'file_name': file_name}
    return render(request, 'document/allot-document-file.html', context)


@login_required
def documentBrowser(request):
    """
Generic document browser with various filters
Filters: Project, document type, status, due date etc.
"""
    employee = request.user.employee
    doc_list = []
    doc_file_list = []
    project_list = Project.objects.filter(members__id=employee.id)
    doc_type_list = employee.designation.document_type_permission.all()
    form = DocumentBrowserForm()
    form.fields['project'].queryset = project_list
    form.fields['doc_type'].queryset = doc_type_list

    if request.method == 'POST':
        form = DocumentBrowserForm(request.POST)
        form.fields['project'].queryset = project_list
        form.fields['doc_type'].queryset = doc_type_list
        project = request.POST.get('project')
        doc_type = request.POST.get('doc_type')
        doc_list = Document.objects.filter(project=project,
                                           document_user=employee,
                                           document_type=doc_type)
        for doc in doc_list:
            last_file = doc.documentfile_set.last()
            doc_last_file = {}  # dictionary for key value access in template
            doc_last_file['id'] = doc.id
            doc_last_file['name'] = doc.label
            doc_last_file['user'] = doc.document_user
            doc_last_file['save'] = doc.save_count
            doc_last_file['file_id'] = last_file.id
            doc_last_file['last_file_name'] = last_file.filename
            doc_last_file['last_file_created'] = last_file.created_date.date()
            if last_file.due_date:
                doc_last_file['last_file_due'] = last_file.due_date.date()
            else:
                doc_last_file['last_file_due'] = 'N.A.'
            doc_last_file['last_file_status'] = last_file.get_status_display
            doc_file_list.append(doc_last_file)

    context = {'form': form, 'doc_file_list': doc_file_list}
    return render(request, 'document/document-browser.html', context)
