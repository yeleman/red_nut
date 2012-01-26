# encoding=utf-8

import re

from red_nut.nut.models import *
from red_nut.nut.models.Period import MonthPeriod

from datetime import date


def handler(message):
    """ NUT SMS router """
    def main_nut_handler(message):
        keyword = 'nut'
        commands = {
            'stock': nut_consumption,
            'fol': nut_followup,
            'register': nut_register,
            'research': nut_search,
            'off': nut_disable}

        if message.content.lower().startswith('nut '):
            for cmd_id, cmd_target in commands.items():
                command = '%s %s' % (keyword, cmd_id)
                if message.content.lower().startswith(command):
                    n, args = re.split(r'^%s\s?' \
                                       % command, \
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


def resp_error(message, action):
    message.respond(u"[ERREUR] Impossible de comprendre le SMS pour %s"
                                                               % action)
    return True


def nut_register(message, args, sub_cmd, cmd):
    """ Incomming:
            nut register code_health_center first_name last_name
            surname_mother sex birth_date #weight height oed pb nbr
        Outgoing:
            [SUCCES] Le rapport de name_health_center a ete enregistre.
            Son id est 8.
            or  [ERREUR] Votre rapport n'a pas été enregistrer"""

    try:
        register_data, follow_up_data = args.split('#')

        hc_code, first_name, last_name, mother, \
                                        sex, dob = register_data.split()
        weight, height, oedema, muac, \
                                nb_plumpy_nut = follow_up_data.split()
    except:
        return resp_error(message, u"enregistrement")
    try:
        # On essai prendre le seat
        hc = HealthCenter.objects.get(code=hc_code)
    except:
        # On envoi un sms pour signaler que le code n'est pas valide
        message.respond(u"[ERREUR] %(hc)s n'est pas un code de Centre "
                        u"valide." % {'hc': hc_code})
        return True

    # creating the patient record
    patient = Patient()
    patient.first_name = first_name.replace('_', ' ').title()
    patient.last_name = last_name.replace('_', ' ').title()
    patient.surname_mother = mother.replace('_', ' ').title()
    patient.birth_date = date(*[int(v) for v in dob.split('-')])
    patient.create_date = date.today()
    patient.sex = sex.upper()
    patient.health_center = hc
    try:
        patient.save()
    except:
        return resp_error(message, u"enregistrement")

    # adding patient to the program
    programio = ProgramIO()
    programio.patient = patient
    programio.event = programio.SUPPORT
    programio.date = date.today()
    programio.save()

    # creating a followup event
    weight = float(weight)
    height = int(height)
    oedema = {'yes': DataNut.OEDEMA_YES,
              'no': DataNut.OEDEMA_NO,
              'unknown': DataNut.OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) \
                              if not nb_plumpy_nut.lower() == '-' else 0
    datanut = add_followup_data(patient=patient, weight=weight,
                                height=height,
                                oedema=oedema, muac=muac,
                                nb_plumpy_nut=nb_plumpy_nut)
    if not datanut:
        message.respond(u"/!\ %(full_name)s enregistre avec ID#%(id)d."
                        u" Donnees nutrition non enregistres."
                        % {'full_name': patient.full_name(),
                           'id': patient.id})
        return True

    message.respond(u"[SUCCES] %(full_name)s enregistre avec ID#%(id)d."
                    u" Donnees nutrition enregistres." \
                    % {'full_name': patient.full_name_mother(),
                       'id': patient.id})
    return True


def add_followup_data(**kwargs):
    try:
        datanut = DataNut(**kwargs)
        datanut.save()
        return datanut
    except:
        return None


def nut_followup(message, args, sub_cmd, cmd):
    """ Incomming:
            nut fol id_patient weight height oedema muac
             nb_plumpy_nut(optional)
             danger_sign(optional)
        Outgoing:
            [SUCCES] Les donnees nutritionnelles de full_name ont
            ete bien enregistre.
            or error message """

    try:
        patient_id, weight, height, oedema, \
                                      muac, nb_plumpy_nut = args.split()
    except:
        return resp_error(message, u"suivi")

    try:
        patient = Patient.objects.get(id=int(patient_id))
    except:
        message.respond(u"[ERREUR] Aucun patient trouve pour ID#%s" %
                                                             patient_id)
        return True

    if patient.last_data_event().event == ProgramIO.OUT:
        message.respond(u"[ERREUR] ce patient n'est plus dans le programme")
        return True

    # creating a followup event
    weight = float(weight)
    height = int(height)
    oedema = {'yes': DataNut.OEDEMA_YES,
              'no': DataNut.OEDEMA_NO,
              'unknown': DataNut.OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) \
                              if not nb_plumpy_nut.lower() == '-' else 0
    datanut = add_followup_data(patient=patient, weight=weight,
                                height=height, oedema=oedema,
                                muac=muac, nb_plumpy_nut=nb_plumpy_nut)
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
            example 1: nut research pmib iba Fad Diarra
            example 2: nut research pmib - Fad Diarra "Si le first_name vide"
            example 3: nut research pmib - Fad n
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
        message.respond(u"[ERREUR] %(hc)s n'est pas un code de Centre "
                        u"valide." % {'hc': hc_code})
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
        return fmt % {'id': p.id,
                      'first': p.first_name.title(),
                      'last': p.last_name.title(),
                      'mother': p.surname_mother.title()}

    if not len(patients.all()):
        message.respond(u"[ERREUR] Pas de patient trouve. "
                        u"Essayez une recherche plus large.")
        return True

    msg = u"[SUCCES] %d trouves: %s" % (len(patients.all()),
          ", ".join([display_name(patient, fmt)
                for patient in patients.all()]))
    message.respond(msg[:160])
    return True


def nut_disable(message, args, sub_cmd, cmd):
    """  Incomming:
            nut off id_patient reason
            example reason: (a= abandon, t = transfer ...)
         Outgoing:
            [SUCCES] full_name ne fait plus partie du programme.
            or error message """

    try:
        patient_id, reason = args.split()
    except:
        return resp_error(message, u"OUTe")
    try:
        patient = Patient.objects.get(id=patient_id)
    except:
        message.respond(u"[ERREUR] Aucun patient trouve pour ID#%s" \
                                                            % patient_id)
        return True

    programio = ProgramIO()
    programio.patient = patient
    programio.event = programio.OUT
    programio.reason = reason
    programio.date = date.today()
    programio.save()
    message.respond(u"[SUCCES] %(full_name)s ne fait plus partie "
                    u"du programme." %
                    {'full_name': patient.full_name()})
    return True


def nut_consumption(message, args, sub_cmd, cmd):
    """ Incomming:
            nut stock type_health_center code_health_center month year
             #input_type initial received used received #input_type initial
            received used received
            example: nut stock URENAM pmib 1 2012 #nie 11 22 18 2
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
        message.respond(u"[ERREUR] %(hc)s n'est pas un code de Centre "
                        u"valide." % {'hc': hc_code})
        return True

    try:
        period = MonthPeriod.find_create_from(year=int(year),
                                              month=int(month))
    except:
        message.respond(u"[ERREUR] %s-%s n'est pas une periode valide."
                        % (month, year))
        return True

    now_period = MonthPeriod.find_create_by_date(date.today())
    if period != now_period.previous():
        message.respond(u"[ERREUR] Impossible d'enregistrer le rapport"
                        u"de conso pour %s. Envoyez pour %s"
                        % (period.full_name(), now_period.previous() \
                                                         .full_name()))
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

        if ConsumptionReport.objects.filter(period=period, \
                                            health_center=hc, \
                                            input_type=input_type).count():
            cr = ConsumptionReport.objects.get(period=period, \
                                               health_center=hc, \
                                               input_type=input_type)
        else:
            cr = ConsumptionReport(period=period, health_center=hc, \
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
        message.respond(u"[ERREUR] %d rapport de conso en erreur."
                        u" Verifiez toutes les donnees et renvoyez -- %s"
                                        % (len(error), ', '.join(errors)))
        return True

    message.respond(u"[SUCCES] %d rapports de conso enregistres pour %s."
                                        % (len(success), period.full_name()))
    return True
