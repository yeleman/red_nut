# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Period'
        db.create_table('nut_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_type', self.gf('django.db.models.fields.CharField')(default='custom', max_length=15)),
        ))
        db.send_create_signal('nut', ['Period'])

        # Adding unique constraint on 'Period', fields ['start_on', 'end_on', 'period_type']
        db.create_unique('nut_period', ['start_on', 'end_on', 'period_type'])

        # Adding model 'Input'
        db.create_table('nut_input', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('unit', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
        ))
        db.send_create_signal('nut', ['Input'])

        # Adding model 'HealthCenter'
        db.create_table('nut_healthcenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('nut_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nut.HealthCenter'], null=True, blank=True)),
        ))
        db.send_create_signal('nut', ['HealthCenter'])

        # Adding model 'NutritionalData'
        db.create_table('nut_nutritionaldata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nutritional_data', to=orm['nut.Patient'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 10, 5, 0, 0))),
            ('weight', self.gf('django.db.models.fields.FloatField')()),
            ('height', self.gf('django.db.models.fields.FloatField')()),
            ('oedema', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('muac', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('danger_sign', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('nb_plumpy_nut', self.gf('django.db.models.fields.IntegerField')(max_length=30, null=True, blank=True)),
        ))
        db.send_create_signal('nut', ['NutritionalData'])

        # Adding model 'Patient'
        db.create_table('nut_patient', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nut_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('surname_mother', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('health_center', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patients', to=orm['nut.HealthCenter'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 10, 5, 0, 0))),
            ('birth_date', self.gf('django.db.models.fields.DateField')()),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('nut', ['Patient'])

        # Adding model 'ProgramIO'
        db.create_table('nut_programio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 10, 5, 0, 0))),
            ('event', self.gf('django.db.models.fields.CharField')(default='e', max_length=30)),
            ('reason', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='programios', to=orm['nut.Patient'])),
        ))
        db.send_create_signal('nut', ['ProgramIO'])

        # Adding model 'ConsumptionReport'
        db.create_table('nut_consumptionreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('health_center', self.gf('django.db.models.fields.related.ForeignKey')(related_name='consumption_reports', to=orm['nut.HealthCenter'])),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(related_name='consumption_reports', to=orm['nut.Period'])),
            ('input_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='consumption_reports', to=orm['nut.Input'])),
            ('initial', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('received', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('used', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('lost', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('nut', ['ConsumptionReport'])


    def backwards(self, orm):
        # Removing unique constraint on 'Period', fields ['start_on', 'end_on', 'period_type']
        db.delete_unique('nut_period', ['start_on', 'end_on', 'period_type'])

        # Deleting model 'Period'
        db.delete_table('nut_period')

        # Deleting model 'Input'
        db.delete_table('nut_input')

        # Deleting model 'HealthCenter'
        db.delete_table('nut_healthcenter')

        # Deleting model 'NutritionalData'
        db.delete_table('nut_nutritionaldata')

        # Deleting model 'Patient'
        db.delete_table('nut_patient')

        # Deleting model 'ProgramIO'
        db.delete_table('nut_programio')

        # Deleting model 'ConsumptionReport'
        db.delete_table('nut_consumptionreport')


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
            'muac': ('django.db.models.fields.SmallIntegerField', [], {}),
            'nb_plumpy_nut': ('django.db.models.fields.IntegerField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'oedema': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nutritional_data'", 'to': "orm['nut.Patient']"}),
            'weight': ('django.db.models.fields.FloatField', [], {})
        },
        'nut.patient': {
            'Meta': {'object_name': 'Patient'},
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