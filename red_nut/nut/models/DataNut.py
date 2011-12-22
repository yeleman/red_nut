# encoding=utf-8
# maintainer: Alou

from django.db import models
from Patient import Patient


class DataNut(models.Model):
    """ """
    class Meta:
        app_label = 'nut'
        verbose_name = u"DataNut"
        verbose_name_plural = u"DataNuts"

    OEDEMA_YES = 'Y'
    OEDEMA_NO = 'N'
    OEDEMA_UNKOWN = 'U'
    OEDEMA_CHOICES = (
        (OEDEMA_YES, u"Yes"),
        (OEDEMA_NO, u"No"),
        (OEDEMA_UNKOWN, u"Unknown"))


    patient = models.ForeignKey(Patient,
                                related_name='patient',\
                                verbose_name=("Patient"))
    date = models.DateField(verbose_name=("Date"))
    weight = models.FloatField(u"Poids (kg)", blank=True, null=True)
    heught = models.FloatField(u"Taille (kg)", blank=True, null=True)
    oedema = models.CharField(u"Oedema", max_length=1, \
                              choices=OEDEMA_CHOICES)
    muac = models.SmallIntegerField(u"MUAC (mm)", blank=True, null=True)
    danger_sign = models.CharField(max_length=30, verbose_name=("Danger sign"))

    def __unicode__(self):
        return u"%(patient)s %(weight)skg/%(heught)scm %(pb)smm "\
        "%(danger_sign)s %(date)s" % {"date": self.date,
                                      "patient": self.patient,
                                      "heught": self.heught,
                                      "weight": self.weight,
                                      "pb": self.muac,
                                      "danger_sign": self.danger_sign}
