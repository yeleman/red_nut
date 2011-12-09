#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou/Fadiga

import datetime
from django.db import models


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

    date = models.DateField(verbose_name=(u"Date"),\
                                            default=datetime.datetime.today)
    event = models.CharField(max_length=30, verbose_name=(u"Type"),\
                                             choices=Event_type, default=N)
    reason = models.CharField(max_length=30, verbose_name=(u"Type"),\
                                             choices=Reason_type, default=N)

    def __unicode__(self):
        return (u'%(date)s %(event)s %(reason)s') % \
                {"date": self.date, "event": self.event, \
                                    "reason": self.reason}
