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
        input_ = InputOutputProgram.objects.filter(patient__id=patient.id) \
                                   .latest('date')
        datanuts = DataNut.objects.filter(patient__id=num).order_by('-date')
        datanut = datanuts.latest('date')
        context.update({'category': category,
                    'patient': patient,
                    'input_': input_,
                    'datanut': datanut,
                    'datanuts': datanuts})
        list_muac = [datanut.muac for datanut in datanuts]
        list_weight = [datanut.weight for datanut in datanuts]
        print 'Muac', list_muac
        print 'Weight', list_weight
    except DataNut.DoesNotExist:
        input_ = InputOutputProgram.objects.filter(patient__id=patient.id) \
                                   .latest('date')
        context.update({'error': 'aucun details nutritionnel',
                        'patient': patient, "input_": input_})
    except InputOutputProgram.DoesNotExist:
        context.update({'error': 'aucun details nutritionnel',
                        'patient': patient})

    return render(request, 'details_child.html', context)
