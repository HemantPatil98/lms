from django.db import models
from django.contrib.auth.models import User,Group
from datetime import datetime
from django.shortcuts import render,HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

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
        try:
            file = request.FILES['file']
            file._name=title+now.strftime("%m-%d-%Y, %H:%M:%S")+"."+file._name.split('.')[1]
        except:
            file = ''
        try:
            id = request.POST['id']
            note = notice.objects.all().get(id=id)
            note.title = title
            note.description = description
            note.type = type
            note.file = file if file != '' else None
            note.externallink = externallink
            note.save()
        except:
            note = notice(title=title,description=description,file=file,externallink=externallink,
                          createdby=request.user,type=type)
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
    student_performance_row = models.IntegerField(blank=True,null=True)
    student_profile_row = models.IntegerField(blank=True,null=True)
    otp = models.CharField(max_length=6)
    photo = models.FileField(upload_to='profile_photo/')
    certificate = models.ForeignKey(certificate_request,on_delete=nothing,blank=True,null=True)

    def __str__(self):
        return self.user_id.username

class extra_data(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class timeline(models.Model):
    generator = models.ForeignKey(User,on_delete=nothing)
    generatedtime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    body = models.TextField()

    def __str__(self):
        return self.title

    ###
    @login_required(login_url='')
    def viewtimeline(request):
        return render(request, 'student/timeline.html')

    ###
    @login_required(login_url='')
    def addtimeline(request):

        if request.method == "POST":
            ti = timeline(generator=request.user, title=request.POST['title'], type=request.POST['type'],
                          body=request.POST['body'])
            ti.save()
        return render(request, 'student/timeline.html')

    ###
    @login_required(login_url='')
    def deletetimeline(request):
        if request.method == "GET":
            id = request.GET['id']
            ti = timeline.objects.get(id=id)
            ti.delete()
        return render(request, 'student/timeline.html')

    ###
    @login_required(login_url='')
    def timelinedata(request):
        pre = int(request.GET['pre'])
        data = timeline.objects.all().order_by('-id')[pre:pre + 20]

        timel = []
        if len(data) > 0:
            for d in data:
                vars(d)['_state'] = 'none'
                vars(d)['name'] = User.objects.get(id=vars(d)['generator_id']).first_name
                now = datetime.now(timezone.utc)
                d.body = str(d.body).replace('"', '')
                vars(d)['date'] = d.generatedtime.strftime('%d %B %Y')
                if (now - d.generatedtime).days > 0:
                    time = str((now - d.generatedtime).days) + " days"
                else:
                    time = ((now - d.generatedtime).seconds // 60)
                    if time > 60:
                        time = str(time // 60) + " hr"
                    else:
                        time = str(time) + " min"
                vars(d)['time'] = time
                vars(d)['generatedtime'] = ""
                timel.append((vars(d)))

        else:
            timel = "-1"
        timel = str(timel).replace("'", '"')

        return HttpResponse(timel)


class groupsinfo(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    course = models.TextField(max_length=15)
    startdate = models.DateField()
    enddate = models.DateField()

    def __str__(self):
        return self.group.name