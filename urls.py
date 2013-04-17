from django.conf.urls import patterns, include, url
from .feeds import LastestPostsFeed
from .views import *

urlpatterns = patterns('kablaam.apps.ginyu.views',
    # archive views
    url(r'^archive/$', PostArchiveIndexView.as_view(),
        name='PostArchiveIndexView'),

    url(r'archive/(?P<year>\d{4})/$', PostYearArchiveView.as_view(),
        name="yearly"),

    url(r'^rss/', LastestPostsFeed()),

    # detail views
    url(r'^(?P<slug>[-_\w]+)/$', PostDetailView.as_view(),
        name='PostDetailView'),

    url(r'^tags/(?P<tag>[-\w]+)/$', 'TagListView', name='TagListView'),

    # index view
    url(r'^$', PostListView.as_view(),
        name='PostListView'),

)
