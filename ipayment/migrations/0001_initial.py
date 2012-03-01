# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Confirmation'
        db.create_table('ipayment_confirmation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shopper_id', self.gf('django.db.models.fields.IntegerField')()),
            ('vendor_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ret_booknr', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_errorcode', self.gf('django.db.models.fields.IntegerField')()),
            ('trx_paymentmethod', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_trx_number', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_transdatetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('ret_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('trx_typ', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('addr_name', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('trx_amount', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=12, decimal_places=2)),
            ('trx_remoteip_country', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('trx_currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('ret_authcode', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('trx_paymenttyp', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('ret_status', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('trxuser_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('ipayment', ['Confirmation'])


    def backwards(self, orm):
        
        # Deleting model 'Confirmation'
        db.delete_table('ipayment_confirmation')


    models = {
        'ipayment.confirmation': {
            'Meta': {'object_name': 'Confirmation'},
            'addr_name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ret_authcode': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'ret_booknr': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'ret_errorcode': ('django.db.models.fields.IntegerField', [], {}),
            'ret_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'ret_status': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'ret_transdatetime': ('django.db.models.fields.DateTimeField', [], {}),
            'ret_trx_number': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'shopper_id': ('django.db.models.fields.IntegerField', [], {}),
            'trx_amount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'trx_currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'trx_paymentmethod': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'trx_paymenttyp': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'trx_remoteip_country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'trx_typ': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'trxuser_id': ('django.db.models.fields.IntegerField', [], {}),
            'vendor_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ipayment']
