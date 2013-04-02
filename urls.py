from django.conf.urls import patterns, include, url
from django.views.generic.dates import YearArchiveView

from ginyu.models import Post
from ginyu.views import *

urlpatterns = patterns('ginyu.views',
    # archive views
    url(r'^archive/$', PostArchiveIndexView.as_view(),
        name='PostArchiveIndexView'),

    url(r'archive/(?P<year>\d{4})/$', PostYearArchiveView.as_view(),
        name="yearly"),

    # detail views
    url(r'^(?P<slug>[-_\w]+)/$', PostDetailView.as_view(),
        name='PostDetailView'),

    # index view
    url(r'^$', PostListView.as_view(),
        name='PostListView'),
)
