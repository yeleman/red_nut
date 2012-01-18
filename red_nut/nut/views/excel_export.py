#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.http import HttpResponse
from nut.exports import report_as_excel
from nut.models import Stock, HealthCenter, Patient, DataNut


def excel_export(request, *args, **kwargs):
    context = {'category': 'export'}
    num = kwargs["id"]
    health_Center = HealthCenter.objects.get(id=num)
    patients = Patient.objects.filter(health_Center=health_Center)
    datanuts = DataNut.objects.filter(patient__health_Center=health_Center)
    stocks = Stock.objects.filter(health_Center=health_Center)
    context.update({'stocks': stocks})

    # check permission or raise 403
    try:
        file_name = 'NUT_%(health_Center)s.%(month)s.%(year)s.xls' \
                    % {'health_Center': stocks[0].health_Center, \
                       'month': stocks[0].period.middle().month, \
                       'year': stocks[0].period.middle().year}
    except IndexError:
        if patients:
            file_name = 'NUT_%(health_Center)s.xls' \
                    % {'health_Center': patients[0].health_Center}
        else:
            return HttpResponse('rien')

    file_content = report_as_excel(stocks, patients, datanuts).getvalue()

    response = HttpResponse(file_content, \
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    response['Content-Length'] = len(file_content)

    return response


    #~ return HttpResponse('Pas de rapport de stock dispo')



