#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import os

from django.http import HttpResponse

abs_path = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(abs_path)


def export_bd(request):
    """ """

    fullpath = os.path.join(ROOT_DIR, 'rednut.sqlite')
    response = HttpResponse(file(fullpath).read())
    response['Content-Type'] = 'application/sqlite'
    response['Content-Disposition'] = 'attachment; filename="rednut.sqlite"'
    return response
