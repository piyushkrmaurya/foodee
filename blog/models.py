from django.contrib.auth.models import User
from django.db import migrations, models
from orders.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

class Post(models.Model):
    min_read = models.IntegerField()
    date_added = models.DateField(auto_now_add=True)
    quoted_text= models.CharField(max_length = 100)
    heading = models.CharField(max_length = 100)
    content = models.CharField(max_length = 2000)
    tags = models.ManyToManyField(Tag) 
    chef_name = models.CharField(max_length = 30)
    chef_details = models.CharField(max_length = 250)
    image = models.ImageField(upload_to='static/post/images/',max_length = 500, null=True, blank=True)
    slug = models.SlugField(unique = True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.heading)
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.heading

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name = 'comments', on_delete = models.CASCADE)
    user = models.ForeignKey(User, related_name = 'comments', on_delete = models.CASCADE)
    subject = models.CharField(max_length = 200)
    message = models.CharField(max_length = 500)
    date_added = models.DateField(auto_now_add=True)
