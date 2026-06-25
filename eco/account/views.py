from django.shortcuts import render,redirect
from account.forms import user_register,user_login,address_form,UserProfileForm
from account.models import MyUser,UserProfileModel,AddressModel
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import address_form,UserProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

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


@login_required
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

import json
@login_required
def editAddressView(request,id):
    address = get_object_or_404(
        AddressModel,
        user=request.user,
        id=id
    )
    #GET
    if request.method == 'GET':
        data={
            "name":address.name,
            "mobile":address.mobile,
            "pincode":address.pincode,
            "locality":address.locality,
            "address":address.address,
            "city":address.city,
            "state":address.state,
            "landmark":address.landmark,
            "alternate_mobile":address.alternate_mobile,
            "address_type":address.address_type
        }

        return JsonResponse(data)
    
    # POST (UPDATE)
    print("request.post=>",request.POST)
    print("request.body=>",request.body)
    print(json.loads(request.body))
    if request.method == 'POST':
        data = json.loads(request.body)
        form=address_form(
            data,
            instance=address
        )
        if form.is_valid():
            update_address=form.save(commit=False)
            update_address.user=request.user
            update_address.save()

            return JsonResponse({
                "success":True
            })
        return JsonResponse({
            "success":False,
            "errors":form.errors
        })
   
# delete view  start  here
@login_required
def deleteAddressView(request,id):
    if request.method == 'POST':
        address = get_object_or_404(AddressModel,user=request.user,id=id)
        address.delete()
        return JsonResponse({
            "success":True
        })
    return JsonResponse({
        "success":False
    })

@login_required
def userprofile(request):
    user_address = AddressModel.objects.filter(user=request.user)
    profile = UserProfileModel.objects.filter(user=request.user).first()
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_form = form.save(commit=False)
            profile_form.user = request.user
            profile_form.save()
            print("Saved Successfully")
    else:
        form = UserProfileForm(instance=profile)
        print(form.errors)
    
    addr_form = address_form()

    context = {
        "form": form,
        "addr_form": addr_form, 
        "user_address":user_address
    }
    return render(request, "accounts/userprofile.html", context)


