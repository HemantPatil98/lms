from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout


# Create your views here.
def log_in(request):
    email = request.POST['email']
    password = request.POST['password']
    us = authenticate(request, username=email, password=password)
    if us is not None:
        login(request, us)
        messages.info(request, "Successfully Log In")
        # Redirect to a success page.
        # response = redirect('index')
        return HttpResponse("Success")
    else:
        messages.info(request, "Log In Failed")
        # response = redirect('index')
        return HttpResponse("Failed")
