#!/usr/bin/env python
# encoding: utf-8
# maintainer: Fad/Alou

import datetime
import logging
import locale

import reversion
from django.conf import settings

from red_nut.nut.models import Patient, Seat

from nosms.models import Message
from nosms.utils import send_sms

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def nosms_handler(message):
    def main_nut_handler(message):
        if message.text.lower().startswith('nut '):
            if message.text.lower().startswith('nut stock'):
                return nut_stock(message)
            if message.text.lower().startswith('nut register'):
                return nut_register(message)
            if message.text.lower().startswith('nut research'):
                return id_information_research(message)
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


def nut_register(message):
    """ Ajout d'un nouveau patient
    params: nut + register + code siège + nom + prénom + prénom mère +DDN/age"""
    nut, register, code_seat, first_name, last_name, surname_mother, \
                        DDN_Age = message.text.strip().lower().split()
    try:
        # On essai prendre le seat
        seat = Seat.objects.get(code=code_seat)
    except:
        # On envoi un sms pour signaler que le code n'est pas valid
        message.respond(u"[ERROR] %(seat)s n'est un code siège valid" % \
                                                        {'seat': code_seat})
        seat = None
    if seat != None:
        report = Patient()
        report.first_name = first_name
        report.last_name = last_name
        report.surname_mother = surname_mother
        report.DDN_Age = DDN_Age
        report.seat = seat
        report.save()
        message.respond(u"[SUCCES] Le rapport de %(seat)s a ete "
                        u"enregistre. Le du est #%(code)s." \
                        % {'seat': seat, 'code': report.id})
    return True


def id_information_research(message):
    """Infos pour recherche ID
    params: nut + research + code_seat + nom(optionel) + prénom(optionel) \
                                            + prénom mère(optionel)"""

    nut, research, code_seat, first_name, last_name, \
                    surname_mother = message.text.strip().lower().split()

    if last_name == "n" and first_name == "n":
        try:
            patient = Patient.objects.get(surname_mother=surname_mother)
            message.respond(u"%(surname_mother)s à pour code %(code)s." \
                                % {'surname_mother': surname_mother, \
                                'code': patient.id})
        except:
            message.respond(u"%(surname_mother)s n'est pas enregistrer" \
                        % {'surname_mother': surname_mother})

    if last_name == "n" and surname_mother == "n":
        try:
            patient = Patient.objects.get(first_name=first_name)
            message.respond(u"%(first_name)s à pour code %(code)s." \
                            % {'first_name': first_name, 'code': patient.id})
        except:
            message.respond(u"%(first_name)s n'est pas enregistrer" \
                        % {'first_name': first_name})

    if first_name == "n" and surname_mother =="n":
        try:
            patient = Patient.objects.get(last_name=last_name)
            message.respond(u"%(last_name)s à pour code %(code)s." \
                            % {'last_name': last_name, 'code': patient.id})
        except:
            message.respond(u"%(last_name)s n'est pas enregistrer" \
                        % {'last_name': last_name})
    if first_name != "n" and surname_mother != "n" and last_name != "n":
        try:
            patient = Patient.objects.get(last_name=last_name, \
                                          surname_mother=surname_mother, \
                                             first_name=first_name)
            message.respond(u"Il à pour code %(code)s." \
                                    % {'code': patient.id})
        except:
            message.respond(u"%(last_name)s  %(last_name)s "
                            u"n'est pas enregistrer" \
                            % {'first_name': first_name,\
                                'last_name': last_name})

    return True
