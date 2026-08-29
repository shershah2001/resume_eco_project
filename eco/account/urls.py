from django.urls import path
from account import views
from carts.views import checkout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/',views.registerView,name="register"),
    path('login/',views.userlogin,name='login'),
    path('userprofile/',views.userprofile,name="userprofile"),
    path('address/',views.addressView,name="address"),
    path('address/<int:id>/', views.editAddressView, name='edit_address'),
    path('address/delete/<int:id>/',views.deleteAddressView,name="delete_address"),
    path('logout/',views.userlogout,name="logout"),
    path('logoutconfirmation/',views.logoutconfirmationpage,name='logoutconfirmationpage'),
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html'
    ),name="password_change"),
    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/change_password_confirmation.html'
    ),name="password_change_done"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="accounts/forgotpassword.html"
    ),name="password_reset"),
    path("password-reset/done/",auth_views.PasswordResetDoneView.as_view(),name="password_reset_done"),
    path("reset/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),name="password_reset_confirm"),
   path("reset/done/",auth_views.PasswordResetCompleteView.as_view(),name="password_reset_complete"),
   
]
