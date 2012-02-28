#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import datetime, date
from django.db import models

from healthcenter import HealthCenter


class Patient(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

    SEX_MALE = 'M'
    SEX_FEMELLE = 'F'
    SEX_CHOICES = (
        (SEX_MALE, u"Masculin"),
        (SEX_FEMELLE, u"Féminin"),)

    first_name = models.CharField(max_length=30, verbose_name=(u"Prénom"))
    last_name = models.CharField(max_length=30, verbose_name=(u"Nom"))
    surname_mother = models.CharField(max_length=30, \
                                          verbose_name=(u"Prénom de la mère"))
    health_center = models.ForeignKey(HealthCenter, related_name='patients',
                                                      verbose_name=("Clinic"))
    create_date = models.DateTimeField(verbose_name=("Date d'enregistrement"),
                                                     default=datetime.today())
    birth_date = models.DateField(verbose_name=(u"Date de naissance"))
    sex = models.CharField(u"Sexe", max_length=1, choices=SEX_CHOICES)
    contact = models.CharField(max_length=100, verbose_name=(u"contact"),
                                                        blank=True, null=True)

    def __unicode__(self):
        return (u'%(first_name)s %(last_name)s %(mother)s %(birth_date)s'
                 '%(health_center)s') % \
                {"first_name": self.first_name, \
                 "last_name": self.last_name, \
                 "mother": self.surname_mother, \
                 "birth_date": self.birth_date, \
                 "health_center": self.health_center}

    def full_name(self):
        """return full name"""
        return (u'%(first_name)s %(last_name)s' % \
                                {"first_name": self.first_name.capitalize(),
                                "last_name": self.last_name.capitalize()})

    def full_name_id(self):
        """ return full name and id """
        return u"%s#%d" % (self.full_name(), self.id)

    def full_name_mother(self):
        """ return full name of mother """
        return u"%s/%s" % (self.full_name(), self.surname_mother.capitalize())

    def full_name_all(self):
        return u"%s#%d" % (self.full_name_mother(), self.id)

    def last_visit(self):
        """ return date of last visit """
        last = self.last_data_nut()
        if last:
            return last.date
        return None

    @classmethod
    def avg_weight_delta(cls, qs=None):
        """ return avg weight """
        qs = qs
        if qs == None:
            qs = cls.objects.all()

        list_weight = [p.weight_delta_since_input for p in qs]

        try:
            return sum(list_weight) / len(list_weight)
        except ZeroDivisionError:
            return 0

    @property
    def weight_delta_since_input(self):
        from programIO import ProgramIO
        date = self.programios.filter(event=ProgramIO.SUPPORT).latest().date
        nut_data = tuple(self.nutritional_data.filter(date__gte=date))
        try:
            return nut_data[-1].weight - nut_data[0].weight
        except:
            return 0

    def delay_since_last_visit(self):
        now = date.today()
        return now - (self.last_visit() or now)

    def last_data_nut(self):
        from nutritional_data import NutritionalData
        return NutritionalData.objects.filter(patient=self) \
                                      .order_by('-date')[0]

    def last_data_event(self):
        from programIO import ProgramIO
        return ProgramIO.objects.filter(patient=self)\
                                         .order_by('-date')[0]

    @property
    def is_late(self):
        """ """
        return self.delay_since_last_visit().days > 10