from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.db import connection

from django.contrib.auth.decorators import login_required
from orders.forms import SignUpForm, UpdateProfileForm
from datetime import datetime, time, date
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem,Tag
from blog.models import Post
from collections import namedtuple

#fetch objects relating to sql query
def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    nt_result = namedtuple('Result', [col[0] for col in cursor.description])
    return [nt_result(*row) for row in cursor.fetchall()]

#fetch dictionary relating to sql query
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

#page to run sql queries
def sql(request):
    cursor = connection.cursor()
    if request.method=="POST":
        sql = request.POST.get('sql')
        if request.user.is_staff:
            try:
                cursor.execute(sql)
                data = namedtuplefetchall(cursor)
            except:
                data = "There's an error in your query!"
        else:
            data = ";-)"
        return render(request, "sql.html", {'title': "SQL", 'data': data})
    return render(request, "sql.html", {'title': "SQL"})

#the home page
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
    posts = Post.objects.all().order_by('-date_added')
    top_post = posts[0]
    other_posts = posts[1:5]
    tags = Tag.objects.all()
    return render(request, "home.html", {'title': "Home", 'cart': cart, 'dishes': dishes, 'favs': favs, 'top_post':top_post, 'other_posts':other_posts, 'tags':tags})

#profile page for the user
@login_required
def profile(request):
    try:
        if Order.objects.filter(profile = profile, status = 1).count() > 9:
            request.user.profile.premium = True
            request.user.profile.save()
    except:
        pass
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

#signup page
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

#update profile page for user
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

#history of orders
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
