from django.urls import path
from searchfunctionality import views


urlpatterns = [
    path('search/',views.searchview,name="search")   
]
