# Generated by Django 3.1.7 on 2021-04-23 05:01

from django.conf import settings
from django.db import migrations, models
import lms.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lms', '0002_auto_20210415_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='createdby',
            field=models.ForeignKey(default=1, on_delete=lms.models.nothing, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notice',
            name='type',
            field=models.CharField(choices=[('Notice', 'Notice'), ('Placement', 'placement')], default=1, max_length=12),
            preserve_default=False,
        ),
    ]
