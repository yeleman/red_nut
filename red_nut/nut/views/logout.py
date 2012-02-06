#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect


def logout(request):
    """ logout est la views qui permet de se deconnecter """

    django_logout(request)
    return redirect("login")
