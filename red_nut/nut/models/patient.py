#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import datetime, date
from django.db import models
from django.db.models.query import QuerySet

from healthcenter import HealthCenter
from nutritional_data import NutritionalData

from nut.tools.utils import weight_gain_calc


class PatientURENQS(QuerySet):

    def sam(self):
        return [patient for patient in self
                if patient.uren == NutritionalData.SAM]

    def mam(self):
        return [patient for patient in self
                if patient.uren == NutritionalData.MAM]

    def samp(self):
        return [patient for patient in self
                if patient.uren == NutritionalData.SAMP]

    def all_uren(self):
        return [patient for patient in self
                if patient.uren in (NutritionalData.SAMP, NutritionalData.SAM)]


class PatientURENManager(models.Manager):

    def get_query_set(self):
        return PatientURENQS(self.model, using=self._db)


class Patient(models.Model):
    """ """

    class Meta:
        app_label = 'nut'
        ordering = ('create_date',)

    SEX_MALE = 'M'
    SEX_FEMELLE = 'F'
    SEX_CHOICES = (
        (SEX_MALE, u"Masculin"),
        (SEX_FEMELLE, u"Féminin"),)

    nut_id = models.CharField(max_length=30, verbose_name=(u"Identifiant"),
                                                           unique=True)
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

    objects = models.Manager()
    by_uren = PatientURENManager()

    def __unicode__(self):
        return (u'%(first_name)s %(last_name)s %(mother)s %(create_date)s'
                 '%(health_center)s') % \
                {"first_name": self.first_name, \
                 "last_name": self.last_name, \
                 "mother": self.surname_mother, \
                 "create_date": self.create_date, \
                 "health_center": self.health_center}

    @property
    def uren(self):
        return self.nutritional_data.latest().diagnosis

    @property
    def status(self):
        return self.last_data_event().event

    def is_healing(self):
        from programIO import ProgramIO
        return (self.status == ProgramIO.OUT
                and self.last_data_event().reason == ProgramIO.HEALING)

    def in_program(self):
        from programIO import ProgramIO
        return self.status == ProgramIO.SUPPORT

    def program_periods(self):
        """ A list of in-progran periods

            (join_date, leave_date, nb_of_days) """

        periods = []
        ind = None
        outd = None
        for pio in self.programios.order_by('date'):
            if pio.event == pio.SUPPORT:
                ind = pio.date
            elif pio.event == pio.OUT:
                outd = pio.date
                periods.append((ind, outd, (outd - ind).days))
                ind = None
                outd = None
        if ind:
            periods.append((ind, None, None))
        return periods

    def last_program(self):
        return self.program_periods()[-1]

    def first_program(self):
        return self.program_periods()[0][0]

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
    def avg_weight_gain(cls, qs=None):
        """ return avg weight """
        qs = qs
        if qs == None:
            qs = cls.by_uren.all().all_uren()

        list_weight = [p.weight_gain() for p in qs if p.is_healing()]
        try:
            return sum(list_weight) / len(list_weight)
        except ZeroDivisionError:
            return 0

    @property
    def weight_delta_since_input(self):
        from programIO import ProgramIO
        io_date = self.programios.filter(event=ProgramIO.SUPPORT).latest().date
        nut_data = tuple(self.nutritional_data.filter(date__gte=io_date))
        try:
            return nut_data[-1].weight - nut_data[0].weight
        except:
            return 0

    def delay_since_last_visit(self):
        now = date.today()
        return now - (self.last_visit() or now)

    def last_data_nut(self):
        return NutritionalData.objects.filter(patient=self) \
                                      .order_by('-date')[0]

    def first_data_nut(self):
        return NutritionalData.objects.filter(patient=self) \
                                      .order_by('date')[0]

    def last_data_event(self):
        from programIO import ProgramIO
        return ProgramIO.objects.filter(patient=self)\
                                         .order_by('-date')[0]

    @property
    def is_late(self):
        """ """
        return self.delay_since_last_visit().days > 14

    @property
    def dob(self):
        return ((self.create_date.date() - self.birth_date).days) / 30

    def weight_gain(self):
        """ return weight gain per patient"""

        visits = self.last_inprogram_data()
        last_datanut = list(visits)[-1]
        min_datanut = visits.order_by('weight')[0]

        return weight_gain_calc(last_datanut, min_datanut)

    def last_inprogram_data(self):
        """ return all datanut for patient since last entrance."""

        from programIO import ProgramIO
        # all datanut for patient since last entrance.
        last_entrance = ProgramIO.objects.filter(event=ProgramIO.SUPPORT) \
                                         .filter(patient=self).latest()
        return self.nutritional_data.filter(date__gte=last_entrance.date)

    @classmethod
    def get_nut_id(cls, hc_code, uren, center_id, hc=None):
        """ build a nutrition ID based on UREN, HC and HC-id """
        if not hc:
            try:
                hc = HealthCenter.objects.get(code=hc_code.lower())
            except HealthCenter.DoesNotExist:
                hc = None

        uren_level = NutritionalData.URENS.get(uren.lower(), None)

        # check that all parts are in place
        if not hc or not hc.nut_code:
            raise ValueError(u"Invalid Health Center")

        if not uren_level:
            raise ValueError(u"Invalid UREN")

        if not hc.parent or not hc.parent.nut_code:
            raise ValueError(u"Invalid District")

        return (u"%(region_code)s/%(district_code)s/"
               u"%(uren)s%(center)s/%(center_id)s"
               % {'region_code': '09',
                  'district_code': hc.parent.nut_code,
                  'uren': uren_level,
                  'center': hc.nut_code.title(),
                  'center_id': center_id.zfill(4)})

    @classmethod
    def get_patient_nut_id(cls, hc_code, uren, center_id, hc=None):
        try:
            nut_id = cls.get_nut_id(hc_code, uren, center_id, hc)
        except ValueError as e:
            raise cls.DoesNotExist(e)

        return cls.objects.get(nut_id=nut_id)
