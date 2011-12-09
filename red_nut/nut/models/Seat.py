#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.db import models


class Seat(models.Model):
    """ """
    class Meta:
        app_label = 'nut'
        verbose_name = u"Seat"
        verbose_name_plural = u"Seats"
    name = models.CharField(max_length=30, verbose_name=("Name"))
    code = models.CharField(max_length=30, verbose_name=("Code"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}
