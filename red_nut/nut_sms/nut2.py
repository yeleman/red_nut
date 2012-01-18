
from nosmsd.utils import send_sms

from red_nut.nut.models import *
from red_nut.nut.models.Period import MonthPeriod

from datetime import date

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def handler(message):
    """ NUT SMS router """
    def main_nut_handler(message):
        keyword = 'nut'
        commands = {
            'stock': nut_stock,
            'fol': nut_followup,
            'register': nut_register,
            'research': nut_search,
            'off': nut_disable}

        if message.text.lower().startswith('nut '):
            for cmd_id, cmd_target in commands.items():
                command = '%s %s' % (keyword, cmd_id)
                if message.text.lower().startswith(command):
                    n, args = re.split(r'^%s\s?' \
                                       % command, message.text.lower().strip())
                    return cmd_target(message,
                                      args=args,
                                      sub_cmd=cmd_id,
                                      cmd=command)
        else:
            return False

    if main_nut_handler(message):
        message.status = Message.STATUS_PROCESSED
        message.save()
        logger.info(u"[HANDLED] msg: %s" % message)
        return True
    logger.info(u"[NOT HANDLED] msg : %s" % message)
    return False


def resp_error(message, action):
    message.respond(u"[ERREUR] Impossible de comprendre le SMS pour %s" % action)
    return True


def nut_register(message, args, sub_cmd, cmd):
    """ Incomming:
            nut register code_health_center first_name last_name
            surname_mother sex birth_date #weight height oed pb nbr
        Outgoing:
            [SUCCES] Le rapport de name_health_center a ete enregistre. Son id est 8.
            or  [ERREUR] Votre rapport n'a pas été enregistrer"""

    try:
        register_data, follow_up_data = args.split('#')

        hc_code, first_name, last_name, mother, sex, dob = register_data.split()
        weight, height, oedema, muac, nb_plumpy_nut = follow_up_data.split()
    except:
        return resp_error(message, u"enregistrement")


    try:
        # On essai prendre le seat
        hc = HealthCenter.objects.get(code=hc_code)
    except:
        # On envoi un sms pour signaler que le code n'est pas valid
        message.respond(u"[ERREUR] %(hc)s n'est pas un code de Centre "
                        u"valide." % {'hc': hc_code})
        return True

    # creating the patient record
    patient = Patient()
    patient.first_name = first_name
    patient.last_name = last_name
    patient.surname_mother = mother
    patient.birth_date = date(*[int(v) for v in dob.split('-')])
    patient.create_date = date.today()
    patient.sex = sex.upper()
    patient.health_center = hc
    try:
        patient.save()
    except:
        return resp_error(message, u"enregistrement")

    # adding patient to the program
    programio = ProgramIO() # ProgramIO
    programio.patient = patient
    programio.event = programio.EN_CHARGE
    programio.date = datetime.today()
    programio.save()

    # creating a followup event
    weight = float(weight)
    height = int(height)
    oedema = {'yes': DataNut.OEDEMA_YES,
              'no': OEDEMA_NO,
              'unknown': OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) if not nb_plumpy_nut.lower() == '-' else 0
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


def add_followup_data(**kwargs)
    try:
        datanut = DataNut(**kwargs)
        datanut.save()
        return datanut
    except:
        return None


def nut_followup(message, args, sub_cmd, cmd):
    """ Incomming:
            nut fol id_patient weight height oedema muac nb_plumpy_nut(optional)
             danger_sign(optional)
        Outgoing:
            [SUCCES] Les donnees nutritionnelles de full_name ont
            ete bien enregistre.
            or error message """

    try:
        patient_id, weight, height, oedema, muac, nb_plumpy_nut = args.split()
    except:
        return resp_error(message, u"suivi")

    try:
        patient = Patient.objects.get(id=int(patient_id))
    except:
        message.respond(u"[ERREUR] Aucun patient trouve pour ID#%s" % patient_id)
        return True

    # creating a followup event
    weight = float(weight)
    height = int(height)
    oedema = {'yes': DataNut.OEDEMA_YES,
              'no': OEDEMA_NO,
              'unknown': OEDEMA_UNKNOWN}[oedema.lower()]
    muac = int(muac)
    nb_plumpy_nut = int(nb_plumpy_nut) if not nb_plumpy_nut.lower() == '-' else 0
    datanut = add_followup_data(patient=patient, weight=weight,
                                height=height,
                                oedema=oedema, muac=muac,
                                nb_plumpy_nut=nb_plumpy_nut)
    if not datanut:
        return resp_error(message, u"suivi")

    message.respond(u"[SUCCES] Donnees nutrition enregistres pour %(full_name)s" \
                    % {'full_name': patient.full_name_id()})
    return True


def nut_search(message, args, sub_cmd, cmd):
    """ Incomming:
            nut research code_health_center first_name(op) last_name(op)
             surname_mother(op)
            None = n
        Outgoing:
            Il existe nbr de resultat patient(s) du prénom first_name: last_name
            surname_mother de l'id 7, last_name surname_mother de l'id 8.
            or  Il n'existe aucun patient du prénom first_name """


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
        return resp_error(message, u"sorti")
    try:
        patient = Patient.objects.get(id=patient_id)
    except:
        message.respond(u"[ERREUR] Aucun patient trouve pour ID#%s" \
                                                            % patient_id)
        return True

    programio = ProgramIO()
    programio.patient = patient
    programio.event = programio.SORTI
    programio.reason = reason
    programio.date = datetime.today()
    programio.save()
    message.respond(u"[SUCCES] %(full_name)s ne fait plus partie "
                    u"du programme." %
                    {'full_name': patient.full_name()})
    return True


def nut_stock(message, args, sub_cmd, cmd):
    """ Incomming:
            nut stock type_health_center code_health_center month year #intrant stock_initial
            stock_received stock_used stock_lost #intrant stock_initial
            stock_received stock_used stock_lost
        Outgoing:
            [SUCCES] Le rapport de stock de health_center a ete bien enregistre.
            or error message """
