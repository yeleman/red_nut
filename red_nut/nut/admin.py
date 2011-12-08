#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: alou

from django.contrib import admin
from models import (Seat, DataNut, Input, input_output_Program,\
                    Patient, Nutperiod,Stock)

admin.site.register(Seat)
admin.site.register(DataNut)
admin.site.register(Input)
admin.site.register(input_output_Program)
admin.site.register(Patient)
admin.site.register(Nutperiod)
admin.site.register(Stock)
