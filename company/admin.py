from django.contrib import admin

from .models import Company, Designation, Employee

# Register your models here.
admin.site.register(Company)
admin.site.register(Designation)
admin.site.register(Employee)
