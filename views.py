from django.shortcuts import render
from .models import Tag, Post


def post_list(request, *args, **kwargs):
    """returns a list of blog posts using our custom manager"""
    post_list = Post.objects.active()
    t = "post_list.html"

    context = {
        "posts": post_list,
    }

    return render(request, t, context)
