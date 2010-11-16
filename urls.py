from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^post/', 'djangoobjfeed.views.post_comment'),
)
