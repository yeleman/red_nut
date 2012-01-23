#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from settings import MEDIA_ROOT, DEBUG
from django.views.generic.simple import direct_to_template
#~ from django.views.decorators.cache import cache_page

from nut import views
from export_bd import export_bd

admin.autodiscover()


urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Examples:
    url(r'^/?$', views.dashboard, name='index'),
    url(r'^children/(?P<num>\d+)*$', views.children, name='children'),
    url(r'^child_delay/(?P<num>\d+)*$', views.child_delay, \
                                                        name='child_delay'),
    url(r'^details_child/(?P<id>\d+)$', views.details_child, \
                                                        name='details_child'),
    url(r'^health_center?$', views.health_center, \
                                                        name='health_center'),
    url(r'^details_health_center/(?P<id>\d+)$', views.details_health_center, \
                                                name='details_health_center'),
    # url(r'^red_nut/', include('red_nut.foo.urls')),

    url(r'^about/$', direct_to_template, \
         {'template': 'about.html'}, name='about'),

    url(r'^excel_export/?$', views.excel_export, name='excel_export'),

    url(r'^export_bd/$', export_bd, name="export_bd"),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$',
             'django.views.static.serve',
             {'document_root': MEDIA_ROOT, 'show_indexes': True}, \
             name='media'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
