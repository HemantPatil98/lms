# Generated by Django 3.1.7 on 2021-05-07 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_auto_20210507_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam_attempts',
            name='marks',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
