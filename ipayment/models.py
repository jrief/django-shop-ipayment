#-*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from shop.util.fields import CurrencyField

class Confirmation(models.Model):
    """
    Model to store every confirmation for successful or failed payments. 
    """
    class Meta:
        verbose_name = _('IPayment Confirmation')

    shopper_id = models.IntegerField()
    vendor_comment = models.TextField(null=True, blank=True)
    ret_booknr = models.CharField(max_length=63, )
    ret_errorcode = models.IntegerField()
    trx_paymentmethod = models.CharField(max_length=63)
    ret_trx_number = models.CharField(max_length=63)
    ret_transdatetime = models.DateTimeField()
    ret_ip = models.IPAddressField()
    trx_typ = models.CharField(max_length=63)
    addr_name = models.CharField(max_length=63, verbose_name='Cardholder name')
    trx_amount = CurrencyField()
    trx_remoteip_country = models.CharField(blank=True, max_length=2)
    trx_currency = models.CharField(max_length=4)
    ret_authcode = models.CharField(blank=True, max_length=63)
    trx_paymenttyp = models.CharField(max_length=63)
    ret_status = models.CharField(max_length=63)
    trxuser_id = models.IntegerField()
