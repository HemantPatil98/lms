from django.db import models
from django.contrib.auth.admin import User
# Create your models here.
def nothing():
    pass

class course(models.Model):
    name = models.CharField(max_length=15)
    instructions = models.TextField(null=True)
    type = models.CharField(max_length=15)
    time = models.IntegerField(default=30)

    def __str__(self):
        return self.name

class exam_attempts(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(course,on_delete=models.CASCADE)
    attempt = models.IntegerField()
    marks = models.IntegerField()

    def __str__(self):
        return self.attempt

class questions(models.Model):
    course = models.ForeignKey(course,on_delete=nothing)
    question = models.CharField(max_length=50)
    file = models.FileField(upload_to='mcq_questions/')
    explanation = models.TextField(null=True)

    def __str__(self):
        return self.question

class options(models.Model):
    question = models.ForeignKey(questions,on_delete=models.CASCADE)
    option = models.CharField(max_length=50)
    status = models.BooleanField(default=False)
    explanation = models.CharField(max_length=250)

    def __str__(self):
        return self.option

class program(models.Model):
    course = models.ForeignKey(course,on_delete=nothing)
    programe = models.CharField(max_length=250)
    file = models.FileField(upload_to='programs/')

    def __str__(self):
        return self.programe
