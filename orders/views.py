from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem, Review
from django.db import connection
from collections import namedtuple
from django.db.models import Q

cursor = connection.cursor()

#fetch objects relating to sql query
def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

#fetch dictionary relating to sql query
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

#fetch order with status 0
def get_order(profile_id):
    try:
        cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(profile_id) +" AND `status` = 0)")
        orders = namedtuplefetchall(cursor)
        print(orders)
        if not orders:
            cursor.execute("INSERT INTO `orders_order`(`profile_id`) VALUES('"+str(profile_id)+"')")
            cursor.execute("SELECT `id` FROM `orders_order` WHERE (`profile_id` = "+ str(profile_id) +" AND `status` = 0)")
            orders = namedtuplefetchall(cursor)
        return orders[0]
    except Exception as e:
        print(e)
        return None

#fetch cart
def get_cart(order_id):
    try:
        cursor.execute("SELECT `orders_dish`.*, `orders_orderitem`.`quantity`  FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order_id))
        return namedtuplefetchall(cursor)
    except:
        return None


#fetch all the dishes in cart
def get_cart_dishes(order_id):
    try:
        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish` INNER JOIN `orders_orderitem` ON (`orders_dish`.`id` = `orders_orderitem`.`dish_id`) WHERE `orders_orderitem`.`order_id` = "+str(order_id))
        return namedtuplefetchall(cursor)
    except:
        return None

#fetch favourite dishes of user
def get_favs(profile_id):
    try:
        cursor.execute("SELECT `orders_dish`.* FROM `orders_dish`,`orders_profile_favs` WHERE `dish_id` = orders_dish.id AND `profile_id` = "+str(profile_id))
        return namedtuplefetchall(cursor)
    except:
        return None

#fetch a particular dish
def get_dish(dish_name=None, dish_id=None):
    try:
        if dish_name:
            dish_name = ' '.join(dish_name.split('_')).capitalize()
            cursor.execute("SELECT * FROM `orders_dish` WHERE `name` = '"+dish_name+"'")
            return namedtuplefetchall(cursor)[0]
        elif dish_id:
            cursor.execute("SELECT * FROM `orders_dish` WHERE `id` = "+str(dish_id))
            return namedtuplefetchall(cursor)[0]
    except:
        return None

#get user rating for a particular dish
def get_rating(request, dish_id):
    try:
        review = Review.objects.get(profile=request.user.profile, dish__id=dish_id)
        bright = review.stars*"x"
        dark = (5-review.stars)*"x"
    except Exception as e:
        print(e)
        bright = ""
        dark = 5*"x"
    try:
        reviews = Review.objects.filter(dish__id=dish_id)
        stars = sum([x.stars for x in reviews])/reviews.count()
    except Exception as e:
        print(e)
        stars = 0
    return (stars, bright, dark)

#search for  dishes
def search(request):
    profile = None
    order = None
    cart = None
    if not request.user.is_anonymous:
        profile = request.user.profile
        order = get_order(request.user.profile.id)
        cart = get_cart_dishes(order.id)

    keyword = request.GET.get('keyword')
    if keyword in ["vegetarian", "veg"]:
        result = Dish.objects.filter(tags__name="vegetarian")
    elif keyword in ["non vegetarian", "non veg", "non-vegetarian", "non-veg", "nonveg"]:
        result = Dish.objects.filter(tags__name="non vegetarian")
    else:
        result = Dish.objects.filter(Q(name__icontains = keyword) | Q(description__icontains = keyword) | Q(tags__name__icontains = keyword)).distinct()

    return render(request, "search.html", {'title': keyword, 'profile': profile, 'cart': cart, 'result':result})

#render dish page
def dish(request, dish_name=None, dish_id=None):
    if not request.user.is_anonymous:
        order = get_order(request.user.profile.id)
        cart = get_cart_dishes(order.id)
        favs = get_favs(request.user.profile.id)
    else:
        order = None
        cart = None
        favs = None
    try:
        dish = get_dish(dish_name, dish_id)
    except:
        dish = None

    stars,bright,dark = get_rating(request,dish.id)

    return render(request, "dish.html", {'title': dish.name, 'dish': dish, 'cart':cart, 'favs':favs, 'stars':stars, 'bright':bright, 'dark':dark})

#view for changing user rating using AJAX call
@login_required
def changeStars(request, dish_id):
	if request.method=="GET":
		stars = int(request.GET.get('stars'))
		try:
			review = Review.objects.filter(profile=request.user.profile, dish__id=dish_id)[0]
		except:
			review = Review.objects.create(profile=request.user.profile, dish=Dish.objects.get(id=dish_id))

		review.stars = min(5, stars)
		review.stars = max(0, review.stars) 
		review.save()

		return HttpResponse('true')

#add or remove a dish from user favorites
@login_required
def toggleFav(request, dish_id):

    favs = get_favs(request.user.profile.id)

    dish = get_dish(dish_id = dish_id)

    if dish not in favs:
        cursor.execute("INSERT INTO `orders_profile_favs`(`dish_id`, `profile_id`) VALUES("+str(dish_id)+","+str(request.user.profile.id)+")")
        return HttpResponse({"success": "true"})
    else:
        cursor.execute("DELETE FROM `orders_profile_favs` WHERE `dish_id`="+str(dish_id)+" AND `profile_id`="+str(request.user.profile.id))
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

#render cart page
@login_required
def cart(request):
    if Order.objects.filter(profile = request.user.profile, status = 1).count() > 9:
        request.user.profile.premium = True
        request.user.profile.save()
    order = get_order(request.user.profile.id)
    cart = get_cart(order.id)
    return render(request, "cart.html", {'title': 'Cart', 'cart': cart, 'profile': request.user.profile})

#add a dish to cart
@login_required
def addToCart(request, dish_id):

    order = get_order(request.user.profile.id)

    dish = get_dish(dish_id = dish_id)

    if(dish.id not in order):
        cursor.execute("INSERT INTO `orders_orderitem`(`dish_id`, `order_id`, `quantity`) VALUES("+ str(dish.id) +", "+ str(order.id) +", 1)")
        return HttpResponse({"success": "true"})
    return HttpResponse({"success": "false"})

#remove a dish from cart
@login_required
def removeFromCart(request,dish_id):
    order = get_order(request.user.profile.id)
    cursor.execute("DELETE FROM `orders_orderitem` WHERE (`dish_id` = "+ str(dish_id) +" AND `order_id` ="+ str(order.id) +")")
    return HttpResponse({"success": "true"})

#change quantity of a dish item in cart
@login_required
def changeQuantity(request, dish_id, quantity):
    try:
        order = get_order(request.user.profile.id)
        if quantity>0 and quantity<=10:
            cursor.execute("UPDATE `orders_orderitem` SET `quantity`="+str(quantity)+" WHERE (`dish_id` = "+ str(dish_id) +" AND `order_id` ="+ str(order.id) +")")
            return HttpResponse({"success": "true"})
    except Exception as e:
        print(e)
    return HttpResponse({"success": "false"})

#empty the cart
@login_required
def emptyCart(request):
    cursor.execute("DELETE FROM `orders_order` WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
    return HttpResponse({"success": "true"})

#finalize the order 
@login_required
def orderNow(request):
    cursor.execute("UPDATE `orders_order` SET `status`=1 WHERE (`profile_id` = "+ str(request.user.profile.id) +" AND `status` = 0)")
    return HttpResponse({"success": "true"})




