from django.conf.urls import patterns, include, url

from ginyu.views import post_list

urlpatterns = patterns("",
    url(r'^$', "ginyu.views.post_list", name="post_list"),
)