# Generated by Django 3.1.7 on 2021-06-09 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='questions_count',
            field=models.IntegerField(default=2),
        ),
    ]
