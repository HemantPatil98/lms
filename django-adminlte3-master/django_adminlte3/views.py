from django.shortcuts import render,HttpResponse,redirect

def st(request):
    return render(request,'adminlte/login.html')