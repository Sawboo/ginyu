from django.views.generic import ListView, DetailView, ArchiveIndexView
from django.views.generic.dates import YearArchiveView
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Count
from .models import Post, Tag

# Goodbye function based views, hello class based views.
# For more information on the magic going on here see the docs:
#
# https//docs.djangoproject.com/en/1.5/ref/class-based-views/


class PostListView(ListView):
    """A view that returns a list of posts objects."""
    model = Post
    queryset = Post.objects.active()
    template_name = "post_list.html"
    paginate_by = 10


def TagListView(request, tag):
    """A view that returns a list of posts objects with a given tag."""
    t = get_object_or_404(Tag, name=tag)
    posts = Post.objects.active().filter(tags__name=tag)
    return render_to_response(
        'tag_list.html', {
            'object_list': posts,
            'tag_name': t.name,
            'num_posts': len(posts), }, context_instance=RequestContext(request))


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
    paginate_by = 20


class PostYearArchiveView(YearArchiveView):
    """returns a list of post objects published in a given year"""
    model = Post
    queryset = Post.objects.active()
    template_name = 'post_archive_yearly.html'
    date_field = 'publish_date'
    make_object_list = True
    paginate_by = 20
