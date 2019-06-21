'''payments urls'''
from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^do_cc/(\w+)/$', 'payments.views.do_cc',  name='do_cc'),
	#url(r'^do_cc/(\w+)/$', 'payments.views.do_cc_madra',  name='do_cc'),
           )
