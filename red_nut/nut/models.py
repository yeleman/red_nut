#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga


import datetime
from django.db import models


class Seat(models.Model):
    name = models.CharField(max_length=30, verbose_name=("Name"))
    code = models.CharField(max_length=30, verbose_name=("Code"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}


class DataNut(models.Model):
    date = models.CharField(max_length=30, verbose_name=("Name"))
    weight = models.CharField(max_length=30, verbose_name=("weight"))
    heught = models.PositiveIntegerField(verbose_name=("heught"))
    pb = models.PositiveIntegerField(verbose_name=("PB"))
    danger_sign = models.CharField(max_length=30, verbose_name=("Danger sign"))
    def __unicode__(self):
        return u'%(name)s' % {"name": self.date}
