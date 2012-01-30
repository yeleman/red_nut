#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from settings import MEDIA_ROOT, DEBUG
from django.views.generic.simple import direct_to_template

from nut import views

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^/?$', views.dashboard, name='index'),
    url(r'^children/(?P<num>\d+)*$', views.children, name='children'),
    url(r'^child_delay/(?P<num>\d+)*$', views.child_delay,
                                        name='child_delay'),
    url(r'^details_child/(?P<id>\d+)$', views.details_child,
                                        name='details_child'),
    url(r'^health_center?$', views.health_center,
                             name='health_center'),
    url(r'^details_health_center/(?P<id>\d+)$', views.details_health_center,
                                                name='details_health_center'),

    url(r'^about/$', direct_to_template,
         {'template': 'about.html'}, name='about'),

    url(r'^excel_export/?$', views.excel_export, name='excel_export'),

    url(r'^export_bd/$', views.export_db, name="export_db"),


    url(r'^admin/', include(admin.site.urls)),
)

