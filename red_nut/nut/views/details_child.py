#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.shortcuts import render

from nut.models import Patient, DataNut, InputOutputProgram


def details_child(request, *args, **kwargs):
    """ Details sur un enfant """
    num = kwargs["id"]
    category = 'details_child'
    context = {}
    patient = Patient.objects.filter(id=num)[0]
    try:
        output = InputOutputProgram.objects.filter(patient__id=patient.id, event='s') \
                                   .latest('date')
        context.update({"output": output})
    except:
        pass

    try:
        input_ = InputOutputProgram.objects.filter(patient__id=patient.id) \
                                   .latest('date')
        data_nuts =  DataNut.objects.filter(patient__id=num)
        datanuts =data_nuts.order_by('-date')
        datanuts_ = data_nuts.order_by('date')
        datanut = datanuts.latest('date')
        context.update({'category': category, 'patient': patient, \
                        'input_': input_, 'datanut': datanut, \
                        'datanuts': datanuts})
        list_muac = [datanut.muac for datanut in datanuts_]
        list_weight = [datanut.weight for datanut in datanuts_]
        graph_date = [datanut.date.strftime('%d/%m') for datanut in datanuts_]
        graph_data = [{'name': "Poids", 'data': list_weight}, \
                                {'name': "MUAC", 'data': list_muac}]
        context.update({"graph_date": graph_date, "graph_data": graph_data})
    except DataNut.DoesNotExist:
        input_ = InputOutputProgram.objects.filter(patient__id=patient.id) \
                                   .latest('date')
        context.update({'error': 'aucun details nutritionnel',
                        'patient': patient, "input_": input_})
    except InputOutputProgram.DoesNotExist:
        context.update({'error': 'aucun details nutritionnel',
                        'patient': patient})

    return render(request, 'details_child.html', context)
