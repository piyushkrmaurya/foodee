from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from orders.forms import SignUpForm, UpdateProfileForm
from datetime import datetime, time, date
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem

def home(request):
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
    dishes = Dish.objects.all()
    return render(request, "home.html", {'title':"Home", 'profile':profile, 'cart':cart, 'dishes':dishes})
    
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
    user = request.user
    profile = user.profile
    title = (user.first_name+" "+user.last_name)
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
    if not title or title==" ":
        title = user.username
    return render(request, "profile.html", {'title':title, 'cart': cart, 'profile':profile})

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
    profile = request.user.profile
    try:
        orders = Order.objects.filter(profile = request.user.profile).filter(status__gt = 0).all()
        order_items = [OrderItem.objects.filter(order = order) for order in orders]
        orders = zip(order_items, orders)
    except Order.DoesNotExist:
        orders = None
    return render(request, "my_orders.html", {'title':"My Orders", 'orders': orders, 'profile':profile})
