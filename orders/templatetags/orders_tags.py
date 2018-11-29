from django import template
from orders.models import Dish

register = template.Library()

@register.simple_tag()
def multiply(price, quantity, *args, **kwargs):
    return price*quantity

@register.simple_tag()
def total(cart, *args, **kwargs):
    value = 0
    for item in cart:
        value = value + item.price*item.quantity
    if value>=1000:
        return min(100, value*0.9)
    return value

@register.simple_tag()
def total_for_premium(cart, *args, **kwargs):
    value = 0
    for item in cart:
        value = value + item.price*item.quantity
    return max(value-200, value*0.9)

@register.simple_tag()
def showStatus(status, *args, **kwargs):
    if status==1:
        return "Order placed"
    elif status==2:
        return "Order dispatched"
    elif status==3:
        return "Order delivered"

@register.simple_tag()
def get_veg_non_veg(dish, *args, **kwargs):
    if Dish.objects.get(pk=dish.id).tags.filter(name='vegetarian'):
        return 'veg'
    elif Dish.objects.get(pk=dish.id).tags.filter(name='non vegetarian'):
        return 'non-veg'
