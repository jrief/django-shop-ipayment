from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('',
    (r'^shop/', include('shop.urls')),
)
