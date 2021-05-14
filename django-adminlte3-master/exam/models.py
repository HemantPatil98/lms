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

    class Meta:
        unique_together = (('name', 'type'),)

    def __str__(self):
        return self.name

class exam_attempts(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(course,on_delete=models.CASCADE)
    attempt = models.IntegerField()
    marks = models.IntegerField(blank=True)

    class Meta:
        unique_together = (('student', 'course','attempt'),)

    def __str__(self):
        return str(self.student)

class questions(models.Model):
    course = models.ForeignKey(course,on_delete=nothing)
    question = models.TextField()
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    file = models.FileField(upload_to='mcq_questions/')
    explanation = models.TextField(null=True)

    def __str__(self):
        return self.question
#
# class options(models.Model):
#     question = models.ForeignKey(questions,on_delete=models.CASCADE)
#     option = models.CharField(max_length=50)
#     status = models.BooleanField(default=False)
#     explanation = models.CharField(max_length=250)
#
#     def __str__(self):
#         return self.option

class program(models.Model):
    course = models.ForeignKey(course,on_delete=nothing)
    programe = models.CharField(max_length=250)
    file = models.FileField(upload_to='programs/')

    def __str__(self):
        return self.programe

class program_ans(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(course,on_delete=models.CASCADE)
    program = models.ForeignKey(program,on_delete=models.CASCADE)
    answer = models.TextField()
    attempt = models.IntegerField()

    class Meta:
        unique_together = (('student', 'course','program','attempt'),)