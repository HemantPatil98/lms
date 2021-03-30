from django.shortcuts import render

# Create your views here.
def addstudent(request):
    return render(request,'admin/add_student1.html')


def viewstudent(request):
    fp = open('student_profile.txt', 'r')
    sheetid = fp.read()
    fp.close()

    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    data = sheetsapi.sheetvalues(sheetid,sheetname)
    print(data)
    return HttpResponse("")