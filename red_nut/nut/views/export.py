#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou, Fadiga

"""
    Contains functions dedicated to export the whole database into
    various format such as XLS and sqlite
"""

import os
import subprocess

from datetime import datetime

from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required

from nut.models import  HealthCenter
from nut.tools.export import report_as_excel


@login_required
def excel_export(request, *args, **kwargs):

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

    # args = ['sqlite3', settings.DB_PATH, '.dump']
    # if getattr(subprocess, 'check_output', None):
    #     response = HttpResponse(subprocess.check_output(args))
    # else:
    #     response = HttpResponse(subprocess.Popen(args,
    #                             stdout=subprocess.PIPE).communicate()[0])

    # DB_PATH is now a zipped MySQL plain SQL dump
    response = open(settings.DB_PATH).read()

    response['Content-Type'] = 'application/zip; charset=binary'
    response['Content-Disposition'] = ('attachment; '
                                       'filename="rednut_%s.sql.zip"' %
                                        datetime.today().strftime('%d-%m-%Y'))

    return response


@login_required
def export_sqlite_db(request):

    if not os.path.exists(settings.DB_PATH):
        raise Http404

    response = HttpResponse(file(settings.DB_PATH).read())
    response['Content-Type'] = 'application/sqlite'
    response['Content-Disposition'] = 'attachment; filename="%s"' % \
                                        os.path.basename(settings.DB_PATH)
    return response
