#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin
from models import Seat, DataNut, Input, inputOutputProgram, Patient, \
                                                                Nutperiod

admin.site.register(Seat)
admin.site.register(DataNut)
admin.site.register(Input)
admin.site.register(inputOutputProgram)
admin.site.register(Patient)
admin.site.register(Nutperiod)
