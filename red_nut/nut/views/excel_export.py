#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from nut.export_excel import report_as_excel
from nut.models import HealthCenter


@login_required
def excel_export(request, *args, **kwargs):

    health_centers = HealthCenter.objects.all()
    date = datetime.today()

    file_name = 'NUT_base%s-%s-%d.xls' % (date.day, date.month, date.year)

    file_content = report_as_excel(health_centers).getvalue()

    response = HttpResponse(file_content, \
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    return response
