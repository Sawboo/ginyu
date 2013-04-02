from django.conf.urls import patterns, include, url

from ginyu.views import post_list

urlpatterns = patterns('ginyu.views',
    url(r'^$', 'post_list', name='post_list'),
    url(r'^(?P<slug>[-\w]+)/$', 'post_detail', name='post_detail'),
)