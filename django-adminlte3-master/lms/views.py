from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from . import sheetsapi
import datetime
from django.contrib.auth.models import User,Group,Permission,GroupManager
from .models import notice
# Create your views here.
def log_in(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        us = authenticate(request, username=username, password=password)
        print(us)

        if us is not None:
            login(request, us)
            messages.info(request, "Successfully Log In")
            # Redirect to a success page.
            # response = redirect('index')
            print('success')
            return redirect(index)
        else:
            messages.info(request, "Log In Failed")
            response = redirect(login_form)
            return response

    return HttpResponse("")

def log_out(request):
    logout(request)
    return redirect(login_form)

def login_form(request):
    return  render(request,'student/login_form.html')

def index(request):
    if request.user.is_staff:
        return render(request,'admin/adminindex.html')
    else:
        return render(request,'admin/index.html')

# def addstudent(request):
    # return HttpResponse("hi")

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

        fp = open('student_profile.txt', 'r')
        sheetid = fp.read()
        fp.close()

        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-4)+1"
        if sheetsapi.sheetvalues(sheetid, sheetname) is None:
            index = 1

        # print(filledaddstudentform)

        row = sheetsapi.appendsheet(sheetid, [index, ""] + filledaddstudentform)
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

        fp = open('student_performance.txt', 'r')
        sheetid = fp.read()
        fp.close()

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

        print(student_performance)


        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-1)+1"
        if sheetsapi.sheetvalues(sheetid, sheetname) is None:
            index = 1
        # print(filledaddstudentform)
        student_performance = [x for x in student_performance.values()]

        sheetsapi.appendsheet(sheetid,student_performance)


        username = randomstring(request)
        password = randomstring(request)


        us = User.objects.create_user(username=username+":"+str(int(row)+1),first_name=request.POST['name'],
                  password=password,email=request.POST['emailid'])
        us.save()
        # message to be sent
        header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

        message = header + '\n Username: ' + username + '\n Password: ' + password + ' \n\n'
        print(message)

        # mail(us.email,message)


    return render(request,'admin/add_student.html')

def viewstudent(request):
    fp = open('student_profile.txt', 'r')
    sheetid = fp.read()
    fp.close()

    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    data = sheetsapi.sheetvalues(sheetid,sheetname)
    print(data)
    return render(request,'admin/view_data.html',{'data':data})

def viewperformance(request):
    fp = open('student_performance.txt', 'r')
    sheetid = fp.read()
    fp.close()
    sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
    data = sheetsapi.sheetvalues(sheetid, sheetname)
    return render(request,'admin/view_performance.html',{'data':data})

def admin(request):
    return render(request, 'admin/index.html')
    if request.method == 'POST':
        us = authenticate(username=request.POST['username'],password=request.POST['password'])
        if us is not None:
            login(request,us)
            print("login")
            return render(request,'admin/index.html')
        else:
            print("failed")
            return render(request,'admin/login.html')
    else:
        return render(request, 'admin/login.html')

def addgroups(requet):
    if requet.method == 'POST':
        print(requet.POST['gname'])
        if not Group.objects.filter(name=requet.POST['gname']):
            gp=Group(name=requet.POST['gname'])
            gp.save()
            for permission in requet.POST.getlist('permission'):
                pass
        else:
            gp=Group.objects.filter(name=requet.POST['gname'])[0]

        print(requet.POST.getlist('permissions'))

        print(gp.permissions.set(requet.POST.getlist('permissions')))


        return render(requet,'admin/add_groups.html',{'gname':gp,'permissions':Permission.objects.all()})
    return render(requet,'admin/add_groups.html')
    # return render(requet,'admin/test.html')

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
        return render(request,'admin/view_groups.html',{'groups':Group.objects.all(),'gname':gp.name,'group_per':gp_per,'permissions':Permission.objects.all()})
    return render(request, 'admin/view_groups.html', {'groups': Group.objects.all()})

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

            # message to be sent
            header = 'To:' + us.email + '\n' + 'From: paniket281@gmail.com  \n' + 'Subject:Fortune Cloud LMS Passsword \n'

            message = header + '\n Username: ' + us.username + '\n Password: ' + us.password + ' \n\n'
            print(message)

            # mail(us.email,message)

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

        return render(request, 'admin/add_users.html', {'groups': Group.objects.all(),'gname':gp.name,'perm':perm,'permissions':Permission.objects.all(),'member':us})
    return render(request,'admin/add_users.html',{'groups':Group.objects.all()})

def viewmembers(request):
    if request.method == 'POST':
        us = User.objects.filter(id=request.POST['id'])[0]
        vars(us)[request.POST['field']]=request.POST['data']
        us.save()
        print(request.POST['id'])
    members = User.objects.filter(is_staff=True)
    groups = Group.objects.all()

    # memb_grp = [{member.id:{'grp_id':group.id,'grp_name':group.name}} for member in members for group in groups]
    memb_grp = {member.id: {'grp_id':group.id,'grp_name':group.name} for member in members for group in groups}
    # print(memb_grp[0][members[0].id])
    print(memb_grp)
    return render(request,'admin/view_users.html',{'members':members,'groups':groups,'memb_grp':memb_grp})

def viewprofile(request):
    fp = open('student_profile.txt', 'r')
    sheetid = fp.read()
    fp.close()
    row = int(request.user.username.split(':')[1])
    range = "!A"+str(row)+":AS"+str(row+3)
    # print(range)
    values = sheetsapi.sheetvalues(SPREADSHEET_ID=sheetid,sheetname='Apr - Mar 2021',range=range)
    # print(values[0])
    fields = ["id","datetime","center","dateofadmission","course","batchstartdate","modulestartfrom","trainingmode",
              "name","address","dateofbirth","contact","emailid","alternatecontact","examination","stream","collegename",
              "boardname","yearofpassing","percentage","fees","mode","regammount","installment1","installment2",
              "installment3","regdate","installment1date","installment2date","installment3date",'remark']

    profile = [dict(zip(fields,values[0])),dict(zip(fields,values[1])),dict(zip(fields,values[2])),dict(zip(fields,values[3]))] #list data to object
    print(profile[1])
    return render(request,'admin/profile.html',{'profile':profile})

def studentupdate(request,idvalue,row,col,value,cell):
    fp = open('student_profile.txt', 'r')
    SPREADSHEET_ID = fp.read()
    fp.close()
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

        print(filledaddstudentform)
        sheetname = "Apr - Mar " + datetime.datetime.now().strftime("%Y")
        index = "=INDIRECT(" + '"A"' + "&ROW()-4)+1"
        if sheetsapi.sheetvalues(SPREADSHEET_ID, sheetname) is None:
            index = 1

        print(filledaddstudentform)

        rowv = int(request.user.username.split(":")[1])
        row = sheetsapi.updatesheet(SPREADSHEET_ID,rowv, col, [index, ""] + filledaddstudentform, cell=False)
        # print(print(type(int.from_bytes(row.getvalue(),"big"))))
        # row = int.from_bytes(row.getvalue(),"big")
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+1, col, ["", ""] + [""] * 12 + acced[0], cell=False)
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+2, col, ["", ""] + [""] * 12 + acced[1], cell=False)
        sheetsapi.updatesheet(SPREADSHEET_ID,rowv+3, col, ["", ""] + [""] * 12 + acced[2], cell=False)
        # sheetsapi.updatesheet(SPREADSHEET_ID, row, col, value=filledaddstudentform, cell=False)
        return redirect(viewprofile)
    else:
        sheetsapi.updatesheet(SPREADSHEET_ID,row,col,value,cell)
        # fp = open('student_performance.txt', 'r')
        # sheetid = fp.read()
        # fp.close()
        # sheetsapi.updatesheet(SPREADSHEET_ID,idvalue,col,value,cell)
        return redirect(viewstudent)

    return HttpResponse("")

def studentpupdate(request,row,col,value,cell):
    fp = open('student_performance.txt', 'r')
    sheetid = fp.read()
    fp.close()
    sheetsapi.updatesheet(sheetid,row,col,value,cell)
    return redirect(request,viewperformance)

def attendance(request):
    return render(request,'admin/attendance.html')

def addnotice(request):
    # data : ""
    if request.method == 'POST':
        notice.addnoticein(request)
    data = notice.objects.all()
    print(data)
    return render(request,'admin/add_notice.html',{'data':data})

def randomstring(request):
    import secrets
    import string

    N = 7
    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                  for i in range(N))

    return str(res)

def mail(reciver,message):
    # Python code to illustrate Sending mail from
    # your Gmail account
    import smtplib

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login("paniket281@gmail.com", "jswwqzmaxpxdjpnb")


    # sending the mail
    s.sendmail("paniket281@gmail.com", reciver, message)

    # terminating the session
    s.quit()





















def test(request):
    return render(request,'admin/add_users.html')
