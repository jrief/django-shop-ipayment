========================
django-shop-ipayment
========================

This module is a payment backend module for django-SHOP, using IPayment (https://ipayment.de)
from the 1und1 company in Germany. It can be used for credit card and other kind of payments.
Currently only IPayment's silent CGI mode is implemented, which does not require a PCI DSS
certification (https://www.pcisecuritystandards.org/) for your shop, because your software never
"sees" the credit card numbers. With this module your customer never visibly "leaves" your shop to
enter his credit card numbers. You are therefore in full control over all design aspects of the
payment process, something which for instance is not possible with PayPal.

Installation
=============
Clone this module from github::

    git clone git@github.com:jrief/django-shop-ipayment.git

and move the sub-directory 'ipayment' into your projects path.

Configuration
=============

In settings.py
 - add ‘ipayment’ to INSTALLED_APPS.
 - add 'ipayment.offsite_backend.OffsiteIPaymentBackend' to SHOP_PAYMENT_BACKENDS.
 - add the IPAYMENT configuration dictionary, see below.

With this configuration, all sensible data is passed to IPayment within the submission form as
hidden fields, but visible to the customer. In order to detect data manipulations a check-sum is
built using some of the sensible fields (trxUserId, trxPassword and more) together with the given
‘securityKey’.

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

With this configuration, all sensible data (trxUserId, trxPassword and more) are passed to IPayment
using a separate SOAP call, invoked from the shop's web-application. This method requires that your
shop can speak HTTP to the outside world. Whenever possible, use this configuration, because it is
safer.

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


All the given values from these sample configurations work on the IPayment's sandbox. Thus these
values are immediately suitable to check functionality without the need of setting up an account at
IPayment. If you register for IPayment, you get access to a configuration interface and other values
will be assigned to your shop.


Implementation
=============

Note that IPayment contacts your web-server in order to confirm payments. Therefore during testing
make sure, that your django-SHOP is reachable from the Internet with a name resolvable by DNS.


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
Jacob