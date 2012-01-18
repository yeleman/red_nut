#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.db import models
from HealthCenter import HealthCenter
from Period import Period
from Input import Input
from DataNut import DataNut


class Stock(models.Model):
    """ """
    class Meta:
        app_label = 'nut'
        verbose_name = u"Stock"
        verbose_name_plural = u"Stocks"
    health_center = models.ForeignKey(HealthCenter,\
                                related_name='Health_center',\
                                verbose_name="Health_center")
    period = models.ForeignKey(Period,related_name='period',\
                                        verbose_name='Period')
    intrant = models.ForeignKey(Input,\
                                    related_name='input',\
                                    verbose_name='Input')
    stock_initial = models.PositiveIntegerField(verbose_name="Stock initial")
    stock_received = models.PositiveIntegerField(verbose_name="Stock received")
    stock_used = models.PositiveIntegerField(verbose_name="Stock used")
    stock_lost = models.PositiveIntegerField(verbose_name="Stock lost")

    def remaining(self):
        re = (self.stock_initial + self.stock_received) -\
             (self.stock_used + self.stock_lost)
        return re

    def __unicode__(self):
        restant = self.remaining()
        return u'%(health_center)s le restant est %(re)s' \
                 % {"health_center": self.health_center, "re": restant}
