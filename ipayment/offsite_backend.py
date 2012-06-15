#-*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from suds.client import Client
import hashlib
import logging
import traceback
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from forms import SessionIPaymentForm, SensibleIPaymentForm, ConfirmationForm
from models import Confirmation


class OffsiteIPaymentBackend(object):
    '''
    Glue code to let django-SHOP talk to the ipayment backend.
    '''
    backend_name = 'IPayment'
    url_namespace = 'ipayment'
    ALLOWED_CONFIRMERS = ('212.227.34.218', '212.227.34.219', '212.227.34.220')
    
    #===========================================================================
    # Defined by the backends API
    #===========================================================================
    
    def __init__(self, shop):
        self.shop = shop
        self.logger = logging.getLogger(__name__)
        assert type(settings.IPAYMENT).__name__=='dict', \
            "You need to configure an IPAYMENT dictionary in settings"
        assert settings.IPAYMENT['useSessionId'] or \
            settings.IPAYMENT.has_key('securityKey') and len(settings.IPAYMENT['securityKey'])>=6, \
            "In IPAYMENT, useSessionId must be True, or a securityKey must contain at least 6 characters" 

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.view_that_asks_for_money, name='ipayment'),
            url(r'^hidden$', self.payment_was_successful, name='ipayment_hidden'),
            url(r'^success$', self.ipayment_return_success_view, name='ipayment_success'),
            url(r'^error$', self.view_that_asks_for_money, name='ipayment_error'),
        )
        return urlpatterns

    #===========================================================================
    # Views
    #===========================================================================

    def view_that_asks_for_money(self, request):
        '''
        Show this form to ask for the customers credit cards content. This
        content MUST never be posted to the local server, because we are not
        allowed to "see" the customers credit card numbers without a PCI DSS
        certification. Instead these numbers are sent directly to the IPayment
        server. The communication between us and IPayment is done through a
        separate channel.
        '''
        if request.method != 'GET':
            return HttpResponseBadRequest()
        context = self.get_context(request)
        return render_to_response('payment.html', context)

    def get_context(self, request):
        order = self.shop.get_order(request)
        ipayment_data = self._get_hidden_context(order)
        meta = { 'accountId': settings.IPAYMENT['accountId'], 'isError': False }
        if request.GET.has_key('ret_errorcode') and int(request.GET['ret_errorcode'])>0:
            meta['isError'] = True
            meta['errorMessage'] = request.GET['ret_errormsg']
            ipayment_data['addr_name'] = request.GET['addr_name']

        # Fill the form content
        if settings.IPAYMENT['useSessionId']:
            # sensible data is send to IPayment in a separate SOAP call
            ipayment_data['ipayment_session_id'] = self._get_session_id(request, order)
            form = SessionIPaymentForm(ipayment_data)
        else:
            # sensible data is send using this form, but signed to detect manipulation attempts
            ipayment_data.update(self._get_sessionless_context(request, order))
            ipayment_data['trx_securityhash'] = self._calc_trx_security_hash(ipayment_data)
            form = SensibleIPaymentForm(ipayment_data)
        return RequestContext(request, { 'ipayment_form': form, 'ipayment_meta': meta })

    def _get_hidden_context(self, order):
        return {
            'silent': 1,
            'shopper_id': self.shop.get_order_unique_id(order),
            'advanced_strict_id_check': 1,
            'invoice_text': settings.IPAYMENT['invoiceText'] % self.shop.get_order_short_name(order),
            'error_lang': 'en', # TODO: determine this value from language settings
        }

    def _get_sessionless_context(self, request, order):
        processorUrls = self._get_processor_urls(request)
        return {
            'trxuser_id': settings.IPAYMENT['trxUserId'],
            'trxpassword': settings.IPAYMENT['trxPassword'],
            'trx_amount': int(self.shop.get_order_total(order)*100),
            'trx_currency': settings.IPAYMENT['trxCurrency'],
            'trx_paymenttyp': settings.IPAYMENT['trxPaymentType'],
            'redirect_url': processorUrls['redirectUrl'],
            'silent_error_url': processorUrls['silentErrorUrl'],
            'hidden_trigger_url': processorUrls['hiddenTriggerUrl'],
        }

    def _get_session_id(self, request, order):
        """
        Create a SOAP call containing sensitive data, such as trxUserId and trxPassword and
        invoked directly at the IPayment's server returning a sessionID. Therefore these
        sensitive fields have not to be displayed in the clients browser.  
        """
        soapClient = Client('https://ipayment.de/service/3.0/?wsdl')
        sessionData = {
            'accountData': { 
                'accountId': settings.IPAYMENT['accountId'],
                'trxuserId': settings.IPAYMENT['trxUserId'],
                'trxpassword': settings.IPAYMENT['trxPassword'],
                'adminactionpassword': settings.IPAYMENT['adminActionPassword'], 
            },
            'transactionData': {
                'trxAmount': int(self.shop.get_order_total(order)*100),
                'trxCurrency': settings.IPAYMENT['trxCurrency'],
            },
            'transactionType': settings.IPAYMENT['trxType'],
            'paymentType': settings.IPAYMENT['trxPaymentType'],
            'processorUrls': self._get_processor_urls(request)
        }
        result = soapClient.service.createSession(**sessionData)
        self.logger.debug('Created sessionID by SOAP call to IPayment: %s' % result.__str__())
        return result

    def _get_processor_urls(self, request):
            url_scheme = 'https://' if request.is_secure() else 'http://'
            url_domain = get_current_site(request).domain
            return {
                'redirectUrl': url_scheme + url_domain + reverse('ipayment_success'),
                'silentErrorUrl': url_scheme + url_domain + reverse('ipayment_error'),
                'hiddenTriggerUrl': url_scheme + url_domain + reverse('ipayment_hidden'),
            }

    #===========================================================================
    # Handlers, which process GET redirects initiated by IPayment
    #===========================================================================

    def ipayment_return_success_view(self, request):
        """
        The view the customer is redirected to from the IPayment server after a
        successful payment.
        This view is called after 'payment_was_successful' has been called, so
        the confirmation of the payment is always available here.
        """
        if request.method != 'GET':
            return HttpResponseBadRequest('Request method %s not allowed here' %
                                          request.method)
        try:
            shopper_id = int(request.GET['shopper_id'])
            self.logger.info('IPayment for order %s redirected client with status %s',
                             shopper_id, request.GET['ret_status'])
            if request.GET['ret_status'] != 'SUCCESS':
                return HttpResponseRedirect(self.shop.get_cancel_url())
            confirmation = Confirmation.objects.filter(shopper_id=shopper_id)
            if confirmation.count() == 0:
                raise SuspiciousOperation('Redirect by IPayment rejected: '
                    'No order confirmation found for shopper_id %s.' % shopper_id)
            return HttpResponseRedirect(self.shop.get_finished_url())
        except Exception as exception:
            # since this response is sent to IPayment, catch errors locally
            logging.error(exception.__str__())
            traceback.print_exc()
            return HttpResponseServerError('Internal error in ' + __name__)

    #===========================================================================
    # Handlers, which process POST data from IPayment
    #===========================================================================

    @csrf_exempt
    def payment_was_successful(self, request):
        '''
        This listens to a confirmation sent by one of the IPayment servers.
        Valid payments are commited as confirmed payments into their model.
        The intention of this view is not to display any useful information,
        since the HTTP-client is a server located at IPayment.
        '''
        if request.method != 'POST':
            return HttpResponseBadRequest()
        try:
            if settings.IPAYMENT['checkOriginatingIP']:
                self._check_originating_ipaddr(request)
            post = request.POST.copy()
            if post.has_key('trx_amount'):
                post['trx_amount'] = (Decimal(post['trx_amount'])/Decimal('100')) \
                                                    .quantize(Decimal('0.00'))
            if post.has_key('ret_transdate') and post.has_key('ret_transtime'):
                post['ret_transdatetime'] = datetime.strptime(
                    post['ret_transdate']+' '+post['ret_transtime'],
                    '%d.%m.%y %H:%M:%S')
            confirmation = ConfirmationForm(post)
            if not confirmation.is_valid():
                raise SuspiciousOperation('Confirmation by IPayment rejected: '
                            'POST data does not contain all expected fields.')
            if not settings.IPAYMENT['useSessionId']:
                self._check_ret_param_hash(request.POST)
            confirmation.save()
            order = self.shop.get_order_for_id(confirmation.cleaned_data['shopper_id'])
            self.logger.info('IPayment for %s confirmed %s', order, 
                             confirmation.cleaned_data['ret_status'])
            if confirmation.cleaned_data['ret_status'] == 'SUCCESS':
                self.shop.confirm_payment(order, confirmation.cleaned_data['trx_amount'], 
                    confirmation.cleaned_data['ret_trx_number'], self.backend_name)
            return HttpResponse('OK')
        except Exception as exception:
            # since this response is sent to IPayment, catch errors locally
            logging.error('POST data: ' + request.POST.__str__())
            logging.error(exception.__str__())
            traceback.print_exc()
            return HttpResponseServerError('Internal error in ' + __name__)

    def _check_originating_ipaddr(self, request):
        """
        Check that the request is coming from a trusted source. A list of
        allowed sources is hard coded into this module.
        If the software is operated behind a proxy, instead of using the remote
        IP address, the HTTP-header HTTP_X_FORWARDED_FOR is evaluated against
        the list of allowed sources.
        """
        # TODO: use request.get_host()
        originating_ip = request.META['REMOTE_ADDR']
        if settings.IPAYMENT['reverseProxies'].count(originating_ip):
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                forged = True
                for client in request.META['HTTP_X_FORWARDED_FOR'].split(','):
                    if self.ALLOWED_CONFIRMERS.count(client):
                        forged = False
                        originating_ip = client
                        break
                if forged:
                    raise SuspiciousOperation('Request invoked from suspicious IP address %s'
                                    % request.META['HTTP_X_FORWARDED_FOR'])
            else:
                logging.warning('Allowed proxy servers are declared, but header HTTP_X_FORWARDED_FOR is missing')
        elif not self.ALLOWED_CONFIRMERS.count(originating_ip):
            raise SuspiciousOperation('Request invoked from suspicious IP address %s'
                                      % originating_ip)
        self.logger.debug('POST data received from IPayment[%s]: %s.' 
                          % (originating_ip, request.POST.__str__()))

    def _calc_trx_security_hash(self, data):
        """
        POST data sent to IPayment can be signed using some parameters and our secretKey.
        Calculate this checksum and return it.
        """
        md5 = hashlib.md5()
        md5.update(data['trxuser_id'].__str__())
        md5.update(data['trx_amount'].__str__())
        md5.update(data['trx_currency'])
        md5.update(data['trxpassword'])
        md5.update(settings.IPAYMENT['securityKey'])
        return md5.hexdigest()

    def _check_ret_param_hash(self, data):
        """
        POST data sent by IPayment is signed using some reply parameters and our secretKey.
        Check if ret_param_checksum contains a feasible content.
        """
        if not data.has_key('ret_param_checksum'):
            raise SuspiciousOperation('POST data from IPayment does not contain expected parameter "ret_param_checksum"')
        md5 = hashlib.md5()
        md5.update(data['trxuser_id'].__str__())
        md5.update(data['trx_amount'].__str__())
        md5.update(data['trx_currency'])
        md5.update(data['ret_authcode'])
        md5.update(data['ret_booknr'])
        md5.update(settings.IPAYMENT['securityKey'])
        if md5.hexdigest() != data['ret_param_checksum']:
            raise SuspiciousOperation('Checksum delivered by IPayment does not match internal hash digest.')
