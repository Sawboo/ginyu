from django.conf.urls import patterns, url
from .feeds import LastestPostsFeed
from .views import *

urlpatterns = patterns('sawboo.ginyu.views',
    # archive views
    url(r'^archive/$', PostArchiveIndexView.as_view(),
        name='PostArchiveIndexView'),

    url(r'(?P<year>\d{4})/$', PostYearArchiveView.as_view(),
        name="yearly"),

    url(r'^rss/', LastestPostsFeed()),

    url(r'^tags/all/$', TagListAll.as_view(), name='TagListAll'),

    url(r'^tags/(?P<tag>[-\w]+)/?$', 'TagListView', name='TagListView'),

    # detail views
    url(r'^(?P<year>\d{4})/(?P<slug>[-_\w]+)/$', PostDetailView.as_view(),
        name='PostDetailView'),

    # index view
    url(r'^$', PostListView.as_view(),
        name='PostListView'),

)
