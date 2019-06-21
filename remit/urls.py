'''remit urls'''
from django.conf.urls import patterns, include, url
#import landingapp as landingapp
#import accounts as accounts
from django.conf import settings
from django.views.generic import TemplateView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.contrib.auth.views import password_reset
from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME

urlpatterns = patterns('',

                       # Examples:
                       url(r'^$', 'landingapp.views.landing_page', name='index'),


                       url(r'^uganda$', 'landingapp.views.landing_page',
                           {'country': 'UG'}, name='landing_uganda'),


                       url(r'^kenya$', 'landingapp.views.landing_page',
                           {'country': 'KE'}, name='landing_kenya'),
                       url(r'^rwanda$', 'landingapp.views.landing_page',
                           {'country': 'RW'}, name='landing_rwanda'),

                       url(r'^home$', 'remit.views.home_page', name='home'),
                       url(r'^home/kenya$', 'remit.views.home_page',
                           {'country': 'KE'}, name='send_lohgkenya'),
                       url(r'^home/uganda$', 'remit.views.home_page',
                           {'country': 'UG'}, name='send_uganda'),
                       url(r'^home/rwanda$', 'remit.views.home_page',
                           {'country': 'RW'}, name='send_rwanda'),

                       url(r'^paybill$', 'remit.views.paybill', name='paybill'),
                       url(r'^wallet$', 'remit.views.wallet', name='wallet'),

                       #url(r'^bitcoin/', include('btc.urls')),
                       #url(r'^api/', include('api.urls')),

                       #url(r'^bitcoin/', include('btc.urls')),
                      # url(r'^api/', include('api.urls')),

                       url(r'^faq$', 'landingapp.views.faq', name='faq'),
                       url(r'^tos$', 'landingapp.views.tos', name='tos'),
                       url(r'^policy$', 'landingapp.views.policy', name='policy'),
                       url(r'^rate$', 'landingapp.views.rate', name='rate'),

                       #url(r'^bitcoin$', 'remit.views.bitcoin', name='bitcoin'),


                       url(r'^contact_us$',
                           'landingapp.views.contact_us', name='contact_us'),
                       url(r'^about_us$', 'landingapp.views.about_us',
                           name='about_us'),
                       url(r'^history$', 'landingapp.views.history',
                           name='history'),
                       url(r'^clinics$', 'landingapp.views.clinics',
                           name='clinics'),

                       url(r'^hospitals$', 'landingapp.views.hospitals',
                           name='hospitals'),


                       url(r'^doctors$', 'landingapp.views.doctors',
                           name='doctors'),

                         url(r'^doctors$', 'landingapp.views.doctors',
                           name='doctors'),


                       url(r'^dentist$', 'landingapp.views.dentist',
                           name='dentist'),
                      
                        url(r'^surgeon$', 'landingapp.views.surgeon',
                           name='surgeon'),
                        
                         url(r'^ gendoctor$', 'landingapp.views.gen_doctor',
                           name='gendoctor'),

                       

                       url(r'^careers$', 'landingapp.views.careers',
                           name='careers'), 
                       url(r'^members$', 'landingapp.views.members',
                           name='members'), 
                       url(r'^publications$', 'landingapp.views.publications',
                           name='publications'), 
                       url(r'^statistics$', 'landingapp.views.statistics',
                           name='statistics'),
                       url(r'^legislation$', 'landingapp.views.legislation',
                           name='legislation'),
                       url(r'^funding$', 'landingapp.views.funding',
                           name='funding'),
                       url(r'^e-consult$', 'landingapp.views.econsult',
                           name='e-consult'),
                       
                       url(r'^districts$', 'landingapp.views.districts',
                           name='districts'),
                       url(r'^forums$', 'landingapp.views.forums',
                           name='forums'),
                       url(r'^support$', 'landingapp.views.support',
                           name='support'),
                       url(r'^education$', 'landingapp.views.education',
                           name='education'),
                       url(r'^health$', 'landingapp.views.health',
                           name='health'),
                       url(r'^livelihood$', 'landingapp.views.livelihood',
                           name='livelihood'),
                       url(r'^disaster$', 'landingapp.views.disaster',
                           name='disaster'),
                       url(r'^civics$', 'landingapp.views.civics',
                           name='civics'),
                       url(r'^healthcare$', 'landingapp.views.healthcare',
                           name='healthcare'),
                       url(r'^join$', 'landingapp.views.signup2',
                           name='join'),
                       url(r'^support$', 'landingapp.views.support',
                           name='support'),
                       url(r'^donate$', 'landingapp.views.donate',
                           name='donate'),
                       url(r'^policiesandissues$', 'landingapp.views.policiesandissues',
                           name='policiesandissues'),
                       url(r'^diseasesandconditions$', 'landingapp.views.diseasesandconditions',
                           name='diseasesandconditions'),
                       url(r'^costfinancing$', 'landingapp.views.costfinancing',
                           name='costfinancing'),
                       url(r'^medicaldirectory$', 'landingapp.views.medicaldirectory',
                           name='medicaldirectory'),

                       url(r'^clinic_name$', 'landingapp.views.clinic_name',
                           name='clinic_name'),

                       url(r'^clinic_spec$', 'landingapp.views.clinic_spec',
                           name='clinic_spec'),

                          url(r'^nurse_spec$', 'landingapp.views.nurse_spec',
                           name='nurse_spec'),

                       url(r'^labs_spec$', 'landingapp.views.labs_spec',
                           name='labs_spec'),

                       url(r'^hospitals_spec$', 'landingapp.views.hospitals_spec',
                           name='hospitals_spec'),

                       url(r'^clinic_search$', 'landingapp.views.clinic_search',
                           name='clinic_search'),

                       url(r'^hospitals_locate$', 'landingapp.views.hospitals_locate',
                           name='hospitals_locate'),


                       url(r'^clinic_locate$', 'landingapp.views.clinic_locate',
                           name='clinic_locate'),


                       url(r'^labs_locate$', 'landingapp.views.labs_locate',
                           name='labs_locate'),


                       url(r'^labs_region$', 'landingapp.views.labs_region',
                           name='labs_region'),

                       url(r'^labs$', 'landingapp.views.labs',
                           name='labs'),

                        url(r'^hospitals_region$', 'landingapp.views.hospitals_region',
                           name='hospitals_region'),

                       url(r'^clinic_region$', 'landingapp.views.clinic_region',
                           name='clinic_region'),

                       url(r'^nurse_home$', 'landingapp.views.nurse_home',
                           name='nurse_home'),


                       url(r'^nurse_search$', 'landingapp.views.nurse_search',
                           name='nurse_search'),


                        url(r'^nurse_locate$', 'landingapp.views.nurse_locate',
                           name='nurse_locate'),


                       url(r'^nurse_region$', 'landingapp.views.nurse_region',
                           name='nurse_region'),

                       


                       url(r'^Hiv_Aids$', 'landingapp.views.Hiv_Aids',
                           name='Hiv_Aids'),


                       url(r'^how_it_works$', 'landingapp.views.how_remit_works',
                           name='how_it_works'),

                       # app verification and such
                       url(r'^6DUU4UGQ.html', 'remit.views.verification'),


                       url(r'^404$', 'remit.views.custom_404', name='custom_404'),
                       url(r'^503$', 'remit.views.custom_503', name='custom_503'),


                       url(r'^sitemap.xml', 'landingapp.views.root_file', {
                           'filename': 'sitemap.xml',
                           'content_type': "application/xhtml+xml"}
                           ),




                       url(r'^500$', 'remit_admin.views.admin_503',
                           name='admin_503'),

                       url(r'^phonebook/editphonebook$',
                           'remit.views.edit_phonebook', name='edit_phonebook'),
                       url(r'^phonebook/deletefromphonebook$',
                           'remit.views.delete_from_phonebook', name='delete_from_phonebook'),
                       url(r'^phonebook/addtophonebook$',
                           'remit.views.add_to_phonebook', name='add_to_phonebook'),
                       url(r'^phonebook$', 'remit.views.phonebook',
                           name='phonebook'),

                       url(r'^transactions/(\w+)/$',
                           'remit.views.transaction', name='transaction'),
                       url(r'^transactions$',
                           'remit.views.transactions', name='transactions'),
                       url(r'^transactions/pending$',
                           'remit.views.pending_transactions', name='pending_transactions'),
                       # url(r'^remit/', include('remit.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),


                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       # url(r'^admin/settings/', include('dbsettings.urls')),
                       # url(r'^mr_tasty_fried_chicken/', include(
                       #    admin.site.urls)),

                       url(r'^chuck/', include(
                           admin.site.urls)),

                       url(r'^signup/$', 'accounts.views.signup', name='signup'),
                       url(r'^join/$', 'accounts.views.signup2', name='join'),
                       url(r'^login/$', 'accounts.views.signin', name='login'),
                       url(r'^send_now/$', 'accounts.views.add_landing_form_data',
                           name='add_landing_form_data'),

                       url(r'^recover_pass/$', 'accounts.views.recover_pass',
                           name='recoverpassword'),
                       url(r'^recover_pass/confirm/$',
                           'accounts.views.recover_pass_confirm', name='recoverpasswordconfirm'),





                       url(r'^account/userdetails/$',
                           'accounts.views.userdetails_form', name='userdetailsform'),
                       



                       #url(r'^signout/$','accounts.views.signout', name='signout'),
                       url(r'^signout/$', 'django.contrib.auth.views.logout', {
                           'next_page': settings.BASE_URL}, name="signout"),
                       url(r'^account/updatephonenumber/$',
                           'accounts.views.update_phonenumber', name='update_phonenumber'),
                       url(r'^account/resend/verificationemail/$',
                           'accounts.views.resend_verification_email', name='resend_verification_email'),
                       url(r'^account/send/verificationsms/$',
                           'accounts.views.send_verification_sms', name='send_verification_sms'),
                  

                       url(r'^account/resend/(\w+)/$',
                           'accounts.views.resendcode', name='resend'),

                       url(r'^account/resend/phoneverificationcode/$',
                           'accounts.views.resendcode', {'name': 'phoneverificationcode'}),

                       url(r'^account/uploadpassport/$',
                           'accounts.views.upload_passport', name='uploadpassport'),


                       url(r'^account/$', 'accounts.views.account', name='account'),
                       url(r'^account/$', 'accounts.views.account',
                           name='preferences'),


                       (r'^payments/', include(
                           'payments.urls')),


                       url(r'^server/checkphonebook/$',
                           'remit.views.ajax_server', name='ajax_check_phonebook'),

                       url(r'^server/querypaybillaccount/$',
                           'remit.views.ajax_server', name='querypaybillaccount'),

                       url(r'^activate/account/(\w+)/$',
                           'accounts.views.activate_email', name='activateemail'),
                       url(r'^activate/phonenumber/(\w+)/$',
                           'accounts.views.activate_sms', name='activatesms'),

                       url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                                                  content_type='text/plain')),

                       url(r'^static/uploads/images/uploads/(?P<image>.*)$',
                           'remit.views.restricted_media_view'),

                       url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.STATIC_ROOT, 'show_indexes': False}),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),

                       url(r'^session_security/', include(
                           'session_security.urls')),

                       url(r'^donate1$', 'landingapp.views.view_that_asks_for_money', name='donate1'),
                       url(r'^tinymce/', include('tinymce.urls')),

                       


                       )


# if settings.DEBUG:
#    debug_patterns = patterns('',
#      url(r'^do_cc/(\w+)/$', 'remit.test_views.do_cc',  name='do_cc'),
#      )
#    urlpatterns = debug_patterns + urlpatterns


handler404 = 'remit.views.custom_404'
handler403 = 'remit.views.custom_403'
handler500 = 'remit.views.custom_503'
