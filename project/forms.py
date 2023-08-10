from django.forms import ModelForm

from .models import Project


class NewProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'short_code', 'members']
