from django.contrib.auth.models import User
from django.db import migrations, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='static/tags/images/', default='static/tags/images/dish.jpg',max_length = 500, blank=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    pic = models.ImageField(upload_to='static/dish/images/', default='static/dish/images/dish.jpg',max_length = 500, blank=True)
    tags = models.ManyToManyField(Tag)
    price = models.IntegerField()
    description = models.CharField(max_length=500)
    type = models.BooleanField()

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/profile/images/', default='static/profile/images/user.png',max_length = 500,  blank=True)
    favs = models.ManyToManyField(Dish, blank=True)
    phone = models.CharField(max_length=10, blank=False)
    address = models.TextField(max_length=500, blank=True)
    premium = models.BooleanField(default=False)

    def __str__(self):
        name = self.user.first_name+' '+self.user.last_name
        if name and not name=='':
            return name
        return self.user.username


class Order(models.Model):
    PAYMENT_MODES = (
        ('C', 'Cash'),
        ('D', 'Card'),
        ('O', 'Online Banking'),
    )
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    items = models.ManyToManyField(Dish, through='OrderItem')
    order_time = models.DateField(auto_now_add=True, null=True)
    payment_mode = models.CharField(max_length=1, choices=PAYMENT_MODES, default='C', blank=True, null=True)
    status = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return str(self.profile)+' Order '+str(self.id)


class OrderItem(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, blank=False)

    def __str__(self):
        return str(self.dish)


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    description = models.CharField(max_length=500, blank=True)
    post_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.profile)+' Review '+str(self.id)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
