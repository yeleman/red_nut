#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga


import datetime
from django.db import models
from bolibana.models import Period

class Patient(models.Model):
    """ """
    first_name = models.CharField(max_length=30, verbose_name=(u"Prénom"))
    last_name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    surname_mother = models.CharField(max_length=30, \
                                      verbose_name=(u"Prénom de la mère"))
    DDN_Age = models.PositiveIntegerField(_(u"DDN/Age"))
    cscom = models.CharField(max_length=30, verbose_name=(u"CSCOM"))

    def __unicode__(self):
        return _(u'%(first_name)s %(last_name)s') % \
                {"first_name": self.first_name, "last_name": self.last_name}


class input_output_Program(models.Model):
    """ """

    N = ""
    E = "e"
    S = "s"
    Event_type = ((N, "----"), (E, u"Entrer"), (S, u"Sortie"))

    ADBANDONMENT = "a"
    HEALING = "h"
    TANSFER = "t"
    DEATH = "d"
    NON-RESPONDENT = "n"
    Reason_type = ((N, "----"), (ADBANDONMENT, "abandon"), \
                    (HEALING, u"guérison"), (TANSFER, "transfer"), \
                    (DEATH, u"deces"), (NON-RESPONDENT, u"non-repondant"))

    date = models.DateField(verbose_name=(u"Date"),\
                                            default=datetime.datetime.today)
    event = models.CharField(max_length=30,verbose_name=(u"Type"),\
                                             choices=Event_type, default=N)
    reason = models.CharField(max_length=30, verbose_name=(u"Type"),\
                                             choices=Reason_type, default=N)

    def __unicode__(self):
        return _(u'%(date)s %(event)s %(reason)s') % \
                {"date": self.date, "event": self.event, \
                                    "reason": self.reason}


class Input(models.Model):
    """ """

    N = ""
    KG = "g"
    BOX = "bo"
    BAG = "ba"
    Unit_type = ((N, "----"), (KG, u"KG"), (BOX, u"Boite"), (BAG, u"sachet")

    name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    code = models.CharField(max_length=30, verbose_name=(u"Code"))

    unit = models.CharField(max_length=30, verbose_name=(u"Unité"),\
                                             choices=Reason_type, default=N)

    def __unicode__(self):
        return _(u'%(name)s %(code)s %(unit)s') % \
                {"name": self.name, "code": self.code, \
                                    "unit": self.unit}

class Nutperiod(models.Model):
    """ """
    name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    start_on = models.DateField(verbose_name=(u"Date"))
    end_on = models.DateField(verbose_name=(u"Date"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}


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
