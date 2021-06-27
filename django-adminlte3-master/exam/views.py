from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import Group,Permission
from django.contrib import messages
from datetime import datetime
from django.core import serializers
from .models import *
import random
import os
import json

from lms import models,sheetsapi
from lms.sheetfields import all_fields_index

# from lms.models import gpinfo
# Create your views here.

###
@login_required(login_url='')
def add_course(request):
    if request.method == 'POST':
        cname = request.POST['cname']
        count = 0
        type = request.POST['type']
        SPREADSHEET_ID = ""
        crs = course.objects.filter(name=cname, type=type)

        if(len(crs)==1):
            crs=crs[0]
            crs.instructions=request.POST['instructions']
            crs.time = request.POST['time']
            crs.save()
        else:
            crs = course(name=cname,type=type,time=request.POST['time'],questions_count=request.POST['count'])
            if not os.path.exists('media/videos/courses/'+cname):
                os.mkdir('media/videos/courses/'+cname)
            if not os.path.exists('media/videos/thumb/'+cname):
                os.mkdir('media/videos/thumb/'+cname)

            try:
                SPREADSHEET_ID = models.extra_data.objects.get(name=type).value
            except:
                if type != 'ORAL':
                    if type == 'MCQ':
                        fields = ["Question","Option1","Option2","Option3","Option4","Answer",'Explanation']
                    elif type == 'PRACTICAL':
                        fields = ["Program"]
                    elif type == 'PROGRAM':
                        fields = ["Program"]
                    SPREADSHEET_ID = sheetsapi.createsheet(name=type,columns=fields,sheetname=cname)
                    ext = models.extra_data(name=type, value=SPREADSHEET_ID)
                    ext.save()
                    ext = models.extra_data(name=cname+"_"+type,value=1)
                    ext.save()
            else:
                if type != 'ORAL':
                    if type == 'MCQ':
                        fields = ["Question", "Option1", "Option2", "Option3", "Option4", "Answer",'Explanation']
                    elif type == 'PRACTICAL':
                        fields = ["Program"]
                    elif type == 'PROGRAM':
                        fields = ["Program"]
                    sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=cname,columns=fields)
                    ext = models.extra_data(name=(cname+"_"+type),value=1)
                    ext.save()

            crs.save()
            messages.success(request,crs.name +" " + crs.type + " Added Successfully")
            return redirect(add_course)
    ext = models.extra_data.objects.all()
    ext1 = {}
    cr = course.objects.all()
    for c in cr:
        if c.type != 'ORAL':
            ext1[c.type] = ext.get(name=c.type).value
    ext = ext1

    courses = course.objects.values_list('name', flat=True).distinct()
    return render(request,'add_course.html',{'courses':courses,'ext':ext,'crs':crs})

###
@login_required(login_url='')
def add_questions(request):
    if request.method == 'POST':
        cname = request.POST['cname']
        count = 0
        type = request.POST['type']
        SPREADSHEET_ID = ""
        try:
            crs = course.objects.get(name=cname,type=type)
            try:
                crs.instructions=request.POST['instructions']
            except:
                pass

            crs.save()
        except:
            crs = course(name=cname,type=type,time=request.POST['time'])
            if not os.path.exists('media/videos/courses/'+cname):
                os.mkdir('media/videos/courses/'+cname)
            if not os.path.exists('media/videos/thumb/'+cname):
                os.mkdir('media/videos/thumb/'+cname)

            try:
                SPREADSHEET_ID = models.extra_data.objects.get(name=type).value
            except:
                if type != 'ORAL':
                    if type == 'MCQ':
                        fields = ["Question","Option1","Option2","Option3","Option4","Answer",'Explanation']
                    elif type == 'PRACTICAL':
                        fields = ["Program"]
                    elif type == 'PROGRAM':
                        fields = ["Program"]
                    SPREADSHEET_ID = sheetsapi.createsheet(name=type,columns=fields,sheetname=cname)
                    ext = models.extra_data(name=type, value=SPREADSHEET_ID)
                    ext.save()
                    ext = models.extra_data(name=cname+"_"+type,value=1)
                    ext.save()
            else:
                if type != 'ORAL':
                    if type == 'MCQ':
                        fields = ["Question", "Option1", "Option2", "Option3", "Option4", "Answer",'Explanation']
                    elif type == 'PRACTICAL':
                        fields = ["Program"]
                    elif type == 'PROGRAM':
                        fields = ["Program"]
                    sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=cname,columns=fields)
                    ext = models.extra_data(name=(cname+"_"+type),value=1)
                    ext.save()

            crs.save()
        courses = course.objects.all()

        if type == 'MCQ':
            for field in request.POST:
                if field.find('question')==0:
                    qno = field.replace('question','')
                    choice = "choice"+qno
                    expla = "explanation"+qno
                    choices = request.POST.getlist(choice)
                    ans = choices[int(qno)]
                    try :
                        explanation = request.POST[expla]
                    except:
                        explanation = ""
                    q = questions(course=crs,question=request.POST[field],
                                  option1=choices[0],option2=choices[1],option3=choices[2],option4=choices[3],
                                  answer=ans,explanation=explanation)
                    q.save()

            count = questions.objects.all().filter(course=crs)

        elif type == 'PRACTICAL':
            for field in request.POST:
                if field.find('question')==0:
                    p = program(course=crs,programe=request.POST[field])
                    p.save()

            count = program.objects.all().filter(course=crs)

        elif type == 'PROGRAM':
            for field in request.POST:
                if field.find('question')==0:
                    p = program(course=crs,programe=request.POST[field])
                    p.save()

            count = program.objects.all().filter(course=crs)

        messages.info(request,'Question Added')
        return redirect('index')

    ext = models.extra_data.objects.all()
    ext1 = {}
    cr = course.objects.all()
    for c in cr:
        if c.type != 'ORAL':
            ext1[c.type] = ext.get(name=c.type).value
    ext = ext1

    courses = course.objects.values_list('name', flat=True).distinct()
    return render(request,'add_question.html',{'courses':courses,'ext':ext})

###
@login_required(login_url='')
def mcq_exam(request):
    if request.method == 'POST':
        count = 0
        cname = request.POST['cname']
        type = request.POST['type']
        crs = course.objects.get(name=cname, type=type)
        courses = course.objects.values_list('name', flat=True).distinct()
        attempt = exam_attempts.objects.filter(student=request.user, course=crs)
        attempt = len(attempt)

        if crs.type == 'MCQ':
            ques = questions.objects.all().filter(course=crs)
            ques = list(ques)
            random.shuffle(ques)
            ques_set = random.sample(set(ques),crs.questions_count)


            return render(request, 'mcq_exam.html',
                          {'crs': crs, 'count': count, 'courses': courses, 'ques_set': ques_set, 'attempt':attempt})
        elif crs.type == 'PRACTICAL':

            if 'prog_set' in request.COOKIES:
                prog_set = json.loads(request.COOKIES['prog_set'].replace("'",'"'))

            else:
                prog = program.objects.all().filter(course=crs.id)
                prog_set = random.sample(set(prog), crs.questions_count)
                abc = str(serializers.serialize('json', list(prog_set), fields=('programe')))
                prog_set = json.loads(abc)

            response =  render(request, 'practicle_exam.html', {'crs': crs, 'count': count, 'courses': courses,
                                                           'prog_set': prog_set,'attempt':attempt})

            response.set_cookie(key='prog_set',value=prog_set,max_age=4*60*1000)

            return response

        elif crs.type == 'PROGRAM':
            prog = program.objects.all().filter(course=crs.id)
            prog_set = random.sample(set(prog), crs.questions_count)

            if 'prog_set' in request.COOKIES:
                prog_set = json.loads(request.COOKIES['prog_set'].replace("'",'"'))

            else:
                prog = program.objects.all().filter(course=crs.id)
                prog_set = random.sample(set(prog), crs.questions_count)

                abc = str(serializers.serialize('json', list(prog_set), fields=('programe')))
                prog_set = json.loads(abc)

            response = render(request, 'practicle_exam.html', {'crs': crs, 'count': count, 'courses': courses,
                                                       'prog_set': prog_set,'attempt':attempt})

            response.set_cookie(key='prog_set', value=prog_set, max_age=4 * 60 * 1000)

            return response

    courses = []
    for g in request.user.groups.filter(permissions=Permission.objects.get(name='exam')):
        gp = models.groupsinfo.objects.get(group=g.id)
        courses.append(gp.course)
    return render(request,'mcq_exam.html',{'courses':courses})

###
@login_required(login_url='')
def view_questions(request,pageno=1):
    if request.user.is_superuser:
        if request.method == 'POST':
            count = 0
            cname = request.POST['cname']
            type = request.POST['type']
            crs = course.objects.get(name=cname, type=type)
            ques = questions.objects.all().filter(course=crs.id)
            ques_set = ques
            pageno = request.POST['page']
            p = Paginator(ques_set, 20)
            page = p.page(pageno)
            courses = course.objects.values_list('name', flat=True).distinct()

            messages.info(request,'Question Loaded')
            return render(request,'view_questions.html',{'crs':crs,'count':count,'courses':courses,'ques_set':page})
        courses = course.objects.values_list('name', flat=True).distinct()
        return render(request,'view_questions.html', {'courses': courses})
    return redirect(request,'index')

###
@login_required(login_url='')
def mcq_validate(request):
    marks = 0
    answers = []
    anss = request.POST
    for qno in request.POST['qnos'].split(','):
        ans = "ans"+qno
        q = questions.objects.get(id=int(qno))
        answers.append({'question':qno,'answer':q.answer})
        if ans in anss:
            ans = request.POST[ans]
            if q.answer == ans:
                marks += 2

    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    result_attempts = exam_attempts.objects.filter(student=request.user,course=crs)

    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    row = models.user_profile.objects.get(user_id=request.user).student_performance_row
    row = int(row)

    if crs.name == 'C':
        col = all_fields_index['student_performance']['C Theory (Out of 40)']
    elif crs.name == 'SQL':
        col = all_fields_index['student_performance']['Sql Theory (Out of 40)']
    elif crs.name.find('Core')==0:
        col = all_fields_index['student_performance']['Core Theory (Out of 40)']
    elif crs.name.find('Adv')==0:
        col = all_fields_index['student_performance']['Adv Theory (Out of 40)']


    y = request.user.date_joined.strftime('%Y')

    SHEET_NAME = "Apr - Mar "+y

    hmarks = 0
    for h in result_attempts:
        if h.marks >= marks:
            hmarks=h.marks

    if len(result_attempts)==0:
        attempt = 1
        result = exam_attempts(student=request.user,course=crs,attempt=attempt,marks=marks)
        result.save()
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=row, value=[marks], col=col, cell=True)
    elif len(result_attempts)<crs.attempts_allowed:
        attempt = len(result_attempts)+1
        result = exam_attempts(student=request.user, course=crs, attempt=attempt, marks=marks)
        result.save()
        if marks>hmarks:
            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=row,value=[marks],col=col,cell=True)
    else:
        attempt = "Attempts Overed"

    data = {
        "marks":marks,
        "attempt": attempt,
        "answers":answers
    }
    messages.info(request,'Mcq Validated')
    return HttpResponse(str(data))


from django.views.decorators.csrf import csrf_exempt
###
@csrf_exempt
@login_required(login_url='')
def get_answers(request):
    q_a_set = questions.objects.filter(id=request.POST.getlist('question_set[]'))
    return HttpResponse(str(q_a_set).replace("'",'"').replace('False','false').replace('True','true'))

###
@login_required(login_url='')
def practicle_exam(request):
    return render(request,'practicle.exam')

###
@login_required(login_url='')
def sync_questions(request):
    courses = course.objects.all()
    ext = models.extra_data.objects.all()
    for c in courses:
        if c.type == "MCQ":
            SPREADSHEET_ID = models.extra_data.objects.get(name='MCQ').value
            ext_row = ext.get(name=c.name+"_MCQ")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            ques = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":G1000")
            if ques:
                for q in ques:
                    if len(q)<8:
                        q = q+([""]*(7-len(q)))
                    q = questions(course=c,question=q[0],option1=q[1],option2=q[2],option3=q[3],option4=q[4],answer=q[5],explanation=q[6])
                    q.save()
                ext_row.value = int(last_update) + len(ques)
                ext_row.save()
        elif c.type == "PRACTICAL":
            SPREADSHEET_ID = models.extra_data.objects.get(name='PRACTICAL').value
            ext_row = ext.get(name=c.name+"_PRACTICAL")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            programs = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":F1000")
            if programs:
                for p in programs:
                    p = program(course=c,programe=p[0])
                    p.save()
                ext_row.value = int(last_update) + len(programs)
                ext_row.save()
        elif c.type == "PROGRAM":
            SPREADSHEET_ID = models.extra_data.objects.get(name='PROGRAM').value
            ext_row = ext.get(name=c.name+"_PROGRAM")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            programs = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":F1000")
            if programs:
                for p in programs:
                    p = program(course=c,programe=p[0])
                    p.save()
                ext_row.value = int(last_update) + len(programs)
                ext_row.save()
    messages.info(request,'Questione Sync Complete')
    return HttpResponse("")

###
@login_required(login_url='')
def savepracticle(request):
    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    result = exam_attempts.objects.filter(student=request.user, course=crs)
    attempt = 1 if len(result) == 0 else 2 if len(result) < 2 else "Attempts Overed"

    if attempt != "Attempts Overed":
        for field in request.POST:
            if field.find('ans') == 0:
                pno = field.replace('ans', '')
                answer = request.POST[field]
                prog = program.objects.get(id=pno)
                p = program_ans(student=request.user, course=crs, program=prog, answer=answer, attempt=attempt)
                p.save()

        result = exam_attempts(student=request.user, course=crs, attempt=attempt)
        result.save()
        messages.info(request, 'Practical saved successfully')
    else:
    # if attempt != "Attempts Overed":
    #     result = exam_attempts(student=request.user, course=crs, attempt=attempt)
    #     result.save()
        messages.error(request,'Attempts Overed')

    return redirect('index')

###
@login_required(login_url='')
def practicle_validate(request):
    courses = course.objects.values_list('name', flat=True).distinct()
    gnames = Group.objects.all() if request.user.is_superuser else request.user.groups.all()
    gnames = [x.name for x in gnames]
    return render(request,'validate_practicle.html',{"courses":courses,"groups":gnames})

###
@login_required(login_url='')
def getdata_practicle(request):
    cname = request.GET['cname']
    type = request.GET['type']

    crs = course.objects.get(name=cname,type=type)
    exa = exam_attempts.objects.filter(course=crs).order_by('-id')
    data = []
    for e in exa:
        a = vars(e)
        a["_state"] = 'none'
        c = vars(course.objects.get(id=a["course_id"]))
        c["_state"] = 'none'
        c['course'] = c['name']
        c.pop('name')

        try:
            g = Group.objects.get(name=request.GET['gname'])
        except:
            g = ''

        if g in User.objects.get(id=a['student_id']).groups.all() or request.GET['gname']=='All_groups':
            s = vars(User.objects.get(id=a['student_id']))
            a['name'] = s['first_name']
            id = str(a['id'])
            a.update(c)
            a = {str(k).upper(): str(v).upper() for k, v in a.items()}
            a['ID'] = id
            if type == 'PRACTICAL':
                a['PROGRAMS'] = "?attempt_id="+id
            elif type == 'PROGRAM':
                p = program_file.objects.get(student=a['STUDENT_ID'],course=crs,attempt=a['ATTEMPT'])
                a['FILE'] = p.file.name
                a['QUATION'] = p.program.programe

            data.append(a)
        # print(a)
    return HttpResponse(str(data).replace('None',"'none'").replace("'",'"'))

def getdata_oral(request):
    gname = request.GET['gname']
    us = User.objects.all() if gname == 'All_groups' else User.objects.filter(groups__name=gname)
    # if gname != 'All_groups':
    #     us = User.objects.filter(groups__name=gname)
    # else:
    #     us = User.objects.all()
    us = serializers.serialize('json',list(us),fields=('first_name')).replace('pk','ID').replace('first_name','NAME')

    return HttpResponse(us)

###
@login_required(login_url='')
def view_practicle(request):
    attempt = request.GET['attempt_id']
    ex = exam_attempts.objects.get(id=int(attempt))
    prog_ans = program_ans.objects.filter(student=ex.student_id,course=ex.course.id,attempt=ex.attempt)
    courses = course.objects.values_list('name', flat=True).distinct()

    crs = course.objects.get(id=ex.course.id)
    gname = prog_ans[0].student.groups.get(name__startswith=crs.name).name

    return render(request,'view_practical1.html',{'crs':crs,'courses':courses,'prog_set':prog_ans,'ex':ex,'gname':gname})

###
@login_required(login_url='')
def marks_practicle(request):
    marks = 0
    for m in request.POST.getlist('marks'):
        print(m,type(m))
        marks += int(m)
    attempt = request.POST['attempt']
    ex = exam_attempts.objects.get(id=int(attempt))
    ex.marks = marks
    ex.save()
    crs = ex.course
    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
    row = models.user_profile.objects.get(user_id=ex.student).student_performance_row
    row = int(row)


    if crs.name == 'C':
        col = all_fields_index['student_performance']['C Practical (Out of 40)']
    elif crs.name == 'SQL':
        col = all_fields_index['student_performance']['Sql Practical (Out of 40)']
    elif crs.name.find('Core') == 0:
        col = all_fields_index['student_performance']['Core Practical (Out of 40)']
    elif crs.name.find('Adv') == 0:
        col = all_fields_index['student_performance']['Adv Practical (Out of 40)']

    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=sheetname, row=row+1, value=[marks], col=col, cell=True)

    return HttpResponse("<script type=text/javascript>window.close()</script>")

###
@login_required(login_url='')
def saveprogram(request):
    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    for field in request.FILES:
        if field.find('file')==0:
            file = request.FILES[field]

            pno = field.replace('file', '')
            prog = program.objects.get(id=pno)

            result = exam_attempts.objects.filter(student=request.user, course=crs)
            if len(result) == 0:
                attempt = 1
                file._name = request.user.first_name + str(attempt) +"."+ file._name.split('.')[1]
                prf = program_file(student=request.user, course=crs, program=prog, file=file, attempt=attempt)
                prf.save()
            elif len(result) < 2:
                attempt = 2
                file._name = request.user.first_name + str(attempt) +"."+ file._name.split('.')[1]
                prf = program_file(student=request.user, course=crs, program=prog, file=file, attempt=attempt)
                prf.save()
            else:
                attempt = "Attempts Overed"
            if attempt != "Attempts Overed":
                result = exam_attempts(student=request.user, course=crs, attempt=attempt)
                result.save()

        messages.info(request,'Program saved successfully')
        return redirect('index')


    return redirect('index')

###
@login_required(login_url='')
def setprogrammarks(request):
    id = request.GET['id']
    value = request.GET['value']
    ex = exam_attempts.objects.get(id=id)
    ex.marks = value
    ex.save()

    crs = ex.course
    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    row = models.user_profile.objects.get(user_id=request.user).student_performance_row
    row = int(row)

    if crs.name.find('Adv') == 0:
        col = all_fields_index['student_performance']['Adv Practical (Out of 40)']
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=row, value=[value], col=col, cell=True)
        messages.info(request,'Program marks saved')
    if crs.name.find('WD') == 0:
        col = all_fields_index['student_performance']['WD Practical (Out of 150)']
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=row, value=[value], col=col, cell=True)
        messages.info(request,'Program marks saved')
    return HttpResponse("")

def setoralmarks(request):
    id = request.GET['id']
    marks = request.GET['marks']
    gname = request.GET['gname']
    gp = Group.objects.filter(name=gname)
    gpinfo = models.groupsinfo.filter(group=gp)
    us = User.objects.get(id=id)
    up = models.user_profile.objects.filter(user_id=us)
    row = up.student_performance_row
    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value

    # sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=row, value=[marks], col=col, cell=True)
    return HttpResponse("")