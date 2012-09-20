====================
django-shop-ipayment
====================

This module is a payment backend module for django-SHOP, using IPayment 
(https://ipayment.de) from the 1und1 company in Germany. It can be used for
credit card and other kind of payments.

Currently only IPayment's silent CGI mode is implemented, which does not require
a PCI DSS certification (https://www.pcisecuritystandards.org/) for your shop,
because your software never "sees" the credit card numbers. With this module
your customer never visibly "leaves" your shop to enter his credit card numbers.
You are therefore in full control over all design aspects of the payment
process, something which for instance is not possible with PayPal.

Installation
============
Clone this module from github::

    git clone git@github.com:jrief/django-shop-ipayment.git

and move the sub-directory 'ipayment' into your projects path.

Configuration
=============

In settings.py

* Add ‘ipayment’ to INSTALLED_APPS.
* Add 'ipayment.offsite_backend.OffsiteIPaymentBackend' to SHOP_PAYMENT_BACKENDS.
* Add the one of the IPAYMENT configuration dictionaries, see below.
* Test your application using the sandbox.
* Then close a deal with http://ipayment.de , and populate your configurations
  according to the given settings.

With this configuration, all sensible data is passed to IPayment within the
submission form as hidden fields, but visible to the customer. In order to
detect data manipulations, a check-sum is built using some of the sensible fields
(``trxUserId``, ``trxPassword`` and more) together with the given ``securityKey``.
Use this configuration, whenever your shop is not able to speak HTTPS to the 
outside world. Many administrators of datacenters inhibit HTTPS traffic from
inside to the Internet. In these situations, use this configuration::

    IPAYMENT = {
        'accountId': 99999,
        'trxUserId': 99998,
        'trxType': 'preauth', # details in ipayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
        'trxPassword': '0',
        'trxCurrency': 'EUR',
        'trxPaymentType': 'cc', # payment type credit card
        'adminActionPassword': '5cfgRT34xsdedtFLdfHxj7tfwx24fe',
        'useSessionId': False,
        'securityKey': 'testtest',
        'invoiceText': 'Example-Shop Invoice: %s', # The text shown on the customers credit card roll
    }

With this configuration, all sensible data (``trxUserId``, ``trxPassword`` and
more) are passed to IPayment using a separate SOAP call, invoked from the shop's
web-application. This method requires that your shop can speak HTTPS to the
outside world. Whenever possible, use this configuration, because it is
safer::

    IPAYMENT = {
        'accountId': 99999,
        'trxUserId': 99999,
        'trxType': 'preauth', # details in ipayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
        'trxPassword': '0',
        'trxCurrency': 'EUR',
        'trxPaymentType': 'cc', # payment type credit card
        'adminActionPassword': '5cfgRT34xsdedtFLdfHxj7tfwx24fe',
        'useSessionId': True,
        'invoiceText': 'Example-Shop Invoice: %s', # The text shown on the customers credit card roll
    }


All the given values from these sample configurations work on the IPayment's
sandbox. Thus these values are immediately suitable to check functionality
without the need of setting up an account at IPayment. If you register for
IPayment, you get access to a configuration interface and other values
will be assigned to your shop.

For your reference, you can use the following test credit card numbers:
* Visa Test Card: 4012888888881881
* Master Test Card: 5105105105105100
* The expiration date must be set to the present date or later.
* As Credit Card Checkcode use any three digits.


Testing
=======

Note that IPayment contacts your web-server in order to confirm payments.
Therefore during testing make sure, that your testing environment is reachable
from the Internet with a name resolvable by DNS. You might have to configure
your firewall, so that your workstation is reachable on port 80.
If you do not have a domain name which resolves onto your extrenal IP address,
use a dynamic DNS service, as listed here http://dnslookup.me/dynamic-dns/.

Set the host name of your environment in tests/testapp/settings.py::

    HOST_NAME = 'ipayment.example.net'

The unit test must start a web service which listens on port 80 of your testing
environment. This feature is only available in Django-1.4 or greater. To run the
test on its own, invoke::

   cd tests/testapp
   python manage.py test --liveserver 0.0.0.0:80 

If you run Django behind a proxy, such as Apache or nginx, run:: 

   cd tests/testapp
   python manage.py test --liveserver 127.0.0.1:8080

These values depend on your testing environment.

If you have trouble running these tests, try to reach the shop using a browser,
while the test suite is running, which is about 20 seconds. The test suite has
an artificial delay, because it has to wait for external events.

TODO
====

IPayment offers a lot of different payment options, some of which require a PCI
DSS certification and communicate using SOAP. Currently I have no plans to
support these.

CHANGES
=======

0.0.5
Unit tests have been written to check for both kind of payment methods.

0.0.4
Fixed the update of the correct status in table order.

0.0.3
django-shop-ipayment is able to pass sensible data to IPayment and gets a
session key on return.
This key then is used in the customers payment form, instead of passing sensible
data.

Security
========

If using a proxy, disable forwarding the X_HTTP_FORWARD header, but make sure,
that the proxy sets the X_HTTP_FORWARD header with the IP address of the client.
This header is used to assure that payment notifications originate from
IPayment. If you have trouble with your proxy settings, disable this security
feature in settings.py ::
   IPAYMENT = {
      ...
       'checkOriginatingIP': False,
      ...
   }

Contributing
============

Feel free to post any comment or suggestion for this project on the django-shop
mailing list at https://groups.google.com/forum/#!forum/django-shop

Have fun!
Jacob
