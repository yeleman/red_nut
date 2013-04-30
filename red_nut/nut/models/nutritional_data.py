# encoding=utf-8
# maintainer: Alou

from datetime import datetime
from django.db import models
from zscore import zscore_from


class NutritionalData(models.Model):
    """ Données nutritionneles d'un enfant """

    class Meta:
        app_label = 'nut'
        verbose_name = u"Nutrional Data"
        verbose_name_plural = u"Nutritional Data"
        ordering = ('date',)
        get_latest_by = 'date'

    SAM = 'sam'
    SAMP = 'samp'
    MAM = 'mas'
    URENS = {SAM: u"URENAS",
             SAMP: u"URENI",
             MAM: u"URENAM"}

    URENS_FR = {SAM: u"MAS",
                SAMP: u"MAS+",
                MAM: u"MAM"}

    OEDEMA_YES = 'Y'
    OEDEMA_NO = 'N'
    OEDEMA_UNKNOWN = 'U'
    OEDEMA_CHOICES = (
        (OEDEMA_YES, u"Oui"),
        (OEDEMA_NO, u"Non"),
        (OEDEMA_UNKNOWN, u"Inconnu"))

    SIGN_DIARRHEA = "d"
    DANGER_SIGN_CHOICES = ((SIGN_DIARRHEA, "Diarrhée"),)

    patient = models.ForeignKey("Patient", related_name='nutritional_data',
                                verbose_name="Patients")

    date = models.DateField(verbose_name="Date", default=datetime.now())

    weight = models.FloatField(u"Poids (kg)")
    height = models.FloatField(u"Taille (cm)")

    oedema = models.CharField(u"Oedème", max_length=1, choices=OEDEMA_CHOICES)

    muac = models.SmallIntegerField(u"MUAC (mm)")

    danger_sign = models.CharField(max_length=30,
                                   choices=DANGER_SIGN_CHOICES,
                                   verbose_name="Signe de danger",
                                   blank=True, null=True)

    nb_plumpy_nut = models.IntegerField(max_length=30,
                                        verbose_name=u"Sachets plumpy nut données",
                                        blank=True, null=True)
    is_ureni = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%(patient)s %(date)s/%(weight)skg/%(height)scm %(pb)smm "\
               % {"patient": self.patient, "height": self.height,
                  "weight": self.weight, "pb": self.muac, "date": self.date}

    @property
    def diagnosis(self):
        '''Diagnosis of the patient'''
        if self.is_ureni:
            return self.SAMP
        elif self.oedema == self.OEDEMA_YES:
            return self.SAMP
        if self.muac is None or self.muac == 0:
            return None
        elif self.muac < 115 or zscore_from(self.height, self.weight) < -3:
            return self.SAM
        elif self.muac < 136:
            return self.MAM
