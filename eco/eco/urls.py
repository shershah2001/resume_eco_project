from django.contrib import admin
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from products import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include('account.urls')),
    path('cart/',include('carts.urls')),
    path('',views.home,name='home'),
    path('store/',include('products.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)