from django.shortcuts import render,redirect,HttpResponse

def error(request):
    return render(request,'student/base.html')