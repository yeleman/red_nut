#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu}

APP='nut'
DATABASE='rednut'


class RedNutRouter(object):

    def allow_syncdb(self, db, model):
        if model._meta.app_label == APP:
            return db == DATABASE
        else:
            return False if db == DATABASE else None
        return None

    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP:
            return DATABASE
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == APP:
            return DATABASE
        return None
