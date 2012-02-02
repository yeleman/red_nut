#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from settings import MEDIA_ROOT, DEBUG
from django.views.generic.simple import direct_to_template

from nut import views
from export_bd import export_bd

admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', views.login, name="login"),
    url(r"^logout$", views.logout, name="logout"),
    url(r'^dashboard/?$', views.dashboard, name='index'),
    url(r'^children/(?P<num>\d+)*$', views.children, name='children'),
    url(r'^child_delay/(?P<num>\d+)*$', views.child_delay, \
                                                        name='child_delay'),
    url(r'^details_child/(?P<id>\d+)$', views.details_child, \
                                                        name='details_child'),
    url(r'^health_center?$', views.health_center, \
                                                        name='health_center'),
    url(r'^details_health_center/(?P<id>\d+)$', views.details_health_center, \
                                                name='details_health_center'),

    url(r'^about/$', direct_to_template, \
         {'template': 'about.html'}, name='about'),

    url(r'^excel_export/?$', views.excel_export, name='excel_export'),

    url(r'^export_bd/$', export_bd, name="export_bd"),

    url(r'^media/(?P<path>.*)$',
             'django.views.static.serve',
             {'document_root': MEDIA_ROOT, 'show_indexes': True}, \
             name='media'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
