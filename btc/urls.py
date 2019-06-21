from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('', url(r'^$', 'btc.views.home',
                               name='home'),
 url(r'^send/', 'btc.views.send_bitcoin',
                               name='send_bitcoin'),)
