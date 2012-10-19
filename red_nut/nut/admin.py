#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin

from models import (Period, Input, Patient, ProgramIO, HealthCenter,
                    NutritionalData, ConsumptionReport)


class HealthCenterAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'code')


class PatientAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','create_date', 'first_name', 'last_name',
                    'sex', 'surname_mother', 'contact', 'birth_date',
                    'health_center')
    list_filter = ('create_date','health_center',)


class ProgramIOAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'event', 'reason')
    list_filter = ('date', 'reason','patient__health_center','patient',)


class NutritionalDataAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'weight', \
                    'height', 'oedema', 'muac')
    list_filter = ('date','patient__health_center','patient',)


class ConsumptionReportAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'period', 'input_type', 'initial', \
                    'received', 'used', 'lost')
    list_filter = ('period','health_center',)


admin.site.register(HealthCenter, HealthCenterAdmin)
admin.site.register(NutritionalData, NutritionalDataAdmin)
admin.site.register(Input)
admin.site.register(ProgramIO, ProgramIOAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Period)
admin.site.register(ConsumptionReport, ConsumptionReportAdmin)
