from django.conf.urls import patterns, include, url
from pexproject.views import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf.urls import handler404
#from django.contrib import admin



urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', index, name='index'),
    #url(r'^$', 'pexproject.views.index'),
    url(r'', include('social_auth.urls')),
    #url(r'^facebooklogin', facebooklogin, name='facebooklogin'),
    
    url(r'^login', login, name='login'),
    #url(r'^google4fcc5c6791037930', include('webmaster_verification.urls')),
    url(r'^google4fcc5c6791037930$', lambda r: HttpResponse("google-site-verification: google4fcc5c6791037930.html")),
    #url(r'^webmaster', webmaster, name='webmaster'),
    #url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    
    url(r'^subscribe', subscribe, name='subscribe'),
    url(r'^blog', blog, name='blog'),
    url(r'^blog/$', blog, name='blog'),
    url(r'^sendFeedBack', sendFeedBack, name='sendFeedBack'),
    url(r'^mailchimp', mailchimp, name='mailchimp'),
    url(r'^createPassword', createPassword, name='createPassword'),
    url(r'^checkData', checkData, name='checkData'),
    url(r'^myRewardPoint', myRewardPoint, name='myRewardPoint'),
    url(r'^manageAccount', manageAccount, name='manageAccount'),
    url(r'^forgotPassword', forgotPassword, name='forgotPassword'),
    url(r'^signup', signup, name='signup'),
    url(r'^staticPage', staticPage, name='staticPage'),
    url(r'^contactUs', contactUs, name='contactUs'),
    url(r'^logout', logout, name='logout'),
    url(r'^flights', flights, name='flights'),

    url(r'^Admin/$', Admin, name='Admin'),
    url(r'^Admin/login/$', admin_login, name='admin_login'),
    url(r'^Admin/logout', admin_logout, name='admin_logout'),
    
    url(r'^Admin/email_template/$', email_template, name='email_template'),
    url(r'^Admin/email_template/new/$', email_template_update, name='email_template_new'),
    url(r'^Admin/email_template/(?P<id>\d+)/$', email_template_update, name='email_template_update'),
    url(r'^Admin/email_template/(?P<id>\d+)/delete/$', email_template_delete, name='email_template_delete'),

    url(r'^Admin/static_page/$', static_page, name='static_page'),

    url(r'^Admin/city_image/$', city_image, name='city_image'),
    url(r'^Admin/city_image/new/$', city_image_update, name='city_image_new'),
    url(r'^Admin/city_image/(?P<id>\d+)/$', city_image_update, name='city_image_update'),
    url(r'^Admin/city_image/(?P<id>\d+)/delete/$', city_image_delete, name='city_image_delete'),
    url(r'^Admin/get_cityname', get_cityname, name='get_cityname'),

    url(r'^Admin/hotel/$', hotel, name='hotel'),
    url(r'^Admin/hotel/new/$', hotel_update, name='hotel_new'),
    url(r'^Admin/hotel/(?P<id>\d+)/$', hotel_update, name='hotel_update'),
    url(r'^Admin/hotel/(?P<id>\d+)/delete/$', hotel_delete, name='hotel_delete'),
    
    url(r'^Admin/google_ad/$', google_ad, name='google_ad'),
    url(r'^Admin/google_ad/new/$', google_ad_update, name='google_ad_new'),
    url(r'^Admin/google_ad/(?P<id>\d+)/$', google_ad_update, name='google_ad_update'),
    url(r'^Admin/google_ad/(?P<id>\d+)/delete/$', google_ad_delete, name='google_ad_delete'),

    url(r'^Admin/blog_list/$', blog_list, name='blog_list'),
    url(r'^Admin/blog_list/new/$', blog_list_update, name='blog_list_new'),
    url(r'^Admin/blog_list/(?P<id>\d+)/$', blog_list_update, name='blog_list_update'),
    url(r'^Admin/blog_list/(?P<id>\d+)/delete/$', blog_list_delete, name='blog_list_delete'),

    url(r'^Admin/customer/$', customer, name='customer_list'),
    url(r'^Admin/customer/new/$', customer_update, name='customer_new'),
    url(r'^Admin/customer/(?P<id>\d+)/$', customer_update, name='customer_update'),
    url(r'^Admin/customer/(?P<id>\d+)/delete/$', customer_delete, name='customer_delete'),

    url(r'^Admin/token/$', token, name='token_list'),
    url(r'^Admin/token/new/$', token_update, name='token_new'),
    url(r'^Admin/token/(?P<id>\d+)/$', token_update, name='token_update'),
    url(r'^Admin/token/(?P<id>\d+)/delete/$', token_delete, name='token_delete'),

    url(r'^hotels/$', hotels, name='hotels'),
    url(r'^search_hotel/$', search_hotel),
    url(r'^api/hotels/$', api_search_hotel),
    url(r'^api/flights/$', api_search_flight),
    
    url(r'^index', index, name='index'),
    url(r'^useralert',useralert,name='useralert'),
    #url(r'^searchLoading',searchLoading,name='searchLoading'),
    url(r'^search',search, name='search'),
    url(r'^get_airport', get_airport, name='get_airport'),
    url(r'^getsearchresult', getsearchresult, name='getsearchresult'),
    url(r'^multicity', multicity, name='multicity'),
    url(r'^share', share, name='share'),
    url(r'^filter', filter, name='filter'),
    url(r'^getFlexResult', getFlexResult, name='getFlexResult'),
    #url(r'^apitest', apitest, name='apitest'),
    
    #url(r'^$','social_auth.urls',namespace='social'),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes':True}),
]
'''
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )'''
#handler404 = error
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
