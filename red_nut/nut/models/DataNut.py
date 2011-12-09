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
    patient = models.ForeignKey(Patient,
                                related_name='patient',\
                                verbose_name=("Patient"))
    date = models.DateField(verbose_name=("Date"))
    weight = models.CharField(max_length=30, verbose_name=("weight"))
    heught = models.PositiveIntegerField(verbose_name=("heught"))
    pb = models.PositiveIntegerField(verbose_name=("PB"))
    danger_sign = models.CharField(max_length=30, verbose_name=("Danger sign"))

    def __unicode__(self):
        return u"%(patient)s %(weight)skg/%(heught)scm %(pb)smm "\
        "%(danger_sign)s %(date)s" % {"date": self.date,
                                      "patient": self.patient,
                                      "heught": self.heught,
                                      "weight": self.weight,
                                      "pb": self.pb,
                                      "danger_sign": self.danger_sign}
