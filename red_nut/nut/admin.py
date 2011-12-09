#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin

from models.Period import Period
from models.Input  import Input
from models.Patient  import Patient
from models.InputOutputProgram  import InputOutputProgram

#~ admin.site.register(Seat)
#~ admin.site.register(DataNut)
admin.site.register(Input)
admin.site.register(InputOutputProgram)
admin.site.register(Patient)
admin.site.register(Period)
#~ admin.site.register(Stock)
