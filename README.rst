========================
django-shop-ipayment
========================

This module is a payment backend module for django-SHOP, using IPayment (https://ipayment.de)
from the 1und1 company in Germany.

Installation
=============
Clone this module from github::

    git clone git@github.com:jrief/django-shop-ipayment.git

In settings.py, add ipayment to INSTALLED_APPS and add 'ipayment.offsite_backend.OffsiteIPaymentBackend'
to django-SHOP's SHOP_PAYMENT_BACKENDS setting.

Configuration
=============

In settings.py, add to following dictionary::

    IPAYMENT = {
        'accountID': 99999,
        'trxuser_id': 99998,
        'trx_typ': 'preauth', # details in ipayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
        'trxpassword': '0',
        'trx_currency': 'EUR',
        'trx_paymenttyp': 'cc', # payment type credit card
        'error_lang': 'en', # TODO: determine this value from language settings
        'securityKey': 'testtest',
    }

These values work on the IPayment's sandbox. If you register for IPayment your must use those values.

Implementation
=============

Currently only IPayment's silent mode CGI is implemented, which does not require a PCI DSS
certification (www.pcisecuritystandards.org), but which allows to implement every detail of your
payments forms.

Note that IPayment contacts your web-server in order to confirm payments. Therefore make sure,
that your django-SHOP is reachable from the Internet with a name resolvable by DNS.

TODO
=============

An optional but nice feature I plan to implement, is to let django-shop-ipayment create a session on the
IPayment servers and use the returned session-ID in the following forms instead of passing account
data using hidden fields.

Unit tests have to be written.

IPayment offers a lot of different payment options, some of which require a PCI DSS certification
and communicate using SOAP. Currently I have no plans to support these.

Contributing
=============

Feel free to post any comment or suggestion for this project on the django-shop
mailing list at https://groups.google.com/forum/#!forum/django-shop

Have fun!
