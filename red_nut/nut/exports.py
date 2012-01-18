#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

import xlwt
import StringIO

def report_as_excel(stocks, patients, datanuts):
    """ Export les données du stock en xls """
    # On crée le doc xls
    book = xlwt.Workbook(encoding='utf-8')
    if stocks:
        # On crée une feuille nommé Stocks
        sheet = book.add_sheet(u"Stocks")

        sheet.write_merge(0, 0, 0, 12, u"Tableau des consomations d'intrants.")
        sheet.write(1, 0, u"CSCOM")
        sheet.write(1, 1, stocks[0].health_center.name)
        sheet.write(3, 0, u"Intrant")
        sheet.write(3, 1, u"Initial")
        sheet.write(3, 2, u"Reçu")
        sheet.write(3, 3, u"Utilsé")
        sheet.write(3, 4, u"Perdu")
        sheet.write(3, 5, u"Restant")
        sheet.write(3, 6, u"Période")
        i = 4
        for stock in stocks:
            sheet.write(i, 0, stock.input_type.name)
            sheet.write(i, 1, stock.initial)
            sheet.write(i, 2, stock.received)
            sheet.write(i, 3, stock.used)
            sheet.write(i, 4, stock.lost)
            sheet.write(i, 5, stock.remaining())
            sheet.write(i, 6, stock.period.full_name())
            i += 1
    if patients or datanuts:
        # On crée une feuille nommé patients
        sheet_patient = book.add_sheet(u"patients")
        # J'agrandi les colonne à trois fois la normale.
        sheet_patient.col(0).width = 0x0d00 * 3
        sheet_patient.col(1).width = 0x0d00 * 3
        sheet_patient.col(2).width = 0x0d00 * 3
        sheet_patient.col(5).width = 0x0d00 * 2
        sheet_patient.col(6).width = 0x0d00 * 2
        sheet_patient.col(7).width = 0x0d00 * 2
        sheet_patient.col(10).width = 0x0d00 * 2

        sheet_patient.write_merge(0, 0, 0, 11, u"Liste des patients.")
        sheet_patient.write(2, 0, u"CSCOM")
        sheet_patient.write(4, 0, u"Nom")
        sheet_patient.write(4, 1, u"Prénom")
        sheet_patient.write(4, 2, u"Mère")
        sheet_patient.write(4, 3, u"DDN")
        sheet_patient.write(4, 4, u"Sexe")
        sheet_patient.write(4, 5, u"Date d'enregistrement")
        sheet_patient.write(4, 6, u"Dernier status")
        sheet_patient.write(4, 7, u"Derniere visite")
        sheet_patient.write(4, 8, u"Poids")
        sheet_patient.write(4, 9, u"Taille")
        sheet_patient.write(4, 10, u"Perimètre brachial")
        sheet_patient.write(4, 11, u"Oedème")
        i = 5
        for patient in patients:
            datanut_patients = datanuts.filter(patient__id=patient.id) \
                                      .order_by('date')
            sheet_patient.write(i, 0, patient.last_name)
            sheet_patient.write(i, 1, patient.first_name)
            sheet_patient.write(i, 2, patient.surname_mother)
            sheet_patient.write(i, 3, patient.birth_date.strftime("%d %b %Y"))
            sheet_patient.write(i, 4, patient.sex)
            sheet_patient.write(i, 5, patient.create_date.strftime("%d %b %Y"))
            sheet_patient.write(i, 6, patient.last_data_event().get_event_display())
            sheet_patient.write(i, 7, patient.last_visit().strftime("%d %b %Y"))
            sheet_patient.write(i, 8, patient.last_data_nut().weight)
            sheet_patient.write(i, 9, patient.last_data_nut().height)
            sheet_patient.write(i, 10, patient.last_data_nut().muac)
            sheet_patient.write(i, 11, patient.last_data_nut().get_oedema_display())
            i += 1
            if datanut_patients:
                for data in datanut_patients:
                    sheet_patient.write(i, 7, patient.last_visit().strftime("%d %b %Y"))
                    sheet_patient.write(i, 8, patient.last_data_nut().weight)
                    sheet_patient.write(i, 9, patient.last_data_nut().height)
                    sheet_patient.write(i, 10, patient.last_data_nut().muac)
                    sheet_patient.write(i, 11, patient.last_data_nut().get_oedema_display())
                    i += 1

    stream = StringIO.StringIO()
    book.save(stream)

    return stream
