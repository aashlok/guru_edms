import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from .models import DocumentType, Document, DocumentFile
from .forms import (DocumentTypeForm, NewDocumentForm, NewDocumentFileForm,
                    DocumentFileRevisionForm)
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
    form = NewDocumentForm()
    # permission check

    context = {'form': form}
    return render(request, '', context)


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
    form = NewDocumentFileForm()
    # permission check

    context = {'form': form}
    return render(request, '', context)


@login_required
def fetchDocumentFile(request, pk):
    """
Employee who is assigned to work on file fetches the same to his workstation.
No fetch form is required. Only confirmation page is shown.
Simple copy is made from File Server to employee workstation.
File flag is changed to working status.
"""
    return redirect('')


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
