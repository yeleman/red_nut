#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

import os

from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from nut import views
from settings import STATIC_ROOT, MEDIA_ROOT

urlpatterns = patterns('',
    # Examples:
    url(r'^/?$', views.dashboard.dashboard, name='index'),
    url(r'^children?$', views.children.children, name='children'),
    url(r'^details_child?$', views.details_child.details_child, \
                                                        name='details_child'),
    url(r'^health_center?$', views.health_center.health_center, \
                                                        name='health_center'),
    url(r'^details_health_center?$', views.details_health_center \
                                                    .details_health_center, \
                                                name='details_health_center'),
    # url(r'^red_nut/', include('red_nut.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$',
             'django.views.static.serve',
             {'document_root': MEDIA_ROOT, 'show_indexes': True}, \
             name='media'),
)
