#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

import os

from django.http import HttpResponse, Http404
from django.conf import settings

abs_path = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(abs_path)


def export_bd(request):
    """ """
    djpath = settings.DATABASES['default']['NAME']
    if os.path.exists(djpath):
        fullpath = djpath
    else:
        fullpath = os.path.join(ROOT_DIR, djpath)

    if not os.path.exists(fullpath):
        raise Http404
    response = HttpResponse(file(fullpath).read())
    response['Content-Type'] = 'application/sqlite'
    response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(fullpath)
    return response
