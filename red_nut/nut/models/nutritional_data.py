# encoding=utf-8
# maintainer: Alou

from datetime import datetime
from django.db import models


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
    MAS = 'mas'

    URENS = {SAM: u"URENAS",
             SAMP: u"URENI",
             MAS: u"URENAM"}

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

    date = models.DateField(verbose_name="Date", default=datetime.today)

    weight = models.FloatField(u"Poids (kg)")
    height = models.FloatField(u"Taille (cm)")

    oedema = models.CharField(u"Oedème", max_length=1, choices=OEDEMA_CHOICES)

    muac = models.SmallIntegerField(u"MUAC (mm)")

    danger_sign = models.CharField(max_length=30,
                                   choices=DANGER_SIGN_CHOICES,
                                   verbose_name="Signe de danger",
                                   blank=True, null=True)

    nb_plumpy_nut = models.IntegerField(
                                max_length=30,
                                verbose_name=u"Sachets plumpy nut données",
                                blank=True, null=True)

    def __unicode__(self):
        return u"%(patient)s %(date)s/%(weight)skg/%(height)scm %(pb)smm "\
         % {"patient": self.patient, "height": self.height, \
                "weight": self.weight, "pb": self.muac, "date": self.date}

    @property
    def diagnosis(self):
        '''Diagnosis of the patient'''
        if self.muac is None or self.muac == 0:
            return None
        elif self.muac < 80:
            return "SAM+"
        elif self.oedema == 'Y' or self.muac < 110:
            return "SAM"
        elif self.muac < 125:
            return "MAM"
