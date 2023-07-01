from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


from .models import DocumentType
from .forms import DocumentTypeForm
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
