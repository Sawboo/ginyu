from django.conf.urls import patterns, url
from .feeds import LastestPostsFeed
from .views import *

urlpatterns = patterns('sawboo.ginyu.views',

    # Post detail views
    url(r'^(?P<year>\d{4})/(?P<slug>[-_\w]+)/$', PostDetailView.as_view(),
        name='PostDetailView'),

    # archive views
    url(r'^archive/$', PostArchiveIndexView.as_view(),
        name='PostArchiveIndexView'),

    url(r'(?P<year>\d{4})/$', PostYearArchiveView.as_view(),
        name="yearly"),

    # RSS feed
    url(r'^rss/', LastestPostsFeed()),

    # Tag views
    url(r'^tags/all/$', TagListAll.as_view(), name='TagListAll'),

    url(r'^tags/(?P<tag>[-\w]+)/?$', 'TagListView', name='TagListView'),

    # Page view
    url(r'^(?P<slug>[-_\w]+)/$', PageDetailView.as_view(),
        name='PageDetailView'),

    # Index view
    url(r'^(?P<page>[0-9]+)/$', PostListView.as_view(),
        name='PostListView'),

    # Index view
    url(r'^$', PostListView.as_view(),
        name='PostListView'),

)
