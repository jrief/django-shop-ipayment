#-*- coding: utf-8 -*-
from datetime import datetime
import hashlib

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render_to_response
from django.template import Context, Template, RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt

import logging
import traceback
import forms

class OffsiteIPaymentBackend(object):
    '''
    Glue code to let django-SHOP talk to the ipayment backend.
    '''
    backend_name = "IPayment"
    url_namespace = "ipayment"
    ALLOWED_CONFIRMERS = ('212.227.34.218', '212.227.34.219', '212.227.34.220', '127.0.0.1')
    
    #===========================================================================
    # Defined by the backends API
    #===========================================================================
    
    def __init__(self, shop):
        self.shop = shop
        self.logger = logging.getLogger(__name__)
        assert type(settings.IPAYMENT).__name__=='dict', "You need to configure IPAYMENT in settings"
        
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.view_that_asks_for_money, name='ipayment'),
            url(r'^error$', self.view_that_asks_for_money, name='ipayment_error'),
            url(r'^success$', self.ipayment_return_success_view, name='ipayment_success'),
            url(r'^hidden$', self.payment_was_successful, name='ipayment_hidden'),
        )
        return urlpatterns
    
    #===========================================================================
    # Views
    #===========================================================================
    
    def view_that_asks_for_money(self, request):
        '''
        Show this form to ask for the customers credit cards content. This content shall never be
        transferred to the local server, instead it is send directly to the IPayment server.
        '''
        if request.method != 'GET':
            return HttpResponseBadRequest()

        order = self.shop.get_order(request)
        ipaymentConf = settings.IPAYMENT.copy() 
        ipaymentConf['trx_amount'] = int(self.shop.get_order_total(order)*100)
        ipaymentConf['silent'] = 1
        ipaymentConf['shopper_id'] = self.shop.get_order_unique_id(order)
        ipaymentConf['advanced_strict_id_check'] = 1
        ipaymentConf['invoice_text'] = self.shop.get_order_short_name(order) # more creativity here!

        # determine return addresses
        url_scheme = 'https://' if request.is_secure() else 'http://'
        url_domain = get_current_site(request).domain
        ipaymentConf['redirect_url'] = url_scheme + url_domain + reverse('ipayment_success')
        ipaymentConf['silent_error_url'] = url_scheme + url_domain + reverse('ipayment_error')
        ipaymentConf['hidden_trigger_url'] = url_scheme + url_domain + reverse('ipayment_hidden')

        # Create the form content
        extra = { 'accountID': settings.IPAYMENT['accountID'], 'isError': False, 'securityHash': self.calcTrxSecurityHash(ipaymentConf), }
        if request.GET.has_key('ret_errorcode') and int(request.GET['ret_errorcode'])>0:
            extra['isError'] = True
            extra['errorMessage'] = request.GET['ret_errormsg']
            ipaymentConf['addr_name'] = request.GET['addr_name']
        context = { 'form': forms.CustomerForm(ipaymentConf), 'extra': extra }
        rc = RequestContext(request, context)
        return render_to_response("payment.html", rc)
    
    def ipayment_return_success_view(self, request):
        if request.method != 'GET':
            return HttpResponseBadRequest()
        self.logger.debug('ipayment_return_success_view')
        return render_to_response("success.html", {})
    
    #===========================================================================
    # Handlers, which process POST data from IPayment
    #===========================================================================
    
    @csrf_exempt
    def payment_was_successful(self, request):
        '''
        This listens to a confirmation sent by one of the IPayment servers.
        It is not intended to display any useful information to the client.
        '''
        if request.method != 'POST':
            return HttpResponseBadRequest()
        try:
            # assert that this request is not forged 
            if request.META['REMOTE_ADDR'] == '127.0.0.1' and self.ALLOWED_CONFIRMERS.count(request.META['HTTP_X_FORWARDED_FOR']) == 0 or self.ALLOWED_CONFIRMERS.count(request.META['REMOTE_ADDR']) == 0:
                raise SuspiciousOperation('Request invoked from suspicious IP address %s' % request.META['REMOTE_ADDR'])
            post = request.POST.copy()
            if post.has_key('trx_amount'):
                post['trx_amount'] = float(post['trx_amount'])/100.0
            if post.has_key('ret_transdate') and post.has_key('ret_transtime'):
                post['ret_transdatetime'] = datetime.strptime(post['ret_transdate']+" "+post['ret_transtime'], "%d.%m.%y %H:%M:%S")
            confirmation = forms.ConfirmationForm(post)
            if not confirmation.is_valid():
                raise SuspiciousOperation('Confirmation by IPayment rejected: POST data does not contain all expected fields.')
            if not self.checkRetParamHash(request.POST):
                raise SuspiciousOperation('Confirmation by IPayment rejected: Attempt to send manipulated POST data.')
            confirmation.save()
            order = self.shop.get_order_for_id(confirmation.cleaned_data['shopper_id'])
            self.logger.info('IPayment for %s returned %s', order, confirmation.cleaned_data['ret_status'])
            if confirmation.cleaned_data['ret_status'] == 'SUCCESS':
                self.shop.confirm_payment(order, confirmation.cleaned_data['trx_amount'], confirmation.cleaned_data['ret_trx_number'], self.backend_name)
            template = Template("OK")
            return HttpResponse(template.render(Context()))
        except Exception as exception:
             # since this response is sent to IPayment, catch errors locally
            logging.error(exception.__str__())
            traceback.print_exc()
            return HttpResponseServerError('Internal error in ' + __name__)

    def calcTrxSecurityHash(self, data):
        """
        POST data sent to IPayment can be signed using some parameters and our secretKey.
        Calculate this checksum and return it.
        """
        if not settings.IPAYMENT.has_key('securityKey') or not settings.IPAYMENT['securityKey']:
            return False # its OK, if no secret given
        md5 = hashlib.md5()
        md5.update(data['trxuser_id'].__str__())
        md5.update(data['trx_amount'].__str__())
        md5.update(data['trx_currency'])
        md5.update(data['trxpassword'])
        md5.update(settings.IPAYMENT['securityKey'])
        return md5.hexdigest()

    def checkRetParamHash(self, data):
        """
        POST data sent by IPayment is signed using some reply parameters and our secretKey.
        Check if ret_param_checksum contains a feasible content.
        """
        if not settings.IPAYMENT.has_key('securityKey') or not settings.IPAYMENT['securityKey']:
            return True # its unsafe but OK to to give a securityKey 
        if not data.has_key('ret_param_checksum'):
            return False 
        md5 = hashlib.md5()
        md5.update(data['trxuser_id'].__str__())
        md5.update(data['trx_amount'].__str__())
        md5.update(data['trx_currency'])
        md5.update(data['ret_authcode'])
        md5.update(data['ret_booknr'])
        md5.update(settings.IPAYMENT['securityKey'])
        return md5.hexdigest() == data['ret_param_checksum']
