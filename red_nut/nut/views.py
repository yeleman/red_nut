#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Alou & Fadiga

from django.shortcuts import render_to_response


def home(request):
    """ Home"""
    c = {'home': 'home'}
    return render_to_response('home.html', c)
