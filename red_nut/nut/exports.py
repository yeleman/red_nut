#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

import xlwt
import StringIO
from nut.models import ConsumptionReport, HealthCenter, Patient, DataNut
def report_as_excel(health_centers):
    """ Export les données du stock en xls """
    # On crée le doc xls
    book = xlwt.Workbook(encoding='utf-8')
    # On crée les feuilles
    sheet = book.add_sheet(u"Consommations")
    sheet_patient = book.add_sheet(u"Enfants")

    # J'agrandi les colonnes.
    sheet_patient.col(1).width = 0x0d00 * 2
    sheet_patient.col(2).width = 0x0d00 * 3
    sheet_patient.col(3).width = 0x0d00 * 3
    sheet_patient.col(4).width = 0x0d00 * 2
    sheet_patient.col(7).width = 0x0d00 * 2
    sheet_patient.col(8).width = 0x0d00 * 2
    sheet_patient.col(9).width = 0x0d00 * 2
    sheet_patient.col(12).width = 0x0d00 * 2
    sheet.col(1).width = 0x0d00 * 2

    i = 0
    i_ = 0

    #entete consommation d'intrant
    sheet.write(i, 0, u"Code")
    sheet.write(i, 1, u"CSCOM")
    sheet.write(i, 2, u"Intrant")
    sheet.write(i, 3, u"Initial")
    sheet.write(i, 4, u"Reçu")
    sheet.write(i, 5, u"Utilsé")
    sheet.write(i, 6, u"Perdu")
    sheet.write(i, 7, u"Restant")
    sheet.write(i, 8, u"Période")

    #entete liste des enfants

    sheet_patient.write(i_, 0, u"ID")
    sheet_patient.write(i_, 1, u"CSCOM")
    sheet_patient.write(i_, 2, u"Nom")
    sheet_patient.write(i_, 3, u"Prénom")
    sheet_patient.write(i_, 4, u"Mère")
    sheet_patient.write(i_, 5, u"DDN")
    sheet_patient.write(i_, 6, u"Sexe")
    sheet_patient.write(i_, 7, u"Date d'enregistrement")
    sheet_patient.write(i_, 8, u"Dernier status")
    sheet_patient.write(i_, 9, u"Derniere visite")
    sheet_patient.write(i_, 10, u"Poids")
    sheet_patient.write(i_, 11, u"Taille")
    sheet_patient.write(i_, 12, u"Perimètre brachial")
    sheet_patient.write(i_, 13, u"Oedème")
    sheet_patient.write(i_, 14, u"date de visite")

    for health_center in health_centers:
        consumptionreports = ConsumptionReport.objects\
                                        .filter(health_center=health_center)
        if consumptionreports:
            for stock in consumptionreports:
                i += 1
                sheet.write(i, 0, stock.health_center.code)
                sheet.write(i, 1, stock.health_center.name)
                sheet.write(i, 2, stock.input_type.name)
                sheet.write(i, 3, stock.initial)
                sheet.write(i, 4, stock.received)
                sheet.write(i, 5, stock.used)
                sheet.write(i, 6, stock.lost)
                sheet.write(i, 7, stock.remaining())
                sheet.write(i, 8, stock.period.full_name())

        patients = Patient.objects.filter(health_center=health_center)
        datanuts = DataNut.objects.filter(patient__health_center=health_center)
        if patients:
            for patient in patients:
                i_ += 1
                datanut_patients = datanuts.filter(patient__id=patient.id) \
                                          .order_by('date')
                sheet_patient.write(i_, 0, patient.id)
                sheet_patient.write(i_, 1, patient.health_center.name)
                sheet_patient.write(i_, 2, patient.last_name)
                sheet_patient.write(i_, 3, patient.first_name)
                sheet_patient.write(i_, 4, patient.surname_mother)
                sheet_patient.write(i_, 5, patient.birth_date\
                                                  .strftime("%d/%m/%Y"))
                sheet_patient.write(i_, 6, patient.sex)
                sheet_patient.write(i_, 7, patient.create_date\
                                                  .strftime("%d/%m/%Y"))
                sheet_patient.write(i_, 8, patient.last_data_event()\
                                                  .event)
                sheet_patient.write(i_, 9, patient.last_visit()\
                                                  .strftime("%d/%m/%Y"))
                sheet_patient.write(i_, 10, patient.last_data_nut().weight)
                sheet_patient.write(i_, 11, patient.last_data_nut().height)
                sheet_patient.write(i_, 12, patient.last_data_nut().muac)
                sheet_patient.write(i_, 13,patient.last_data_nut()\
                                                  .oedema)
                if datanut_patients:
                    for data in datanut_patients:
                        if data != patient.last_data_nut():
                            i_ += 1
                            sheet_patient.write(i_, 0,\
                                        patient.last_data_nut()\
                                        .patient.id)
                            sheet_patient.write(i_, 9,\
                                        patient.last_data_nut()\
                                        .date.strftime("%d/%m/%Y"))
                            sheet_patient.write(i_, 10,\
                                        patient.last_data_nut().weight)
                            sheet_patient.write(i_, 11,
                                        patient.last_data_nut().height)
                            sheet_patient.write(i_, 12,
                                        patient.last_data_nut().muac)
                            sheet_patient.write(i_, 13,
                                    patient.last_data_nut()\
                                    .oedema)
                            sheet_patient.write(i_, 14,
                                    patient.last_data_nut()\
                                    .date.strftime("%d/%m/%Y"))
    stream = StringIO.StringIO()
    book.save(stream)

    return stream
