from django.contrib.syndication.views import Feed
from .models import Post


class LastestPostsFeed(Feed):
    """
    Creates an RSS feed from recent Post objects.
    Be sure to update the title, link, and description
    fields as needed.

    """
    title = 'Ginyu RSS'
    link = 'http://example.com/'
    description = 'Ginyu is a technical blogging platform developed with Django.'

    def items(self):
        # Slice the queryset to show the 10 newest posts.
        return Post.objects.active().order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.rendered_excerpt

    def item_link(self, item):
        return item.get_absolute_url()