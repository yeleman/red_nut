# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NutritionalData.is_ureni'
        db.add_column('nut_nutritionaldata', 'is_ureni',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NutritionalData.is_ureni'
        db.delete_column('nut_nutritionaldata', 'is_ureni')


    models = {
        'nut.consumptionreport': {
            'Meta': {'object_name': 'ConsumptionReport'},
            'health_center': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'consumption_reports'", 'to': "orm['nut.HealthCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'input_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'consumption_reports'", 'to': "orm['nut.Input']"}),
            'lost': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'consumption_reports'", 'to': "orm['nut.Period']"}),
            'received': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'used': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'nut.healthcenter': {
            'Meta': {'object_name': 'HealthCenter'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'nut_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nut.HealthCenter']", 'null': 'True', 'blank': 'True'})
        },
        'nut.input': {
            'Meta': {'object_name': 'Input'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        'nut.nutritionaldata': {
            'Meta': {'ordering': "('date',)", 'object_name': 'NutritionalData'},
            'danger_sign': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 10, 5, 0, 0)'}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ureni': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'muac': ('django.db.models.fields.SmallIntegerField', [], {}),
            'nb_plumpy_nut': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'oedema': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nutritional_data'", 'to': "orm['nut.Patient']"}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        },
        'nut.patient': {
            'Meta': {'ordering': "('create_date',)", 'object_name': 'Patient'},
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 5, 0, 0)'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'health_center': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patients'", 'to': "orm['nut.HealthCenter']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'nut_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'surname_mother': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'nut.period': {
            'Meta': {'unique_together': "(('start_on', 'end_on', 'period_type'),)", 'object_name': 'Period'},
            'end_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'custom'", 'max_length': '15'}),
            'start_on': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nut.programio': {
            'Meta': {'ordering': "('date',)", 'object_name': 'ProgramIO'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 5, 0, 0)'}),
            'event': ('django.db.models.fields.CharField', [], {'default': "'e'", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'programios'", 'to': "orm['nut.Patient']"}),
            'reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['nut']