# encoding=utf-8

import re

from datetime import date, datetime, timedelta

from django.db import IntegrityError

from red_nut.nut.models import (Patient, ProgramIO, NutritionalData,
                                HealthCenter, Input, ConsumptionReport)
from red_nut.nut.models.period import MonthPeriod
from nosmsd.utils import send_sms


FOL_NUMBER = "70061482"


def handler(message):
    """ NUT SMS router """
    def main_nut_handler(message):
        keyword = 'nut'
        commands = {'stock': nut_consumption,
                    'fol': nut_followup,
                    'register': nut_register,
                    'research': nut_search,
                    'off': nut_disable,
                    'test': nut_test,
                    'echo': nut_echo}

        if message.content.lower().startswith('nut '):
            for cmd_id, cmd_target in commands.items():
                command = '%s %s' % (keyword, cmd_id)
                if message.content.lower().startswith(command):
                    n, args = re.split(r'^%s\s?' % command,
                                       message.content.lower().strip())
                    return cmd_target(message,
                                      args=args,
                                      sub_cmd=cmd_id,
                                      cmd=command)
        else:
            return False

    if main_nut_handler(message):
        message.status = message.STATUS_PROCESSED
        message.save()
        return True
    return False


def nut_test(message, **kwargs):
    try:
        code, msg = message.content.split('nut test')
    except:
        msg = ''

    msg = u"Received on %(date)s: %(msg)s" % {'date': datetime.now(),
                                              'msg': msg}
    message.respond(msg)
    send_sms(FOL_NUMBER, msg)
    return True


def nut_echo(message, **kwargs):
    message.respond(kwargs['args'])
    return True


def formatdate(date_str, as_datetime=False):

    now = date.today()

    # we received a date
    if re.match(r'^\d{8}$', date_str):
        try:
            adate = date(int(date_str[0:4]),
                         int(date_str[4:6]),
                         int(date_str[6:8]))
        except:
            raise ValueError(u"[ERREUR] Date incorrecte.")
    # we received a number of month
    else:
        try:
            adate = now - timedelta(30 * int(date_str)) - timedelta(15)
        except ValueError:
            raise ValueError(u"[ERREUR] Nombre de mois incorrect.")

    if adate > now:
        raise ValueError(u"[ERREUR] La date est dans le futur.")

    if as_datetime:
        dt_now = datetime.now()
        return datetime(adate.year, adate.month, adate.day,
                        dt_now.hour, dt_now.minute, dt_now.second)
    else:
        return adate


def resp_error(message, action):
    msg = u"[ERREUR] Impossible de comprendre le SMS pour %s" % action
    message.respond(msg)
    send_sms(FOL_NUMBER, msg)
    return True


def save_error(message, action):
    msg = u"[ERREUR] %s" % action
    message.respond(msg)
    send_sms(FOL_NUMBER, msg)
    return True


def clean_up_pid(patient_id):
    # remove neg sign if exist or decimal point
    return patient_id.replace('-', '').replace('.', '')


def nut_register(message, args, sub_cmd, cmd):
    """ Incomming:
            nut register hc_code, create_date, patient_id,
                         first_name, last_name, mother, sex, dob, contact
                         #weight height oed pb nbr, is_ureni
            exple: 'nut register sab3 20121004 23 Moussa Kone Camara M 7
                    35354#6 65 YES 111 25 0'
        Outgoing:
            [SUCCES] Le rapport de name_health_center a ete enregistre.
            Son id est 8.
            or  [ERREUR] Votre rapport n'a pas été enregistrer"""

    try:
        register_data, follow_up_data = args.split('#')

        hc_code, create_date, patient_id, first_name, last_name, mother, sex, dob, contact = register_data.split()

        weight, height, oedema, muac, nb_plumpy_nut, is_ureni = follow_up_data.split()
    except:
        return resp_error(message, u"enregistrement")
    try:
        # On essai prendre le seat
        hc = HealthCenter.objects.get(code=hc_code.lower())
    except:
        # On envoi un sms pour signaler que le code n'est pas valide
        msg = u"[ERREUR] %(hc)s n'est pas un code de Centre valide."\
              % {'hc': hc_code}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    # check date
    try:
        registration_date = formatdate(create_date, True)
    except ValueError as e:
        return resp_error(message, e)
    # Car on ne traite que les URENI pour l'instant
    type_uren = NutritionalData.SAM
    # True or False
    is_ureni = bool(int(is_ureni))

    if is_ureni:
        if hc_code in ["qmali", "cr"]:
            type_uren = NutritionalData.SAMP
        else:
            msg = u"[ERREUR] Seul les CSREF ont le droit " \
                  u"d'enregistrer les enfants URENI"
            message.respond(msg)
            send_sms(FOL_NUMBER, msg)
            return True
    try:
        patient_id = clean_up_pid(patient_id)
        nut_id = Patient.get_nut_id(hc_code, type_uren.lower(), patient_id)
    except ValueError as e:
        return resp_error(message, e)

    patient = Patient()
    patient.nut_id = nut_id
    patient.first_name = first_name.replace('_', ' ').title()
    patient.last_name = last_name.replace('_', ' ').title()
    patient.surname_mother = mother.replace('_', ' ').title()
    patient.create_date = registration_date
    try:
        patient.birth_date = formatdate(dob)
    except ValueError as e:
        message.respond(u"[ERREUR] %(e)s" % {'e': e})
        return True

    patient.sex = sex.upper()
    patient.contact = contact
    patient.health_center = hc
    try:
        patient.save()
    except IntegrityError:
        patient = Patient.objects.get(nut_id=nut_id)
        save_error(message, u"/!\ l'identifiant #%(id)s appartient déjà à"
                            u" %(full_name)s. enregistré au centre"
                            u" %(health_center)s le %(date)s"
                            u" Pour plus d'information, appelez ce numéro %(admin)s"
                   % {'full_name': patient.full_name(), 'id': nut_id,
                      'date': patient.create_date.strftime("%x %H: %Mmm %Ss"),
                      'health_center': patient.health_center.name,
                      'admin': FOL_NUMBER})
        return False
    except:
        return save_error(message, u"Impossible d'enregistrer ce rapport dans "
                                   u"la base des donnees")

    # adding patient to the program
    programio = ProgramIO()
    programio.patient = patient
    programio.event = programio.SUPPORT
    programio.date = registration_date
    try:
        programio.save()
    except:
        return resp_error(message, u"enregistrement")

    # creating a followup event
    weight = float(weight)
    height = float(height)
    oedema = {'yes': NutritionalData.OEDEMA_YES,
              'no': NutritionalData.OEDEMA_NO,
              'unknown': NutritionalData.OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) if not str(nb_plumpy_nut).lower() == '-' else 0
    datanut = add_followup_data(patient=patient, weight=weight,
                                height=height, oedema=oedema, muac=muac,
                                nb_plumpy_nut=nb_plumpy_nut,
                                is_ureni=is_ureni,
                                date=registration_date)
    if not datanut:
        msg = u"/!\ %(full_name)s enregistre avec ID#%(id)s." \
              u" Donnees nutrition non enregistres." % {'full_name': patient.full_name(), 'id': nut_id}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    message.respond(u"[SUCCES] %(full_name)s enregistre avec ID#%(id)s."
                    u" Donnees nutrition enregistres." % {'full_name': patient.full_name_mother(), 'id': nut_id})
    return True


def add_followup_data(**kwargs):
    try:
        datanut = NutritionalData(**kwargs)
        datanut.save()
        return datanut
    except:
        return None


def nut_followup(message, args, sub_cmd, cmd):

    """ Incomming:
            nut fol hc_code reporting_d  patient_id weight height
                oedema muac nb_plumpy_nut(optional), is_ureni
        exple: 'nut fol sab3 20121004 sam 23 5 65 YES 120 2 1'

        Outgoing:
            [SUCCES] Donnees nutrition mise a jour pour full_name #id
            or error message """

    try:
        hc_code, reporting_d, type_uren, patient_id, weight, height, oedema, muac, nb_plumpy_nut, is_ureni = args.split()
    except:
        return resp_error(message, u"suivi")

    try:
        patient_id = clean_up_pid(patient_id)
        patient = Patient.get_patient_nut_id(hc_code, type_uren.lower(), patient_id)
    except:
        msg = u"[ERREUR] Aucun patient trouve pour ID#%s" % patient_id
        message.respond()
        send_sms(FOL_NUMBER, msg)
        return True

    try:
        followup_date = formatdate(reporting_d)
        followup_datetime = formatdate(reporting_d, True)
    except ValueError as e:
        return resp_error(message, e)

    # creating a followup event
    is_ureni = bool(int(is_ureni))
    weight = float(weight)
    height = float(height)
    oedema = {'yes': NutritionalData.OEDEMA_YES,
              'no': NutritionalData.OEDEMA_NO,
              'unknown': NutritionalData.OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) if not nb_plumpy_nut.lower() == '-' else 0

    if patient.last_data_nut().date == followup_date:
        last_data_nut = patient.last_data_nut()
        last_data_nut.weight = weight
        last_data_nut.height = height
        last_data_nut.oedema = oedema
        last_data_nut.muac = muac
        last_data_nut.nb_plumpy_nut = nb_plumpy_nut
        last_data_nut.is_ureni = is_ureni
        last_data_nut.save()
        message.respond(u"[SUCCES] Donnees nutrition mise a jour pour "
                        u"%(full_name)s" % {'full_name': patient.full_name_id()})
        return True

    if patient.last_data_nut().date > followup_date:
        msg = u"[ERREUR] La date du dernier suivi pour" \
              u" %(full_name)s est superieur que la date utilise" % {'full_name': patient.full_name_id()}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    if patient.last_data_event().event == ProgramIO.OUT:
        programio = ProgramIO()
        programio.patient = patient
        programio.event = programio.SUPPORT
        programio.date = followup_datetime
        programio.save()

    datanut = add_followup_data(patient=patient, weight=weight,
                                height=height, oedema=oedema,
                                muac=muac, nb_plumpy_nut=nb_plumpy_nut,
                                is_ureni=is_ureni,
                                date=followup_date)
    if not datanut:
        return resp_error(message, u"suivi")

    message.respond(u"[SUCCES] Donnees nutrition enregistres pour "
                    u"%(full_name)s" % {'full_name': patient.full_name_id()})
    return True


def nut_search(message, args, sub_cmd, cmd):
    """ Incomming:
            nut research code_health_center first_name(op) last_name(op)
             surname_mother(op)
            None = n
            example 1: nut research dasco iba Fad Diarra
            example 2: nut research dasco - Fad Diarra "Si le first_name vide"
            example 3: nut research dasco - Fad n
                        "Si le first_name et surname_mother sont vide"

        Outgoing:
            Il existe nbr de resultat patient(s) pour XXX: last_name
            surname_mother de l'id 7, last_name surname_mother de l'id 8.
            or  Il n'existe aucun patient du prénom first_name """

    try:
        hc_code, first, last, mother = args.split()
    except:
        return resp_error(message, u"recherche")

    try:
        hc = HealthCenter.objects.get(code=hc_code)
    except:
        msg = u"[ERREUR] %(hc)s n'est pas un code de Centre valide." % {'hc': hc_code}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    first = first.replace('_', ' ') if first != '-' else None
    last = last.replace('_', ' ') if last != '-' else None
    mother = mother.replace('_', ' ') if mother != '-' else None

    patients = Patient.objects.filter(health_center=hc)

    display = ['first', 'last', 'mother']

    if first:
        patients = patients.filter(first_name__icontains=first)
        display.remove('first')

    if last:
        patients = patients.filter(last_name__icontains=last)
        display.remove('last')

    if mother:
        patients = patients.filter(surname_mother__icontains=mother)
        display.remove('mother')

    if not len(display):
        fmt = u"%(first)s#%(id)s"
    else:
        fmt = u"/".join(["%%(%s)s" % d for d in display]) + u"#%(id)s"

    def display_name(p, fmt):
        return fmt % {'id': p.nut_id,
                      'first': p.first_name.title(),
                      'last': p.last_name.title(),
                      'mother': p.surname_mother.title()}

    if not len(patients.all()):
        message.respond(u"[ERREUR] Pas de patient trouve. "
                        u"Essayez une recherche plus large.")
        return True

    msg = u"[SUCCES] %d trouves: %s" % (len(patients.all()),
          ", ".join([display_name(patient, fmt) for patient in patients.all()]))
    message.respond(msg[:160])
    return True


def nut_disable(message, args, sub_cmd, cmd):
    """  Incomming:
            hc_code, date_disable, patient_id, weight, height, muac,
            reason
            example reason: (a= abandon, t = transfer ...)
            example data: 'nut off sab3 20120925 sam 23 - - - a'
         Outgoing:
            [SUCCES] full_name ne fait plus partie du programme.
            or error message """

    try:
        hc_code, date_disable, type_uren, patient_id, weight, height, muac, reason = args.split()
    except ValueError:
        # Todo: A supprimer une fois la version 07 de application java"
        # est deployé au cscom
        hc_code, date_disable, type_uren, patient_id, reason = args.split()
        weight = None
        height = None
        muac = None
    except:
        return resp_error(message, u"la sortie")

    try:
        quitting_date = formatdate(date_disable)
        quitting_datetime = formatdate(date_disable, True)
    except ValueError as e:
        return resp_error(message, e)

    try:
        patient_id = clean_up_pid(patient_id)
        patient = Patient.get_patient_nut_id(hc_code, type_uren.lower(), patient_id)
    except:
        msg = u"[ERREUR] Aucun patient trouve pour ID#%s" % patient_id
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    if patient.last_data_nut().date > quitting_date:
        msg = u"[ERREUR] La date du dernier suivi pour ID# %s est " \
              u"superieur que la date utilise" % patient.nut_id
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    if patient.last_data_event().event == ProgramIO.OUT:
        msg = u"/!\ %(full_name)s est deja sortie du programme." % {'full_name': patient.full_name()}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    if reason == ProgramIO.HEALING and weight:
        datanut = add_followup_data(patient=patient, weight=weight,
                                    height=height, muac=muac,
                                    oedema=NutritionalData.OEDEMA_NO,
                                    nb_plumpy_nut=0,
                                    date=quitting_date)
        if not datanut:
            message.respond(u"/!\ %(full_name)s enregistre avec ID#%(id)s."
                            u" Donnees nutrition non enregistres."
                            % {'full_name': patient.full_name(),
                               'id': patient_id})
            return True

    programio = ProgramIO()
    programio.patient = patient
    programio.event = programio.OUT
    programio.reason = reason
    programio.date = quitting_datetime
    programio.save()
    message.respond(u"[SUCCES] %(full_name)s ne fait plus partie "
                    u"du programme." % {'full_name': patient.full_name()})
    return True


def nut_consumption(message, args, sub_cmd, cmd):
    """ Incomming:
            nut stock type_health_center code_health_center month year
             #input_type initial received used received #input_type initial
            received used received
            example: nut stock URENAM dasco 1 2012 #nie 11 22 18 2
                     #csb 22 22 22 2 #uni 2 32 22 2 #hui 21 25 45 1
                     #suc 23 12 30 0 #mil 32 15 32 2
        Outgoing:
            [SUCCES] Le rapport de stock de health_center a ete bien
            enregistre.
            or error message """

    try:
        general, reports = args.split('#', 1)
        hc_type, hc_code, month, year = general.split()
    except:
        return resp_error(message, u"stock")

    try:
        hc = HealthCenter.objects.get(code=hc_code)
    except:
        msg = u"[ERREUR] %(hc)s n'est pas un code de Centre valide." % {'hc': hc_code}
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    try:
        period = MonthPeriod.find_create_from(year=int(year),
                                              month=int(month))
    except:
        msg = u"[ERREUR] %s-%s n'est pas une periode valide." % (month, year)
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    now_period = MonthPeriod.find_create_by_date(date.today())
    if period != now_period.previous():
        msg = u"[ERREUR] Impossible d'enregistrer le rapport de conso pour %s.\
                 Envoyez pour %s" % (period.full_name(), now_period.previous().full_name())
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    try:
        all_reports = reports.split('#')
    except:
        return resp_error(message, u"stock")

    success = []
    errors = []
    for areport in all_reports:
        try:
            icode, initial, received, used, lost = areport.split()
            input_type = Input.objects.get(code=icode.lower())
        except:
            errors.append(icode)

        if ConsumptionReport.objects.filter(period=period,
                                            health_center=hc,
                                            input_type=input_type).count():
            cr = ConsumptionReport.objects.get(period=period,
                                               health_center=hc,
                                               input_type=input_type)
        else:
            cr = ConsumptionReport(period=period, health_center=hc,
                                   input_type=input_type)
        cr.initial = int(initial)
        cr.received = int(received)
        cr.used = int(used)
        cr.lost = int(lost)
        try:
            cr.save()
            success.append(cr)
        except:
            errors.append(icode)

    if len(errors):
        msg = u"[ERREUR] %d rapport de conso en erreur. Verifiez toutes les" \
              u" donnees et renvoyez -- %s" % (len(errors), ', '.join(errors))
        message.respond(msg)
        send_sms(FOL_NUMBER, msg)
        return True

    message.respond(u"[SUCCES] %d rapports de conso enregistres pour %s."
                    % (len(success), period.full_name()))
    return True
