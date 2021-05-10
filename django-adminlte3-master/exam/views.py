from django.shortcuts import render,redirect,HttpResponse
from .models import *
import random
from django.core.paginator import Paginator

# Create your views here.
def add_questions(request):
    if request.method == 'POST':
        print(request.POST)
        cname = request.POST['cname']
        # print(cname)
        count = 0
        try:
            crs = course.objects.get(name=cname,type=request.POST['type'])
            crs.instructions=request.POST['instructions']
            crs.time=request.POST['time']
            crs.save()
        except:
            crs = course(name=cname,type=request.POST['type'],time=request.POST['time'])
            crs.save()
        courses = course.objects.all()

        if request.POST['type'] == 'MCQ':
            for field in request.POST:
                if field.find('question')==0:
                    qno = field.replace('question','')
                    choice = "choice"+qno
                    ans = "ans"+qno
                    expla = "explanation"+qno
                    # print(field,qno,choice)
                    # print(request.POST[field])
                    q = questions(course=crs,question=request.POST[field])
                    q.save()
                    # print(request.POST.getlist(choice))
                    for op,i in zip(request.POST.getlist(choice),range(1,len(request.POST.getlist(choice))+1)):
                        o = options(question=q,option=op,status=False)
                        o.save()
                        # print(op,i)
                        if str(i) in request.POST.getlist(ans):
                            # print(op,i)
                            o.status=True
                            try:
                                o.explanation=request.POST[expla]
                            except:
                                pass
                            o.save()
                    # print(request.POST.getlist(ans))
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
        try:
            if type == "MCQ":
                crs = course.objects.get(id=1,name=cname, type=type)
            else:
                crs = course.objects.get(name=cname, type=type)
        except:
            crs = course.objects.get(name=cname,type=type)
            pass
        # print(crs.id)
        if crs.type == 'MCQ':
            ques = questions.objects.all().filter(course=crs.id)
            rand_question = random.sample(set(ques),20)
            # print(rand_question)
            ques_set = []
            for q in rand_question:
                a = {}
                a['question']=(q)
                a['options']=(options.objects.all().filter(question=q))
                ques_set.append(a)
                # print(a)
            print(ques_set)
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
            crs = course.objects.get(id=1, name=cname, type=type)
            # print(crs.id)
            ques = questions.objects.all().filter(course=crs.id)
            # rand_question = random.sample(set(ques), 20)
            # print(rand_question)
            ques_set = []
            for q in ques:
                a = {}
                a['question'] = (q)
                a['options'] = (options.objects.all().filter(question=q))
                ques_set.append(a)
                # print(a)
            print(ques_set)
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
    for field in request.POST:
        marks = 0
        if field.find('ans')==0:
            # print(field)
            qno = field.replace("ans",'')
            q = questions.objects.get(id=int(qno))
            for opt in request.POST.getlist(field):
                if options.objects.get(id=int(opt)).status:
                    print(qno, opt)
                    flag = True
                    print("true")
                else:
                    flag = False
                    print("false")
                    break
            if flag:
                marks +=2
                print("success")

    crs = course.objects.get(id=1,name=request.POST['cname'])
    result = exam_attempts.objects.filter(student=request.user)
    if len(result)==0:
        result = exam_attempts(student=request.user,course=crs,attempt=1,marks=marks)
        result.save()
    elif len(result)<2:
        result = result[0]
        result.course = crs
        result.attempt = 2
        result.marks = marks
        result.save()
    else:
        return HttpResponse("Attempts Overed")

    print(marks)
    return HttpResponse(str(marks))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def get_answers(request):
    print("hi")
    print(request.POST)

    # print(request.POST['question-set[]'])
    q_a_set = []
    for q in request.POST.getlist('question_set[]'):
        dic = {}
        opts = []
        for o in options.objects.filter(question=int(q)):
            # a = vars(o)
            vars(o)['_state'] = "none"
            print(vars(o))
            opts.append(vars(o))
        dic['question'] = q
        dic['options'] = opts
        q_a_set.append(dic)
    print(q_a_set)
    return HttpResponse(str(q_a_set).replace("'",'"').replace('False','false').replace('True','true'))


def practicle_exam(request):
    return  render(request,'practicle.exam')