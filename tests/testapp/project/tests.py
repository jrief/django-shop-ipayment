# -*- coding: utf-8 -*-
import time
import httplib
import urllib
import urlparse
import random
from decimal import Decimal
from django.contrib.sites.models import Site
from django.test import LiveServerTestCase
from django.test.client import Client, RequestFactory
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User
from shop.util.cart import get_or_create_cart
from shop.addressmodel.models import Country
from shop.models.ordermodel import Order
from shop.backends_pool import backends_pool
from shop.tests.util import Mock
from ipayment.models import Confirmation
from models import DiaryProduct


class IPaymentTest(LiveServerTestCase):
    def setUp(self):
        current_site = Site.objects.get(id=settings.SITE_ID)
        current_site.domain = settings.HOST_NAME
        current_site.save()
        self._create_fake_order()
        self.ipayment_backend = backends_pool.get_payment_backends_list()[0]
        self.factory = RequestFactory()
        self.request = Mock()
        setattr(self.request, 'session', {})
        setattr(self.request, 'is_secure', lambda: False)
        user = User.objects.create(username="test", email="test@example.com",
            first_name="Test", last_name="Tester",
            password="sha1$fc341$59561b971056b176e8ebf0b456d5eac47b49472b")
        setattr(self.request, 'user', user)
        self.country_usa = Country(name='USA')
        self.country_usa.save()
        self.client = Client()
        self.client.login(username='test', password='123')
        self._create_cart()
        self._go_shopping()

    def tearDown(self):
        time.sleep(10)  # this keeps the server running for a while

    def _create_cart(self):
        self.product = DiaryProduct(isbn='1234567890', number_of_pages=100)
        self.product.name = 'test'
        self.product.slug = 'test'
        self.product.short_description = 'test'
        self.product.long_description = 'test'
        self.product.unit_price = Decimal('1.0')
        self.product.save()
        self.cart = get_or_create_cart(self.request)
        self.cart.add_product(self.product, 1)
        self.cart.save()

    def _go_shopping(self):
        # add address information
        post = {
            'ship-name': 'John Doe',
            'ship-address': 'Rosestreet',
            'ship-address2': '',
            'ship-zip_code': '01234',
            'ship-city': 'Toledeo',
            'ship-state': 'Ohio',
            'ship-country': self.country_usa.pk,
            'bill-name': 'John Doe',
            'bill-address': 'Rosestreet',
            'bill-address2': '',
            'bill-zip_code': '01234',
            'bill-city': 'Toledeo',
            'bill-state': 'Ohio',
            'bill-country': self.country_usa.pk,
            'shipping_method': 'flat',
            'payment_method': 'ipayment',
        }
        response = self.client.post(reverse('checkout_selection'), post, follow=True)
        urlobj = urlparse.urlparse(response.redirect_chain[0][0])
        self.assertEqual(resolve(urlobj.path).url_name, 'checkout_shipping')
        urlobj = urlparse.urlparse(response.redirect_chain[1][0])
        self.assertEqual(resolve(urlobj.path).url_name, 'flat')
        self.order = self.ipayment_backend.shop.get_order(self.request)

    def _simulate_payment(self):
        """
        Simulate a payment to the IPayment processor.
        The full payment information is sent with method POST. Make sure your
        test environment is reachable from the Internet. This test will
        a) invoke a POST request from IPayment to this server
        b) redirect the client to a given URL on this server
        Both actions shall result in the confirmation of the payment.
        """
        post = self.ipayment_backend.get_hidden_context(self.order)
        post['advanced_strict_id_check'] = 0  # disabled for testing only
        # (see ipayment_Technik-Handbuch.pdf page 32)
        if settings.IPAYMENT['useSessionId']:
            post['ipayment_session_id'] = self.ipayment_backend.get_session_id(self.request, self.order)
        else:
            post.update(self.ipayment_backend.get_sessionless_context(self.request, self.order))
            post['trx_securityhash'] = self.ipayment_backend._calc_trx_security_hash(post)
        post.update({
            'addr_name': 'John Doe',
            'cc_number': '4012888888881881',  # Visa test credit card number
            'cc_checkcode': '123',
            'cc_expdate_month': '12',
            'cc_expdate_year': '2029',
        })
        ipayment_uri = '/merchant/%s/processor/2.0/' % settings.IPAYMENT['accountId']
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        conn = httplib.HTTPSConnection('ipayment.de')
        conn.request("POST", ipayment_uri, urllib.urlencode(post), headers)
        httpresp = conn.getresponse()
        self.assertEqual(httpresp.status, 302, 'Expected to be redirected back from IPayment')
        redir_url = urlparse.urlparse(httpresp.getheader('location'))
        query_params = urlparse.parse_qs(redir_url.query)
        redir_uri = redir_url.path + '?' + redir_url.query
        conn.close()
        self.assertEqual(query_params['ret_status'][0], 'SUCCESS', 'IPayment reported: ' + redir_uri)

        # IPayent redirected the customer onto 'redir_uri'. Continue to complete the order.
        response = self.client.get(redir_uri, follow=True)
        self.assertEqual(len(response.redirect_chain), 1, '')
        urlobj = urlparse.urlparse(response.redirect_chain[0][0])
        self.assertEqual(resolve(urlobj.path).url_name, 'thank_you_for_your_order')
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(pk=self.order.id)
        self.assertEqual(order.status, Order.COMPLETED)
        confirmation = Confirmation.objects.get(shopper_id=self.order.id)
        self.assertEqual(confirmation.ret_status, 'SUCCESS')

    def _create_fake_order(self):
        """
        Create a fake order with a random order id, so that the following real
        order does not start with 1. Otherwise this could cause errors if this
        test is invoked multiple times.
        """
        order_id = random.randint(100001, 999999)
        Order.objects.create(id=order_id, status=Order.CANCELLED)

    def test_without_session(self):
        """
        Simulate a payment to the IPayment processor without using a session.
        """
        setattr(settings, 'IPAYMENT', settings.IPAYMENT_WITHOUT_SESSION)
        self._simulate_payment()

    def test_with_session(self):
        """
        Simulate a payment to the IPayment processor using a session id generated
        through a SOAP invocation.
        """
        setattr(settings, 'IPAYMENT', settings.IPAYMENT_WITH_SESSION)
        self._simulate_payment()
