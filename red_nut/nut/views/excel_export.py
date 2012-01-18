#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.http import HttpResponse
from nut.exports import report_as_excel
from nut.models import Stock, Seat, Patient, DataNut


def excel_export(request, *args, **kwargs):
    context = {'category': 'export'}
    num = kwargs["id"]
    seat = Seat.objects.get(id=num)
    patients = Patient.objects.filter(seat=seat)
    datanuts = DataNut.objects.filter(patient__seat=seat)
    stocks = Stock.objects.filter(seat=seat)
    context.update({'stocks': stocks})

    # check permission or raise 403
    try:
        file_name = 'NUT_%(seat)s.%(month)s.%(year)s.xls' \
                    % {'seat': stocks[0].seat, \
                       'month': stocks[0].period.middle().month, \
                       'year': stocks[0].period.middle().year}
    except IndexError:
        if patients:
            file_name = 'NUT_%(seat)s.xls' \
                    % {'seat': patients[0].seat}
        else:
            return HttpResponse('rien')

    file_content = report_as_excel(stocks, patients, datanuts).getvalue()

    response = HttpResponse(file_content, \
                            content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    response['Content-Length'] = len(file_content)

    return response


        #~ return HttpResponse('Pas de rapport de stock dispo')



