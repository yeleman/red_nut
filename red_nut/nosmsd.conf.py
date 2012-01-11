#!/usr/bin/env python
# encoding=utf-8

NOSMSD_HANDLER = 'red_nut.nut_sms.nut.handler'
NOSMSD_GETTEXT = True
NOSMSD_GETTEXT_LOCALE = 'fr_FR.UTF-8'

NOSMSD_DATABASE = {'type': 'MySQL', 'name': 'rednutsms'}
NOSMSD_DATABASE_OPTIONS = {'user': 'rednutsms', 'passwd': 'rednutsms',
                           'host': 'localhost', 'use_unicode': True}
