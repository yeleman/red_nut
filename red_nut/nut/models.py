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
    DDN_Age = models.PositiveIntegerField(u"DDN/Age")
    cscom = models.CharField(max_length=30, verbose_name=(u"CSCOM"))

    def __unicode__(self):
        return (u'%(first_name)s %(last_name)s') % \
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
    NON_RESPONDENT = "n"
    Reason_type = ((N, "----"), (ADBANDONMENT, "abandon"), \
                    (HEALING, u"guérison"), (TANSFER, "transfer"), \
                    (DEATH, u"deces"), (NON_RESPONDENT, u"non-repondant"))

    date = models.DateField(verbose_name=(u"Date"),\
                                            default=datetime.datetime.today)
    event = models.CharField(max_length=30,verbose_name=(u"Type"),\
                                             choices=Event_type, default=N)
    reason = models.CharField(max_length=30, verbose_name=(u"Type"),\
                                             choices=Reason_type, default=N)

    def __unicode__(self):
        return (u'%(date)s %(event)s %(reason)s') % \
                {"date": self.date, "event": self.event, \
                                    "reason": self.reason}


class Input(models.Model):
    """ """

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

class Nutperiod(models.Model):
    """ """
    name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    start_on = models.DateField(verbose_name=(u"Date"))
    end_on = models.DateField(verbose_name=(u"Date"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}


class Seat(models.Model):
    """ """
    name = models.CharField(max_length=30, verbose_name=("Name"))
    code = models.CharField(max_length=30, verbose_name=("Code"))

    def __unicode__(self):
        return u'%(name)s' % {"name": self.name}


class DataNut(models.Model):
    """ """
    patient = models.ForeignKey(Patient,
                                related_name='patient',\
                                verbose_name=("Patient"))
    date = models.CharField(max_length=30, verbose_name=("Name"))
    weight = models.CharField(max_length=30, verbose_name=("weight"))
    heught = models.PositiveIntegerField(verbose_name=("heught"))
    pb = models.PositiveIntegerField(verbose_name=("PB"))
    danger_sign = models.CharField(max_length=30, verbose_name=("Danger sign"))

    def __unicode__(self):
        return u'%(date)s' % {"date": self.date}


class Stock(models.Model):
    """ """
    seat = models.ForeignKey(Seat,\
                                related_name='seat',\
                                verbose_name=("Seat"))
    nutperiod = models.ForeignKey(Nutperiod,
                                        related_name='nutperiod',\
                                        verbose_name='Period')
    alou = models.ForeignKey(Input,\
                                    related_name='input',\
                                    verbose_name='Input')
    stock_initial = models.PositiveIntegerField(verbose_name=("Stock initial"))
    stock_received = models.PositiveIntegerField(verbose_name=("Stock received"))
    stock_used = models.PositiveIntegerField(verbose_name=("Stock used"))
    stock_lost = models.PositiveIntegerField(verbose_name=("Stock lost"))

    def __unicode__(self):
        return u'%(seat)s' % {"date": self.seat}




