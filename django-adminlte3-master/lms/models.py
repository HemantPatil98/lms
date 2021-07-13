from django.db import models
from django.contrib.auth.models import User,Group
from datetime import datetime
from django.shortcuts import render,HttpResponse,redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core import serializers
# Create your models here.


class notice(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    generateddate = models.DateTimeField()
    file = models.FileField(upload_to="notice/")
    externallink = models.CharField(max_length=100)
    createdby = models.ForeignKey(User,on_delete=models.CASCADE)
    type = models.CharField(max_length=12,choices=(('Notice','Notice'),('Placement','placement')),default='Notice')

    def __str__(self):
        return self.title

    @login_required(login_url='')
    def addnotice(request,view=False):
        if request.method == 'POST':
            title = request.POST['subject']
            description = request.POST['description']
            externallink = request.POST['externallink']
            type = request.POST['type']
            now = datetime.now()
            try:
                file = request.FILES['file']
                file._name = title + now.strftime("%m-%d-%Y, %H:%M:%S") + "." + file._name.split('.')[1]
            except:
                file = ''
            if 'id' in request.POST:
                id = request.POST['id']
                note = notice.objects.filter(id=id)
                note.update(title=title, description=description, externallink=externallink,file=file,
                            createdby=request.user, type=type)
            else:
                note = notice(title=title, description=description, file=file, externallink=externallink,
                              createdby=request.user, type=type,generateddate=datetime.now())
                note.save()
        if request.user.is_staff:
            if view:
                data = notice.objects.all().order_by('-id').filter(createdby=request.user)
            else:
                data = notice.objects.all().order_by('-id')
        else:
            data = notice.objects.all().order_by('-id')
        try:
            pageno = request.GET['page']
        except:
            pageno = 1

        count = 11 if request.user.is_staff else 12
        P = Paginator(data,count)

        page = P.page(pageno)

        up = user_profile.objects.all().filter(user_id=request.user.id)[0]


        return render(request, 'student/add_notice.html', {'data': page, 'up': up})

    def getnotice(request):
        notices = notice.objects.filter(generateddate__gte=request.user.date_joined).order_by('-id')
        us_profile = user_profile.objects.get(user_id=request.user)
        pageno = request.GET['pageno']
        try:
            pageno = int(request.GET['pageno'])
        except:
            pageno = 1

        P = Paginator(notices,10)

        page = P.page(pageno) if pageno <= P.num_pages else []

        if not us_profile.last_notice and len(notices):
            us_profile.last_notice = notices[0].id

        if len(notices):
            if us_profile.last_notice < notices[0].id:
                new_notices = []
                for i in notices.filter(id__gt= us_profile.last_notice):
                    new_notices.append(i.id)
                unread_notices = us_profile.unread_notices.replace('[', '').replace(']', '')
                unread_notices = unread_notices.split(', ')
                if unread_notices != ['']:
                    unread_notices = [int(x) for x in unread_notices]
                    us_profile.unread_notices = unread_notices + new_notices
                else:
                    us_profile.unread_notices = new_notices

                us_profile.last_notice = notices[0].id

        notices = serializers.serialize('json',list(page),fields=('title', 'description','generateddate','file','externallink'))

        if us_profile.unread_notices == '':
            us_profile.unread_notices = []

        us_profile.save()

        return HttpResponse(notices+";"+str(us_profile.unread_notices))

    def markreadnotice(request):
        us_profile = user_profile.objects.get(user_id=request.user.id)
        unread_notices = us_profile.unread_notices.replace('[','').replace(']','')
        unread_notices = unread_notices.split(', ') #request.session['unread_notices']
        unread_notices = [int(x) for x in unread_notices if x != '']

        id = int(request.GET['id'])
        if id in unread_notices:
            unread_notices.remove(id)
        us_profile.unread_notices= unread_notices

        us_profile.save()

        return redirect('index')

    def readallnotice(request):
        us_profile = user_profile.objects.get(user_id=request.user.id)
        us_profile.unread_notices = []
        us_profile.save()
        messages.info(request,"All Notices Read")
        return redirect('index')

class certificate_request(models.Model):
    student_id = models.ForeignKey(User,on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=10)
    certificate = models.FileField(upload_to='certificate/')
    certificate_status = models.CharField(max_length=10,default="In Process")

    def __str__(self):
        return self.student_id.first_name

class user_profile(models.Model):
    user_id = models.OneToOneField(User,on_delete=models.CASCADE)
    student_performance_row = models.IntegerField(blank=True,null=True)
    student_profile_row = models.IntegerField(blank=True,null=True)
    otp = models.CharField(max_length=6)
    photo = models.FileField(upload_to='profile_photo/',blank=True,null=True)
    certificate = models.ForeignKey(certificate_request,on_delete=models.CASCADE,blank=True,null=True)
    unread_notices = models.TextField(blank=True,null=True)
    last_notice = models.IntegerField(blank=True,null=True)
    declaration = models.DateField(null=True,blank=True)

    def __str__(self):
        return self.user_id.username

class extra_data(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class timeline(models.Model):
    generator = models.ForeignKey(User,on_delete=models.CASCADE)
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
        # for i in range(0,len(data)-1):
        #     vars(data[i])["generator"] = data[i].generator.username
        # print(data)
        timel = []
        if len(data) > 0:
            for d in data:
                vars(d)['_state'] = 'none'
                vars(d)['name'] = User.objects.get(id=vars(d)['generator_id']).first_name
                now = datetime.now(timezone.utc)
                vars(d)['body'] = str(d.body).replace('"',"`")
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
        timel = str(timel).replace("'", '"').replace("`","'")

        # abc = serializers.serialize('json',list(timel),fields=('title', 'body','type','generator','generatedtime'))



        # print(abc)
        return HttpResponse(timel)

class groupsinfo(models.Model):
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    course = models.TextField(max_length=15)
    startdate = models.DateField()
    enddate = models.DateField()

    def __str__(self):
        return self.group.name