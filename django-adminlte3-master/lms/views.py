from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from . import sheetsapi
import datetime
from django.contrib.auth.models import User,Group,Permission
from .models import notice,user_profile,extra_data,certificate_request,timeline
from exam.models import course
from django.core.paginator import Paginator
import itertools
import os

# Create your views here.
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)
        print(us)
        if us is not None:
            try:
                ab = user_profile.objects.filter(user_id=us.id)[0]
                vars(ab)['_state'] = None
                print(vars(ab))
                request.session['ab']=vars(ab)

            except:
                pass
            messages.info(request, "Successfully Log In")
            # Redirect to a success page.
            # response = redirect('index')
            print('success')
            print(us.last_login)
            if us.last_login !=None:
                login(request, us)
                return redirect(index)
            else:
                login(request, us)

                return redirect(reset_password)
        else:
            messages.info(request, "Username and password not match")
            response = redirect(login_form)
            return response

    return HttpResponse("")

def log_out(request):
    logout(request)
    return redirect(login_form)

def login_form(request):
    try:
        if request.has_key(user):
            return redirect('index')
    except:
        return render(request,'student/login_form.html')

def reset_password(request):
    # print(user_profile.objects.all().filter(user_id=request.user.id)[0].otp)
    if request.method=='POST':
        try:
            us = User.objects.get(username=request.POST['username'])
            up = user_profile.objects.get(user_id=us.id)
        except:
            print("user not found")
            messages.info(request,'User not found')
            return redirect(reset_password)
        # up = user_profile.objects.all().filter(user_id=User.objects.all().filter(username=request.POST['username'])[0])
        if up.otp==request.POST['otp']:
            # us=User.objects.all().filter(username=request.POST['username'])[0]
            us.set_password(request.POST['password'])
            us.save()
            login(request,us)
            print("success")
            messages.info(request,'Password reset succesful')
            return redirect('index')
        else:
            print("failed")
            messages.info(request,'Failed to reset password')
            return redirect(reset_password)
    return render(request,'student/reset_password.html')

def index(request):

    try:
        flag=request.user
    except:
        return redirect('login_form')
    if request.user.is_staff:
        # notice1 = ""
        from .models import notice
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""

        # stat = {'ucount':len(user.objects.all()),'gcount':len(Group.objects.all())}
        return render(request,'student/adminindex.html',{'notice':notice1})
    else:
        day = datetime.datetime.now()
        day = day.strftime("%d")
        print(request.session.has_key('feedback'))

        if day == "20":
            if not request.session.has_key('feedback'):
                request.session['feedback'] = True
        else:
            if request.session.has_key('feedback'):
                if request.session['feedback'] == False:
                    del request.session['feedback']

        # fp = open('student_profile.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        sheetid = extra_data.objects.get(name='student_profile').value
        # row = int(request.user.username.split(':')[1])
        up = user_profile.objects.get(user_id=request.user)
        performance_row = up.student_performance_row
        range = "!A" + str(performance_row) + ":AS" + str(performance_row + 3)
        # print(range)
        values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid, sheetname='Apr - Mar 2021', range=range)
        # print(values)
        fields = ["id", "datetime", "center", "dateofadmission", "course", "batchstartdate", "modulestartfrom",
                  "trainingmode",
                  "name", "address", "dateofbirth", "contact", "emailid", "alternatecontact", "examination", "stream",
                  "collegename",
                  "boardname", "yearofpassing", "percentage", "fees", "mode", "regammount", "installment1",
                  "installment2",
                  "installment3", "regdate", "installment1date", "installment2date", "installment3date", 'remark']

        profile = [dict(zip(fields, values[0])), dict(zip(fields, values[1])), dict(zip(fields, values[2])),
                   dict(zip(fields, values[3]))]  # list data to object
        # print(profile[1])
        from .models import notice
        notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request, 'student/index.html', {'profile': profile,'notice':notice1,'up':up})


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

def addgroups(request):
    print(request.POST)
    if request.method == 'POST':
        gname = request.POST['gname']
        gp = Group.objects.filter(name=gname)
        if len(gp) == 0:
            gp=Group(name=gname)
            gp.save()
            messages.info(request,'Group created')
            SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
            attendance = ["id","user_id", "name", "contact", "emailid"]
            sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,columns=attendance)
            messages.info(request, gname + " is added in sheet")
        else:
            gp=gp[0]

        for permission in request.POST.getlist('permissions'):
            gp.permissions.add(permission)

        pre = gp.permissions.all()

        groups = Group.objects.all().order_by('-id')
        members = User.objects.all().order_by('-id')

        request_member = [int(x) for x in request.POST.getlist('members')]
        # print(request_member)
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
                    index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
                    if sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=gname) is None:
                        index = 1
                    values = [index,m.id,m.first_name,m.last_name,m.email]
                    sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,values=values)
                    messages.info(request,m.first_name+" is added")

        memb_pre = []  # group existing members
        for m in members:
            if len(m.groups.filter(name=gname))==1:
                memb_pre.append(m)

        videolist = []

        if (gname.find("C_")==0):
            videos = "media/videos/courses/" + 'C/'
            # print(os.listdir(videos))
            for v in os.listdir(videos):
                videolist.append(v.split(".")[0])

        print(videolist)
        # notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        # print(memb)
        courses = course.objects.values_list('name', flat=True).distinct()
        return render(request,'student/add_groups.html',{'gname':gp,'permissions':Permission.objects.all()[68::],'pre':pre,
                                                        'members':members,'memb_pre':memb_pre,'up':up,'groups':groups,
                                                         'notice':notice1,'vpermissions':videolist,'courses':courses})
    groups = Group.objects.all()

    # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_groups.html',{'groups':groups})

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

        notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request,'student/view_groups.html',{'groups':Group.objects.all(),'gname':gp.name,
                                                          'group_per':gp_per,'memb_pre':memb_pre,'permissions':Permission.objects.all(),
                                                          'members':members,'up':up,'notice':notice1})

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request, 'student/view_groups.html', {'groups': Group.objects.all(),'up':up,'notice':notice1})

def addusers(request):
    if request.method == "POST":
        gp = Group.objects.filter(name=request.POST['gname'])[0]
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        print(gp_per)
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        print(request.POST['username'])
        if not request.POST['username']:
            us = User(username=email,first_name=fname,last_name=lname,email=email,password=randomstring(request),is_staff=True)
            us.save()
            messages.info(request,"User added successfully")
            # message to be sent
            header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + us.username + '\n Password: ' + us.password + ' \n\n'
            print(message)

            mail(us.email,message)

        else:
            us = User.objects.get(username=request.POST['username'])

        if request.POST['gname']:
            us_gp = [us_gp.id for us_gp in us.groups.all()]
            print(us_gp)
            if gp.id not in us_gp:
                us.groups.add(gp.id)
            # print(us.groups.all())
        add_per = [int(add_per) for add_per in request.POST.getlist('permissions')]
        usr_per = [usr_per.id for usr_per in Permission.objects.filter(user=us)]
        print(usr_per)
        for per in add_per:
            if per not in gp_per:
                us.user_permissions.add(per)
                us.save()
                print(per)

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
                                                          'permissions':Permission.objects.all(),'member':us,'up':up,
                                                          'notice':notice1})

    notice1 = ""
    try:
        notice1 = notice.objects.all().order_by('-generateddate')[0:5]
    except:
        notice1 = ""
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_users.html',{'groups':Group.objects.all(),'up':up,'notice':notice1})

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
    # fp = open('student_profile.txt', 'r')
    # sheetid = fp.read()
    # fp.close()
    sheetid = extra_data.objects.get(name='student_profile').value
    up = user_profile.objects.get(user_id=request.user.id)
    row = up.student_performance_row
    range = "!A"+str(row)+":AS"+str(row+3)
    # print(range)
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)
    # print(values[0])
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
    # fp = open('student_profile.txt', 'r')
    # SPREADSHEET_ID = fp.read()
    # fp.close()
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
        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
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

        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
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




def randomstring(request):
    import secrets
    import string

    N = 7
    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

    return str(res)

def mail(reciver,message):
    import smtplib
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("paniket281@gmail.com", "jswwqzmaxpxdjpnb")
        s.sendmail("paniket281@gmail.com", reciver, message)
        s.quit()
        # messages.info(request,"Email send")
    except:
        # messages.info(request,"Email failed")
        pass




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
    sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
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
    sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
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
    # fp = open('student_profile.txt', 'r')
    # SPREADSHEET_ID = fp.read()
    # fp.close()
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    print(rowv)
    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=int(row) + 2, value=rowv)
    return HttpResponse("")

def change_user_data(request):
    return HttpResponse("")

def get_data(request,table):
    if table == 'attendance':
        # fp = open('attendance.txt')
        # SPREADSHEET_ID = fp.read()
        # fp.close()
        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    if table == 'profile':
        # fp = open('student_profile.txt')
        # SPREADSHEET_ID = fp.read()
        # fp.close()
        SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    if table == 'performance':
        # fp = open('student_performance.txt')
        # SPREADSHEET_ID = fp.read()
        # fp.close()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    if table == 'feedback':
        # fp = open('student_performance.txt')
        # SPREADSHEET_ID = fp.read()
        # fp.close()
        SPREADSHEET_ID = extra_data.objects.get(name='feedback').value

    SHEET_NAME = request.GET['sheetname']
    print(SHEET_NAME)
    # sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=SHEET_NAME,range='!A1:GZ')
    data = []
    fields = [x for x in values[0]]
    for row,i in zip(values[1::1],range(len(values))):
        dict = {'rowIndex':i}
        for s, j in zip(fields, range(len(fields))):
            if j < len(row):
                dict[s] = row[j]
            else:
                dict[s] = ''
        data.append(dict)
    # print(str(data)[508::])
    messages.info(request,'Data fetch successfully')
    return HttpResponse(str(data))

def set_data(request,table):
    # print(request.GET['row'])
    # print(request.GET['rowv'])
    # row = request.GET['row']
    rowv = request.GET['rowv'].split(',')
    row = rowv[0]
    rowv = rowv[1::]
    # print(row,rowv[4::])
    print(row,rowv)
    if table != 'attendance':
        if table == 'profile':
            # fp = open('student_profile.txt')
            # SPREADSHEET_ID = fp.read()
            # fp.close()
            SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
        if table == 'performance':
            # fp = open('student_performance.txt')
            # SPREADSHEET_ID = fp.read()
            # fp.close()
            SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value

        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=int(row) + 2, value=rowv)
    elif table == 'attendance':
        # fp = open('attendance.txt')
        # SPREADSHEET_ID = fp.read()
        # fp.close()
        SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
        rowv = request.GET['rowv'].split(',')
        row = request.GET['row']
        SHEET_NAME = request.GET['sheetname']
        print(SHEET_NAME)
        print(rowv)
        print(type(rowv[0]))
        if (type(rowv[0])==int):
            rowv = [x for x in rowv]
        else:
            rowv = [int(x) for x in rowv]

        print(rowv)

        rowv.sort()
        date = datetime.datetime.now()
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        # day = day.strip("0")
        # month=month.strip("0")
        currentdate=day+"/"+month+"/"+year
        print(currentdate)
        present = [currentdate]
        # rowv.sort()
        print(rowv)
        print(row)
        for i in range(0,rowv[-1]+1):
            # print(i)
            if i in rowv:
                present.append("p")
            else:
                present.append("")
        print(present)
        row = int(row)
        a=""
        while row>1:
            a+=(chr((row%26)+65))
            row = row/26
        print(a)
        sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,values=present,sheetname=SHEET_NAME,range='!'+a+':'+a+'',dimension="COLUMNS")
        messages.info(request,'Data saved successfully')
    return HttpResponse("")

def sendotp(request):
    otp = randomstring(request)
    print(request.GET)
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
        print(up.otp)
        header = 'To:' + us[0].username + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS OTP \n'

        message = header + '\n Username: ' + request.GET['username'] + '\n OTP: ' + otp + ' \n\n'
        print(message)

        mail(us[0].username,message)
        messages.info(request,'Otp send successfully')
        return HttpResponse("otp send successufully")
    else:
        messages.info(request,'Username not found')
        return HttpResponse("username not found")

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
    print(request.FILES['file'])
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
    cr.save()
    print(file)
    print(request.POST['id'])
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
            now = datetime.datetime.now(datetime.timezone.utc)
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
    day = datetime.datetime.now()
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