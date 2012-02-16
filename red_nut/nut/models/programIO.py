#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

from datetime import datetime
from django.db import models

from patient import Patient


class OutProgramIOManager(models.Manager):

    def get_query_set(self):
        qs = super(OutProgramIOManager, self).get_query_set()
        return qs.filter(event=ProgramIO.OUT)

    def avg_days(self):
        """
             Return the average program duration days for
             all patients that are out of the program.
        """
        qs = self.get_query_set()
        list_num_days = [out.program_duration.days for out in qs]
        try:
            return sum(list_num_days) / len(list_num_days)
        except ZeroDivisionError:
            return 0


class HealingProgramIOManager(OutProgramIOManager):
    def get_query_set(self):
        qs = super(HealingProgramIOManager, self).get_query_set()
        return qs.filter(reason=ProgramIO.HEALING)


class AbandonmentProgramIOManager(OutProgramIOManager):
    def get_query_set(self):
        qs = super(AbandonmentProgramIOManager, self).get_query_set()
        return qs.filter(reason=ProgramIO.ADBANDONMENT)


class NonRespProgramIOManager(OutProgramIOManager):
    def get_query_set(self):
        qs = super(NonRespProgramIOManager, self).get_query_set()
        return qs.filter(reason=ProgramIO.NON_RESPONDENT)


class DeathProgramIOManager(OutProgramIOManager):
    def get_query_set(self):
        qs = super(DeathProgramIOManager, self).get_query_set()
        return qs.filter(reason=ProgramIO.DEATH)


class ProgramIO(models.Model):
    """ """

    class Meta:
        app_label = 'nut'
        ordering = ('date',)
        get_latest_by = 'date'

    SUPPORT = "e"
    OUT = "s"
    Event_type = ((SUPPORT, u"En charge"), (OUT, u"Sorti"))

    NEANT = ""
    ADBANDONMENT = "a"
    HEALING = "h"
    TANSFER = "t"
    DEATH = "d"
    NON_RESPONDENT = "n"
    Reason_type = ((NEANT, "----"), (ADBANDONMENT, "abandon"),
                   (HEALING, u"guérison"), (TANSFER, "transfer"),
                   (DEATH, u"deces"), (NON_RESPONDENT, u"non-repondant"))

    objects = models.Manager()  # he default manager.
    out = OutProgramIOManager()
    nonresp = NonRespProgramIOManager()
    healing = HealingProgramIOManager()
    abandon = AbandonmentProgramIOManager()
    death = DeathProgramIOManager()

    date = models.DateTimeField(verbose_name=(u"Date"),
                            default=datetime.today())
    event = models.CharField(max_length=30, verbose_name=(u"Evenement"),
                                    choices=Event_type, default=SUPPORT)
    reason = models.CharField(max_length=30, null=True, blank=True,
                              verbose_name=(u"Raison"),
                              choices=Reason_type, default=NEANT)
    patient = models.ForeignKey(Patient, related_name='programios',
                                         verbose_name=("Patient"))

    @property
    def is_output(self):
        return self.event == self.OUT

    @property
    def program_duration(self):
        if self.event == self.OUT:
            return self.date - self.patient.create_date

    def __unicode__(self):
        return ((u'%(patient)s %(event)s %(reason)s %(date)s') %
                    {"event": self.event, "date": self.date,
                     "patient": self.patient.full_name(),
                     "reason": self.reason})
