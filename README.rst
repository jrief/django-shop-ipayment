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

In settings.py, add the following dictionary::

In this configuration, all sensible data is passed to IPayment within the form visible in the
customers browser. In order to detect data manipulations a checksum is built using some of the forms
fields together with the given securityKey.

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
        'invoiceText': 'Example-Shop Invoice: %s',
    }

In this configuration, all sensible data is passed to IPayment using a separate SOAP call.
This method requires that the shop web-application can invoke HTTP-requests to IPayment.

    IPAYMENT = {
        'accountId': 99999,
        'trxUserId': 99999,
        'trxType': 'preauth', # details in ipayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
        'trxPassword': '0',
        'trxCurrency': 'EUR',
        'trxPaymentType': 'cc', # payment type credit card
        'adminActionPassword': '5cfgRT34xsdedtFLdfHxj7tfwx24fe',
        'useSessionId': True,
        'invoiceText': 'Example-Shop Invoice: %s',
    }


The given values work on the IPayment's sandbox. If you register for IPayment other values will be
assigned to your shop. You can test IPayment without setting up an account.

Implementation
=============

Currently only IPayment's silent mode CGI is implemented, which does not require a PCI DSS
certification (www.pcisecuritystandards.org), but which allows to implement every detail of your
payments forms.

Note that IPayment contacts your web-server in order to confirm payments. Therefore make sure,
that your django-SHOP is reachable from the Internet with a name resolvable by DNS.

TODO
=============

Unit tests have to be written.

IPayment offers a lot of different payment options, some of which require a PCI DSS certification
and communicate using SOAP. Currently I have no plans to support these.

CHANGES
=============
0.0.3
django-shop-ipayment is able to pass sensible data to IPayment and gets a session key on return.
This key then is used in the customers payment form, instead of passing sensible data.

Contributing
=============

Feel free to post any comment or suggestion for this project on the django-shop
mailing list at https://groups.google.com/forum/#!forum/django-shop

Have fun!
