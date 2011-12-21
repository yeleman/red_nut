#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render


def details_health_center(request):
    category = 'details_health_center'
    context = {}
    context.update({"category": category})

    return render(request, 'details_health_center.html', context)
