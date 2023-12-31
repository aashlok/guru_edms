# Generated by Django 4.2.2 on 2023-06-25 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(help_text=('Simple name of Document set at creation', 'NOT name of actual file'), max_length=50, verbose_name='Label')),
                ('created_date', models.DateTimeField(auto_now=True, help_text='Date of adding document to project', verbose_name='Created')),
                ('active', models.BooleanField(default=True, help_text='Status flag whether document be available for modification', verbose_name='Active')),
                ('save_count', models.IntegerField(default=0, help_text='Total number of modifications document undergone', verbose_name='Save Count')),
                ('information', models.TextField(blank=True, help_text='Basic information about document', max_length=500, null=True, verbose_name='Information')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_code', models.CharField(help_text='Short code used in naming of the document', max_length=4, verbose_name='Code')),
                ('extension', models.CharField(help_text='Allowable file extension for document type, seperated by space', max_length=20, verbose_name='Extension')),
                ('label', models.CharField(help_text='Common Name of Document Type', max_length=50, verbose_name='Label')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(help_text='Actual filename to be stored after renamed according topredecided scheme of file labelling', max_length=50, verbose_name='FileName')),
                ('central_folder', models.CharField(blank=True, help_text='Project folder location at central file server', max_length=200, null=True, verbose_name='Central Folder')),
                ('fetch_folder', models.CharField(blank=True, help_text='Project folder location at employee workstation for use', max_length=200, null=True, verbose_name='Fetch Folder')),
                ('access_date', models.DateTimeField(blank=True, help_text='DateTime when file is fetched by user employee', null=True, verbose_name='Accessed')),
                ('modified_date', models.DateTimeField(blank=True, help_text='DateTime when file is reuploaded to server after modification', null=True, verbose_name='Modified')),
                ('due_date', models.DateTimeField(blank=True, help_text='DateTime set by manager to finish given task on file', null=True, verbose_name='Due')),
                ('status', models.CharField(choices=[('n', 'New'), ('i', 'Issued'), ('p', 'In Progress'), ('r', 'Revised'), ('a', 'Approved'), ('f', 'Final'), ('z', 'Frozen')], help_text='File status set at every movement of fileCauses file to show up at various dashboards', max_length=1, verbose_name='Status')),
                ('version', models.IntegerField(default=0, help_text='Major modification to file saved as reference pointAlways saved to central store', verbose_name='Version')),
                ('revision', models.IntegerField(default=0, help_text='Minor modification to file on day to day basis,Earlier file overwrite or new copy depending onusers choice depending on scale of modification', verbose_name='Revision')),
                ('task_comment', models.TextField(blank=True, help_text='Instruction given by manager to employeeat time of issuing file for modification', max_length=200, null=True, verbose_name='Task')),
                ('revision_comment', models.TextField(blank=True, help_text='Information given by employee to managerafter completion of given task and file upload', max_length=200, null=True, verbose_name='Comment')),
                ('is_stub', models.BooleanField(default=True, help_text='when database entry exists but file operation is failedor file does not physically exist', verbose_name='Stub')),
                ('document', models.ForeignKey(help_text='Parent Document', on_delete=django.db.models.deletion.RESTRICT, to='document.document', verbose_name='Parent Document')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.ForeignKey(help_text='Document Type according to classification scheme', on_delete=django.db.models.deletion.CASCADE, to='document.documenttype', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='document',
            name='document_user',
            field=models.ForeignKey(blank=True, help_text='Employee to whom document is allotted', null=True, on_delete=django.db.models.deletion.SET_NULL, to='company.employee', verbose_name='User'),
        ),
        migrations.AddField(
            model_name='document',
            name='project',
            field=models.ForeignKey(help_text='Parent Project', on_delete=django.db.models.deletion.CASCADE, to='project.project', verbose_name='Parent Project'),
        ),
    ]
