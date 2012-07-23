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
    name = models.CharField(max_length=30, verbose_name=u"Name")
    code = models.CharField(max_length=30, verbose_name=u"Code", unique=True)
    nut_code = models.CharField(max_length=10, verbose_name=u"Nutrition Code")
    parent = models.ForeignKey("HealthCenter", verbose_name=u"Parent")


    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}
