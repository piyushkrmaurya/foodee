from django.contrib import admin
from orders.models import Profile, Dish, Order, Tag, OrderItem, Review

admin.site.register(Profile)
admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Tag)
admin.site.register(Review)
