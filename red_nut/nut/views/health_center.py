#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.contrib import messages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import Seat


def health_center(request):
    category = 'health_center'
    context = {}
    context.update({"category": category})

    seats = Seat.objects.all()

    context.update({"seats": seats})
    return render(request, 'health_center.html', context)
