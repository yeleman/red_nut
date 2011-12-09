#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

import datetime
from django.db import models


class Patient(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

    first_name = models.CharField(max_length=30, verbose_name=(u"Prénom"))
    last_name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    surname_mother = models.CharField(max_length=30, \
                                      verbose_name=(u"Prénom de la mère"))
    DDN_Age = models.PositiveIntegerField(u"DDN/Age")
    cscom = models.CharField(max_length=30, verbose_name=(u"CSCOM"))

    def __unicode__(self):
        return (u'%(first_name)s %(last_name)s') % \
                {"first_name": self.first_name, "last_name": self.last_name}

