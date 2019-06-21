'''admin configurations'''
from django.contrib import admin
import remit_admin.views as remit_admin
from django.conf.urls import *
from django.contrib.auth.models import User
import remit.settings as settings
from django.contrib.auth.models import Group
# remove defaults
admin.site.unregister(User)
admin.site.unregister(Group)


'''
register admin urls
'''


def get_admin_urls(urls):
    def get_urls():
        my_urls = patterns('',
                           url(r'^audits/$', admin.site.admin_view(
                               remit_admin.audits_trails), name="audits_trails"),
                           url(r'^export_data/$', admin.site.admin_view(
                               remit_admin.export_data), name="export_data"),
                           url(r'^users/admin/add/$', admin.site.admin_view(
                               remit_admin.create_stuff_user), name="create_admin_user"),

                           url(r'^add_health_info/$', admin.site.admin_view(
                               remit_admin.add_health_info), name="add_health_info"),
                           url(r'^add_law_info/$', admin.site.admin_view(
                               remit_admin.add_law_info), name="add_law_info"),
                           url(r'^add_pub_info/$', admin.site.admin_view(
                               remit_admin.add_pub_info), name="add_pub_info"),

                           url(r'^add_educ_info/$', admin.site.admin_view(
                               remit_admin.add_educ_info), name="add_educ_info"),



                           url(r'^users/admin/add/cc/$', admin.site.admin_view(
                               remit_admin.create_customer_care_user), name="create_customer_care_user"),

                           url(r'^users/admin/$', admin.site.admin_view(
                               remit_admin.stuff_users), name="view_admin_user"),

                           url(r'^users/health/$', admin.site.admin_view(
                               remit_admin.health_users), name="view_health_user"),


                         



                           url(r'^customer_care/transactions/search/$', admin.site.admin_view(
                               remit_admin.phonenumber_transaction_search), name="cc_transaction_search"),


                           url(r'^users/admin/edit/(\w+)/$', admin.site.admin_view(
                               remit_admin.edit_stuff_user), name="edit_admin_user"),

                           url(r'^reports/$', admin.site.admin_view(
                               remit_admin.reports), name="admin_reports"),
                           url(r'^users/blockuser/$', admin.site.admin_view(
                               remit_admin.block_user), name="admin_block_user"),
                           url(r'^users/unblockuser/$', admin.site.admin_view(
                               remit_admin.unblock_user), name="admin_unblock_user"),
                           url(r'^users/verifyuser/$', admin.site.admin_view(
                               remit_admin.verify_user), name="admin_verify_user"),
                           url(r'^users/unverifyuser/$', admin.site.admin_view(
                               remit_admin.unverify_user), name="admin_unverify_user"),
                           url(r'^users/(\w+)/$', admin.site.admin_view(
                               remit_admin.users), name="admin_users"),
                           url(r'^user/(\w+)/contact/$', admin.site.admin_view(
                               remit_admin.contact_user), name="contact_user"),
                           url(r'^transactions/resend/$', admin.site.admin_view(
                               remit_admin.resend_transaction), name="admin_resend_transaction"),
                           url(r'^transactions/process/$', admin.site.admin_view(
                               remit_admin.process_transaction), name="admin_process_transaction"),
                           url(r'^transactions/(\w+)/$', admin.site.admin_view(
                               remit_admin.transactions), name="admin_transactions"),
                           url(r'^transactions/(\w+)/(\w+)/$', admin.site.admin_view(
                               remit_admin.transactions), name="admin_user_transactions"),
   
                           #
                           url(r'^billtransactions/(\w+)/$', admin.site.admin_view(
                            remit_admin.bill_transactions), name="bill_transactions"),
                            url(r'^billtransactions/(\w+)/(\w+)/$', admin.site.admin_view(
                            remit_admin.transactions), name="admin_user_transactions"),





                           url(r'^transaction/(\w+)/receipt/$', admin.site.admin_view(
                               remit_admin.transaction_receipt), name="transaction_receipt"),


                           url(r'^tradelance/$', admin.site.admin_view(
                                remit_admin.tradelance), name="tradelance"),

                           url(r'^tradelance/response/$', admin.site.admin_view(
                                remit_admin.tradelance_response), name="tradelance_response"),


                           url(r'^transaction/(\w+)/resend_transaction_email/$', admin.site.admin_view(
                               remit_admin.resend_transaction_email), name="resend_transaction_email"),

                           url(r'^transaction/(\w+)/edit/$', admin.site.admin_view(
                               remit_admin.edit_transaction), name="edit_transaction"),
                           url(r'^transaction/(\w+)/$', admin.site.admin_view(
                               remit_admin.view_transaction), name="admin_transaction"),
                           url(r'^user/(\w+)/$', admin.site.admin_view(
                               remit_admin.user), name="admin_user"),
                           url(r'^rates/(?P<code>.+)/$', admin.site.admin_view(
                               remit_admin.rates), name="admin_rates"),
                           url(r'^charges_limits/(?P<code>.+)/$', admin.site.admin_view(
                               remit_admin.charges_limits), name="admin_charges_limits"),
                           url(r'^logs/$', admin.site.admin_view(
                               remit_admin.logs), name="admin_logs"),
                           url(r'^seo/$', 'seo.views.seo', name="admin_seo"),
                           url(r'^logout/$', 'django.contrib.auth.views.logout',
                               {'next_page': settings.BASE_URL}, name="admin_logout"),
                           url(r'^$', admin.site.admin_view(
                               remit_admin.home), name="admin_dashboard"),
                           # url(r'^users/$', admin.site.admin_view(remit_admin.users),name="admin_verified_users"),

                           )
        return my_urls + urls
    return get_urls

admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
