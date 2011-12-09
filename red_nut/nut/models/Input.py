#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

import datetime
from django.db import models


class Input(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

    N = ""
    KG = "g"
    BOX = "bo"
    BAG = "ba"
    Unit_type = ((N, "----"), (KG, u"KG"), (BOX, u"Boite"), (BAG, u"sachet"))

    name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    code = models.CharField(max_length=30, verbose_name=(u"Code"))

    unit = models.CharField(max_length=30, verbose_name=(u"Unité"),\
                                             choices=Unit_type, default=N)

    def __unicode__(self):
        return (u'%(name)s %(code)s %(unit)s') % \
                {"name": self.name, "code": self.code, \
                                    "unit": self.unit}
