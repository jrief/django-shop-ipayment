# Django settings for example project.
import socket

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Jacob Rief', 'jacob.rief@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# The hostname of this testing server visible to the outside world
HOST_NAME = socket.gethostname()

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/static/'

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h2%uf!luks79rw^4!5%q#v2znc87g_)@^jf1og!04@&&tsf7*9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

import django
if django.VERSION[0] < 1 or django.VERSION[1] < 4:
    raise('This test requires at least Django-1.4')

ROOT_URLCONF = 'testapp.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'polymorphic',  # We need polymorphic installed for the shop
    'shop',  # The django SHOP application
    'shop.addressmodel',
    'ipayment',
    'project',  # the test project application
)

# The shop settings:
SHOP_CART_MODIFIERS = []
SHOP_SHIPPING_BACKENDS = []

# Shop module settings
SHOP_SHIPPING_BACKENDS = (
    'shop.shipping.backends.flat_rate.FlatRateShipping',
)

SHOP_PAYMENT_BACKENDS = (
    'ipayment.offsite_backend.OffsiteIPaymentBackend',
)

# Shop module settings
SHOP_SHIPPING_FLAT_RATE = '10'  # That's just for the flat rate shipping backend

IPAYMENT_WITHOUT_SESSION = {
    'accountId': 99999,
    'trxUserId': 99998,
    'trxType': 'preauth',  # IPayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
    'trxPassword': '0',
    'trxCurrency': 'EUR',
    'trxPaymentType': 'cc',  # payment type: credit card
    'adminActionPassword': '5cfgRT34xsdedtFLdfHxj7tfwx24fe',
    'useSessionId': False,
    'securityKey': 'testtest',
    'invoiceText': 'Example-Shop Invoice: %s',
    'checkOriginatingIP': True,
    'reverseProxies': [ '127.0.0.1' ],  # List of allowed reverse proxies
}

IPAYMENT_WITH_SESSION = {
    'accountId': 99999,
    'trxUserId': 99999,
    'trxType': 'preauth',  # IPayment_Technik-Handbuch_2010-03.pdf (Seite 13-15)
    'trxPassword': '0',
    'trxCurrency': 'EUR',
    'trxPaymentType': 'cc',  # payment type: credit card
    'adminActionPassword': '5cfgRT34xsdedtFLdfHxj7tfwx24fe',
    'useSessionId': True,
    'securityKey': 'testtest',
    'invoiceText': 'Example-Shop Invoice: %s',
    'checkOriginatingIP': True,
    'reverseProxies': [ '127.0.0.1' ],  # List of allowed reverse proxies
}

IPAYMENT = IPAYMENT_WITHOUT_SESSION.copy()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'ipayment.offsite_backend': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
