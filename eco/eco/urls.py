from django.contrib import admin
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from products import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('account.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path('cart/',include('carts.urls')),
    path('',views.home,name='home'),
    path('products/',include('products.urls')),
    path('wishlist/',include('wishlist.urls')),
    path("orders/",include('orders.urls')),
    path('store/',include('searchfunctionality.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)