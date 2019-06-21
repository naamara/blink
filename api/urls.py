'''classified views'''

from django.conf.urls import patterns, url, include
from rest_framework import routers, serializers
#from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
router = routers.DefaultRouter()
import api.views as views


urlpatterns = patterns('',


                       # user login
                       url(r'^accounts/login/$', views.LoginUser.as_view()),



                       # payments
                       url(r'^payments/checknumber/(?P<msisdn>[0-9\w]+)/$',
                           views.CheckNumber.as_view()),

                       url(r'^payments/serverstatus/$',
                           views.UserProfile.as_view()),

                       url(r'^payments/transactionid/$',
                           views.GetTransactionId.as_view()),

                       url(r'^payments/savetransaction/$',
                           views.SaveTransaction.as_view()),

                       url(r'^payments/bills/querybill/$',
                           views.QueryBill.as_view()),

                       url(r'^payments/bills/paybill/$',
                           views.PayBill.as_view()),

                       url(r'^payments/bills/status/$',
                           views.BillStatus.as_view()),

                       url(r'^payments/transactionstatus/(?P<transactionid>[0-9\w]+)/$',
                           views.UserProfile.as_view()),

                       url(r'^sendmoney/(?P<transactionid>[0-9\w]+)/$',
                           views.DepositMoney.as_view()),

                       url(r'^user/profile/$',
                           views.UserProfile.as_view()),

                       url(r'^user/transactions/$',
                           views.UserTransactions.as_view()),

                       url(r'^user/transactions/pending/$',
                           views.PendingTransactions.as_view()),

                       url(r'^user/transactions/complete/$',
                           views.CompleteTransactions.as_view()),

                       url(r'^user/transaction/(?P<hashid>.+)/$',
                           views.UserTransaction.as_view()),

                       url(r'^user/phonebook/$',
                           views.UserPhonebook.as_view()),

                       url(r'^rates/$',
                           views.Rates.as_view(),),

                       url(r'^rates/(?P<hashid>.+)/$',
                           views.CountryRates.as_view(),),

                       url(r'^do_cc$', views.UserDoCC.as_view()),

                       )
