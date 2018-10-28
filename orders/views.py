from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem
from django.db import connection
from collections import namedtuple

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dish(request, dish_name=None, dish_id=None):
    dish = None
    profile = None
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]

        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order.id))
        cart = namedtuplefetchall(cursor)

        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish`,`orders_profile_favs` WHERE `dish_id` = orders_dish.id AND `profile_id` = "+str(request.user.profile.id))
        favs = namedtuplefetchall(cursor)
    except Exception as e:
        print(e)
        order = None
        profile = None
        cart = None
        favs = None
    if dish_name:
        dish_name = ' '.join(dish_name.split('_')).capitalize()
        cursor.execute("SELECT * FROM `orders_dish` WHERE `name` = '"+dish_name+"'")
        dish = namedtuplefetchall(cursor)[0]
    elif dish_id:
        cursor.execute("SELECT * FROM `orders_dish` WHERE `id` = "+str(dish_id))
        dish = namedtuplefetchall(cursor)[0]
    return render(request, "dish.html", {'title': dish.name, 'dish': dish, 'cart':cart, 'favs':favs})

@login_required
def toggleFav(request, dish_id):
    cursor = connection.cursor()
    cursor.execute("SELECT `orders_dish`.* FROM `orders_dish`,`orders_profile_favs` WHERE `dish_id` = orders_dish.id AND `profile_id` = "+str(request.user.profile.id))
    favs = namedtuplefetchall(cursor)

    cursor.execute("SELECT * FROM `orders_dish` WHERE `id` = "+str(dish_id))
    dish = namedtuplefetchall(cursor)[0]

    if dish not in favs:
        cursor.execute("INSERT INTO `orders_profile_favs`(`dish_id`, `profile_id`) VALUES("+str(dish_id)+","+str(request.user.profile.id)+")")
        return HttpResponse({"success": "true"})
    else:
        cursor.execute("DELETE FROM `orders_profile_favs` WHERE `dish_id`="+str(dish_id)+" AND `profile_id`="+str(request.user.profile.id))
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

@login_required
def cart(request):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]

        cursor.execute("SELECT `orders_dish`.*, `orders_orderitem`.`quantity` FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order.id))
        cart = namedtuplefetchall(cursor)
    except:
        order = None
        cart = None
    return render(request, "cart.html", {'title': 'Cart', 'cart': cart, 'profile': request.user.profile})

@login_required
def addToCart(request,dish_id):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]
    except:
        cursor.execute("INSERT INTO `orders_order`(`profile_id`, `status`) VALUES("+ str(request.user.profile.id) +", 0)")
        order = namedtuplefetchall(cursor)[0]

    cursor.execute("SELECT * FROM `orders_dish` WHERE `id` = "+str(dish_id))
    dish = namedtuplefetchall(cursor)[0]

    if(dish.id not in order):
        cursor.execute("INSERT INTO `orders_orderitem`(`dish_id`, `order_id`, `quantity`) VALUES("+ str(dish.id) +", "+ str(order.id) +", 1)")
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

@login_required
def removeFromCart(request,dish_id):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]
    except:
        pass
    cursor.execute("DELETE FROM `orders_orderitem` WHERE (`dish_id` = "+ str(dish_id) +" AND `order_id` ="+ str(order.id) +")")
    return HttpResponse({"success": "true"})

@login_required
def changeQuantity(request, dish_id, quantity):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]
        if quantity>0 and quantity<=10:
            cursor.execute("UPDATE `orders_orderitem` SET `quantity`="+str(quantity)+" WHERE (`dish_id` = "+ str(dish_id) +" AND `order_id` ="+ str(order.id) +")")
            return HttpResponse({"success": "true"})
    except Exception as e:
        print(e)
    return HttpResponse({"success": "false"})

@login_required
def emptyCart(request):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
    return HttpResponse({"success": "true"})

@login_required
def orderNow(request):
    cursor = connection.cursor()
    cursor.execute("UPDATE `orders_order` SET `status`=1 WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
    return HttpResponse({"success": "true"})




