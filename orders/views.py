from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem

def dish(request, dish_name=None, dish_id=None):
    dish = None
    profile = None
    try:
        order = Order.objects.filter(profile = request.user.profile).get(status = 0)
        cart = order.items.all()
    except Order.DoesNotExist:
        order = None
        cart = None
    if not request.user.is_anonymous:
        profile = request.user.profile
    if dish_name:
        dish_name = ' '.join(dish_name.split('_')).capitalize()
        dish = Dish.objects.get(name=dish_name)
    elif dish_id:
        dish = Dish.objects.get(id=dish_id)
    return render(request, "dish.html", {'title': dish.name, 'dish': dish, 'cart':cart, 'profile': profile})

@login_required
def toggleFav(request, dish_id):
    profile = request.user.profile
    dish = Dish.objects.get(id=dish_id)
    if dish not in profile.favs.all():
        profile.favs.add(dish)
        return HttpResponse({"success": "true"})
    else:
        profile.favs.remove(dish)
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

@login_required
def cart(request):
    try:
        order = Order.objects.filter(profile = request.user.profile).get(status = 0)
        cart = OrderItem.objects.filter(order = order)
    except Order.DoesNotExist:
        order = None
        cart = None
    return render(request, "cart.html", {'title': 'Cart', 'cart': cart, 'profile': request.user.profile})

@login_required
def addToCart(request,dish_id):
    try:
        order = Order.objects.filter(profile = request.user.profile).get(status = 0)
    except Order.DoesNotExist:
        order = Order.objects.create(status = 0, profile = request.user.profile)
    
    dish = Dish.objects.get(id = dish_id)
    if(dish not in order.items.all()):
        OrderItem.objects.create(dish = Dish.objects.get(id = dish_id), order = order)
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

@login_required
def removeFromCart(request,dish_id):
    order = Order.objects.filter(profile = request.user.profile).get(status = 0)
    OrderItem.objects.get(dish = Dish.objects.get(id = dish_id), order = order).delete()
    return HttpResponse({"success": "true"})

@login_required
def changeQuantity(request, dish_id, quantity):
    order = Order.objects.filter(profile = request.user.profile).get(status = 0)
    order_item = OrderItem.objects.get(dish = Dish.objects.get(id = dish_id), order = order)
    if quantity>0 and quantity<=10:
        order_item.quantity = quantity
        order_item.save()
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

@login_required
def emptyCart(request):
    Order.objects.filter(profile = request.user.profile).get(status = 0).delete()
    return HttpResponse({"success": "true"})

@login_required
def orderNow(request):
    order = Order.objects.filter(profile = request.user.profile).get(status = 0)
    order.status = 1
    order.save()
    return HttpResponse({"success": "true"})




