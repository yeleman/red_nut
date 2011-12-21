#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

from datetime import datetime
from django.db import models

from Patient import Patient


class InputOutputProgram(models.Model):
    """ """

    class Meta:
        app_label = 'nut'

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

    date = models.DateField(blank=True, null=True, verbose_name=(u"Date"),
                            default=datetime.today())
    event = models.CharField(max_length=30, verbose_name=(u"Evenement"),\
                                            choices=Event_type, default=N)
    reason = models.CharField(max_length=30, verbose_name=(u"Raison"),\
                                            choices=Reason_type, default=N)
    patient = models.ForeignKey(Patient, verbose_name=("Patient"))

    def __unicode__(self):
        return (u'%(patient)s %(event)s %(reason)s') % {"event": self.event, \
                            "patient": self.patient, "reason": self.reason}
