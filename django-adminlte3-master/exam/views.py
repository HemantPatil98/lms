from django.shortcuts import render,redirect,HttpResponse
from .models import *
import random
from django.core.paginator import Paginator
from lms import models,sheetsapi
# Create your views here.
def add_questions(request):
    if request.method == 'POST':
        print(request.POST)
        cname = request.POST['cname']
        count = 0
        type = request.POST['type']
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
            # crs.save()
            try:
                SPREADSHEET_ID = models.extra_data.objects.get(name=type).value
            except:
                if type == 'MCQ':
                    fields = ["Question","Option1","Option2","Option3","Option4","Answer"]
                else:
                    fields = ["program"]
                SPREADSHEET_ID = sheetsapi.createsheet(name=type,columns=fields,sheetname=cname)
                ext = models.extra_data(name=type, value=SPREADSHEET_ID)
                ext.save()
                ext = models.extra_data(name=cname,value=1)
                ext.save()
                print("IN CREATE SHEET")
            else:
                if type == 'MCQ':
                    fields = ["Question", "Option1", "Option2", "Option3", "Option4", "Answer"]
                else:
                    fields = ["program"]
                sheetsapi.addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=cname,columns=fields)
                ext = models.extra_data(name=(cname+"_"+type),value=1)
                ext.save()
                print("IN ADD SHEET")

            crs.save()
        courses = course.objects.all()

        if request.POST['type'] == 'MCQ':
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
            print(len(count))

        elif request.POST['type'] == 'PROGRAM':
            for field in request.POST:
                print(field)
                if field.find('question')==0:
                    p = program(course=crs,programe=request.POST[field])
                    p.save()

            count = program.objects.all().filter(course=crs)

        return render(request,'add_question.html',{'crs':crs,'courses':courses,'count':count})

    courses = course.objects.all()
    return render(request,'add_question.html',{'courses':courses})

def mcq_exam(request):
    if request.method == 'POST':
        print(request.POST['cname'])
        count = 0
        cname = request.POST['cname']
        type = request.POST['type']
        crs = course.objects.get(name=cname, type=type)

        print(crs.id)
        if crs.type == 'MCQ':
            ques = questions.objects.all().filter(course=crs)
            # print(list(ques))
            ques = list(ques)
            random.shuffle(ques)
            # print(rand_question)
            # print(ques)
            ques_set = ques[:2]
            # for q in rand_question:
            #     a = {}
            #     a['question']=(q)
            #     a['options']=(options.objects.all().filter(question=q))
            #     ques_set.append(a)
            #     # print(a)
            # print(ques_set)
            courses = course.objects.all()
            return render(request, 'mcq_exam.html',
                          {'crs': crs, 'count': count, 'courses': courses, 'ques_set': ques_set})
        elif crs.type == 'PROGRAM':

            prog = program.objects.all().filter(course=crs.id)
            prog_set = random.sample(set(prog),2)
            courses = course.objects.all()

            print(prog_set)
            return render(request, 'practicle_exam.html', {'crs': crs, 'count': count, 'courses': courses, 'prog_set': prog_set})

    courses = course.objects.all()
    return render(request,'mcq_exam.html',{'courses':courses})

def view_questions(request,pageno=1):
    if request.user.is_superuser:
        if request.method == 'POST':
            print(request.POST['cname'])
            count = 0
            cname = request.POST['cname']
            type = request.POST['type']
            crs = course.objects.get(name=cname, type=type)
            # print(crs.id)
            ques = questions.objects.all().filter(course=crs.id)
            # rand_question = random.sample(set(ques), 20)
            # print(rand_question)
            ques_set = ques
            # for q in ques:
            #     a = {}
            #     a['question'] = (q)
            #     a['options'] = (options.objects.all().filter(question=q))
            #     ques_set.append(a)
            #     # print(a)
            # print(ques_set)
            # try:
            #     pageno = request.POST['page']
            # except:
            #     pageno = 1

            # if pageno == 1:
            pageno = request.POST['page']
            p = Paginator(ques_set, 20)
            # else:
            #     p = Paginator(ques_set, 12)
            page = p.page(pageno)
            courses = course.objects.all()
            return render(request,'view_questions.html',{'crs':crs,'count':count,'courses':courses,'ques_set':page})
        courses = course.objects.all()
        return render(request,'view_questions.html', {'courses': courses})
    return redirect(request,'index')

def mcq_validate(request):
    print(request.POST)
    marks = 0
    answers = []
    anss = request.POST
    for qno in request.POST['qnos'].split(','):
        # if field.find('ans')==0:
        ans = "ans"+qno
        q = questions.objects.get(id=int(qno))
        answers.append({'question':qno,'answer':q.answer})
        if ans in anss:
            ans = request.POST[ans]
            # print(ans)
            if q.answer == ans:
                print("Success")
                marks += 2
            else:
                print("Failed")
    print(answers)
    crs = course.objects.get(name=request.POST['cname'],type=request.POST['type'])
    result = exam_attempts.objects.filter(student=request.user,course=crs, type=request.POST['type'])
    if len(result)==0:
        attempt = 1
        result = exam_attempts(student=request.user,course=crs,attempt=attempt,marks=marks)
        result.save()
    elif len(result)<2:
        attempt = 2
        result = exam_attempts(student=request.user, course=crs, attempt=attempt, marks=marks)
        result.save()
    else:
        attempt = "Attempts Overed"

    print(marks)
    data = {
        "marks":marks,
        "attempt": attempt,
        "answers":answers
    }
    return HttpResponse(str(data))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_answers(request):
    print("hi")
    print(request.POST)

    # print(request.POST['question-set[]'])
    # q_a_set = []
    # for q in request.POST.getlist('question_set[]'):
    #     dic = {}
    #     opts = []
    #     for o in options.objects.filter(question=int(q)):
    #         # a = vars(o)
    #         vars(o)['_state'] = "none"
    #         print(vars(o))
    #         opts.append(vars(o))
    #     dic['question'] = q
    #     dic['options'] = opts
    #     q_a_set.append(dic)
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
            ques = sheetsapi.sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=c.name,range="!A"+fetch_from+":F")
            print(last_update)
            print(ques)
            if ques:
                for q in ques:
                    q = questions(course=c,question=q[0],option1=q[1],option2=q[2],option3=q[3],option4=q[4],answer=q[5])
                    q.save()
                ext_row.value = int(last_update) + len(ques)
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
    exa = exam_attempts.objects.all().filter(course=crs)
    # print(exa)
    data = []
    for e in exa:
        a = vars(e)
        a["_state"] = "NONE"
        c = vars(course.objects.get(id=a["course_id"]))
        c["_state"] = "NONE"
        # a["course_id"] = vars(c)
        c['course'] = c['name']
        c.pop('name')
        s = vars(User.objects.get(id=a['student_id']))
        # s.pop("first_name")
        a['name'] = s['first_name']
        a['programs'] = "?attempt_id="+str(a['id'])
        a.update(c)
        # a.update(s)
        # print(c,a)
        data.append(a)
    print(data)
    return HttpResponse(str(data).replace("'",'"').replace('None','"NONE"').upper())

def view_practicle(request):
    attempt = request.GET['ATTEMPT_ID']
    ex = exam_attempts.objects.get(id=int(attempt))
    prog_ans = program_ans.objects.filter(student=ex.student_id,course=ex.course.id,attempt=ex.attempt)
    print(prog_ans)
    courses = course.objects.all()
    crs = courses.get(id=ex.course.id)
    return render(request,'view_practicle.html',{'crs':crs,'courses':courses,'prog_set':prog_ans,'ex':ex})

def marks_practicle(request):
    print(request.POST)
    marks = 0
    for m in request.POST.getlist('marks'):
        marks += int(m)
    print(marks)
    attempt = request.POST['attempt']
    ex = exam_attempts.objects.get(id=int(attempt))
    ex.marks = marks
    ex.save()
    return HttpResponse("")