from django.db import models
from django.urls import reverse


# Create your models here.


class DocumentType(models.Model):
    """
Common Document Types used by the company.
Document Types are alloted to designation to facilitate document
access depending on employee's designation.
Must be set before creating Designations.
"""
    short_code = models.CharField(
        max_length=4,
        help_text='Short code used in naming of the document',
        verbose_name='Code',
    )
    extension = models.CharField(
        max_length=20,
        help_text='Allowable file extension for document type, seperated by space',
        verbose_name='Extension',
    )
    label = models.CharField(
        max_length=50,
        help_text='Common Name of Document Type',
        verbose_name='Label',
    )

    def __str__(self):
        return self.label


class Document(models.Model):
    """
Basic project document,
Stores meta information, not file itself.
Includes its relative connections to file user employee, project,
Includes permanent information about document
"""
    project = models.ForeignKey(
        to='project.Project',
        on_delete=models.CASCADE,
        help_text='Parent Project',
        verbose_name='Parent Project',
    )
    document_user = models.ForeignKey(
        to='company.Employee',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text='Employee to whom document is allotted',
        verbose_name='User',
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.CASCADE,
        help_text='Document Type according to classification scheme',
        verbose_name='Type',
    )
    label = models.CharField(
        max_length=50,
        help_text=('Simple name of Document Folder at creation. '
                   'NOT name of actual file'),
        verbose_name='Label',
    )
    created_date = models.DateTimeField(
        auto_now=True,
        help_text='Date of adding document to project',
        verbose_name='Created',
    )
    active = models.BooleanField(
        default=True,
        help_text='Status flag whether document be available for modification',
        verbose_name='Active',
    )
    save_count = models.IntegerField(
        default=0,
        help_text='Total number of modifications document undergone',
        verbose_name='Save Count',
    )
    information = models.TextField(
        max_length=500,
        null=True, blank=True,
        help_text='Basic information about document',
        verbose_name='Information',
    )

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('', args=[str(self.id)])


class DocumentFile(models.Model):
    """
Document file instances,
Single document has multiple files,
Includes its revision information and comments
includes changing information about document file instances
"""
    document = models.ForeignKey(
        Document,
        on_delete=models.RESTRICT,
        help_text='Parent Document',
        verbose_name='Parent Document',
    )
    filename = models.CharField(
        max_length=50,
        help_text=('Actual filename to be stored after renamed according to'
                   'predecided scheme of file labelling'),
        verbose_name='FileName',
    )
    central_folder = models.CharField(
        max_length=200,
        null=True, blank=True,
        help_text='Project folder location at central file server',
        verbose_name='Central Folder',
    )
    fetch_folder = models.CharField(
        max_length=200,
        null=True, blank=True,
        help_text='Project folder location at employee workstation for use',
        verbose_name='Fetch Folder',
    )
    access_date = models.DateTimeField(
        null=True, blank=True,
        help_text='DateTime when file is fetched by user employee',
        verbose_name='Accessed',
    )
    modified_date = models.DateTimeField(
        null=True, blank=True,
        help_text='DateTime when file is reuploaded to server after modification',
        verbose_name='Modified',
    )
    due_date = models.DateTimeField(
        null=True, blank=True,
        help_text='DateTime set by manager to finish given task on file',
        verbose_name='Due',
    )
    FILE_STATUS = (
        ('n', 'New'),
        ('i', 'Issued'),
        ('p', 'In Progress'),
        ('r', 'Revised'),
        ('a', 'Approved'),
        ('f', 'Final'),
        ('z', 'Frozen')
    )
    status = models.CharField(
        max_length=1,
        choices=FILE_STATUS,
        help_text=('File status set at every movement of file'
                   'Causes file to show up at various dashboards'),
        verbose_name='Status',
    )
    version = models.IntegerField(
        default=0,
        help_text=('Major modification to file saved as reference point'
                   'Always saved to central store'),
        verbose_name='Version',
    )
    revision = models.IntegerField(
        default=0,
        help_text=('Minor modification to file on day to day basis,'
                   'Earlier file overwrite or new copy depending on'
                   'users choice depending on scale of modification'
                   ),
        verbose_name='Revision',
    )
    task_comment = models.TextField(
        max_length=200,
        null=True, blank=True,
        help_text=('Instruction given by manager to employee'
                   'at time of issuing file for modification'),
        verbose_name='Task',
    )
    revision_comment = models.TextField(
        max_length=200,
        null=True, blank=True,
        help_text=('Information given by employee to manager'
                   'after completion of given task and file upload'),
        verbose_name='Comment',
    )
    is_stub = models.BooleanField(
        default=True,
        help_text=('when database entry exists but file operation is failed'
                   'or file does not physically exist'),
        verbose_name='Stub',
    )

    def __str__(self):
        return self.filename

    def get_absolute_url(self):
        return reverse('', args=[str(self.id)])
