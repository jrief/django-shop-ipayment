from setuptools import setup, find_packages
import os

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
]

setup(
    author ="Jacob Rief",
    author_email = "jacob.rief@gmail.com",
    name = 'django-shop-ipayment',
    version = '0.0.3',
    description = 'A payment backend module for django-SHOP, using IPayment (https://ipayment.de) from the 1und1 company in Germany.',
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url = 'https://github.com/jrief/django-shop-ipayment',
    license = 'BSD License',
    platforms = ['OS Independent'],
    keywords='django,django-shop,ipayment',
    classifiers = CLASSIFIERS,
    install_requires = [
        'Django>=1.3',
        'django-shop',
    ],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False
)
