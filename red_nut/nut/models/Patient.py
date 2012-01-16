#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import datetime
from django.db import models
from Seat import Seat


class Patient(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

    SEX_MALE = 'M'
    SEX_FEMELLE = 'F'
    SEX_CHOICES = (
        (SEX_MALE, u"Masculin"),
        (SEX_FEMELLE, u"Feminin"),)


    first_name = models.CharField(max_length=30, verbose_name=(u"Prénom"))
    last_name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    surname_mother = models.CharField(max_length=30, \
                                      verbose_name=(u"Prénom de la mère"))
    seat = models.ForeignKey(Seat,
                            related_name='patient',\
                            verbose_name=("Seat"))
    create_date = models.DateField(verbose_name=("Date d'enregistrement"),\
                                   default=datetime.today)
    DDN_Age = models.DateField(verbose_name=(u"Date de naissance"))
    sex = models.CharField(u"Sexe", max_length=1, \
                              choices=SEX_CHOICES)
    def __unicode__(self):
        return (u'%(first_name)s %(last_name)s %(mother)s %(age)s \
                                                        %(seat)s') % \
                {"first_name": self.first_name, "last_name": self.last_name, \
                 "mother": self.surname_mother, "age": self.DDN_Age, \
                 "seat": self.seat}

    def full_name(self):
        return (u'%(first_name)s %(last_name)s' % \
                                {"first_name": self.first_name.capitalize(),
                                "last_name": self.last_name.capitalize()})
