from django.conf.urls import patterns, include, url
from django.views.generic.dates import YearArchiveView

from .feeds import LastestPostsFeed
from .models import Post
from .views import *

urlpatterns = patterns('ginyu.views',
    # archive views
    url(r'^archive/$', PostArchiveIndexView.as_view(),
        name='PostArchiveIndexView'),

    url(r'archive/(?P<year>\d{4})/$', PostYearArchiveView.as_view(),
        name="yearly"),

    url(r'^rss/', LastestPostsFeed()),

    # detail views
    url(r'^(?P<slug>[-_\w]+)/$', PostDetailView.as_view(),
        name='PostDetailView'),

    # index view
    url(r'^$', PostListView.as_view(),
        name='PostListView'),

)
