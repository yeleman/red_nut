#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin

from models.Period import Period
from models.Input  import Input
from models.Patient  import Patient
from models.ProgramIO  import ProgramIO
from models.HealthCenter  import HealthCenter
from models.nutritional_data  import NutritionalData
from models.ConsumptionReport  import ConsumptionReport


class HealthCenterAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'code')


class PatientAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'first_name', 'last_name', 'sex',\
                        'surname_mother', 'birth_date', 'health_center')


class ProgramIOAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'event', 'reason')


class NutritionalDataAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'weight', \
                    'height', 'oedema', 'muac')


class ConsumptionReportAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'period', 'input_type', 'initial', \
                    'received', 'used', 'lost')


admin.site.register(HealthCenter, HealthCenterAdmin)
admin.site.register(NutritionalData, NutritionalDataAdmin)
admin.site.register(Input)
admin.site.register(ProgramIO, ProgramIOAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Period)
admin.site.register(ConsumptionReport, ConsumptionReportAdmin)
