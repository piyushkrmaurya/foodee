from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from orders.forms import SignUpForm, UpdateProfileForm
from datetime import datetime, time, date
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem
from django.db import connection
from collections import namedtuple

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    nt_result = namedtuple('Result', [col[0] for col in cursor.description])
    return [nt_result(*row) for row in cursor.fetchall()]

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def home(request):
    cursor = connection.cursor()
    try:
        if request.user.profile:
            cursor.execute("SELECT `orders_dish`.* FROM `orders_dish`,`orders_profile_favs` WHERE `dish_id` = orders_dish.id AND `profile_id` = "+str(request.user.profile.id))
            favs = namedtuplefetchall(cursor)

            cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
            order = namedtuplefetchall(cursor)[0]

            cursor.execute("SELECT `orders_dish`.* FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order.id))
            cart = namedtuplefetchall(cursor)

        else:
            order = None
            cart = None
            favs = None
    except:
        order = None
        cart = None
        favs = None
    cursor.execute("SELECT * FROM `orders_dish`")
    dishes = namedtuplefetchall(cursor)
    return render(request, "home.html", {'title': "Home", 'cart': cart, 'dishes': dishes, 'favs': favs})
    
def search(request):
    profile = None
    if not request.user.is_anonymous:
        profile = request.user.profile

    try:
        if profile:
            order = Order.objects.filter(profile = request.user.profile).get(status = 0)
            cart = order.items.all()
        else:
            order = None
            cart = None
    except Order.DoesNotExist:
        order = None
        cart = None

    keyword = request.GET.get('keyword')
    result = Dish.objects.filter(name__icontains=keyword)
    return render(request, "search.html", {'title': keyword, 'profile': profile, 'cart': cart, 'result':result})

@login_required
def profile(request):
    title = (request.user.first_name+" "+request.user.last_name)
    cursor = connection.cursor()
    if request.user.profile:
        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish`,`orders_profile_favs` WHERE `dish_id` = orders_dish.id AND `profile_id` = "+str(request.user.profile.id))
        favs = namedtuplefetchall(cursor)
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
        order = namedtuplefetchall(cursor)[0]

        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order.id))
        cart = namedtuplefetchall(cursor)
    except:
        order = None
        cart = None
    if not title or title==" ":
        title = request.user.username
    return render(request, "profile.html", {'title': title, 'cart': cart, 'favs': favs})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.phone = form.cleaned_data.get('phone')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form, 'title': 'Signup'})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.profile.phone = form.cleaned_data.get('phone')
            user.email = form.cleaned_data.get('email')
            user.profile.address = form.cleaned_data.get('address')
            user.profile.avatar = form.clean_avatar()
            user.save()
            return redirect('/')
    else:
        form = UpdateProfileForm()
    return render(request, 'registration/profile.html', {'form': form})     

@login_required
def myOrders(request):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * from `orders_order` WHERE `profile_id` = "+ str(request.user.profile.id) +" AND `status`>0")
        orders = namedtuplefetchall(cursor)
        order_items = []

        for order in orders:
            cursor.execute("SELECT `orders_dish`.*, `orders_orderitem`.quantity  FROM `orders_dish`, `orders_orderitem`  WHERE `dish_id`=`orders_dish`.id AND `order_id` = "+str(order.id))
            order_item = namedtuplefetchall(cursor)
            order_items.append(order_item)

        orders = list(zip(orders, order_items))

    except Exception as e:
        print(e)
        orders = None

    return render(request, "my_orders.html", {'title': "My Orders", 'orders': orders})
