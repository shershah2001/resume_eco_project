from django.shortcuts import render,redirect
from account.forms import user_register,user_login,address_form,UserProfileForm
from account.models import MyUser,UserProfileModel,AddressModel
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import address_form,UserProfileForm
# Create your views here.


def registerView(request):
    if request.method == "POST":
        form = user_register(request.POST)
        if form.is_valid():
            messages.success(request,"User registered successfully")
            messages.info(request,"Please login to continue")
            # messages.error(request,error)
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


def userlogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


# def addressView(request):
#     if  request.method  == "POST":
#         # address_update = AddressModel.objects.get(user=request.user)
#         form = address_form(request.POST)
#         if form.is_valid():
#             address =  form.save(commit=False)
#             address.user  = request.user
#             address.save()
#             messages.success(request,'Address added successfully')
#             return redirect('address')

#     else:
#         form = address_form()
#         print(form.fields['state'].choices)
#     context={
#         "form":form
#     }
#     return render(request,"accounts/addressform.html",context)
                                                                                                        
# def addressView(request):
#     if request.method == "POST":
#         form = address_form(request.POST)
#         if form.is_valid():
#             address = form.save(commit=False)
#             address.user = request.user
#             address.save()
#             messages.success(request, 'Address added successfully')
#             return redirect('address')
#         else:
#             print("Form errors:", form.errors)  # ← add this
#     else:
#         form = address_form()
#         print("Form fields:", form)  # ← add this
#         print(form.fields['state'].choices)

#     context = {"form": form}
#     return render(request, "accounts/addressform.html", context)                                                                                                       


# ✅ Sahi code
def addressView(request):
    if request.method == "POST":
        form = address_form(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully')
            return redirect('userprofile')
        else:
            print("Form errors:", form.errors)
    else:                          # ← SIRF GET pe blank form
        form = address_form()

    context = {"form": form}
    return render(request, "accounts/addressform.html", context)

# def userprofile(request):   

#     if request.method=="POST":
#         profile = UserProfileModel.objects.filter(user=request.user).first()
#         form = UserProfileForm(request.POST,instance = profile)
#         if form.is_valid():
#             profile_form = form.save(commit=False)
#             profile_form.user = request.user
#             profile_form.save()
#     else:
#         form = UserProfileForm()
#     context={
#         "form":form
#     }
#     return render(request,"accounts/userprofile.html",context)


def userprofile(request):
    if request.method == "POST":
        profile = UserProfileModel.objects.filter(user=request.user).first()
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_form = form.save(commit=False)
            profile_form.user = request.user
            profile_form.save()
    else:
        form = UserProfileForm()

    # ← address_form bhi pass karo
    addr_form = address_form()

    context = {
        "form": form,
        "addr_form": addr_form,   # ← naya
    }
    return render(request, "accounts/userprofile.html", context)


