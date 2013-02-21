#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template

from settings import MEDIA_ROOT
from nut import views

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', views.login, name="login"),
    url(r"^logout$", views.logout, name="logout"),
    url(r'^dashboard/?$', views.dashboard, name='index'),
    url(r'^dashboard/reset?$', views.dashboard_clear_cache, name='reset_cache'),
    url(r'^children/?$', views.children, name='children'),
    url(r'^late_children/(?P<num>\d+)*$', views.child_delay,
                                        name='child_delay'),
    url(r'^children/(?P<id>\d+)/?$', views.details_child,
                                        name='details_child'),
    url(r'^health_centers/?$', views.health_center,
                             name='health_center'),
    url(r'^messages_log/?$', views.log_message,
                             name='log_messages'),
    url(r'^messages_log/detailed/?$', views.sms_per_center,
                             name='sms_per_center'),
    url(r'^health_centers/(?P<id>\d+)$', views.details_health_center,
                                                name='details_health_center'),

    url(r'^about/$', direct_to_template,
         {'template': 'about.html'}, name='about'),

    url(r'^excel_export/?$', views.excel_export, name='excel_export'),

    url(r'^database_export/?$', views.export_db, name="export_db"),


    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$',
             'django.views.static.serve',
             {'document_root': MEDIA_ROOT, 'show_indexes': True},
             name='media'),
)
