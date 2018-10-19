from django import template

register = template.Library()

@register.simple_tag()
def multiply(price, quantity, *args, **kwargs):
    return price*quantity

@register.simple_tag()
def total(cart, *args, **kwargs):
    value = 0
    for item in cart:
        value = value + item.dish.price*item.quantity
    return value

@register.simple_tag()
def showStatus(status, *args, **kwargs):
    if status==1:
        return "Order placed"
    elif status==2:
        return "Order dispatched"
    elif status==3:
        return "Order delivered"

