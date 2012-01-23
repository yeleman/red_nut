#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.db import models
from HealthCenter import HealthCenter
from Period import Period
from Input import Input
from DataNut import DataNut


class ConsumptionReport(models.Model):
    """ """

    class Meta:
        app_label = 'nut'
        verbose_name = u"ConsumptionReport"
        verbose_name_plural = u"ConsumptionReports"

    health_center = models.ForeignKey(HealthCenter,\
                                related_name='Health_center',\
                                verbose_name="Health_center")
    period = models.ForeignKey(Period, related_name='period',\
                                        verbose_name='Period')
    input_type = models.ForeignKey(Input,\
                                    related_name='input',\
                                    verbose_name='Input')
    initial = models.PositiveIntegerField(verbose_name="Stock initial")
    received = models.PositiveIntegerField(verbose_name="Stock received")
    used = models.PositiveIntegerField(verbose_name="Stock used")
    lost = models.PositiveIntegerField(verbose_name="Stock lost")

    def remaining(self):
        re = (self.initial + self.received) - (self.used + self.lost)
        return re

    def __unicode__(self):
        restant = self.remaining()
        return u'%(health_center)s le restant est %(re)s' \
                 % {"health_center": self.health_center, "re": restant}
