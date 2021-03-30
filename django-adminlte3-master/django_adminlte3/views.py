from django.shortcuts import render,HttpResponse,redirect
from . import sheetsapi
import datetime

def st(request):
    return render(request,'adminlte/login.html')

def addstudent(request):
    Basic = {"center":"","dateofadmission":"","course":"","batchstartdate":"","startcourse":"","trainingmode":""}
    Personal_details = {"name":"","address":"","dateofbirth":"","contact":"","emailid":"","alternatecontact":""}
    Educational_details = [
        {'secondary':"", 'stream10':"", 'collegename10':"", 'boardname10':"", 'yearofpassing10':"", 'percentage10':""},
        {'hsecondary':"", 'stream12':"", 'collegename12':"", 'boardname12':"", 'yearofpassing12':"", 'percentage12':""},
        {'graduation':"", 'streamg':"", 'collegenameg':"", 'boardnameg':"", 'yearofpassing':"", 'percentageg':""},
        {'pg':"", 'streampg':"", 'collegenamepg':"", 'boardnamepg':"", 'yearofpassinpg':"", 'percentagepg':""}
    ]

    Fees = {"fees":"","mode":"","regammount":"","installment1":"","installment2":"","installment3":"",
            "regdate":"","installment1date":"","installment2date":"","installment3date":""}

    Remark = {"remark":""}
    addstudentform = {"Basic":Basic,"Personal_details":Personal_details,"Educational_details":Educational_details,"Fees":Fees,"Remark":Remark}


    filledaddstudentform = []

    flag = True

    acced = [[],[],[]]

    i = -1

    for section in addstudentform:
        for fields in addstudentform[section]:
            if isinstance(fields,dict):
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

    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    index = "=INDIRECT(" + '"A"' + "&ROW()-4)+1"
    if sheetsapi.sheetvalues(sheetid,sheetname) is None:
        index = 1

    sheetsapi.appendsheet(sheetid,[index,""]+filledaddstudentform)
    sheetsapi.appendsheet(sheetid,["",""]+[""]*12+acced[0])
    sheetsapi.appendsheet(sheetid,["",""]+[""]*12+acced[1])
    sheetsapi.appendsheet(sheetid,["",""]+[""]*12+acced[2])

    for i in range(10,16):
        filledaddstudentform[i]=acced[2][i-10]
        # print(filledaddstudentform[i])

    print(addstudentform)
    # print(filledaddstudentform)

    fp = open('student_performance.txt', 'r')
    sheetid = fp.read()
    fp.close()

    student_performance = ['name','contact','emailid','dateofadmission','trainingmode',]

    # sheetsapi.appendsheet(sheetid, ["", ""] + filledaddstudentform)

    return HttpResponse("HIs")


def viewstudent(request,table):
    fp = open('student_profile.txt', 'r')
    sheetid = fp.read()
    fp.close()

    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    data = sheetsapi.sheetvalues(sheetid,sheetname)
    print(data)
    return render(request,'admin/view_data.html',{'data':data})