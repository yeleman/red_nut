#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.db import models


class HealthCenter(models.Model):
    """ """
    class Meta:
        app_label = 'nut'
        verbose_name = u"HealthCenter"
        verbose_name_plural = u"HealthCenters"
    name = models.CharField(max_length=30, verbose_name=("Name"))
    code = models.CharField(max_length=30, verbose_name=("Code"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}
