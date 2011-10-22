#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from datetime import date
from django.utils.translation import ugettext
import models

MONTH_CHOICES = (('01', ugettext('Jan')), ('02', ugettext('Feb')), ('03', ugettext('Mar')), ('04', ugettext('Apr')),
                 ('05', ugettext('May')), ('06', ugettext('Jun')), ('07', ugettext('Jul')), ('08', ugettext('Aug')),
                 ('09', ugettext('Sep')), ('10', ugettext('Oct')), ('11', ugettext('Nov')), ('12', ugettext('Dec')))
YEAR_CHOICES = []
for year in range(date.today().year, date.today().year+15):
    YEAR_CHOICES.append((year, year))

class AbstractIPaymentForm(forms.Form):
    """
    Form used to transfer customer data from a shop template to IPayment via Silent-CGI.
    """
    shopper_id = forms.IntegerField(widget=forms.HiddenInput)
    advanced_strict_id_check = forms.IntegerField(widget=forms.HiddenInput)
    invoice_text = forms.CharField(widget=forms.HiddenInput)
    error_lang = forms.CharField(widget=forms.HiddenInput)
    silent = forms.IntegerField(widget=forms.HiddenInput)
    addr_name = forms.CharField()
    cc_expdate_month = forms.ChoiceField(choices=MONTH_CHOICES)
    cc_expdate_year = forms.ChoiceField(choices=YEAR_CHOICES)

class SessionIPaymentForm(AbstractIPaymentForm):
    """
    Form with additional sensible fields, which are not used when a sessionId is used.
    """
    ipayment_session_id = forms.CharField(widget=forms.HiddenInput)

class SensibleIPaymentForm(AbstractIPaymentForm):
    """
    Form with additional sensible fields, which are not used when a sessionId is used.
    """
    trxuser_id = forms.CharField(widget=forms.HiddenInput)
    trxpassword = forms.CharField(widget=forms.HiddenInput)
    trx_amount = forms.IntegerField(widget=forms.HiddenInput) # in cents
    trx_currency = forms.CharField(widget=forms.HiddenInput)
    trx_paymenttyp = forms.CharField(widget=forms.HiddenInput)
    redirect_url = forms.CharField(widget=forms.HiddenInput)
    silent_error_url = forms.CharField(widget=forms.HiddenInput)
    hidden_trigger_url = forms.CharField(widget=forms.HiddenInput)
    trx_securityhash = forms.CharField(widget=forms.HiddenInput)

class ConfirmationForm(forms.ModelForm):
    """
    Form holding confirmation data sent by IPayment when a payment was successful.
    """
    class Meta:
        model = models.Confirmation

