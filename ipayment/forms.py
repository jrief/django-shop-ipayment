# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from django import forms
from datetime import date
import models


MONTH_CHOICES = (
    ('01', _('Jan')), ('02', _('Feb')), ('03', _('Mar')), ('04', _('Apr')),
    ('05', _('May')), ('06', _('Jun')), ('07', _('Jul')), ('08', _('Aug')),
    ('09', _('Sep')), ('10', _('Oct')), ('11', _('Nov')), ('12', _('Dec'))
)
YEAR_CHOICES = []
for year in range(date.today().year, date.today().year+15):
    YEAR_CHOICES.append((year, year))


class AbstractIPaymentForm(forms.Form):
    """
    Form used to transfer customer data from a shop template to IPayment via Silent-CGI.
    """
    shopper_id = forms.IntegerField(widget=forms.HiddenInput)
    advanced_strict_id_check = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    invoice_text = forms.CharField(widget=forms.HiddenInput)
    error_lang = forms.CharField(widget=forms.HiddenInput, initial='en')
    silent = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    addr_name = forms.CharField(label=_('Cardholder name'))
    cc_number = forms.CharField(label=_('Credit card number'))
    cc_checkcode = forms.CharField(label=_('Check code'))
    cc_expdate_month = forms.ChoiceField(choices=MONTH_CHOICES, label=_('Card expire month'))
    cc_expdate_year = forms.ChoiceField(choices=YEAR_CHOICES, label=_('Card expire year'))


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

