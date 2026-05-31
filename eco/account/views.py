from django.shortcuts import render,redirect
from account.forms import user_register,user_login
from account.models import MyUser
from django.contrib.auth import authenticate,login
from django.contrib import messages
# Create your views here.


def registerView(request):
    if request.method == "POST":
        form = user_register(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = user_register()
    context={
        'form':form
    }
    return render(request,"accounts/register.html",context)

def userlogin(request):
    if request.method=='POST':
        form = user_login(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            
            user = authenticate(email=email,password=password)

            if user:
                login(request,user)
                messages.success(request,"Login successful!")
                return redirect('home')
            else:
                messages.error(request,'Invalid email or password')
    else:
        form = user_login()
    context={
        'form':form
    }
    return render(request,'accounts/login.html',context)


def home(request):
    return render(request,'accounts/home.html')
