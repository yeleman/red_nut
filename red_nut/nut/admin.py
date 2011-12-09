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



admin.site.register(Seat, SeatAdmin)
admin.site.register(DataNut)
admin.site.register(Input)
admin.site.register(InputOutputProgram)
admin.site.register(Patient)
admin.site.register(Period)
admin.site.register(Stock)
