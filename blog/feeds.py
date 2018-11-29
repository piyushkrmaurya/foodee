from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post
from . import views

class LatestPostsFeed(Feed):
    title = "Foodee Blog"
    link = "/blog/feed"
    description = "New articles on Foodee!"

    def items(self):
        return Post.objects.all().order_by('-date_added')[:5]

    def item_title(self, item):
        return item.heading

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse(views.post, kwargs={'post_slug': item.slug})