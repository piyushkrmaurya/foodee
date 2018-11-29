from django.contrib import admin
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup),
    path('profile/', views.profile),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('orders.urls')),
    path('my_orders/', views.myOrders),
    path('blog/',include('blog.urls')),
    path('sql', views.sql)
]
