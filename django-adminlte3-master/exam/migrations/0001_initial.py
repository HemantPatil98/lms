# Generated by Django 3.1.7 on 2021-06-04 04:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import exam.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
                ('instructions', models.TextField(null=True)),
                ('type', models.CharField(max_length=15)),
                ('time', models.IntegerField(default=30)),
                ('attempts_allowed', models.IntegerField(default=2)),
            ],
            options={
                'unique_together': {('name', 'type')},
            },
        ),
        migrations.CreateModel(
            name='program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programe', models.CharField(max_length=250)),
                ('file', models.FileField(upload_to='programs/')),
                ('course', models.ForeignKey(on_delete=exam.models.nothing, to='exam.course')),
            ],
        ),
        migrations.CreateModel(
            name='questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('option1', models.CharField(max_length=100)),
                ('option2', models.CharField(max_length=100)),
                ('option3', models.CharField(max_length=100)),
                ('option4', models.CharField(max_length=100)),
                ('answer', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='mcq_questions/')),
                ('explanation', models.TextField(null=True)),
                ('course', models.ForeignKey(on_delete=exam.models.nothing, to='exam.course')),
            ],
        ),
        migrations.CreateModel(
            name='program_file',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='programs/')),
                ('attempt', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.course')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.program')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'course', 'attempt')},
            },
        ),
        migrations.CreateModel(
            name='program_ans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('attempt', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.course')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.program')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'course', 'program', 'attempt')},
            },
        ),
        migrations.CreateModel(
            name='exam_attempts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt', models.IntegerField()),
                ('marks', models.IntegerField(null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'course', 'attempt')},
            },
        ),
    ]
