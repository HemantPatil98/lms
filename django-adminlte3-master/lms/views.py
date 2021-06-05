from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from datetime import datetime
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import itertools
import os

from .models import notice,user_profile,extra_data,certificate_request,groupsinfo
from .extra_functions import randomstring,mail,mailletter
from .sheetfields import student_profile,student_performance,attendance,batch_schedule,feedback
from .pdfgenerator import Render,Pdf
from . import sheetsapi
from exam.models import course

# Create your views here.

###
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)

        if us is not None:
            try:
                ab = user_profile.objects.get(user_id=us.id)
                vars(ab)['_state'] = None
                request.session['ab']=vars(ab)
                # print(vars(request.session))
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
            if request.user.is_authenticated:
                us = authenticate(username=request.user.username,password=request.POST['oldpassword'])
                if us is not None:
                    us.set_password(request.POST['password'])
                    us.save()
                    login(request, us)
                    messages.success(request, 'Password reset succesful')
                    return redirect('index')
                else:
                    return redirect('reset_password')

            else:
                us = User.objects.filter(username=request.POST['username'])
                if len(us)==1:
                    us =us[0]
                    password = randomstring(request)
                    us.set_password(password)
                    us.save()
                    header = 'To:' + us.username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

                    message = header + '\n Username: ' + us.username + '\n New Password: ' + password + ' \n\n'
                    mail(us.email, message)

                    print(message)
                    messages.success(request,'Password reset successfully')
                    messages.success(request,'Check email for new password')
                    return redirect(login_form)
                else:
                    messages.error(request,'Username Not Found')
                    return redirect(reset_password)
        except:
            messages.error(request,'Error')
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

        performance = dict(zip(student_performance, values[0]))  # list data to object

        us = User.objects.get(id=request.user.id)
        gps = us.groups.all()

        per = {}
        for g in gps:
            gpinfo = groupsinfo.objects.get(group=g.id)
            courses = course.objects.values_list('name', flat=True).distinct()
            for c in courses:
                cper = []
                if gpinfo.course == c:
                    if len(g.permissions.filter(name="video")):
                        cper.append('video')
                    if len(g.permissions.filter(name="notes")):
                        cper.append('notes')
                    if len(g.permissions.filter(name="exam")):
                        cper.append('exam')
                    per[c]=cper


        from .models import notice

        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request, 'student/index.html', {'performance': performance,'notice':notice1,'up':up,'per':per,'profile':""})

###
@login_required(login_url='')
def addstudent(request):
    if request.method == 'POST':
        from .models import user_profile
        profile = [['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-4)+1)', ""], ["", ""], ["", ""], ["", ""]]
        for field in itertools.islice(request.POST, 2, None):
            val = request.POST.getlist(field)
            for i in range(0, 4):
                try:
                    profile[i].append(val[i])
                except:
                    profile[i].append("")
        if request.user.is_staff:
            performance = ['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)', profile[0][8],
                           profile[0][11] + "/" + profile[0][12]
                , profile[0][13], profile[0][3], profile[0][7], profile[0][5], profile[0][4], profile[0][6]]
            # print(performance)

            SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
            # print(len(performance),[""]*len(student_performance),len(student_performance)-len(performance),performance)
            performance = performance + [""]*(len(student_performance)-len(performance)) if len(performance)<len(student_performance) else performance
            print(len(performance),performance)
            performance[student_performance.index('C Total Marks')] = '=sum(INDIRECT("N"&row()),INDIRECT("O"&row()),INDIRECT("P"&row()))'
            performance[student_performance.index('Sql Total Marks')] = '=sum(INDIRECT("U"&row()),INDIRECT("V"&row()),INDIRECT("W"&row()))'
            performance[student_performance.index('WD Total Marks')] = '=sum(INDIRECT("AB"&row()),INDIRECT("AC"&row()))'
            performance[student_performance.index('Core Total Marks')] = '=sum(INDIRECT("AL"&row()),INDIRECT("AM"&row()),INDIRECT("AN"&row()))'
            performance[student_performance.index('Adv Total Marks')] = '=sum(INDIRECT("AT"&row()),INDIRECT("AU"&row(),INDIRECT("AV"&row()))'
            performance[student_performance.index('Total Marks (Out of 700)')] = '=sum(INDIRECT("Q"&row()),INDIRECT(&row()),INDIRECT("AD"&row()),INDIRECT("AM"&row()),INDIRECT("AU"&row()),INDIRECT("BA"&row()))'
            performance[student_performance.index('Eligible For Certificate(Y/N)')] = '''=IF(AND(INDIRECT("N"&ROW())>27,INDIRECT("O"&ROW())>27,INDIRECT("P"&ROW())>13,INDIRECT("U"&ROW())>27,INDIRECT("V"&ROW())>27,INDIRECT("W"&ROW())>27,INDIRECT("AB"&ROW())>105,INDIRECT("AC"&ROW())>17,NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),INDIRECT("AJ"&ROW())>27,INDIRECT("AK"&ROW())>27,INDIRECT("AL"&ROW())>13,NOT(ISBLANK(INDIRECT("AN"&ROW()))),INDIRECT("AR"&ROW())>27,INDIRECT("AS"&ROW())>27,INDIRECT("AT"&ROW())>13,NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),INDIRECT("BA"&ROW())>70,NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
            performance[student_performance.index('Eligible For Placement(Y/N)')] = '''=IF(AND(,NOT(ISBLANK(INDIRECT("N"&ROW()))),NOT(ISBLANK(INDIRECT("O"&ROW()))),NOT(ISBLANK(INDIRECT("P"&ROW()))),NOT(ISBLANK(INDIRECT("U"&ROW()))),NOT(ISBLANK(INDIRECT("V"&ROW()))),NOT(ISBLANK(INDIRECT("W"&ROW()))),NOT(ISBLANK(INDIRECT("AB"&ROW()))),NOT(ISBLANK(INDIRECT("AC"&ROW()))),NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),NOT(ISBLANK(INDIRECT("AJ"&ROW()))),NOT(ISBLANK(INDIRECT("AK"&ROW()))),NOT(ISBLANK(INDIRECT("AL"&ROW()))),NOT(ISBLANK(INDIRECT("AN"&ROW()))),NOT(ISBLANK(INDIRECT("AR"&ROW()))),NOT(ISBLANK(INDIRECT("AS"&ROW()))),NOT(ISBLANK(INDIRECT("AT"&ROW()))),NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),NOT(ISBLANK(INDIRECT("BA"&ROW()))),NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''

            if request.user.is_staff:
                performance_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[performance])
            else:
                sp = user_profile.objects.get(id=request.user.id)
                y = request.user.date_joined.strftime('%Y')
                SHEET_NAME = "Apr - Mar " + y
                performance_row = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=sp.student_performance_row,
                                                        value=[performance])

        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value

        if request.user.is_staff:
            profile_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=profile)
        else:
            sp = user_profile.objects.get(id=request.user.id)
            profile = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=sp.student_profile_row,value=profile)

        if request.user.is_staff:
            username = request.POST['emailid']
            password = randomstring(request)

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
                us_profile = user_profile.objects.get(user_id=request.user.id)
                us_profile.photo = file
                us_profile.save()
            # message to be sent

            params = {
                'addate': datetime.now(),
                'name': request.user.first_name,
                'contact': request.POST['contact']
            }
            Render.render_to_file('student/pdf.html', params)

            header = 'To:' + us.username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + username + '\n Password: ' + password + ' \n\n'
            print(message)

            mailletter(us.email,message)

            messages.info(request,'Student added successfully')
        else:
            from .models import user_profile
            try:
                file = request.FILES['photo']
                file._name = str(request.user.username +"."+ file._name.split('.')[1])
            except:
                file = ""
            us_profile = user_profile.objects.get(user_id=request.user.id)
            us_profile.photo=file
            us_profile.save()
            vars(us_profile)['_state'] = None
            request.session['ab']=vars(us_profile)
            messages.info(request,'Profile updated successfully')

        return redirect('index')

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request,'student/add_student.html',{'notice':notice1})


### #####
@login_required(login_url='')
def addgroups(request,view="false"):
    if request.method == 'POST':
        gname = request.POST['gname']
        gp = Group.objects.filter(name=gname)
        if len(gp) == 0:
            cname = request.POST['cname']
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            gp=Group(name=gname)
            gp.save()
            gpinfo = groupsinfo(group=gp,course=cname,startdate=startdate,enddate=enddate)
            gpinfo.save()
            messages.info(request,'Group created')
            SPREADSHEET_ID = extra_data.objects.get(name='Attendance').value

            sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,columns=attendance)
            messages.info(request, gname + " is added in sheet")
        else:
            gp=gp[0]
            gpinfo = groupsinfo.objects.get(group_id=gp.id)
            try:
                gpinfo.enddate = request.POST['enddate']
                gpinfo.save()
            except:
                pass
            cname = request.POST['cname']

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

        pre = {'video':'','exam':'','notes':''}
        for p in pre:
            pre[p]=len(gp.permissions.filter(name=p))

        gp_permissions = gp.permissions.all()
        groups = Group.objects.all().order_by('-id')
        members = User.objects.all().order_by('-id')

        try:
            request_member = [int(x) for x in request.POST.get('students').split(',')[:-1:]]
        except:
            request_member=[]

        if request.POST.get('students'):
            for m in members:
                if gp in m.groups.all():
                    if m.id not in request_member:
                        m.groups.remove(gp.id)
                        messages.info(request,m.first_name+" is removed")
                else:
                    if m.id in request_member:
                        m.groups.add(gp.id)
                        SPREADSHEET_ID = extra_data.objects.get(name='Attendance').value
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
        for v in os.listdir(videos):
            videolist.append(v.split(".")[0])

        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        courses = course.objects.values_list('name', flat=True).distinct()
        return render(request,'student/add_groups.html',{'gname':gp,'permissions':Permission.objects.all()[68::],'pre':pre,
                                                        'members':members,'memb_pre':memb_pre,'up':up,'groups':groups,
                                                         'notice':notice1,'vpermissions':videolist,'courses':courses,
                                                         'gpinfo':gpinfo,'gp_permissions':gp_permissions,'view':view})
    groups = Group.objects.all()
    courses = course.objects.values_list('name', flat=True).distinct()

    return render(request,'student/add_groups.html',{'groups':groups,'courses':courses,'view':view})

###
@login_required(login_url='')
def addusers(request):
    if request.method == "POST":
        gp = Group.objects.filter(name=request.POST['gname'])[0]
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        us = User.objects.filter(username=email)
        if len(us)==0:
            us = User(username=email,first_name=fname,last_name=lname,email=email,password=randomstring(request),is_staff=True)
            us.save()
            messages.info(request,"User added successfully")
            # message to be sent
            header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + us.username + '\n Password: ' + us.password + ' \n\n'
            print(message)

            mail(us.email,message)

        else:
            us = us[0]

        if request.POST.getlist('permissions'):
            if request.POST['gname']:
                us_gp = [us_gp.id for us_gp in us.groups.all()]
                if gp.id not in us_gp:
                    us.groups.add(gp.id)

            add_per = [Permission.objects.get(id=add_per).id for add_per in request.POST['permissions'].split(',')[:-1:]]
            usr_per = [usr_per.id for usr_per in Permission.objects.filter(user=us)]
            for per in add_per:
                if per not in gp_per:
                    us.user_permissions.add(per)
                    us.save()

            for per in usr_per:
                if per not in add_per:
                    us.user_permissions.remove(per)
                    us.save()

        usr_per = [usr_per.id for usr_per in Permission.objects.filter(user=us)]
        perm = {'group_per':gp_per,'user_per':usr_per}
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]

        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        return render(request, 'student/add_users.html', {'groups': Group.objects.all(),'gname':gp.name,'perm':perm,
                                                          'permissions':Permission.objects.filter(id__gte=64),'member':us,'up':up,
                                                          'notice':notice1})

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_users.html',{'groups':Group.objects.all(),'up':up,'notice':notice1})

###
@login_required(login_url='')
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

###
def sheetdata(request,table):
    SPREADSHEET_ID = extra_data.objects.get(name=table).value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    if table=='attendance':
        return render(request,'student/attendance.html',{'sheetnames':SHEET_NAMES,"table":table,'notice1':notice1})
    return render(request,'student/sheet_data.html',{'sheetnames':SHEET_NAMES,"table":table,'notice':notice1})

###
@login_required(login_url='')
def viewmembers(request):
    groups = Group.objects.all()
    gnames = []
    for g in groups:
        gnames.append(g.name)

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request, 'student/view_users.html', {'sheetnames': gnames,'notice':notice1})

###
@login_required(login_url='')
def viewprofile(request):
    sheetid = extra_data.objects.get(name='student_profile').value
    up = user_profile.objects.get(user_id=request.user.id)
    row = up.student_performance_row
    range = "!A"+str(row)+":AS"+str(row+3)

    values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)
    profile = [dict(zip(student_profile,values[0])),dict(zip(student_profile,values[1])),
               dict(zip(student_profile,values[2])),dict(zip(student_profile,values[3]))] #list data to object

    up = user_profile.objects.get(user_id=request.user.id)
    try:
        rc = certificate_request.objects.get(student_id=request.user.id)
    except:
        rc = ""

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    up = user_profile.objects.get(user_id=request.user)
    performance_row = up.student_performance_row
    y = request.user.date_joined.strftime('%Y')
    SHEET_NAME = "Apr - Mar " + y
    range = "!" + str(performance_row) + ":" + str(performance_row)
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

    performance = dict(zip(student_performance, values[0]))  # list data to object

    return render(request,'student/profile.html',{'profile':profile,'up':up,'rc':rc,'notice':notice1,
                                                  'performance':performance})

###
@login_required(login_url='')
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

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/view_notice.html',{'up':up,'data':page,'notice':notice1})

###
@login_required(login_url='')
def attendance(request):
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/attendance.html',{'sheetnames':SHEET_NAMES,'notice':notice1})

###
@login_required(login_url='')
def studentattendance(request):
    us = User.objects.get(id=request.user.id)
    gps = us.groups.all()
    data =[]
    SPREADSHEET_ID = extra_data.objects.get(name='Attendance').value
    for g in gps:
        c = groupsinfo.objects.get(group=g.id).course
        value = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=g.name)
        for v in value:
            # print(us.id,int(v[1]),us.id == int(v[1]))
            if us.id == int(v[1]):
                # print(len(v)-6,v.count('p'))
                data.append({'course':c,'per':round(v.count('p')/(len(v)-6)*100,2)})

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/studentattendance.html',{'notice':notice1,'data':data,'gps':gps})

###
@login_required(login_url='')
def addnotice(request):
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

    up = user_profile.objects.all().filter(user_id=request.user.id)[0]

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/add_notice.html',{'data':page,'up':up,'notice':notice1})

###
@login_required(login_url='')
def request_certificate(request):
    cr = certificate_request(student_id=request.user)
    cr.save()
    us = user_profile.objects.get(user_id=request.user.id)
    us.certificate=cr
    us.save()
    messages.info(request,'certificate saved Successfully')
    return redirect('index')

###
@login_required(login_url='')
def addcertificate(request):
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/add_certificate.html',{'notice':notice1})

###
def sendotp(request):
    otp = randomstring(request)
    us = User.objects.all().filter(username=request.GET['username'])
    if len(us)==1:
        up = user_profile.objects.all().filter(user_id=us[0].id)
        if len(up)==0:
            up = user_profile(user_id=request.user,otp=otp)
        else:
            up=up[0]

        up.otp=otp
        up.save()

        header = 'To:' + us[0].username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS OTP \n'

        message = header + '\n Username: ' + us[0].username + '\n OTP: ' + otp + ' \n\n'
        print(message)

        if mail(us[0].email,message) == 'success':
            return HttpResponse("Otp send successfully")
        else:
            return HttpResponse("Failed to send otp")
    else:
        return HttpResponse("Username not found")


###
@login_required(login_url='')
def addfeedback(request):

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


    feedback = data+data1

    SPREADSHEET_ID = extra_data.objects.get(name='Feedback').value

    feedback = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[feedback])

    request.session['feedback'] = False
    return redirect("index")

###
@login_required(login_url='')
def viewfeedback(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    SPREADSHEET_ID = extra_data.objects.get(name='Feedback').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""

    return render(request, 'student/view_feedback.html', {'up': up, 'sheetnames': SHEET_NAMES, 'notice': notice1})

###
@login_required(login_url='')
def schedule(request):
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    return render(request,'student/schedule.html',{'notice': notice1})


@login_required(login_url='')
def pdftest(request):
    return render(request,'student/pdf.html')



####
@login_required(login_url='')
def get_data(request,table):
    SPREADSHEET_ID = extra_data.objects.get(name=table).value
    SHEET_NAME = request.GET['sheetname']

    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=SHEET_NAME,range='!A:GZ')
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
    # messages.info(request,'Data fetch successfully')
    return HttpResponse(str(data))

###
@login_required(login_url='')
def set_data(request,table):
    print(request.GET)
    if table != 'attendance':
        rowv = request.GET.getlist('rowv[]')
        row = rowv[0]
        rowv = rowv[1::]
        SHEET_NAME = request.GET['sheetname']
        if table == 'student_profile':
            SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
        if table == 'student_performance':
            SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
            rowv[student_performance.index('C Total Marks')] = '=sum(INDIRECT("N"&row()),INDIRECT("O"&row()),INDIRECT("P"&row()))'
            rowv[student_performance.index('Sql Total Marks')] = '=sum(INDIRECT("U"&row()),INDIRECT("V"&row()),INDIRECT("W"&row()))'
            rowv[student_performance.index('WD Total Marks')] = '=sum(INDIRECT("AB"&row()),INDIRECT("AC"&row()))'
            rowv[student_performance.index('Core Total Marks')] = '=sum(INDIRECT("AL"&row()),INDIRECT("AM"&row()),INDIRECT("AN"&row()))'
            rowv[student_performance.index('Adv Total Marks')] = '=sum(INDIRECT("AT"&row()),INDIRECT("AU"&row(),INDIRECT("AV"&row()))'
            rowv[student_performance.index('Total Marks (Out of 700)')] = '=sum(INDIRECT("Q"&row()),INDIRECT(&row()),INDIRECT("AD"&row()),INDIRECT("AM"&row()),INDIRECT("AU"&row()),INDIRECT("BA"&row()))'
            rowv[student_performance.index('Eligible For Certificate(Y/N)')] = '''=IF(AND(INDIRECT("N"&ROW())>27,INDIRECT("O"&ROW())>27,INDIRECT("P"&ROW())>13,INDIRECT("U"&ROW())>27,INDIRECT("V"&ROW())>27,INDIRECT("W"&ROW())>27,INDIRECT("AB"&ROW())>105,INDIRECT("AC"&ROW())>17,NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),INDIRECT("AJ"&ROW())>27,INDIRECT("AK"&ROW())>27,INDIRECT("AL"&ROW())>13,NOT(ISBLANK(INDIRECT("AN"&ROW()))),INDIRECT("AR"&ROW())>27,INDIRECT("AS"&ROW())>27,INDIRECT("AT"&ROW())>13,NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),INDIRECT("BA"&ROW())>70,NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
            rowv[student_performance.index('Eligible For Placement(Y/N)')] = '''=IF(AND(,NOT(ISBLANK(INDIRECT("N"&ROW()))),NOT(ISBLANK(INDIRECT("O"&ROW()))),NOT(ISBLANK(INDIRECT("P"&ROW()))),NOT(ISBLANK(INDIRECT("U"&ROW()))),NOT(ISBLANK(INDIRECT("V"&ROW()))),NOT(ISBLANK(INDIRECT("W"&ROW()))),NOT(ISBLANK(INDIRECT("AB"&ROW()))),NOT(ISBLANK(INDIRECT("AC"&ROW()))),NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),NOT(ISBLANK(INDIRECT("AJ"&ROW()))),NOT(ISBLANK(INDIRECT("AK"&ROW()))),NOT(ISBLANK(INDIRECT("AL"&ROW()))),NOT(ISBLANK(INDIRECT("AN"&ROW()))),NOT(ISBLANK(INDIRECT("AR"&ROW()))),NOT(ISBLANK(INDIRECT("AS"&ROW()))),NOT(ISBLANK(INDIRECT("AT"&ROW()))),NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),NOT(ISBLANK(INDIRECT("BA"&ROW()))),NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=int(row)+1, value=[rowv])
    elif table == 'attendance':
        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
        rowv = request.GET.getlist('rowv[]')
        row = request.GET['row']
        SHEET_NAME = request.GET['sheetname']
        # print(rowv)
        if (type(rowv[0])==int):
            rowv = [x for x in rowv]
        else:
            rowv = [int(x) for x in rowv]
        # print(rowv)

        # rowv.sort()
        date = datetime.now()
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")

        currentdate=day+"/"+month+"/"+year
        present = [currentdate]

        for i in range(0,max(rowv)+1):
            if i in rowv:
                present.append("p")
            else:
                present.append("")
        print(rowv,max(rowv),present)
        row = int(row) if request.GET['update']=='true' else int(row)+1
        # col=""
        # while row>1:
        #     col+=(chr((row%26)+65))
        #     row = row/26

        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,value=[present],SHEET_NAME=SHEET_NAME,col=row,row=0,dimension="COLUMNS")
        # messages.info(request,'Data saved successfully')
    return HttpResponse("success")

###
@login_required(login_url='')
def attendance_update(request):
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    rowv = request.GET.getlist('rowv[]')
    row = request.GET['row']
    SHEET_NAME = request.GET['sheetname']

    if (type(rowv[0]) == int):
        rowv = [x for x in rowv]
    else:
        rowv = [int(x) for x in rowv]

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
@login_required(login_url='')
def get_user(request):
    gname = request.GET['gname']
    gp = Group.objects.get(name=gname)
    members = User.objects.all().filter(groups=gp.id)
    memb = []
    abc = []
    for m in members:
        vars(m)['_state']='None'
        key = list(vars(m).keys())
        memb1 = []
        for i in key:
            memb1.append(str(vars(m)[i]))
        key = [k.upper() for k in key]
        memb.append(dict(zip(key,memb1)))
        abc.append(m)
    memb = str(memb).lstrip('_').replace('"','').replace('FIRST_NAME','NAME').replace("True","true").replace("False",'')
    return HttpResponse(str(memb))

###
@login_required(login_url='')
def set_user(request):
    values = request.GET['values'].replace('{','').replace('}','').replace('"','').replace("'",'').split(',')
    val={}
    for i in values:
        kv=i.split(':')
        val[kv[0].lower()]=kv[1]
    us = User.objects.get(id=val['id'])
    us.is_staff = val['is_staff'].capitalize()
    us.is_active = val['is_active'].capitalize()
    us.save()
    # messages.info(request,'Changes saved successfully')
    return HttpResponse('succcess')

###
@login_required(login_url='')
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
    # print(us)
    # for u in us:
    #     st = user_profile.objects.get(user_id=u).student_performance_row
    #     print(st)
    #     v = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname='Apr - Mar 2021',range='!'+str(st)+':'+str(st))
    #     print(v[0][13:17]+v[0][20:24]+v[0][27:30]+v[0][38:41]+v[0][46:49])
    return HttpResponse(str(data).replace('False','false').replace('True','true').replace('_',' '))

###
@csrf_exempt
@login_required(login_url='')
def setcertificate(request):

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
    cr.certificate_status = request.POST['certificate_status']
    cr.save()

    return HttpResponse(str(cr.certificate))


###
@login_required(login_url='')
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

###
@login_required(login_url='')
def students_current_groups(request,gname):
    data = []
    g = Group.objects.get(name=gname)
    for u in User.objects.filter(groups=g.id):
        data.append({'uname': u.first_name, 'uid': u.id,'selected':"true"})

    return HttpResponse(str(data).replace("'",'"'))





def calender(request):
    SPREADSHEET_ID = extra_data.objects.get(name='Batch_Schedule').value
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

def getcalenderevents(request):
    SPREADSHEET_ID = extra_data.objects.get(name='Batch_Schedule').value
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname="Sheet 1")
    data = []
    for v in values:
        event = {}
        event['title'] = v[1] + " / " + v[3]
        event['startTime'] = v[0].split('-')[0]
        event['endTime'] = v[0].split('-')[1]
        event['allDay']= False
        data.append(event)
    data = str(data).replace("'",'"').replace('False','false')
    return HttpResponse(data)

