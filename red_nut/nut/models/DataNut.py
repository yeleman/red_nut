# encoding=utf-8
# maintainer: Alou

from datetime import datetime
from django.db import models
from Patient import Patient


class DataNut(models.Model):
    """ Données nutritionneles d'un enfant """
    class Meta:
        app_label = 'nut'
        verbose_name = u"DataNut"
        verbose_name_plural = u"DataNuts"

    OEDEMA_YES = 'Y'
    OEDEMA_NO = 'N'
    OEDEMA_UNKNOWN = 'U'
    OEDEMA_CHOICES = (
        (OEDEMA_YES, u"Oui"),
        (OEDEMA_NO, u"Non"),
        (OEDEMA_UNKNOWN, u"Inconnu"))

    SIGN_DIARRHEA = "d"
    DANGER_SIGN_CHOICES = ((SIGN_DIARRHEA, "Diarrhée"),)

    patient = models.ForeignKey(Patient, related_name='datanuts',\
                                                verbose_name=("Patients"))
    date = models.DateField(verbose_name=("Date"),\
                                   default=datetime.today)
    weight = models.FloatField(u"Poids (kg)", blank=True, null=True)
    height = models.FloatField(u"Taille (cm)", blank=True, null=True)
    oedema = models.CharField(u"Oedème", max_length=1, \
                              choices=OEDEMA_CHOICES)
    muac = models.SmallIntegerField(u"MUAC (mm)", blank=True, null=True)
    danger_sign = models.CharField(max_length=30, \
                                   choices=DANGER_SIGN_CHOICES, \
                                   verbose_name=("Signe de danger"), \
                                   blank=True, null=True)
    nb_plumpy_nut = models.IntegerField(max_length=30, \
                        verbose_name=(u"Sachets plumpy nut données"), \
                                                blank=True, null=True)

    def __unicode__(self):
        return u"%(patient)s %(weight)skg/%(height)scm %(pb)smm "\
         % { "patient": self.patient, "height": self.height,
                "weight": self.weight, "pb": self.muac,}
