from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from orders.models import Profile,Dish,Order,OrderItem
from blog.models import Post,Comment
from django.db import connection
from collections import namedtuple
from django.shortcuts import render, redirect
from orders.models import Tag

def home(request):
    try:
        posts = Post.objects.all()
    except:
        posts = none
    return render(request, 'blog.html', {'title':'Blog','posts': posts})


def post(request, post_slug):
    posts = Post.objects.all().order_by('-date_added')
    top_post = posts[0]
    other_posts = posts[1:5]
    tags = Tag.objects.all()
    try:
        post = Post.objects.get(slug = post_slug)
    except:
        post = none
    if request.method == 'POST':
        subject = request.POST.get('subject', None)
        message = request.POST.get('message', None)
        if subject and  message and post:
            Comment.objects.create(post = post, subject = subject, message = message, user = request.user)
    return render(request, 'post.html', {'post': post, 'title': post.heading, 'top_post':top_post, 'other_posts':other_posts, 'tags':tags})
