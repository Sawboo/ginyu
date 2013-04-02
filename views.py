from django.views.generic import ListView, DetailView, ArchiveIndexView
from django.views.generic.dates import YearArchiveView
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
    paginate_by = 3


class PostDetailView(DetailView):
    """A view that returns the details of a single post."""
    model = Post
    template_name = "post_detail.html"


class PostArchiveIndexView(ArchiveIndexView):
    """returns a simple list of all post objects"""
    model = Post
    queryset = Post.objects.active()
    date_field = "publish_date"
    template_name = "post_archive.html"
    paginate_by = 3


class PostYearArchiveView(YearArchiveView):
    """returns a list of post objects published in a given year"""
    model = Post
    queryset = Post.objects.active()
    template_name = 'post_archive_yearly.html'
    date_field = 'publish_date'
    make_object_list = True
    paginate_by = 3
