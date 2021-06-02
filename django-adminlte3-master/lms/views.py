from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from . import sheetsapi
from datetime import datetime
from django.contrib.auth.models import User,Group,Permission
from .models import notice,user_profile,extra_data,certificate_request,timeline,groupsinfo
from django.contrib.auth.decorators import login_required
from exam.models import course
from django.core.paginator import Paginator
import itertools
import os
import math

# Create your views here.

###
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)

        if us is not None:
            try:
                ab = user_profile.objects.filter(user_id=us.id)[0]
                vars(ab)['_state'] = None
                request.session['ab']=vars(ab)

            except:
                pass
            messages.info(request, "Successfully Log In")
            if us.last_login !=None:
                login(request, us)

                return redirect(index)
            else:
                login(request, us)

                return redirect(reset_password)
        else:
            messages.error(request, "Username and password not match")
            response = redirect(login_form)
            return response

    return HttpResponse("")

###
def log_out(request):
    logout(request)
    return redirect(login_form)

###
def login_form(request):
    if request.user.username != "":
        return redirect('index')
    else:
        return render(request, 'student/login_form.html')

###
def reset_password(request):

    if request.method=='POST':
        try:
            us = User.objects.get(username=request.POST['username'])
            up = user_profile.objects.get(user_id=us.id)
        except:
            messages.error(request,'User not found')
            return redirect(reset_password)

        if up.otp==request.POST['otp']:
            us.set_password(request.POST['password'])
            us.save()
            login(request,us)
            messages.success(request,'Password reset succesful')
            return redirect('index')
        else:
            messages.warning(request,'Failed to reset password')
            return redirect(reset_password)
    return render(request,'student/reset_password.html')

##
@login_required(login_url='')
def index(request):

    try:
        flag=request.user
    except:
        return redirect('login_form')
    if request.user.is_staff:
        from .models import notice
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""

        return render(request,'student/adminindex.html',{'notice':notice1})
    else:
        day = datetime.now()
        day = day.strftime("%d")

        if day == "20":
            if not request.session.has_key('feedback'):
                request.session['feedback'] = True
        else:
            if request.session.has_key('feedback'):
                if request.session['feedback'] == False:
                    del request.session['feedback']

        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        up = user_profile.objects.get(user_id=request.user)
        performance_row = up.student_performance_row
        range = "!" + str(performance_row) + ":" + str(performance_row)
        values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname='Apr - Mar 2021', range=range)

        fields = ['id', 'Name', 'Contact No', 'Email ID', 'Admission Date', 'Training Mode',
                               'Course Start Date', 'Course',
                               'Course Start From', 'Current Module',
                               'C Trainer Name', 'C module start date', 'C module end date', 'C Theory ( Out of 40)',
                               'C Practical (Out of 40)','C Oral ( Out of 20)', 'C Total Marks',
                               'Sql Trainer Name', 'Sql module start date', 'Sql module end date',
                               'SQl Theory ( Out of 40)','SQl Practical (Out of 40)','SQL Oral ( Out of 20)', 'Sql Total Marks',
                               'WD Trainer Name', 'WD module start date', 'WD module end date',
                               'WD Practical (Out of 150)','WD Oral ( Out of 50)', 'WD Total Marks',
                               'Portfolio URL', 'Mock Interview Remark - 1( Excellent/Good/Poor)', 'Project Guide',
                               'Mini Project',
                               'Core Trainer Name', 'Core module start date', 'Core module end date',
                               'Core Theory ( Out of 40)',
                               'Core Practical (Out of 40)', 'Core Oral ( Out of 20)', 'Core Total Marks',
                               'Mock Interview Remark - 2( Excellent/Good/Poor)',
                               'Adv Trainer Name', 'Adv module start date', 'Adv module end date',
                               'Adv Theory ( Out of 40)',
                               'Adv Practical (Out of 40)', 'Adv Oral ( Out of 20)', 'Adv Total Marks',
                               'Full Course End Date', 'Cravita Poject Start Date',
                               'Mock Interview Remark - 3( Excellent/Good/Poor)',
                               'Soft Skills Marks ( Out of 100 )', 'Final Mock Interview', 'Total Marks ( Out of 700 )',
                               'Eligible For Placement(Y/N)', 'Remark'
                               ]

        performance = dict(zip(fields, values[0]))  # list data to object


        # print(performance)
        us = User.objects.get(id=request.user.id)
        gps = us.groups.all()
        print(us.groups.all())
        per = {}
        for g in gps:
            gpinfo = groupsinfo.objects.get(group=g.id)
            courses = course.objects.values_list('name', flat=True).distinct()
            for c in courses:
                print(gpinfo.course,c)
                cper = []
                if gpinfo.course == c:
                    print(gpinfo.course,c)
                    if len(g.permissions.filter(name="video")):
                        cper.append('video')
                    if len(g.permissions.filter(name="notes")):
                        cper.append('notes')
                    if len(g.permissions.filter(name="exam")):
                        cper.append('exam')
                    per[c]=cper

            print(per)

        from .models import notice
        notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request, 'student/index.html', {'performance': performance,'notice':notice1,'up':up,'per':per,'profile':""})

###
def addstudent(request):
    if request.method == 'POST':
        # print(request.POST)
        # import itertools
        from .models import user_profile
        profile = [['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-4)+1)', ""], ["", ""], ["", ""], ["", ""]]
        for field in itertools.islice(request.POST, 2, None):
            val = request.POST.getlist(field)
            for i in range(0, 4):
                try:
                    profile[i].append(val[i])
                except:
                    profile[i].append("")

        performance = ['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)', profile[0][8],
                       profile[0][11] + "/" + profile[0][12]
            , profile[0][13], profile[0][3], profile[0][7], profile[0][5], profile[0][4], profile[0][6]]
        print(performance)

        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value

        if request.user.is_staff:
            performance_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[performance])
        else:
            sp = user_profile.objects.get(id=request.user.id)
            performance_row = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,row=sp.student_performance_row,
                                                    value=[performance])

        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value

        if request.user.is_staff:
            profile_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=profile)
        else:
            sp = user_profile.objects.get(id=request.user.id)
            profile = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,row=sp.student_profile_row,value=profile)

        if request.user.is_staff:
            username = request.POST['emailid']
            password = randomstring(request)
            print(username)
            us = User.objects.create_user(username=username,first_name=request.POST['name'],
                      password=password,email=request.POST['emailid'],last_name=request.POST['contact'])
            us.save()
            try:
                file = request.FILES['photo']
                file._name = str(request.POST['name']) +"."+ file._name.split('.')[1]
            except:
                file = ""
            from .models import user_profile
            us_profile = user_profile.objects.filter(user_id=us.id)
            if len(us_profile)==0:
                us_profile = user_profile(user_id=us,student_performance_row=(int(performance_row)+1),
                                          student_profile_row=(int(profile_row)+1))
                if file!=0:
                    us_profile.photo = file
                us_profile.save()
            else:
                us_profile.update(photo=file)
                # user_profile.save()
            # message to be sent
            header = 'To:' + us.username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + username + '\n Password: ' + password + ' \n\n'
            print(message)

            mail(us.email,message)
            # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
            messages.info(request,'Student added successfully')
        else:
            messages.info(request,'Profile updated successfully')

        return redirect('index')
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request,'student/add_student.html',{'notice':notice1})

###
def viewstudent(request):
    up = user_profile.objects.get(user_id=request.user.id)
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request,'student/view_data.html',{'up':up,'sheetnames':SHEET_NAMES,'notice':notice1})

###
def viewperformance(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request,'student/view_performance.html',{'up':up,'sheetnames':SHEET_NAMES,'notice':notice1})


def admin(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request, 'student/index.html',{'up':up,'notice':notice1})

###
def addgroups(request,view="false"):
    print(request.POST)
    print(view)
    if request.method == 'POST':
        gname = request.POST['gname']
        # course = request.POST['cname']
        # cname = ''
        gp = Group.objects.filter(name=gname)
        # gpinfo = ''
        if len(gp) == 0:
            cname = request.POST['cname']
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            gp=Group(name=gname)
            gp.save()
            gpinfo = groupsinfo(group=gp,course=cname,startdate=startdate,enddate=enddate)
            gpinfo.save()
            messages.info(request,'Group created')
            SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
            attendance = ["id","user_id", "name", "contact", "email id"]
            sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,columns=attendance)
            messages.info(request, gname + " is added in sheet")
        else:
            gp=gp[0]
            # print(gp.id)
            gpinfo = groupsinfo.objects.get(group_id=gp.id)
            try:
                gpinfo.enddate = request.POST['enddate']
                gpinfo.save()
            except:
                pass
            cname = request.POST['cname']



        # print(permissions)
        if request.POST.get('videopermission'):
            for p in gp.permissions.all():
                if p.name not in request.POST.getlist('videopermission'):
                    gp.permissions.remove(p.id)
            for p in request.POST.getlist('videopermission'):
                p = Permission.objects.get(name=p)
                if p not in gp.permissions.all():
                    gp.permissions.add(p)

        if request.POST.get('pervideo') or request.POST.get('perexam') or request.POST.get('pernotes'):
            permissions = {'video': request.POST.get('pervideo'), 'exam': request.POST.get('perexam'),
                           'notes': request.POST.get('pernotes')}
            for p in permissions:
                if permissions.get(p) == 'on':
                    gp.permissions.add(Permission.objects.get(name=p))
                else:
                    gp.permissions.remove(Permission.objects.get(name=p))

        print(gp.permissions.all())
        pre = {'video':'','exam':'','notes':''}
        for p in pre:
            # print(type(pre))
            pre[p]=len(gp.permissions.filter(name=p))

        gp_permissions = gp.permissions.all()
        # print(gp.permissions.filter(name='video'))
        groups = Group.objects.all().order_by('-id')
        members = User.objects.all().order_by('-id')

        # request_member = [int(x) for x in request.POST.getlist('members')]
        try:
            request_member = [int(x) for x in request.POST.get('students').split(',')[:-1:]]
        except:
            request_member=[]
        # print(request_member)

        if request.POST.get('students'):
            for m in members:
                if gp in m.groups.all():
                    if m.id not in request_member:
                        m.groups.remove(gp.id)
                        messages.info(request,m.first_name+" is removed")
                else:
                    if m.id in request_member:
                        m.groups.add(gp.id)
                        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
                        # print(us)
                        # index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
                        # if sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=gname) is None:
                        index = '=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)'
                        values = [index,m.id,m.first_name,m.last_name,m.email]
                        sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,values=[values])
                        messages.info(request,m.first_name+" is added")

        memb_pre = []  # group existing members
        for m in members:
            if len(m.groups.filter(name=gname))==1:
                memb_pre.append(m)

        videolist = []

        videos = "media/videos/courses/" + cname
        # print(os.listdir(videos))
        for v in os.listdir(videos):
            videolist.append(v.split(".")[0])

        # print(videolist)
        # notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        # print(memb)
        courses = course.objects.values_list('name', flat=True).distinct()
        print(gpinfo.enddate)
        return render(request,'student/add_groups.html',{'gname':gp,'permissions':Permission.objects.all()[68::],'pre':pre,
                                                        'members':members,'memb_pre':memb_pre,'up':up,'groups':groups,
                                                         'notice':notice1,'vpermissions':videolist,'courses':courses,
                                                         'gpinfo':gpinfo,'gp_permissions':gp_permissions,'view':view})
    groups = Group.objects.all()
    courses = course.objects.values_list('name', flat=True).distinct()

    # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_groups.html',{'groups':groups,'courses':courses,'view':view})

    # return render(requet,'student/test.html')


def viewgroups(request):
    if request.method == "POST":
        gp = Group.objects.get(name=request.POST['gname'])
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        print(gp_per)
        # add_per = [int(add_per) for add_per in request.POST.getlist('permissions')]

        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        groups = Group.objects.all().order_by('-id')
        members = User.objects.all().order_by('-id')
        # members = User.objects.all()
        memb_pre = []  #group existing members
        for m in members:
            if m.groups.filter(id=gp.id):
                memb_pre.append(m)
        # memb_grp = {member.id: {'grp_id': group.id, 'grp_name': group.name} for member in members for group in groups}
        pre = {'video': '', 'exam': '', 'notes': ''}
        for p in pre:
            # print(type(pre))
            pre[p] = len(gp.permissions.filter(name=p))

        videolist = []

        gpinfo = groupsinfo.objects.get(group_id=gp.id)


        videos = "media/videos/courses/" + gpinfo.course
        # print(os.listdir(videos))
        for v in os.listdir(videos):
            videolist.append(v.split(".")[0])

        notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request,'student/view_groups.html',{'groups':Group.objects.all(),'gname':gp.name,'pre':pre,
                                                          'group_per':gp_per,'memb_pre':memb_pre,'permissions':Permission.objects.all(),
                                                          'members':members,'up':up,'notice':notice1})

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request, 'student/view_groups.html', {'groups': Group.objects.all(),'up':up,'notice':notice1})

###
def addusers(request):
    if request.method == "POST":
        gp = Group.objects.filter(name=request.POST['gname'])[0]
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        # print(gp_per)
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        # print(request.POST['username'])
        us = User.objects.filter(username=email)
        if len(us)==0:
            us = User(username=email,first_name=fname,last_name=lname,email=email,password=randomstring(request),is_staff=True)
            us.save()
            messages.info(request,"User added successfully")
            # message to be sent
            header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + us.username + '\n Password: ' + us.password + ' \n\n'
            print(message)

            # mail(us.email,message)

        else:
            us = us[0]

        print(request.POST)
        if request.POST.getlist('permissions'):
            if request.POST['gname']:
                us_gp = [us_gp.id for us_gp in us.groups.all()]
                # print(us_gp)
                if gp.id not in us_gp:
                    us.groups.add(gp.id)
                # print(us.groups.all())

            add_per = [Permission.objects.get(id=add_per).id for add_per in request.POST['permissions'].split(',')[:-1:]]
            usr_per = [usr_per.id for usr_per in Permission.objects.filter(user=us)]
            print(usr_per,add_per)
            for per in add_per:
                if per not in gp_per:
                    us.user_permissions.add(per)
                    us.save()
                    # print(per)

            for per in usr_per:
                if per not in add_per:
                    us.user_permissions.remove(per)
                    us.save()

        usr_per = [usr_per.id for usr_per in Permission.objects.filter(user=us)]
        perm = {'group_per':gp_per,'user_per':usr_per}
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]

        notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        return render(request, 'student/add_users.html', {'groups': Group.objects.all(),'gname':gp.name,'perm':perm,
                                                          'permissions':Permission.objects.filter(id__gte=64),'member':us,'up':up,
                                                          'notice':notice1})

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_users.html',{'groups':Group.objects.all(),'up':up,'notice':notice1})

###
def user_permissions(request):
    uid = request.GET['uid']
    us = User.objects.get(id=int(uid))
    per = []
    a = Permission.objects.filter(user=uid)
    for i in [102,103]:
        p = Permission.objects.get(id=i)
        if p in a:
            per.append({'name':p.name,'value':p.id,'selected':'true'})
        else:
            per.append({'name':p.name,'value':p.id})
    return HttpResponse(str(per).replace("'",'"'))

def viewmembers(request):
    groups = Group.objects.all()
    gnames = []
    for g in groups:
        gnames.append(g.name)
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request, 'student/view_users.html', {'sheetnames': gnames,'notice':notice1})


def viewprofile(request):
    sheetid = extra_data.objects.get(name='student_profile').value
    up = user_profile.objects.get(user_id=request.user.id)
    row = up.student_performance_row
    range = "!A"+str(row)+":AS"+str(row+3)
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)
    fields = ["id","datetime","center","dateofadmission","course","batchstartdate","modulestartfrom","trainingmode",
              "name","address","dateofbirth","contact","emailid","alternatecontact","examination","stream","collegename",
              "boardname","yearofpassing","percentage","fees","mode","regammount","installment1","installment2",
              "installment3","regdate","installment1date","installment2date","installment3date",'remark']
    # import json
    profile = [dict(zip(fields,values[0])),dict(zip(fields,values[1])),dict(zip(fields,values[2])),dict(zip(fields,values[3]))] #list data to object
    up = user_profile.objects.get(user_id=request.user.id)
    try:
        rc = certificate_request.objects.get(student_id=request.user.id)
    except:
        rc = ""
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
            notice1 = ""

    # sheetid = extra_data.objects.get(name='student_performance').value
    # up = user_profile.objects.get(user_id=request.user.id)
    # row = up.student_performance_row
    # range = "!A" + str(row) + ":AS" + str(row)
    # # print(range)
    # values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)
    # print(values,values[4])
    return render(request,'student/profile.html',{'profile':profile,'up':up,'rc':rc,'notice':notice1})

def editprofile(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return redirect(request,'index',{'up':up,'notice':notice1})

def viewnotice(request):
    data = notice.objects.all().order_by('-generateddate')
    try:
        pageno = request.GET['page']
    except:
        pageno = 1

    if pageno == 1:
        p = Paginator(data, 11)
    else:
        p = Paginator(data, 12)
    page = p.page(pageno)

    up = user_profile.objects.all().filter(user_id=request.user.id)[0]

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/view_notice.html',{'up':up,'data':page,'notice':notice1})

def studentupdate(request):
    from .models import user_profile as ap
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    cell = 'False'
    up = ap.objects.get(user_id=request.user.id)
    # row = request.user.username.split(':')[1]
    row = up.student_profile_row
    value = ''
    col = 0
    if cell=="False":
        Basic = {"center": "", "dateofadmission": "", "course": "", "batchstartdate": "", "startcourse": "",
                 "trainingmode": ""}
        Personal_details = {"name": "", "address": "", "dateofbirth": "", "contact": "", "emailid": "",
                            "alternatecontact": ""}
        Educational_details = [
            {'secondary': "", 'stream10': "", 'collegename10': "", 'boardname10': "", 'yearofpassing10': "",
             'percentage10': ""},
            {'hsecondary': "", 'stream12': "", 'collegename12': "", 'boardname12': "", 'yearofpassing12': "",
             'percentage12': ""},
            {'graduation': "", 'streamg': "", 'collegenameg': "", 'boardnameg': "", 'yearofpassing': "",
             'percentageg': ""},
            {'pg': "", 'streampg': "", 'collegenamepg': "", 'boardnamepg': "", 'yearofpassinpg': "", 'percentagepg': ""}
        ]

        Fees = {"fees": "", "mode": "", "regammount": "", "installment1": "", "installment2": "", "installment3": "",
                "regdate": "", "installment1date": "", "installment2date": "", "installment3date": ""}

        Remark = {"remark": ""}
        addstudentform = {"Basic": Basic, "Personal_details": Personal_details,
                          "Educational_details": Educational_details, "Fees": Fees, "Remark": Remark}

        filledaddstudentform = []

        flag = True

        acced = [[], [], []]

        i = -1

        for section in addstudentform:
            for fields in addstudentform[section]:
                if isinstance(fields, dict):
                    for field in fields:
                        fields[field] = request.POST.get(field)
                        if flag:
                            if request.POST.get(field):
                                filledaddstudentform.append(request.POST.get(field))
                            else:
                                filledaddstudentform.append("")
                            # flag = False
                        else:
                            # print(i)
                            if request.POST.get(field):
                                acced[i].append(request.POST.get(field))
                            else:

                                acced[i].append("")
                    flag = False
                    i += 1
                else:
                    addstudentform[section][fields] = request.POST.get(fields)
                    if request.POST.get(fields):
                        filledaddstudentform.append(request.POST.get(fields))
                    else:
                        filledaddstudentform.append("")

        # print(filledaddstudentform)
        sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-4)+1"
        import math
        if sheetsapi.sheetvalues(SPREADSHEET_ID, sheetname) is None:
            index = 1
        index = math.ceil(up.student_performance_row)

        # print(filledaddstudentform)

        rowv = int(row)
        performance_row = sheetsapi.updatesheet(SPREADSHEET_ID,rowv, [index, ""] + filledaddstudentform,col, cell=False)
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+1, ["", ""] + [""] * 12 + acced[0], col, cell=False)
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+2, ["", ""] + [""] * 12 + acced[1], col, cell=False)
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+3, ["", ""] + [""] * 12 + acced[2], col, cell=False)
        # sheetsapi.updatesheet(SPREADSHEET_ID, row, col, value=filledaddstudentform, cell=False)

        # fp = open('student_performance.txt', 'r')
        # sheetid = fp.read()
        # fp.close()

        sheetid = extra_data.objects.get(name='student_performance').value
        student_performance = {'id': "", 'name': "", 'contact': "", 'emailid': "", 'dateofadmission': "",
                               'trainingmode': "",
                               'batchstartdate': "", 'course': "", 'startcourse': "", 'currentmodule': "",
                               'ctrainername': "", 'cmodulestartdate': "", 'cmoduleenddate': "", 'ctheory': "",
                               'cpracticle': "", 'coral': "", 'ctotal': "",
                               'sqltrainername': "", 'sqlmodulestartdate': "", 'sqlmoduleenddate': "",
                               'sqlpracticle': "", 'sqloral': "", 'sqltotal': "",
                               'wdtrainername': "", 'wdmodulestartdate': "", 'wdmoduleenddate': "", 'wdpracticle': "",
                               'wdoral': "", 'wdtotal': "", 'portfoiliolink': "",
                               'mock1': "", 'miniguide': "", 'miniproject': "",
                               'coretrainername': "", 'coremodulestartdate': "", 'coremoduleenddate': "",
                               'coretheory': "", 'corepracticle': "", 'coreoral': "", 'coretotal': "",
                               'mock2': "",
                               'advtrainername': "", 'advmodulestartdate': "", 'advmoduleenddate': "", 'advtheory': "",
                               'advpracticle': "", 'advoral': "", 'advtotal': "",
                               'fullcourseenddate': "", 'cravitaprojectstartdate': "",
                               'mock3': "", 'softskillsmarks': "", 'finalmock': "", 'totalmarks': "",
                               'eligibleforplacement': "", 'remark': ""
                               }

        for s in student_performance.keys():
            try:
                student_performance[s] = request.POST[s]
            except:
                student_performance[s] = ""

        # index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        # if sheetsapi.sheetvalues(sheetid, sheetname) is None:
        #     index = 1
        index = math.ceil(up.student_profile_row)

        student_performance['id'] = index

        # print(student_performance)

        sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
        # index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        # if sheetsapi.sheetvalues(sheetid, sheetname) is None:
        #     index = 1
        # print(filledaddstudentform)
        student_performance = [x for x in student_performance.values()]
        # import math
        # print(math.ceil((int(request.user.username.split(':')[1])-1)/4))
        row = up.student_performance_row
        sheetsapi.updatesheet(sheetid,row,student_performance)

        try:
            file = request.FILES['photo']
            file._name = str(request.user.username) +"."+ file._name.split('.')[1]
        except:
            file = ""
        from .models import user_profile
        us_profile = user_profile.objects.all().filter(user_id=request.user.id)
        if len(us_profile)==0:
            us_profile = user_profile(user_id=request.user,student_performance_row=str(int(performance_row)+1),photo=file)
            us_profile.save()
        else:
            us_profile.update(photo=file)

        messages.info(request,'profile updated')
        return redirect(viewprofile)
    else:
        sheetsapi.updatesheet(SPREADSHEET_ID,row,col,value,cell)
        # fp = open('student_performance.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        # sheetsapi.updatesheet(SPREADSHEET_ID,idvalue,col,value,cell)
        messages.info(request,'profile updated')
        return redirect(viewstudent)

    return HttpResponse("")

def attendance(request):
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/attendance.html',{'sheetnames':SHEET_NAMES,'notice':notice1})

def studentattendance(request):
    us = User.objects.get(id=request.user.id)
    gps = us.groups.all()
    data =[]
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    for g in gps:
        c = groupsinfo.objects.get(group=g.id).course
        value = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=g.name)
        for v in value:
            print(us.id,int(v[1]),us.id == int(v[1]))
            if us.id == int(v[1]):
                print(len(v)-6,v.count('p'))
                data.append({'course':c,'per':round(v.count('p')/(len(v)-6)*100,2)})
    print(data)
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/studentattendance.html',{'notice':notice1,'data':data,'gps':gps})

def addnotice(request):
    # data : ""
    if request.method == 'POST':
        notice.addnoticein(request)
    data = notice.objects.all().order_by('-generateddate').filter(createdby=request.user)
    try:
        pageno = request.GET['page']
    except:
        pageno = 1

    if pageno == 1:
        p = Paginator(data,11)
    else:
        p = Paginator(data,12)
    page = p.page(pageno)
    for i in page:
        print(i)
    # print(page)
    # if not request.user.is_staff:
    #     page = notice.objects.all()
    # print(data)
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/add_notice.html',{'data':page,'up':up,'notice':notice1})

def request_certificate(request):
    cr = certificate_request(student_id=request.user)
    cr.save()
    us = user_profile.objects.get(user_id=request.user.id)
    us.certificate=cr
    us.save()
    messages.info(request,'certificate saved Successfully')
    return redirect('index')

def addcertificate(request):
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/add_certificate.html',{'notice':notice1})

def viewcertificate(request):
    return HttpResponse("")



###
def randomstring(request):
    import secrets
    import string

    N = 7
    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

    return str(res)

###
def mail(receiver,body):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    # try:
    s = smtplib.SMTP('mail.fortunecloudindia.com', 587)
    s.starttls()
    s.login("aniket.pawar@cravitaindia.com", "Aniket@123")
    # print(s)
    # s.sendmail("aniket.pawar@cravitaindia.com", reciver, body)
    # s.quit()

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = "aniket.pawar@cravitaindia.com"
    message['To'] = receiver
    message['Subject'] = 'This email has an attacment, a pdf file'

    message.attach(MIMEText(body, 'plain'))

    pdfname = 'es_full.pdf'

    # open the file in bynary
    # binary_pdf = open(pdfname, 'rb')

    # payload = MIMEBase('application', 'octate-stream', Name=pdfname)
    # payload = MIMEBase('application', 'pdf', Name=pdfname)
    # payload.set_payload((binary_pdf).read())
    # payload.set_payload(Pdf)

    # enconding the binary into base64
    # encoders.encode_base64(payload)

    # add header with pdf name
    # payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
    # message.attach(payload)

    text = message.as_string()
    s.sendmail("aniket.pawar@cravitaindia.com", receiver, text)
    s.quit()
    # print('Mail Sent')
    print("success")
    return "success"
    # except:
    #     print("failed")
    #     return "failed"




from django.views.decorators.clickjacking import xframe_options_exempt,xframe_options_sameorigin
@xframe_options_exempt
def student_performance_out(request):
    # request.POST['abc']='abc'
    # print(request.GET['row'].split(','))
    rowv = request.GET['rowv'].split(',')
    # fp = open('student_performance.txt', 'r')
    # SPREADSHEET_ID = fp.read()
    # fp.close()
    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,row=int(rowv[0])+1,value=rowv)
    return HttpResponse("")

@xframe_options_exempt
def student_performance_in(request):
    student_performance = {'id': "", 'name': "", 'contact': "", 'emailid': "", 'dateofadmission': "",
                           'trainingmode': "",
                           'batchstartdate': "", 'course': "", 'startcourse': "", 'currentmodule': "",
                           'ctrainername': "", 'cmodulestartdate': "", 'cmoduleenddate': "", 'ctheory': "",
                           'cpracticle': "", 'coral': "", 'ctotal': "",
                           'sqltrainername': "", 'sqlmodulestartdate': "", 'sqlmoduleenddate': "", 'sqltheory': "",
                           'sqlpracticle': "",
                           'sqloral': "", 'sqltotal': "",
                           'wdtrainername': "", 'wdmodulestartdate': "", 'wdmoduleenddate': "", 'wdpracticle': "",
                           'wdoral': "", 'wdtotal': "", 'portfoliolink': "",
                           'mock1': "", 'miniguide': "", 'miniproject': "",
                           'coretrainername': "", 'coremodulestartdate': "", 'coremoduleenddate': "", 'coretheory': "",
                           'corepracticle': "", 'coreoral': "", 'coretotal': "",
                           'mock2': "",
                           'advtrainername': "", 'advmodulestartdate': "", 'advmoduleenddate': "", 'advtheory': "",
                           'advpracticle': "", 'advoral': "", 'advtotal': "",
                           'fullcourseenddate': "", 'cravitaprojectstartdate': "",
                           'mock3': "", 'softskillsmarks': "", 'finalmock': "", 'totalmarks': "",
                           'eligibleforplacement': "", 'remark': ""
                           }
    # fp = open('student_performance.txt', 'r')
    # sheetid = fp.read()
    # fp.close()
    sheetid = extra_data.objects.get(name='student_performance').value
    sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
    values = sheetsapi.sheetvalues(sheetid, sheetname)
    # print(data)
    # data =[{key:val for key in student_performance for val in data[0]} ]
    # data = [dict(zip(student_performance,data[i])) for i in range(len(data))]
    data = []
    for row in values:
        dict = {}
        for s, i in zip(student_performance, range(len(student_performance))):
            if i < len(row):
                dict[s] = row[i]
            else:
                dict[s] = ''
        data.append(dict)
    return HttpResponse(str(data))

@xframe_options_exempt
def student_profile_in(request):
    student_profile = ["id", "datetime", "center", "dateofadmission", "course", "batchstartdate", "modulestartfrom","trainingmode",
              "name", "address", "dateofbirth", "contact", "emailid", "alternatecontact", "examination", "stream","collegename",
              "boardname", "yearofpassing", "percentage", "fees", "mode", "regammount", "installment1", "installment2",
              "installment3", "regdate", "installment1date", "installment2date", "installment3date", 'remark']
    field = student_profile
    # fp = open('student_profile.txt', 'r')
    # sheetid = fp.read()
    # fp.close()
    sheetid = extra_data.objects.get(name='student_profile').value
    sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
    values = sheetsapi.sheetvalues(sheetid, sheetname)
    # print(data)
    # data =[{key:val for key in student_performance for val in data[0]} ]
    # data = [dict(zip(student_performance,data[i])) for i in range(len(data))]
    data = []
    for row in values:
        dict = {}
        for s, i in zip(field, range(len(field))):
            if i < len(row):
                dict[s] = row[i]
            else:
                dict[s] = ''
        data.append(dict)
    # print(data)
    return HttpResponse(str(data))

def student_profile_out(request):
    rowv = request.GET['rowv'].split(',')
    row = request.GET['row']
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    print(rowv)
    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=int(row) + 2, value=rowv)
    return HttpResponse("")

def change_user_data(request):
    return HttpResponse("")

####
def get_data(request,table):
    if table == 'attendance':
        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    if table == 'profile':
        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    if table == 'performance':
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    if table == 'feedback':
        SPREADSHEET_ID = extra_data.objects.get(name='feedback').value
    if table == 'schedule':
        SPREADSHEET_ID = extra_data.objects.get(name='batch schedule').value

    SHEET_NAME = request.GET['sheetname']

    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=SHEET_NAME,range='!A1:GZ')
    data = []
    fields = [x for x in values[0]]
    for row,i in zip(values[1::1],range(1,len(values))):
        dict = {'rowIndex':i}
        for s, j in zip(fields, range(len(fields))):
            if j < len(row):
                dict[s] = row[j]
            else:
                dict[s] = ''
        data.append(dict)

    # if table == 'attendance':
    #     data1 = []
    #     for d in data:
    #         print(request.user.id, int(d['USER_ID']))
    #         if int(d['USER_ID']) == request.user.id:
    #             data1.append(d)
    #             break
    # data = data1
    # print(data)
    messages.info(request,'Data fetch successfully')
    return HttpResponse(str(data))

###
def set_data(request,table):
    print(request.GET)
    rowv = request.GET.getlist('rowv[]')
    print(rowv)
    row = rowv[0]
    rowv = rowv[1::]
    SHEET_NAME = request.GET['sheetname']
    # print(request.GET)
    # print(row)
    if table != 'attendance':
        if table == 'profile':
            SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
        if table == 'performance':
            SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
            rowv[16] = '=sum(N2,O2,P2)'
            rowv[23] = '=sum(U2,V2,W2,)'
            rowv[29] = '=sum(AB2,AC2)'
            rowv[40] = '=sum(AL2,AM2,AN2,)'
            rowv[48] = '=sum(AT2,AU2,AV2)'
            rowv[-2] = '=IF((IF(N2,1,0)+IF(O2,1,0)+IF(P2,1,0)+IF(U2,1,0)+IF(V2,1,0)+IF(W2,1,0)+IF(AB2,1,0)+IF(AC2,1,0)+IF(AE2,1,0)+IF(AF2,1,0)+IF(AL2,1,0)+IF(AM2,1,0)+IF(AN2,11,0)+IF(AP2,1,0)+IF(AT2,1,0)+IF(AU2,1,0)+IF(AV2,1,0)+IF(AZ2,1,0)+IF(BB2,1,0))=19,"Y","N")'
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=int(row)+1, value=rowv)
    elif table == 'attendance':
        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
        rowv = request.GET['rowv[]']
        row = request.GET['row']
        SHEET_NAME = request.GET['sheetname']
        if (type(rowv[0])==int):
            rowv = [x for x in rowv]
        else:
            rowv = [int(x) for x in rowv]

        rowv.sort()
        date = datetime.now()
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")

        currentdate=day+"/"+month+"/"+year
        present = [currentdate]

        for i in range(0,rowv[-1]+1):
            if i in rowv:
                present.append("p")
            else:
                present.append("")

        row = int(row)
        col=""
        while row>1:
            col+=(chr((row%26)+65))
            row = row/26

        sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,values=[present],sheetname=SHEET_NAME,range='!'+col+':'+col+'',dimension="COLUMNS")
        messages.info(request,'Data saved successfully')
    return HttpResponse("success")

###
def attendance_update(request):
    print(request.GET)
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    rowv = request.GET.getlist('rowv[]')
    row = request.GET['row']
    SHEET_NAME = request.GET['sheetname']
    print(rowv)
    if (type(rowv[0]) == int):
        rowv = [x for x in rowv]
    else:
        rowv = [int(x) for x in rowv]

    # rowv.sort()
    print(rowv,max(rowv))
    date = datetime.now()
    day = date.strftime("%d")
    month = date.strftime("%m")
    year = date.strftime("%Y")

    currentdate = day + "/" + month + "/" + year
    present = [currentdate]

    for i in range(0, max(rowv) + 1):
        if i in rowv:
            present.append("p")
        else:
            present.append("")

    row = int(row)
    col = row

    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, value=present, SHEET_NAME=SHEET_NAME,col=col,row=1, dimension="COLUMNS")
    return HttpResponse("")

###
def sendotp(request):
    otp = randomstring(request)
    # print(request.POST)
    us = User.objects.all().filter(username=request.GET['username'])
    if len(us)==1:
        up = user_profile.objects.all().filter(user_id=us[0].id)
        if len(up)==0:
            up = user_profile(user_id=request.user,otp=otp)
        else:
            up=up[0]
        # print(us.otp)
        up.otp=otp
        up.save()
        # print(up.otp)
        header = 'To:' + us[0].username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS OTP \n'

        message = header + '\n Username: ' + us[0].username + '\n OTP: ' + otp + ' \n\n'
        print(message)

        if mail(us[0].email,message) == 'success':
            return HttpResponse("Otp send successfully")
        else:
            return HttpResponse("Failed to send otp")
    else:
        # messages.error(request,'Username not found')
        return HttpResponse("Username not found")

def get_user(request):
    gname = request.GET['gname']
    gp = Group.objects.get(name=gname)
    members = User.objects.all().filter(groups=gp.id)
    memb = []
    abc = []
    for m in members:
        print(m.groups.all())
        vars(m)['_state']='None'
        key = list(vars(m).keys())
        memb1 = []
        for i in key:
            memb1.append(str(vars(m)[i]))
        key = [k.upper() for k in key]
        memb.append(dict(zip(key,memb1)))
        # pint(m)
        abc.append(m)
    memb = str(memb).lstrip('_').replace('"','').replace('FIRST_NAME','NAME').replace("True","true").replace("False",'')
    # print(memb)
    return HttpResponse(str(memb))


def set_user(request):
    values = request.GET['values'].replace('{','').replace('}','').replace('"','').replace("'",'').split(',')
    val={}
    for i in values:
        kv=i.split(':')
        val[kv[0].lower()]=kv[1]
    print(values,val['is_staff'])
    us = User.objects.get(id=val['id'])
    us.is_staff = val['is_staff'].capitalize()
    us.is_active = val['is_active'].capitalize()
    us.save()
    messages.info(request,'Changes saved successfully')
    return HttpResponse('succcess')

def test(request):
    # print(request.POST)
    if request.method == "POST":
        profile = [['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-4)+1)',""],["",""],["",""],["",""]]
        for field in itertools.islice(request.POST,2,None):
            val = request.POST.getlist(field)
            for i in range(0,4):
                try:
                    profile[i].append(val[i])
                except:
                    profile[i].append("")

        performance = ['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)',profile[0][8],profile[0][11]+"/"+profile[0][12]
            ,profile[0][13],profile[0][3],profile[0][7],profile[0][5],profile[0][4],profile[0][6]]
        print(performance)

        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value

        performance_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,values=[performance])

        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value

        profile_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=profile)

        username = request.POST['emailid']
        password = randomstring(request)
        # print(username)
        us = User.objects.create_user(username=username, first_name=request.POST['name'],
                                      password=password, email=request.POST['emailid'], last_name=request.POST['contact'])
        us.save()
        try:
            file = request.FILES['photo']
            file._name = str(request.POST['name']) + "." + file._name.split('.')[1]
        except:
            file = ""
        from .models import user_profile
        us_profile = user_profile.objects.filter(user_id=us.id)
        if len(us_profile) == 0:
            us_profile = user_profile(user_id=us, student_performance_row=(int(performance_row) + 1),
                                      student_profile_row=(int(profile_row) + 1))
            if file != 0:
                us_profile.photo = file
            us_profile.save()
        else:
            us_profile.update(photo=file)
            # user_profile.save()
        # message to be sent
        header = 'To:' + us.username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

        message = header + '\n Username: ' + username + '\n Password: ' + password + ' \n\n'
        print(message)

        mail(us.email, message)
        # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        messages.info(request, 'Student added successfully')

    return render(request,'student/test.html', )


def getcertificate(request):
    certificate = certificate_request.objects.all().filter(certificate_status=request.GET['status']).order_by('-id')
    data = []
    us = []
    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    if len(certificate):
        key = vars(certificate[0]).keys()
        for c in certificate:
            data1 = {}
            for v in key:
                if v== '_state':
                    data1[v.upper()] = 'none'
                elif v== 'student_id_id':
                    data1['NAME']= User.objects.get(id=vars(c)[v]).first_name
                    us.append(User.objects.get(id=vars(c)[v]).id)
                else:
                    data1[v.upper()]=vars(c)[v]
            data.append(data1)
    print(us)
    # for u in us:
    #     st = user_profile.objects.get(user_id=u).student_performance_row
    #     print(st)
    #     v = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname='Apr - Mar 2021',range='!'+str(st)+':'+str(st))
    #     print(v[0][13:17]+v[0][20:24]+v[0][27:30]+v[0][38:41]+v[0][46:49])
    return HttpResponse(str(data).replace('False','false').replace('True','true').replace('_',' '))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def setcertificate(request):
    print(request.POST)
    try:
        file = request.FILES['file']
        file._name = str(request.user.username.split(':')[0]) + "." + file._name.split('.')[1]
    except:
        file = ""
    id = request.POST['id']
    cn = request.POST['certificate_number']
    cr = certificate_request.objects.get(id=id)
    cr.certificate_number = cn
    cr.certificate = file
    # print(request.POST['certificate_status'])
    cr.certificate_status = request.POST['certificate_status']
    cr.save()
    # print(file)
    # print(request.POST['id'])

    return HttpResponse(str(cr.certificate))

def objtodict(obj):
    print(obj)
    keys = vars(obj).keys()
    dic = {}
    for k in keys:
        if k == 'password':
            pass
        elif not isinstance(vars(obj)[k], (float, int, str, list, dict, tuple)) or k == 'tzinfo' or k == '_state':
            dic[k.upper()] = 'none'
        else:
            dic[k.upper()] = vars(obj)[k]
    # print(dic)
    return dic


def viewtimeline(request):
    return render(request,'student/timeline.html')

def addtimeline(request):
    print(request.POST)
    if request.method == "POST":
        ti = timeline(generator=request.user,title=request.POST['title'],type=request.POST['type'],body=request.POST['body'])
        ti.save()
    return render(request,'student/timeline.html')

def deletetimeline(request):
    print(request.GET)
    if request.method == "GET":
        id = request.GET['id']
        ti = timeline.objects.get(id=id)
        ti.delete()
    return render(request,'student/timeline.html')

def timelinedata(request):
    pre = int(request.GET['pre'])
    data = timeline.objects.all().order_by('-id')[pre:pre+20]
    print(request.GET)
    timel = []
    if len(data)>0:
        for d in data:
            vars(d)['_state'] = 'none'
            vars(d)['name'] = User.objects.get(id=vars(d)['generator_id']).first_name
            # vars(d)['generator_id'] = User.objects.get(id=d.generator_id).first_name
            now = datetime.now(timezone.utc)
            d.body = str(d.body).replace('"','')
            time = ""
            vars(d)['date'] = d.generatedtime.strftime('%d %B %Y')
            # print((now-d.generatedtime))
            if (now - d.generatedtime).days > 0:
                time = str((now - d.generatedtime).days) + " days"
            else:
                time = ((now - d.generatedtime).seconds // 60)
                if time>60:
                    time = str(time // 60) + " hr"
                else:
                    time = str(time) + " min"
            vars(d)['time'] = time
            vars(d)['generatedtime'] = ""
            timel.append((vars(d)))
            # print(vars(d))
    else:
        timel = "-1"
    timel = str(timel).replace("'",'"')
    # print(timel)
    return HttpResponse(timel)



def addfeedback(request):
    print(request.POST)
    day = datetime.now()
    data = ['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)',day.strftime("%d/%M/%Y"),request.user.first_name,
            request.user.last_name,request.user.email]
    data1 =[]
    for field in itertools.islice(request.POST, 1, None):
        val = request.POST.getlist(field)
        for i in range(0, 1):
            try:
                data1.append(val[i])
            except:
                data1.append("")

    print(data+data1)

    feedback = data+data1

    SPREADSHEET_ID = extra_data.objects.get(name='feedback').value

    feedback = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[feedback])

    request.session['feedback'] = False
    return redirect("index")

def viewfeedback(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    SPREADSHEET_ID = extra_data.objects.get(name='feedback').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request, 'student/view_feedback.html', {'up': up, 'sheetnames': SHEET_NAMES, 'notice': notice1})

def students_groups(request,gname):
    gp = Group.objects.all()
    data = [{'groupname':'Students'}]
    nogroup = []
    for g in gp:
        data1 = {}
        data1['groupName']=g.name
        data2 = []
        for u in User.objects.filter(groups=g.id):
            if g.name == gname:
                data2.append({'uname': u.first_name, 'uid': u.id,'selected':"true"})
            else:
                data2.append({'uname':u.first_name,'uid':u.id})
        data1['groupData'] = data2
        data.append(data1)

    for u in User.objects.all():
        if len(u.groups.all())==0:
            nogroup.append({'uname':u.first_name,'uid':u.id})
    data[0]={'groupName':'Students',"groupData":nogroup}

    return HttpResponse(str(data).replace("'",'"'))


def students_current_groups(request,gname):
    data = []
    g = Group.objects.get(name=gname)
    # print(User.objects.filter(groups=g.id))
    for u in User.objects.filter(groups=g.id):
        data.append({'uname': u.first_name, 'uid': u.id,'selected':"true"})

    return HttpResponse(str(data).replace("'",'"'))

def calender(request):
    SPREADSHEET_ID = extra_data.objects.get(name='batch schedule').value
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname="Sheet 1")
    # print(values)
    data = []
    for v in values:
        # print(v)
        event = {}
        # print(v[1].split('-'))
        event['title'] = v[1] + " / " + v[3]
        event['startTime'] = v[0].split('-')[0]
        event['endTime'] = v[0].split('-')[1]
        event['start'] = v[2]
        event['end'] = v[4]
        # event['daysOfweek'] = ['1', '2', '3', '4', '5', '6']
        event['dow']= [1, 4]
        event['allDay'] = False
        data.append(event)
    # data = str(data).replace("'", '"').replace('False', 'false')
    print(data)
    return render(request,'student/calender.html',{'data':data})

def schedule(request):
    return render(request,'student/schedule.html')

def getcalenderevents(request):
    SPREADSHEET_ID = extra_data.objects.get(name='batch schedule').value
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname="Sheet 1")
    # print(values)
    data = []
    for v in values:
        # print(v)
        event = {}
        # print(v[1].split('-'))
        event['title'] = v[1] + " / " + v[3]
        event['startTime'] = v[0].split('-')[0]
        event['endTime'] = v[0].split('-')[1]
        # event['start'] = v[2]
        # event['end'] = v[4]
        # event['daysOfweek'] = ['1', '2', '3', '4', '5', '6']
        # event['dow']= [1, 4]
        event['allDay']= False
        data.append(event)
    data = str(data).replace("'",'"').replace('False','false')
    print(data)
    return HttpResponse(data)

def pdftest(request):

    return render(request,'student/pdf.html')

from io import BytesIO,StringIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa


class Render:

    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)
        

from django.views.generic import View
from django.utils import timezone
from .models import *
# from .render import Render


class Pdf(View):

    def get(self, request):
        # sales = Sales.objects.all()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        SHEET_NAME = "Apr - Mar " +datetime.now().strftime("%Y")
        up = user_profile.objects.get(user_id=request.user.id)
        range = "!"+str(up.student_performance_row)+':'+str(up.student_performance_row)
        values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

        # print(values)
        today = timezone.now()
        params = {
            'today': today,
            'name': request.user.first_name,
            'contact': values[0][2]
        }
        print(bin(Render.render('student/pdf.html', params).as_view()))
        return Render.render('student/pdf.html', params)

