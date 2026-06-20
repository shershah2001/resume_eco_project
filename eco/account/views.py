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
    if request.method == "POST":
        form = user_login(request.POST)

        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=email,
                password=password
            )

            print("USER :", user)

            if user:
                login(request, user)

                next_url = request.POST.get('next')

                if next_url:
                    return redirect(next_url)

                return redirect('home')

            messages.error(request, "Invalid email or password")

    else:
        form = user_login()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )

def userprofile(request):
    return render(request,"accounts/userprofile.html")


