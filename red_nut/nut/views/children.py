#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings


def children(request):
    category = 'children'
    context = {}
    context.update({"category":category})

    return render(request, 'children.html', context)
