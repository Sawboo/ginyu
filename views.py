from django.views.generic import ListView, DetailView, ArchiveIndexView
from .models import Post

# Goodbye function based views, hello class based views.
# For more information on the magic going on here see the docs:
#
# https//docs.djangoproject.com/en/1.5/ref/class-based-views/


class PostListView(ListView):
    """A view that returns a list of posts objects."""

    model = Post
    queryset = Post.objects.active()
    template_name = "post_list.html"


class PostDetailView(DetailView):
    """A view that returns the details of a single post."""
    model = Post
    template_name = "post_detail.html"


class PostArchiveIndexView(ArchiveIndexView):

    model = Post
    date_field = "publish_date"
    template_name = "post_archive.html"
