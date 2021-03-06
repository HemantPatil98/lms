from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from datetime import datetime
from django.contrib.auth.models import User,Group,Permission
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import itertools
import os

from .models import user_profile,extra_data,certificate_request,groupsinfo
from .extra_functions import randomstring,mail,mailletter
from .sheetfields import student_profile,student_performance,all_fields_index,marks
from .pdfgenerator import Render
from . import sheetsapi, sheetfields
from exam.models import course

# Create your views here.

excluded_groups=["Admin","Trainer","Hr"]

###
def config():
    sheetsapi.startsheet()
    sheetfields.indexing_fields()
    sheetfields.make_media_directory()
    try:
        p = Permission(content_type_id=7,name='exam',codename='exam')
        p.save()
        p = Permission(content_type_id=7,name='video',codename='video')
        p.save()
        p = Permission(content_type_id=7,name='notes',codename='noted')
        p.save()
    except:
        pass

    dashboard_permissions = ["student","group","member","attendance","performance","notice","certificate","questions"
        ,"evaluate","timeline","feedback","video_permissions"]

    for i in dashboard_permissions:
        try:
            p = Permission(content_type_id=18,name=i,codename=i)
            p.save()
        except:
            pass
    return HttpResponse("")

def error(request):
    return render(request,'student/base.html')

###
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)

        if us is not None:

            if us.last_login != None:
                login(request, us)
                messages.success(request, "Successfully Log In")
                request.session['profile_photo'] = str(user_profile.objects.get(user_id=request.user.id).photo)
                return redirect(index)
            else:
                if not us.is_staff:
                    params = {
                        'id': us.id,
                        'addate': us.date_joined,
                        'today': datetime.now(),
                        'name': us.first_name,
                        'contact':'1234567890',
                    }
                    Render.render_to_file('student/pdf.html', params)
                    # return render(request,'student/declaration.html',{'username':us.username})
                    request.session['username'] = us.username
                    return redirect('declaration')
                else:
                    login(request, us)
                    messages.success(request, "Successfully Log In")
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
    if request.user.is_authenticated:
        return redirect('index')
    else:
        return render(request, 'student/login_form.html')

###
def reset_password(request):
    if request.method=='POST':
        # try:
        if request.user.is_authenticated:
            us = authenticate(username=request.user.username,password=request.POST['oldpassword'])
            if us is not None:
                us.set_password(request.POST['password'])
                us.save()
                login(request, us)
                request.session['profile_photo'] = str(user_profile.objects.get(user_id=request.user.id).photo)
                messages.success(request, 'Password reset succesful')
                return redirect('index')
            else:
                return redirect(reset_password)
        else:
            us = User.objects.filter(username=request.POST['username'])
            if len(us)==1:
                us =us[0]
                password = randomstring(request)
                us.set_password(password)
                us.save()

                header = 'To:' + us.username + '\n' + 'From: admin@fortunecloudindia.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

                message = header + '\n Username: ' + us.username + '\n New Password: ' + password + ' \n\n'
                mail(us.email, message)

                messages.success(request,'Password reset successfully')
                messages.success(request,'Check email for new password')
                return redirect(login_form)
            else:
                messages.error(request,'Username Not Found')
                return redirect(reset_password)
        # except:
        #     messages.error(request,'Error')
        #     return redirect(reset_password)
    return render(request,'student/reset_password.html')

###
def declaration(request):
    if 'agree' in request.GET:
        if request.GET['agree'] == 'agree':
            us = User.objects.filter(username=request.session['username'])

            if len(us) == 1:
                up = user_profile.objects.get(user_id=us[0])
                up.declaration = datetime.now()
                up.save()
                login(request,us[0])
                return redirect('resspass')
            else:
                messages.info(request,"wrong user")
    return render(request,'student/declaration.html')

###
@login_required(login_url='')
def index(request):
    try:
        flag=request.user.username
    except:
        return redirect('login_form')
    if request.user.is_staff:
        response = render(request,'student/adminindex.html')
        return response
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

        up = user_profile.objects.all().filter(user_id=request.user.id)[0]

        try:
            certificate = certificate_request.objects.get(student_id=request.user)
        except:
            certificate = ""

        response = render(request, 'student/index.html', {'performance': performance,'up':up,'per':per,'profile':"",'certificate':certificate})
        return response

###
@login_required(login_url='')
def addstudent(request):
    print(request.POST)
    if request.method == 'POST':
        y = request.user.date_joined.strftime('%Y')
        SHEET_NAME = "Apr - Mar " + y
        from .models import user_profile
        profile = [['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-4)+1)',""], ["", ""], ["", ""], ["", ""]]
        for field in itertools.islice(request.POST, 2, None):
            val = request.POST.getlist(field)
            for i in range(0, 4):
                try:
                    profile[i].append(val[i])
                except:
                    profile[i].append("")
        print(profile)
        if request.user.is_staff:
            performance = ['=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)',"", profile[0][8],
                           profile[0][11] + "/" + profile[0][12]
                , profile[0][13], profile[0][3], profile[0][7], profile[0][5], profile[0][4], profile[0][6]]

            SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
            performance = performance + [""]*(len(student_performance)-len(performance)) if len(performance)<len(student_performance) else performance
            performance[student_performance.index('C Total Marks (Out of 100)')] = marks['C Total Marks (Out of 100)']
            performance[student_performance.index('Sql Total Marks (Out of 100)')] = marks['Sql Total Marks (Out of 100)']
            performance[student_performance.index('WD Total Marks (Out of 200)')] = marks['WD Total Marks (Out of 200)']
            performance[student_performance.index('Core Total Marks (Out of 100)')] = marks['Core Total Marks (Out of 100)']
            performance[student_performance.index('Adv Total Marks (Out of 100)')] = marks['Adv Total Marks (Out of 100)']
            performance[student_performance.index('Total Marks (Out of 700)')] = marks['Total Marks (Out of 700)']
            performance[student_performance.index('Eligible For Certificate(Y/N)')] = '''=IF(AND(INDIRECT("N"&ROW())>27,INDIRECT("O"&ROW())>27,INDIRECT("P"&ROW())>13,INDIRECT("U"&ROW())>27,INDIRECT("V"&ROW())>27,INDIRECT("W"&ROW())>27,INDIRECT("AB"&ROW())>105,INDIRECT("AC"&ROW())>17,NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),INDIRECT("AJ"&ROW())>27,INDIRECT("AK"&ROW())>27,INDIRECT("AL"&ROW())>13,NOT(ISBLANK(INDIRECT("AN"&ROW()))),INDIRECT("AR"&ROW())>27,INDIRECT("AS"&ROW())>27,INDIRECT("AT"&ROW())>13,NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),INDIRECT("BA"&ROW())>70,NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
            performance[student_performance.index('Eligible For Placement(Y/N)')] = '''=IF(AND(,NOT(ISBLANK(INDIRECT("N"&ROW()))),NOT(ISBLANK(INDIRECT("O"&ROW()))),NOT(ISBLANK(INDIRECT("P"&ROW()))),NOT(ISBLANK(INDIRECT("U"&ROW()))),NOT(ISBLANK(INDIRECT("V"&ROW()))),NOT(ISBLANK(INDIRECT("W"&ROW()))),NOT(ISBLANK(INDIRECT("AB"&ROW()))),NOT(ISBLANK(INDIRECT("AC"&ROW()))),NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),NOT(ISBLANK(INDIRECT("AJ"&ROW()))),NOT(ISBLANK(INDIRECT("AK"&ROW()))),NOT(ISBLANK(INDIRECT("AL"&ROW()))),NOT(ISBLANK(INDIRECT("AN"&ROW()))),NOT(ISBLANK(INDIRECT("AR"&ROW()))),NOT(ISBLANK(INDIRECT("AS"&ROW()))),NOT(ISBLANK(INDIRECT("AT"&ROW()))),NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),NOT(ISBLANK(INDIRECT("BA"&ROW()))),NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
            if request.user.is_staff:
                performance_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[performance])
            else:
                sp = user_profile.objects.get(id=request.user.id)
                performance_row = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,
                                                        row=sp.student_performance_row,value=[performance])

        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value

        if request.user.is_staff:
            profile_row = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=profile)
        else:
            sp = user_profile.objects.get(user_id=request.user)
            profile = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=sp.student_profile_row,value=profile)

        if request.user.is_staff:
            username = request.POST['emailid']
            password = randomstring(request)

            us = User.objects.create_user(username=username,first_name=request.POST['name'],
                      password=password,email=request.POST['emailid'],last_name=request.POST['contact'])
            try:
                file = request.FILES['photo']
                file._name = str(request.user.username) +"."+ file._name.split('.')[1]
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

            params = {
                'id' : us.id,
                'addate': datetime.now(),
                'name': us.first_name,
                'contact': request.POST['contact']
            }
            Render.render_to_file('student/pdf.html', params)

            header = 'To:' + us.username + '\n' + 'From: aniket.pawar@cravitaindia.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'
            matter = '''Dear Candidate,

 

Thank you for enrolling for Job enabling Training program ( EDGE) at Fortune Cloud Technologies. Your admission has been confirmed.

We welcome you to Fortune Cloud family and look forward to many years of a mutually beneficial association. 

Our incredible process has made us unique and by following this process & the rules will certainly make you reach your career destination.

 

PFA the attached execution process..

For any concern, feel free to contact us on 9766439090

 

Kindly acknowledge the receipt of this mail.

 

 

--

Thanks & Regards,

Fortune Cloud Technologies Group

IT Training | Recruitment Services

Contact: +91 ??? 9766439090 | www.fortunecloudindia.com

 

 '''
            message = matter + '\n Username: ' + username + '\n Password: ' + password + ' \n'+'Link:- lms.fortunecloudindia.com\n\n'

            if mailletter(us.email,message) == False:
                messages.error(request,'Failed to add student')
            else:
                us.save()
            messages.success(request,us.username+' added successfully')
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
            messages.info(request,'Profile updated successfully')
            request.session['profile_photo'] = str(us_profile.photo)
        return redirect('index')

    return render(request,'student/add_student.html')

###
@login_required(login_url='')
def addgroups(request,view=False):
    if request.method == 'POST':
        gname = request.POST['gname']
        gp = Group.objects.filter(name=gname)
        groups = Group.objects.all().order_by('-id')
        members = User.objects.all().order_by('-id')
        gpinfo = ""

        if len(gp) == 0:
            cname = request.POST['cname']
            startdate = request.POST['startdate']
            enddate = request.POST['enddate']
            gp=Group(name=gname)
            videos = "media/videos/courses/" + cname
            if not os.path.exists(videos):
                os.mkdir(videos)
            gp.save()
            gpinfo = groupsinfo(group=gp,course=cname,startdate=startdate,enddate=enddate)
            gpinfo.save()
            messages.info(request,'Group created')
            SPREADSHEET_ID = extra_data.objects.get(name='attendance').value

            sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,columns=sheetfields.attendance)
            messages.success(request, gname + " is added in sheet")
            return redirect('addgroups')
        else:
            gp=gp[0]
            gpinfo = groupsinfo.objects.get(group_id=gp.id)


            if 'enddate' in request.POST:
                gpinfo.enddate = request.POST['enddate']
                gpinfo.save()
            cname = request.POST['cname']

        if 'videopermission' in request.POST:
            for p in gp.permissions.all():
                if p.name not in request.POST.getlist('videopermission'):
                    gp.permissions.remove(p.id)
            for p in request.POST.getlist('videopermission'):
                p = Permission.objects.get(name=p)
                if p not in gp.permissions.all():
                    gp.permissions.add(p)

        if 'pervideo' in request.POST or 'perexam' in request.POST or 'pernotes' in request.POST:
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

        if 'students' in request.POST:
            request_member = [int(x) for x in request.POST.get('students').split(',')[:-1:] if x != '']
            for m in members:
                all_groups = m.groups.all()
                if gp in all_groups:
                    if m.id not in request_member:
                        m.groups.remove(gp.id)
                        messages.success(request,m.first_name+" is removed")
                elif(len(all_groups)<6):
                    if m.id in request_member:
                        m.groups.add(gp.id)

                        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
                        index = '=IF(INDIRECT("A"&ROW()-1)="ID",1,INDIRECT("A"&ROW()-1)+1)'
                        values = [index,m.id,m.first_name,m.last_name,m.email]
                        sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,values=[values])
                        messages.info(request,m.first_name+" is added")

                        up = user_profile.objects.get(id=request.user.id)

                        performance_row = up.student_performance_row
                        y = request.user.date_joined.strftime('%Y')
                        SHEET_NAME = "Apr - Mar " + y
                        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
                        if not m.is_staff and cname=='C':
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.user.username],col=all_fields_index['student_performance']['C Trainer Name'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['startdate']],col=all_fields_index['student_performance']['C module start date'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['enddate']],col=all_fields_index['student_performance']['C module end date'],cell=True)
                        if not m.is_staff and cname=='SQL':
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.user.username],col=all_fields_index['student_performance']['Sql Trainer Name'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['startdate']],col=all_fields_index['student_performance']['Sql module start date'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['enddate']],col=all_fields_index['student_performance']['Sql module end date'],cell=True)
                        if not m.is_staff and cname=='WD':
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.user.username],col=all_fields_index['student_performance']['WD Trainer Name'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['startdate']],col=all_fields_index['student_performance']['WD module start date'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['enddate']],col=all_fields_index['student_performance']['WD module end date'],cell=True)
                        if not m.is_staff and cname.find('Core'):
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.user.username],col=all_fields_index['student_performance']['Core Trainer Name'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['startdate']],col=all_fields_index['student_performance']['Core module start date'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['enddate']],col=all_fields_index['student_performance']['Core module end date'],cell=True)
                        if not m.is_staff and cname.find('Adv'):
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.user.username],col=all_fields_index['student_performance']['Adv Trainer Name'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['startdate']],col=all_fields_index['student_performance']['Adv module start date'],cell=True)
                            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME,row=performance_row,
                                                  value=[request.POST['enddate']],col=all_fields_index['student_performance']['Adv module end date'],cell=True)
                else:
                    messages.error(request,m.first_name + ' Group limit exceed')

        memb_pre = []  # group existing members
        for m in members:
            if len(m.groups.filter(name=gname))==1:
                memb_pre.append(m)

        videolist = []

        videos = "media/videos/courses/" + gpinfo.course
        for v in os.listdir(videos):
            videolist.append(v.split(".")[0])

        videolist.sort()

        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        courses = course.objects.values_list('name', flat=True).distinct()

        return render(request,'student/add_groups.html',{'gname':gp,'permissions':Permission.objects.all()[68::],'pre':pre,
                                                        'members':members,'memb_pre':memb_pre,'up':up,
                                                         'vpermissions':videolist,'courses':courses,
                                                         'gpinfo':gpinfo,'gp_permissions':gp_permissions,'view':view})
    groups = Group.objects.all()
    courses = course.objects.values_list('name', flat=True).distinct()

    return render(request,'student/add_groups.html',{'groups':groups,'courses':courses,'view':view})

###
@login_required(login_url='')
def deletegroups(request,gname):
    gp = Group.objects.filter(name=gname)
    for u in User.objects.all():
        if u.groups.filter(name=gname):
            up = user_profile.objects.filter(user_id=u.id)
            up.delete()
            u.delete()
    gp.delete()
    return redirect(index)

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
            password = randomstring(request)
            us = User(username=email,first_name=fname,last_name=lname,email=email,is_staff=True)
            us.set_password(password)
            messages.success(request,"User added successfully")
            # message to be sent
            header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'
            message = header + '\n Username: ' + us.username + '\n Password: ' + password + ' \n\n'

            if mail(us.email,message):
                us.save()
                us.groups.add(gp.id)
        else:
            us = us[0]

        files = request.FILES['photo'] if 'photo' in request.FILES else ''
        us_profile = user_profile(user_id=us) if len(user_profile.objects.filter(user_id=us))==0 else user_profile.objects.get(user_id=us)
        us_profile.photo = files
        us_profile.save()

        if 'permissions' in request.POST and 'gname' in request.POST:
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

        #return render(request, 'student/add_users.html', {'groups': Group.objects.all(),'gname':gp.name,'perm':perm,
         #                                                 'permissions':Permission.objects.filter(id__gte=64),'member':us,'up':up })
        return redirect('index')
    return render(request,'student/add_users.html',{'groups':Group.objects.all().order_by('-id')})

###
@login_required(login_url='')
def reset_user_password(request):
    username = request.GET['username']
    us = User.objects.filter(username=username)
    if us is not None:
        us = us[0]
        password = randomstring(request)
        us.set_password(password)
        us.save()
        header = 'To:' + us.username + '\n' + 'From: admin@fortunecloudindia.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'
        message = header + '\n Username: ' + us.username + '\n New Password: ' + password + ' \n\n'
        mail(us.email,message)
        messages.success("Password Reset Successfull")
    return HttpResponse()

###
@login_required(login_url='')
def user_permissions(request):
    uid = request.GET['uid']
    us = User.objects.get(id=int(uid))
    per = []
    a = Permission.objects.filter(user=uid)
    for i in Permission.objects.all():
        p = Permission.objects.get(id=i.id)
    if p in a:
        per.append({'name':p.name,'value':p.id,'selected':'true'})
    else:
        per.append({'name':p.name,'value':p.id})
    return HttpResponse(str(per).replace("'",'"'))

###
def sheetdata(request,table):
    SPREADSHEET_ID = extra_data.objects.get(name=table).value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    if table=='attendance':
        return render(request,'student/attendance.html',{'sheetnames':SHEET_NAMES,"table":table})
    return render(request,'student/sheet_data.html',{'sheetnames':SHEET_NAMES,"table":table})

###
@login_required(login_url='')
def viewmembers(request):
    groups = Group.objects.all()
    gnames = []
    for g in groups:
        gnames.append(g.name)
    return render(request, 'student/view_users.html', {'sheetnames': gnames})

###
@login_required(login_url='')
def viewprofile(request):
    sheetid = extra_data.objects.get(name='student_profile').value
    up = user_profile.objects.get(user_id=request.user.id)
    row = up.student_profile_row
    range = "!A"+str(row)+":AS"+str(row+3)

    values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)

    student_profile1 = [x.replace(' ','') for x in student_profile]

    profile = [dict(zip(student_profile1,values[0])),dict(zip(student_profile1,values[1])),
               dict(zip(student_profile1,values[2])),dict(zip(student_profile1,values[3]))] #list data to object

    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    up = user_profile.objects.get(user_id=request.user)
    performance_row = up.student_performance_row
    y = request.user.date_joined.strftime('%Y')
    SHEET_NAME = "Apr - Mar " + y
    range = "!" + str(performance_row) + ":" + str(performance_row)
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

    performance = dict(zip(student_performance, values[0]))  # list data to object

    try:
        certificate = certificate_request.objects.get(student_id=request.user)
    except:
        certificate = ""

    return render(request,'student/profile.html',{'profile':profile,'up':up,'certificate':certificate,'performance':performance})

###
@login_required(login_url='')
def attendance(request):
    gnames = Group.objects.all().exclude(name__in=excluded_groups) if request.user.is_superuser else request.user.groups.all().exclude(name__in=excluded_groups)
    gnames = [x.name for x in gnames]

    return render(request,'student/attendance.html',{'sheetnames':gnames})

###
@login_required(login_url='')
def studentattendance(request):
    us = User.objects.get(id=request.user.id)
    gps = us.groups.all()
    data =[]
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    for g in gps:
        c = groupsinfo.objects.get(group=g.id).course
        value = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=g.name)
        for v in value:
            if us.id == int(v[1]) and len(v)>6:
                data.append({'course':c,'per':round(v.count('p')/(len(v)-6)*100,2)})

    return render(request,'student/studentattendance.html',{'data':data,'gps':gps})

###
@login_required(login_url='')
def request_certificate(request):
    if not len(certificate_request.objects.filter(student_id=request.user)):
        cr = certificate_request(student_id=request.user)
        cr.save()
        us = user_profile.objects.get(user_id=request.user.id)
        us.certificate=cr
        us.save()
        messages.success(request,'Certificate Request Saved Successfully')
    else:
        messages.info(request,'Certificate Request Saved Already')
    return redirect('index')

###
@login_required(login_url='')
def addcertificate(request):
    return render(request,'student/add_certificate.html')

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

        header = 'To:' + us[0].username + '\n' + 'From: admin@fortunecloudindia.com  \n' + 'Subject:Fortune Cloud LMS OTP \n'
        message = header + '\n Username: ' + us[0].username + '\n OTP: ' + otp + ' \n\n'

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

    SPREADSHEET_ID = extra_data.objects.get(name='feedback').value
    feedback = sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID, values=[feedback])

    request.session['feedback'] = False
    return redirect("index")

###
@login_required(login_url='')
def viewfeedback(request):
    SPREADSHEET_ID = extra_data.objects.get(name='feedback').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    return render(request, 'student/view_feedback.html', {'sheetnames': SHEET_NAMES})

###
@login_required(login_url='')
def schedule(request):
    SPREADSHEET_ID = extra_data.objects.get(name='batch_schedule').value
    SHEET_NAME = 'Schedule'

    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=SHEET_NAME,range='!A:H')
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
    return render(request,'student/schedule1.html',{'data':data})

###
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


    if table == 'attendance' and not request.user.is_staff:
        data1 = []
        for d in data:
            if int(d['USER_ID']) == request.user.id:
                data1.append(d)
                break
        data = data1

    return HttpResponse(str(data))

###
@login_required(login_url='')
def set_data(request,table):
    try:
        if table != 'attendance':
            rowv = request.GET.getlist('rowv[]')
            row = rowv[0]
            rowv = rowv[1::]
            SHEET_NAME = request.GET['sheetname']
            if table == 'student_profile':
                SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
            if table == 'student_performance':
                SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
                rowv[student_performance.index('C Total Marks (Out of 100)')] = marks['C Total Marks (Out of 100)']
                rowv[student_performance.index('Sql Total Marks (Out of 100)')] = marks['Sql Total Marks (Out of 100)']
                rowv[student_performance.index('WD Total Marks (Out of 200)')] = marks['WD Total Marks (Out of 200)']
                rowv[student_performance.index('Core Total Marks (Out of 100)')] = marks['Core Total Marks (Out of 100)']
                rowv[student_performance.index('Adv Total Marks (Out of 100)')] = marks['Adv Total Marks (Out of 100)']
                rowv[student_performance.index('Total Marks (Out of 700)')] = marks['Total Marks (Out of 700)']
                rowv[student_performance.index('Eligible For Certificate(Y/N)')] = '''=IF(AND(INDIRECT("N"&ROW())>27,INDIRECT("O"&ROW())>27,INDIRECT("P"&ROW())>13,INDIRECT("U"&ROW())>27,INDIRECT("V"&ROW())>27,INDIRECT("W"&ROW())>27,INDIRECT("AB"&ROW())>105,INDIRECT("AC"&ROW())>17,NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),INDIRECT("AJ"&ROW())>27,INDIRECT("AK"&ROW())>27,INDIRECT("AL"&ROW())>13,NOT(ISBLANK(INDIRECT("AN"&ROW()))),INDIRECT("AR"&ROW())>27,INDIRECT("AS"&ROW())>27,INDIRECT("AT"&ROW())>13,NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),INDIRECT("BA"&ROW())>70,NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
                rowv[student_performance.index('Eligible For Placement(Y/N)')] = '''=IF(AND(,NOT(ISBLANK(INDIRECT("N"&ROW()))),NOT(ISBLANK(INDIRECT("O"&ROW()))),NOT(ISBLANK(INDIRECT("P"&ROW()))),NOT(ISBLANK(INDIRECT("U"&ROW()))),NOT(ISBLANK(INDIRECT("V"&ROW()))),NOT(ISBLANK(INDIRECT("W"&ROW()))),NOT(ISBLANK(INDIRECT("AB"&ROW()))),NOT(ISBLANK(INDIRECT("AC"&ROW()))),NOT(ISBLANK(INDIRECT("AE"&ROW()))),NOT(ISBLANK(INDIRECT("AF"&ROW()))),NOT(ISBLANK(INDIRECT("AJ"&ROW()))),NOT(ISBLANK(INDIRECT("AK"&ROW()))),NOT(ISBLANK(INDIRECT("AL"&ROW()))),NOT(ISBLANK(INDIRECT("AN"&ROW()))),NOT(ISBLANK(INDIRECT("AR"&ROW()))),NOT(ISBLANK(INDIRECT("AS"&ROW()))),NOT(ISBLANK(INDIRECT("AT"&ROW()))),NOT(ISBLANK(INDIRECT("AY"&ROW()))),NOT(ISBLANK(INDIRECT("AZ"&ROW()))),NOT(ISBLANK(INDIRECT("BA"&ROW()))),NOT(ISBLANK(INDIRECT("BB"&ROW())))),"Y","N")'''
            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=int(row)+1, value=[rowv])
            return HttpResponse('Success')

        elif table == 'attendance':
            SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
            rowv = request.GET.getlist('rowv[]')
            row = request.GET['row']
            SHEET_NAME = request.GET['sheetname']
            date = datetime.now()
            day = date.strftime("%d")
            month = date.strftime("%m")
            year = date.strftime("%Y")
            currentdate = day + "/" + month + "/" + year
            present = [currentdate]

            if len(rowv):
                rowv = [int(x) for x in rowv]
                for i in range(0, max(rowv) + 1):
                    if i in rowv:
                        present.append("p")
                    else:
                        present.append("")
            else:
                rowv = [""]*50
                present += rowv



            row = int(row) if request.GET['update']=='true' else int(row)+1

            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,value=[present],SHEET_NAME=SHEET_NAME,col=row,row=0,dimension="COLUMNS")
            return HttpResponse('Success')
    except:
        return HttpResponse('Failed')

###
@login_required(login_url='')
def attendance_update(request):
    try:
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
        return HttpResponse('Success')
    except:
        return HttpResponse('Failed')

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
    try:
        values = request.GET['values'].replace('{','').replace('}','').replace('"','').replace("'",'').split(',')
        val={}
        for i in values:
            kv=i.split(':')
            val[kv[0].lower()]=kv[1]
        us = User.objects.get(id=val['id'])
        us.is_staff = val['is_staff'].capitalize()
        us.is_active = val['is_active'].capitalize()
        us.save()
        return HttpResponse('Success')
    except:
        return HttpResponse('Failed')

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

    return HttpResponse(str(data).replace('False','false').replace('True','true').replace('_',' '))

###
@csrf_exempt
@login_required(login_url='')
def setcertificate(request):
    cn = request.POST['certificate_number']

    try:
        file = request.FILES['file']
        file._name = cn + "." + file._name.split('.')[1]
    except:
        file = ""
    id = request.POST['id']
    cr = certificate_request.objects.get(id=id)
    cr.certificate_number = cn
    if file != "":
        cr.certificate = file
    cr.certificate_status = request.POST['certificate_status']
    cr.save()

    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value

    row = user_profile.objects.get(user_id=cr.student_id).student_performance_row


    y = request.user.date_joined.strftime('%Y')
    SHEET_NAME = "Apr - Mar " + y

    values = sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID,SHEET_NAME=SHEET_NAME,row=row,
                                   col=all_fields_index['student_performance']['Certificate No'],
                                   value=[cr.certificate_number],cell=True)
    return HttpResponse("success")

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