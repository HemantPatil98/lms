from django.shortcuts import render,redirect,HttpResponse
from .models import *
import random
from django.contrib import messages
from django.core.paginator import Paginator
from lms import models,sheetsapi
from datetime import datetime
import os
# Create your views here.

student_performance = {'id':"A",'name':"B",'contact':"C",'emailid':"D",'dateofadmission':"E",'trainingmode':"F",'coursestartdate':"G",'course':"H",
                       'coursestartfrom':"I",'currentmodule':"J",
                       'ctrainername':"K",'cmodulestart':"L",'cmoduleend':"M",'ctheory':14,'cpractical':15,'coral':16,'ctotal':17,
                       'sqltrainername':18,'sqlmodulestart':19,'sqlmoduleend':20,'sqltheory':21,'sqlpractical':22,'sqloral':23,'sqltotal':24,
                       'wdtrainername':25,'wdmodulestart':26,'wdmoduleend':27,'wdpractical':8,'wdoral':29,'wdtotal':30,'portfoliolink':31,
                       'mock1':32,'projectguid':33,'miniproject':34,
                       'coretrainername':35,'coremodulestart':36,'coremoduleend':37,'coretheory':38,'corepractical':39,'coreoral':40,'coretotal':41,'mock2':42,
                       'advtrainername':43,'advmodulestart':44,'advmoduleend':45,'advtheory':46,'advpractical':47,'advoral':48,'advtotal':49,
                       'fullcoursseend':"AX",'cravitaprojectstart':"AY",'mock3':"AZ",'softskill':"BA",'finalmock':"BB",'totalmarks':"BC",'eligiableforplacement':"BD",
                       'remark':"BE"}

def add_questions(request):
    if request.method == 'POST':
        print(request.POST)
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
            # crs.time=request.POST['time']
            crs.save()
        except:
            crs = course(name=cname,type=type,time=request.POST['time'])
            os.mkdir('media/videos/courses/PYTHON')
            # crs.save()
            try:
                SPREADSHEET_ID = models.extra_data.objects.get(name=type).value
            except:
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
                print("IN CREATE SHEET")
            else:
                if type == 'MCQ':
                    fields = ["Question", "Option1", "Option2", "Option3", "Option4", "Answer",'Explanation']
                elif type == 'PRACTICAL':
                    fields = ["Program"]
                elif type == 'PROGRAM':
                    fields = ["Program"]
                sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=cname,columns=fields)
                ext = models.extra_data(name=(cname+"_"+type),value=1)
                ext.save()
                print("IN ADD SHEET")

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
                    # sheetsapi.appendsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=type,values=[[request.POST[field],choice[0],
                    #                                                                            choice[1],choice[2],choice[3]]])
            count = questions.objects.all().filter(course=crs)
            print(len(count))

        elif type == 'PRACTICAL':
            for field in request.POST:
                print(field)
                if field.find('question')==0:
                    p = program(course=crs,programe=request.POST[field])
                    p.save()

            count = program.objects.all().filter(course=crs)

        elif type == 'PROGRAM':
            for field in request.POST:
                print(field)
                if field.find('question')==0:
                    p = program(course=crs,programe=request.POST[field])
                    p.save()

            count = program.objects.all().filter(course=crs)

        messages.info(request,'Question Added')
        return render(request,'add_question.html',{'crs':crs,'courses':courses,'count':count})

    ext = models.extra_data.objects.all()

    ext = {'mcq_sheet':ext.filter(name='MCQ')[0].value,'practical_sheet':ext.filter(name='PRACTICAL')[0].value,
           'program_sheet':ext.filter(name='PROGRAM')[0].value}

    courses = course.objects.values_list('name', flat=True).distinct()
    return render(request,'add_question.html',{'courses':courses,'ext':ext})

def mcq_exam(request):
    if request.method == 'POST':
        print(request.POST['cname'])
        count = 0
        cname = request.POST['cname']
        type = request.POST['type']
        crs = course.objects.get(name=cname, type=type)

        print(crs.type)
        if crs.type == 'MCQ':
            ques = questions.objects.all().filter(course=crs)
            ques = list(ques)
            random.shuffle(ques)
            ques_set = ques[:2]
            courses = course.objects.values_list('name', flat=True).distinct()
            attempt = exam_attempts.objects.filter(student=request.user,course=crs)
            attempt = len(attempt)

            return render(request, 'mcq_exam.html',
                          {'crs': crs, 'count': count, 'courses': courses, 'ques_set': ques_set, 'attempt':attempt})
        elif crs.type == 'PRACTICAL':

            prog = program.objects.all().filter(course=crs.id)
            prog_set = random.sample(set(prog),2)
            courses = course.objects.values_list('name', flat=True).distinct()
            attempt = exam_attempts.objects.filter(student=request.user,course=crs)
            attempt = len(attempt)

            return render(request, 'practicle_exam.html', {'crs': crs, 'count': count, 'courses': courses,
                                                           'prog_set': prog_set,'attempt':attempt})

        elif crs.type == 'PROGRAM':
            prog = program.objects.all().filter(course=crs.id)
            prog_set = random.sample(set(prog), 1)
            courses = course.objects.values_list('name', flat=True).distinct()
            attempt = exam_attempts.objects.filter(student=request.user,course=crs)
            attempt = len(attempt)

            return render(request, 'practicle_exam.html', {'crs': crs, 'count': count, 'courses': courses,
                                                           'prog_set': prog_set,'attempt':attempt})

    courses = course.objects.values_list('name', flat=True).distinct()
    return render(request,'mcq_exam.html',{'courses':courses})

def view_questions(request,pageno=1):
    if request.user.is_superuser:
        if request.method == 'POST':
            print(request.POST['cname'])
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

def mcq_validate(request):
    print(request.POST)
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
                # print("Success")
                marks += 2
            # else:
            #     print("Failed")

    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    result_attempts = exam_attempts.objects.filter(student=request.user,course=crs)

    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    row = models.user_profile.objects.get(user_id=request.user).student_performance_row
    row = int(row)

    if crs.name == 'C':
        col = student_performance['ctheory']
    elif crs.name == 'SQL':
        col = student_performance['sqltheory']
    elif crs.name.find('Core')==0:
        col = student_performance['coretheory']
    elif crs.name.find('Adv')==0:
        col = student_performance['advtheory']

    # print(col)
    y = request.user.date_joined.strftime('%Y')
    # print(d)
    SHEET_NAME = "Apr - Mar "+y
    # value = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=SHEET_NAME,range="!"+str(col)+":"+str(col))
    # print(value)
    print(result_attempts)
    hmarks = 0
    for h in result_attempts:
        if h.marks >= marks:
            hmarks=h.marks
    print(hmarks,marks)
    if len(result_attempts)==0:
        attempt = 1
        result = exam_attempts(student=request.user,course=crs,attempt=attempt,marks=marks)
        result.save()
        # SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
        # sp = user_profile.objects.get(user_id=request.user).student_performance_row
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=row, value=[marks], col=col, cell=True)
    elif len(result_attempts)<crs.attempts_allowed:
        attempt = len(result_attempts)+1
        result = exam_attempts(student=request.user, course=crs, attempt=attempt, marks=marks)
        result.save()
        if marks>hmarks:
            sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=SHEET_NAME, row=row,value=[marks],col=col,cell=True)
    else:
        attempt = "Attempts Overed"

    print(marks)
    data = {
        "marks":marks,
        "attempt": attempt,
        "answers":answers
    }
    messages.info(request,'Mcq Validated')
    return HttpResponse(str(data))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_answers(request):
    print("hi")
    print(request.POST)

    q_a_set = questions.objects.filter(id=request.POST.getlist('question_set[]'))
    print(q_a_set)
    return HttpResponse(str(q_a_set).replace("'",'"').replace('False','false').replace('True','true'))

def practicle_exam(request):
    return render(request,'practicle.exam')


def sync_questions(request):
    print("in sync")
    courses = course.objects.all()
    ext = models.extra_data.objects.all()
    for c in courses:
        if c.type == "MCQ":
            SPREADSHEET_ID = models.extra_data.objects.get(name='MCQ').value
            ext_row = ext.get(name=c.name+"_MCQ")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            ques = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":G")
            print(last_update)
            print(ques)
            if ques:
                for q in ques:
                    q = questions(course=c,question=q[0],option1=q[1],option2=q[2],option3=q[3],option4=q[4],answer=q[5],explanation=q[6])
                    q.save()
                ext_row.value = int(last_update) + len(ques)
                ext_row.save()
        elif c.type == "PRACTICAL":
            SPREADSHEET_ID = models.extra_data.objects.get(name='PRACTICAL').value
            ext_row = ext.get(name=c.name+"_PRACTICAL")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            programs = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":F")
            print(programs)
            if programs:
                for p in programs:
                    print(p[0])
                    p = program(course=c,programe=p[0])
                    p.save()
                ext_row.value = int(last_update) + len(programs)
                ext_row.save()
        elif c.type == "PROGRAM":
            SPREADSHEET_ID = models.extra_data.objects.get(name='PROGRAM').value
            ext_row = ext.get(name=c.name+"_PROGRAM")
            last_update = ext_row.value
            fetch_from = str(int(last_update)+1)
            programs = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":F")
            print(programs)
            if programs:
                for p in programs:
                    print(p[0])
                    p = program(course=c,programe=p[0])
                    p.save()
                ext_row.value = int(last_update) + len(programs)
                ext_row.save()
    messages.info(request,'Questione Sync Complete')
    return HttpResponse("")

def savepracticle(request):
    print(request.POST)
    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    for field in request.POST:
        if field.find('ans') == 0:
            pno = field.replace('ans', '')
            answer = request.POST[field]
            prog = program.objects.get(id=pno)

            result = exam_attempts.objects.filter(student=request.user, course=crs)
            if len(result) == 0:
                attempt = 1
                p = program_ans(student=request.user, course=crs, program=prog, answer=answer, attempt=attempt)
                p.save()
            elif len(result) < 2:
                attempt = 2
                p = program_ans(student=request.user, course=crs, program=prog, answer=answer, attempt=attempt)
                p.save()
            else:
                attempt = "Attempts Overed"
    if attempt != "Attempts Overed":
        result = exam_attempts(student=request.user, course=crs, attempt=attempt)
        result.save()
    messages.info(request,'Practical saved successfully')
    return redirect('index')

def practicle_validate(request):
    courses = course.objects.values_list('name', flat=True).distinct()
    return render(request,'validate_practicle.html',{"courses":courses})

def getdata_practicle(request):
    print(request.GET)
    cname = request.GET['cname']
    type = request.GET['type']
    crs = course.objects.get(name=cname,type=type)
    print(crs,type)
    exa = exam_attempts.objects.filter(course=crs).order_by('-id')
    # print(exa)
    data = []
    for e in exa:
        a = vars(e)
        a["_state"] = 'none'
        c = vars(course.objects.get(id=a["course_id"]))
        c["_state"] = 'none'
        c['course'] = c['name']
        c.pop('name')
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
        # a.update(s)
        # print(c,a)
        data.append(a)
    print(data)
    print(str(data).replace('None',"'NONE'"))
    return HttpResponse(str(data).replace('None',"'none'").replace("'",'"'))

def getdata_programs(request):
    return HttpResponse()


def view_practicle(request):
    attempt = request.GET['attempt_id']
    ex = exam_attempts.objects.get(id=int(attempt))
    prog_ans = program_ans.objects.filter(student=ex.student_id,course=ex.course.id,attempt=ex.attempt)
    # print(prog_ans)
    courses = course.objects.values_list('name', flat=True).distinct()
    crs = course.objects.get(id=ex.course.id)
    gname = prog_ans[0].student.groups.get(name__startswith=crs.name).name
    # print(prog_ans[0].student.groups.filter(name_startswith="cname").name)
    return render(request,'view_practicle.html',{'crs':crs,'courses':courses,'prog_set':prog_ans,'ex':ex,'gname':gname})

def marks_practicle(request):
    print(request.POST)
    marks = 0
    for m in request.POST.getlist('marks'):
        marks += int(m)
    # print(marks)
    attempt = request.POST['attempt']
    ex = exam_attempts.objects.get(id=int(attempt))
    ex.marks = marks
    ex.save()
    crs = ex.course
    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    sheetname = "Apr - Mar " + datetime.now().strftime("%Y")
    row = models.user_profile.objects.get(user_id=request.user).student_performance_row
    row = int(row)
    # print(SPREADSHEET_ID, row)
    if crs.name == 'C':
        col = student_performance['cpractical']
    elif crs.name == 'SQL':
        col = student_performance['sqlpractical']
    elif crs.name.find('Core') == 0:
        col = student_performance['corepractical']
    elif crs.name.find('Adv') == 0:
        col = student_performance['advpractical']

    # print(col)

    sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, SHEET_NAME=sheetname, row=row+1, value=[marks], col=col, cell=True)

    return redirect('practical_validate')

def saveprogram(request):
    print(request.FILES)
    print(request.POST)
    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    for field in request.FILES:
        if field.find('file')==0:
            file = request.FILES[field]
            print(file)

            pno = field.replace('file', '')
            # answer = request.POST[field]
            prog = program.objects.get(id=pno)

            result = exam_attempts.objects.filter(student=request.user, course=crs)
            print(result)
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


    return HttpResponse("")

def setprogrammarks(request):
    print(request.GET)
    id = request.GET['id']
    value = request.GET['value']
    ex = exam_attempts.objects.get(id=id)
    ex.marks = value
    ex.save()

    crs = ex.course
    SPREADSHEET_ID = models.extra_data.objects.get(name='student_performance').value
    row = models.user_profile.objects.get(user_id=request.user).student_performance_row
    row = int(row)
    print(SPREADSHEET_ID, row)

    if crs.name.find('Adv') == 0:
        col = student_performance['advpractical']
        print(col)
        sheetsapi.updatesheet(SPREADSHEET_ID=SPREADSHEET_ID, row=row, value=[value], col=col, cell=True)
        messages.info(request,'Program marks saved')
    return HttpResponse("")