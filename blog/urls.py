from django.urls import path, re_path, include
from . import views
from .feeds import LatestPostsFeed

urlpatterns = [
    path('', views.home, name="blog_home"),
    path('feed', LatestPostsFeed()),
    path('post/<str:post_slug>', views.post),
]
