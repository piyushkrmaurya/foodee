from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('dish/<int:dish_id>', views.dish),
    path('dish/<str:dish_name>', views.dish),
    path('toggle_fav/<int:dish_id>', views.toggleFav),
    path('cart/', views.cart),
    path('add_to_cart/<int:dish_id>', views.addToCart),
    path('remove_from_cart/<int:dish_id>', views.removeFromCart),
    path('change_quantity/<int:dish_id>/<int:quantity>', views.changeQuantity),
    path('empty_cart/', views.emptyCart),
    path('order_now/', views.orderNow),
]