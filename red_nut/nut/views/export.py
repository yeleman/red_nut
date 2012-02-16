#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou, Fadiga

"""
    Contains functions dedicated to export the whole database into
    various format such as XLS and sqlite
"""

import os

from datetime import datetime

from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required

from nut.models import  HealthCenter
from nut.tools.export import report_as_excel


@login_required
def excel_export(request, *args, **kwargs):
    context = {'category': 'export'}
    health_centers = HealthCenter.objects.all()
    date = datetime.today()

    file_name = 'NUT_base%s-%s-%d.xls' % (date.day, date.month, date.year)

    response = HttpResponse(report_as_excel(health_centers).getvalue(),
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    return response


@login_required
def export_db(request):

    if not os.path.exists(settings.DB_PATH):
        raise Http404

    response = HttpResponse(file(settings.DB_PATH).read())
    response['Content-Type'] = 'application/sqlite'
    response['Content-Disposition'] = 'attachment; filename="%s"' % \
                                        os.path.basename(settings.DB_PATH)
    return response
