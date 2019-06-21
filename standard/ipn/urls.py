from django.conf.urls  import *
from ipn import views

urlpatterns = patterns('paypal.standard.ipn.views',            
    url(r'^$', views.ipn, name="paypal-ipn"),
)