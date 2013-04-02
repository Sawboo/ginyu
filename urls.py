from django.conf.urls import patterns, include, url

from ginyu.views import PostListView, PostDetailView, PostArchiveIndexView

urlpatterns = patterns('ginyu.views',
    url(r'^$', PostListView.as_view(), name='PostListView'),
    url(r'^archive/$', PostArchiveIndexView.as_view(), name='PostArchiveIndexView'),
    url(r'^(?P<slug>[-_\w]+)/$', PostDetailView.as_view(), name='PostDetailView'),
)