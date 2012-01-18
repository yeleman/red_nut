#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.http import HttpResponse
from nut.exports import report_as_excel
from nut.models import ConsumptionReport, HealthCenter, Patient, DataNut


def excel_export(request, *args, **kwargs):
    context = {'category': 'export'}
    num = kwargs["id"]
    health_center = HealthCenter.objects.get(id=num)
    patients = Patient.objects.filter(health_center=health_center)
    datanuts = DataNut.objects.filter(patient__health_center=health_center)
    consumptionreports = ConsumptionReport.objects.filter(health_center=health_center)
    context.update({'consumptionreports': consumptionreports})

    try:
        file_name = 'NUT_%(health_center)s.%(month)s.%(year)s.xls' \
                    % {'health_center': consumptionreports[0].health_center, \
                       'month': consumptionreports[0].period.middle().month, \
                       'year': consumptionreports[0].period.middle().year}
    except IndexError:
        if patients:
            file_name = 'NUT_%(health_center)s.xls' \
                    % {'health_center': patients[0].health_center}
        else:
            return HttpResponse('rien')

    file_content = report_as_excel(consumptionreports, patients, datanuts).getvalue()

    response = HttpResponse(file_content, \
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    response['Content-Length'] = len(file_content)

    return response
