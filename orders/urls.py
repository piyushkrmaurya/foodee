from django.urls import path, re_path, include
from . import views

urlpatterns = [
    re_path(r'^search/$', views.search),
    path('dish/<int:dish_id>', views.dish),
    path('dish/<str:dish_name>', views.dish),
    path('toggle_fav/<int:dish_id>', views.toggleFav),
    path('cart/', views.cart),
    path('add_to_cart/<int:dish_id>', views.addToCart),
    path('remove_from_cart/<int:dish_id>', views.removeFromCart),
    path('change_quantity/<int:dish_id>/<int:quantity>', views.changeQuantity),
    path('empty_cart/', views.emptyCart),
    path('change_stars/<int:dish_id>', views.changeStars),
    path('order_now/', views.orderNow),
]