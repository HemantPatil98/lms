from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
def nothing():
    pass
class notice(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    generateddate = models.DateTimeField(default=datetime.now)
    file = models.FileField(upload_to="notice/")
    externallink = models.CharField(max_length=100)
    createdby = models.ForeignKey(User,on_delete=nothing)
    type = models.CharField(max_length=12,choices=(('Notice','Notice'),('Placement','placement')),default='Notice')

    def __str__(self):
        return self.title

    def addnoticein(request):
        title = request.POST['subject']
        description = request.POST['description']
        externallink = request.POST['externallink']
        type = request.POST['type']
        now = datetime.now()
        # print(vars(file))
        try:
            file = request.FILES['file']
            file._name=title+now.strftime("%m-%d-%Y, %H:%M:%S")+"."+file._name.split('.')[1]
        except:
            file = ''
        # print(file._name)
        if request.POST['id']:
            id = request.POST['id']
            note = notice.objects.all().get(id=id)
            note.title = title
            note.description = description
            note.type = type
            note.file = file if file is not '' else None
            note.externallink = externallink
            note.save()
        else:
            note = notice(title=title,description=description,file=file,externallink=externallink,createdby=request.user,type=type)
            note.save()

class certificate_request(models.Model):
    student_id = models.ForeignKey(User,on_delete=nothing)
    certificate_number = models.CharField(max_length=10)
    certificate = models.FileField(upload_to='certificate/')
    certificate_status = models.CharField(max_length=10,default="In Process")

    def __str__(self):
        return self.student_id.first_name

class user_profile(models.Model):
    user_id = models.OneToOneField(User,on_delete=nothing)
    student_performance_row = models.IntegerField(null=True)
    otp = models.CharField(max_length=6)
    photo = models.FileField(upload_to='profile_photo/')
    certificate = models.ForeignKey(certificate_request,on_delete=nothing,null=True)

    def __str__(self):
        return self.user_id.username


class extra_data(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name