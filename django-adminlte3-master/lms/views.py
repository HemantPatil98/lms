from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from . import sheetsapi
import datetime
from django.contrib.auth.models import User,Group,Permission,GroupManager
from .models import notice,user_profile,extra_data,certificate_request
from django.core.paginator import Paginator
# Create your views here.
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)
        print(us)
        if us is not None:
            login(request, us)
            ab = user_profile.objects.filter(user_id=us.id)[0]
            vars(ab)['_state'] = None
            print(vars(ab))
            request.session['ab']=vars(ab)
            messages.info(request, "Successfully Log In")
            # Redirect to a success page.
            # response = redirect('index')
            print('success')
            print(us.last_login)
            if us.last_login !=None:
                return redirect(index)
            else:
                return redirect(reset_password)
        else:
            messages.info(request, "Log In Failed")
            response = redirect(login_form)
            return response

    return HttpResponse("")

def log_out(request):
    logout(request)
    return redirect(login_form)

def login_form(request):
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
    if request.user.is_staff:
        return render(request,'student/adminindex.html')
    else:
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
        print(values)
        fields = ["id", "datetime", "center", "dateofadmission", "course", "batchstartdate", "modulestartfrom",
                  "trainingmode",
                  "name", "address", "dateofbirth", "contact", "emailid", "alternatecontact", "examination", "stream",
                  "collegename",
                  "boardname", "yearofpassing", "percentage", "fees", "mode", "regammount", "installment1",
                  "installment2",
                  "installment3", "regdate", "installment1date", "installment2date", "installment3date", 'remark']

        profile = [dict(zip(fields, values[0])), dict(zip(fields, values[1])), dict(zip(fields, values[2])),
                   dict(zip(fields, values[3]))]  # list data to object
        print(profile[1])
        from .models import notice
        notice1 = notice.objects.all().order_by('-generateddate')
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request, 'student/index.html', {'profile': profile,'notice':notice1[0:5],'up':up})


def addstudent(request):
    if request.method == 'POST':
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

        # fp = open('student_profile.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        sheetid = extra_data.objects.get(name='student_profile').value
        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-4)+1"
        if sheetsapi.sheetvalues(sheetid, sheetname) is None:
            index = 1

        # print(filledaddstudentform)
        # print(addstudentform)

        profile_row = sheetsapi.appendsheet(sheetid, [index, ""] + filledaddstudentform)
        sheetsapi.appendsheet(sheetid, ["", ""] + [""] * 12 + acced[0])
        sheetsapi.appendsheet(sheetid, ["", ""] + [""] * 12 + acced[1])
        sheetsapi.appendsheet(sheetid, ["", ""] + [""] * 12 + acced[2])

        # print(request.POST['dateofbirth'])
        #
        for i in range(10, 16):
            filledaddstudentform[i] = acced[2][i - 10]
            # print(filledaddstudentform[i])

        # print(addstudentform)
        # print(filledaddstudentform)

        # fp = open('student_performance.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        sheetid = extra_data.objects.get(name='student_performance').value

        student_performance = {'id':"",'name':"", 'contact':"", 'emailid':"", 'dateofadmission':"", 'trainingmode':"",
                               'batchstartdate':"", 'course':"",'startcourse':"", 'currentmodule':"",
                               'ctrainername':"", 'cmodulestartdate':"", 'cmoduleenddate':"", 'ctheory':"",'cpracticle':"",'coral':"", 'ctotal':"",
                               'sqltrainername':"", 'sqlmodulestartdate':"", 'sqlmoduleenddate':"",'sqlpracticle':"",'sqloral':"", 'sqltotal':"",
                               'wdtrainername':"", 'wdmodulestartdate':"", 'wdmoduleenddate':"",'wdpracticle':"",'wdoral':"", 'wdtotal':"",'portfoiliolink':"",
                               'mock1':"", 'miniguide':"",'miniproject':"",
                               'coretrainername':"", 'coremodulestartdate':"", 'coremoduleenddate':"",'coretheory':"",'corepracticle':"", 'coreoral':"", 'coretotal':"",
                               'mock2':"",
                               'advtrainername':"", 'advmodulestartdate':"", 'advmoduleenddate':"",'advtheory':"",'advpracticle':"", 'advoral':"", 'advtotal':"",
                               'fullcourseenddate':"", 'cravitaprojectstartdate':"",
                               'mock3':"",'softskillsmarks':"", 'finalmock':"", 'totalmarks':"",'eligibleforplacement':"", 'remark':""
                               }

        for s in student_performance.keys():
            try:
                student_performance[s]=request.POST[s]
            except:
                student_performance[s]=""

        index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        if sheetsapi.sheetvalues(sheetid, sheetname) is None:
            index = 1

        student_performance['id'] = index

        # print(student_performance)


        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        if sheetsapi.sheetvalues(sheetid, sheetname) is None:
            index = 1
        # print(filledaddstudentform)
        student_performance = [x for x in student_performance.values()]

        performance_row = sheetsapi.appendsheet(sheetid,student_performance)


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
        notice1 = notice.objects.all().order_by('-generateddate')

        messages.info(request,'Student added successfully')
    return render(request,'student/add_student.html',{'notice':notice1[0:5]})

def viewstudent(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    notice1 = notice.objects.all().order_by('-generateddate')

    return render(request,'student/view_data.html',{'up':up,'sheetnames':SHEET_NAMES,'notice':notice[0:5]})

def viewperformance(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)
    notice1 = notice.objects.all().order_by('-generateddate')

    return render(request,'student/view_performance.html',{'up':up,'sheetnames':SHEET_NAMES,'notice':notice1[0:5]})

def admin(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    notice1 = notice.objects.all().order_by('-generateddate')

    return render(request, 'student/index.html',{'up':up,'notice':notice1[0:5]})
    if request.method == 'POST':
        us = authenticate(username=request.POST['username'],password=request.POST['password'])
        if us is not None:
            login(request,us)
            print("login")
            return render(request,'student/index.html')
        else:
            print("failed")
            return render(request,'student/login.html')
    else:
        return render(request, 'student/login.html')

def addgroups(request):
    if request.method == 'POST':
        gname = request.POST['gname']
        if not Group.objects.filter(name=gname):
            gp=Group(name=gname)
            gp.save()
            messages.info(request,'Group created')
            SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
            attendance = ["id", "name", "contact", "emailid"]
            sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,columns=attendance)
        else:
            gp=Group.objects.filter(name=gname)[0]

        for permission in request.POST.getlist('permissions'):
            gp.permissions.add(permission)

        pre = []
        for i in gp.permissions.all():
            pre.append(i.id)

        groups = Group.objects.all()
        members = User.objects.all()
        memb = []  #group existing members
        for m in members:
            if m.groups.all().filter(name=gname):
                memb.append(m.id)

        for m in request.POST.getlist('members'):
            for i in members.filter(id=int(m)):
                if groups.filter(name=gname)[0] not in i.groups.all():
                    i.groups.add(groups.filter(name=gname)[0].id)
                    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
                    values = User.objects.get(id=int(m))
                    print(values)
                    index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
                    if sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=gname) is None:
                        index = 1
                    values = [index,values.first_name,values.email]
                    sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=gname,values=values)
                    messages.info(request,gname+"is added")
                else:
                    i.groups.remove(Group.objects.all().filter(name=request.POST['gname'])[0].id)

        notice1 = notice.objects.all().order_by('-generateddate')
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request,'student/add_groups.html',{'gname':gp,'permissions':Permission.objects.all(),'pre':pre,
                                                        'members':members,'memb_pre':memb,'up':up,'groups':groups,
                                                         'notice':notice1[0:5]})
    groups = Group.objects.all()

    # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_groups.html',{'groups':groups})

    # return render(requet,'student/test.html')

def viewgroups(request):
    if request.method == "POST":
        gp = Group.objects.filter(name=request.POST['gname'])[0]
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        print(gp_per)
        add_per = [int(add_per) for add_per in request.POST.getlist('permissions')]
        print(request.POST['submit'] == 'submit')
        if request.POST['submit']:
            for per in add_per:
                if per not in gp_per:
                    gp.permissions.add(per)
            for per in gp_per:
                if per not in add_per:
                    gp.permissions.remove(per)
        print(add_per)
        gp_per = [gp_per.id for gp_per in gp.permissions.all()]
        groups = Group.objects.all()
        members = User.objects.all()
        memb_grp = {member.id: {'grp_id': group.id, 'grp_name': group.name} for member in members for group in groups}

        notice1 = notice.objects.all().order_by('-generateddate')
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request,'student/view_groups.html',{'groups':Group.objects.all(),'gname':gp.name,
                                                          'group_per':gp_per,'permissions':Permission.objects.all(),
                                                          'members':members,'up':up,'notice':notice1[0:5]})

    notice1 = notice.objects.all().order_by('-generateddate')
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request, 'student/view_groups.html', {'groups': Group.objects.all(),'up':up,'notice':notice1[0:5]})

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
            us = User(username=randomstring(request),first_name=fname,last_name=lname,email=email,password=randomstring(request),is_staff=True)
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

        notice1 = notice.objects.all().order_by('-generateddate')
        return render(request, 'student/add_users.html', {'groups': Group.objects.all(),'gname':gp.name,'perm':perm,
                                                          'permissions':Permission.objects.all(),'member':us,'up':up,
                                                          'notice':notice1[0:5]})

    notice1 = notice.objects.all().order_by('-generateddate')
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    return render(request,'student/add_users.html',{'groups':Group.objects.all(),'up':up,'notice':notice1[0:5]})

def viewmembers(request):
    groups = Group.objects.all()
    gnames = []
    for g in groups:
        gnames.append(g.name)
    notice1 = notice.objects.all().order_by('-generateddate')
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
    notice1 = notice.objects.all().order_by('-generateddate')
    return render(request,'student/profile.html',{'profile':profile,'up':up,'rc':rc,'notice':notice1[0:5]})

def editprofile(request):
    up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    notice1 = notice.objects.all().order_by('-generateddate')
    return redirect(request,'index',{'up':up,'notice':notice1[0:5]})

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

    notice1 = notice.objects.all().order_by('-generateddate')
    return render(request,'student/view_notice.html',{'up':up,'data':page,'notice':notice1[0:5]})

def studentupdate(request):
    # fp = open('student_profile.txt', 'r')
    # SPREADSHEET_ID = fp.read()
    # fp.close()
    SPREADSHEET_ID = extra_data.objects.get(name='student_profile').value
    cell = 'False'
    row = request.user.username.split(':')[1]
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
        index = math.ceil((int(request.user.username.split(':')[1])-1)/4)

        # print(filledaddstudentform)

        rowv = int(request.user.username.split(":")[1])
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
        index = math.ceil((int(request.user.username.split(':')[1])-1)/4)

        student_performance['id'] = index

        # print(student_performance)

        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        # index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        # if sheetsapi.sheetvalues(sheetid, sheetname) is None:
        #     index = 1
        # print(filledaddstudentform)
        student_performance = [x for x in student_performance.values()]
        # import math
        print(math.ceil((int(request.user.username.split(':')[1])-1)/4))
        row = math.ceil((int(request.user.username.split(':')[1])-1)/4)+1
        sheetsapi.updatesheet(sheetid,row,student_performance)

        try:
            file = request.FILES['photo']
            file._name = str(request.user.username.split(':')[0]) +"."+ file._name.split('.')[1]
        except:
            file = ""
        from .models import user_profile
        us_profile = user_profile.objects.all().filter(user_id=request.user.id)
        if len(us_profile)==0:
            us_profile = user_profile(user_id=request.user,student_performance_row=str(int(performance_row)+1),photo=file)
            us_profile.save()
        else:
            us_profile.update(photo=file)

        messages.inof(request,'profile updated')
        return redirect(viewprofile)
    else:
        sheetsapi.updatesheet(SPREADSHEET_ID,row,col,value,cell)
        # fp = open('student_performance.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        # sheetsapi.updatesheet(SPREADSHEET_ID,idvalue,col,value,cell)
        messages.inof(request,'profile updated')
        return redirect(viewstudent)

    return HttpResponse("")

def attendance(request):
    SPREADSHEET_ID = extra_data.objects.get(name='attendance').value
    SHEET_NAMES = sheetsapi.getsheetnames(SPREADSHEET_ID=SPREADSHEET_ID)

    notice1 = notice.objects.all().order_by('-generateddate')
    return render(request,'student/attendance.html',{'sheetnames':SHEET_NAMES,'notice':notice1[0:5]})


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

    notice1 = notice.objects.all().order_by('-generateddate')
    return render(request,'student/add_notice.html',{'data':page,'up':up,'notice':notice1[0:5]})

def request_certificate(request):
    cr = certificate_request(student_id=request.user)
    cr.save()
    us = user_profile.objects.get(user_id=request.user.id)
    us.certificate=cr
    us.save()
    messages.info(request,'certificate saved Successfully')
    return redirect('index')

def addcertificate(request):
    notice1 = notice.objects.all().order_by('-generateddate')
    return render(request,'student/add_certificate.html',{'notice':notice1[0:5]})

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
    # print(values)
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
    # print(otp)
    us = User.objects.all().filter(username=request.GET['username'])
    if len(us)==1:
        up = user_profile.objects.all().filter(user_id=us[0])
        if len(us)==0:
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
        abc.append(m[0])
    memb = str(memb).lstrip('_').replace('"','').replace('FIRST_NAME','NAME').replace("True","true").replace("False",'')
    # print(memb)
    return HttpResponse(str(abc))


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
    groups = Group.objects.all()
    gnames = []
    for g in groups:
        gnames.append(g.name)
    return render(request,'student/test.html', {'sheetnames': gnames})


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
        elif not  isinstance(vars(obj)[k], (float, int, str, list, dict, tuple)) or k == 'tzinfo' or k == '_state':
            dic[k.upper()] = 'none'
        else:
            dic[k.upper()] = vars(obj)[k]
    # print(dic)
    return dic