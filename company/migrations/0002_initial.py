# Generated by Django 4.2.2 on 2023-06-25 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('document', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='designation',
            name='document_type_permission',
            field=models.ManyToManyField(help_text='Document Types allowed to this designation', related_name='allowed', to='document.documenttype', verbose_name='Permitted Types'),
        ),
    ]
