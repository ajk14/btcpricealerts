from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'alert.views.home', name='home'),
    url(r'^register/', 'alert.views.register', name='register'),
    url(r'^logout/$','django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"), 
    #url(r'^login/$','django.contrib.auth.views.login', {'template_name': 'home.html'}, name="login"), 
    url(r'^login/$','alert.views.myLogin', name="myLogin"), 
#    url(r'^alert/$','alert.views.alert'),
    url(r'^delete/$','alert.views.delete'),
    url(r'^phone/$','alert.views.phone'),
    url(r'^phone/confirmation/$','alert.views.phone_confirmation'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    #url(r'^admin/(.*)', admin.site.root),
    url(r'^accounts/', include('registration.urls')),
   # url(r'^$', direct_to_template, 
     #       { 'template': 'index.html' }, 'index'),

    # url(r'^btcalerts/', include('btcalerts.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
