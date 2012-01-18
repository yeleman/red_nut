#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

from datetime import datetime
from django.db import models

from Patient import Patient


class ProgramIO(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

    EN_CHARGE = "e"
    SORTI = "s"
    Event_type = ((EN_CHARGE, u"En charge"), (SORTI, u"Sorti"))

    NEANT = ""
    ADBANDONMENT = "a"
    HEALING = "h"
    TANSFER = "t"
    DEATH = "d"
    NON_RESPONDENT = "n"
    Reason_type = ((NEANT, "----"), (ADBANDONMENT, "abandon"), \
                    (HEALING, u"guérison"), (TANSFER, "transfer"), \
                    (DEATH, u"deces"), (NON_RESPONDENT, u"non-repondant"))

    date = models.DateField(blank=True, null=True, verbose_name=(u"Date"),
                            default=datetime.today())
    event = models.CharField(max_length=30, verbose_name=(u"Evenement"),\
                                    choices=Event_type, default=EN_CHARGE)
    reason = models.CharField(max_length=30, verbose_name=(u"Raison"),\
                                            choices=Reason_type, default=NEANT)
    patient = models.ForeignKey(Patient, verbose_name=("Patient"))

    def __unicode__(self):
        return (u'%(patient)s %(event)s %(reason)s %(date)s') % \
                    {"event": self.event, "date": self.date, \
                     "patient": self.patient.full_name(), "reason": self.reason}
