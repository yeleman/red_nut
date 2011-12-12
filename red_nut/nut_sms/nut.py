#!/usr/bin/env python
# encoding: utf-8
# maintainer: Fad/Alou

import datetime
import logging
import locale

import reversion
from django.conf import settings

from nosms.models import Message
from nosms.utils import send_sms

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def nosms_handler(message):
    def main_nut_handler(message):
        if message.text.lower().startswith('nut '):
            if message.text.lower().startswith('nut stock'):
                return nut_stock(message)
        else:
            return False

    if main_nut_handler(message):
        message.status = Message.STATUS_PROCESSED
        message.save()
        logger.info(u"[HANDLED] msg: %s" % message)
        return True
    logger.info(u"[NOT HANDLED] msg : %s" % message)
    return False

def nut_stock(message):
    message.respond(u"stock")
    print 'stock'
    return True
