from django.contrib.auth.models import User
from django.db import migrations, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    pic = models.ImageField(upload_to='static/dish/images/', default='static/dish/images/dish.jpg',max_length = 500, blank=True)
    tags = models.ManyToManyField(Tag)
    price = models.IntegerField()
    description = models.CharField(max_length=500)
    type = models.BooleanField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/profile/images/', default='static/profile/images/user.png',max_length = 500,  blank=True)
    favs = models.ManyToManyField(Dish, blank=True)
    phone = models.CharField(max_length=10, blank=False)
    address = models.TextField(max_length=500, blank=True)


class Order(models.Model):
    PAYMENT_MODES = (
        ('C', 'Cash'),
        ('D', 'Card'),
        ('O', 'Online Banking'),
    )
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    items = models.ManyToManyField(Dish, through='OrderItem')
    order_time = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=1, choices=PAYMENT_MODES, default='C', blank=True)
    status = models.IntegerField(default=0, blank=False)


class OrderItem(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, blank=False)


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True)
    post_date = models.DateField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
