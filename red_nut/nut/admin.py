#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin

from models.Period import Period
from models.Input  import Input
from models.Patient  import Patient
from models.InputOutputProgram  import InputOutputProgram
from models.Seat  import Seat
from models.DataNut  import DataNut
from models.Stock  import Stock


class SeatAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'code')


class PatientAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'first_name', 'last_name', \
                        'surname_mother', 'DDN_Age', 'seat')


class InputOutputProgramAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'date', 'event', 'reason')

admin.site.register(Seat, SeatAdmin)
admin.site.register(DataNut)
admin.site.register(Input)
admin.site.register(InputOutputProgram, InputOutputProgramAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Period)
admin.site.register(Stock)
