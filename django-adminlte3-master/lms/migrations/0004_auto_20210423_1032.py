# Generated by Django 3.1.7 on 2021-04-23 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0003_auto_20210423_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='type',
            field=models.CharField(choices=[('Notice', 'Notice'), ('Placement', 'placement')], default='Notice', max_length=12),
        ),
    ]
