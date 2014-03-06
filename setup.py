#!/usr/bin/env python

import sys, os
from setuptools import setup, find_packages

setup(
        name = "SOUND IRC",
        version = "0.1",
        description = "IRC authentication software designed for the Of Sound Mind alliance of EVE Online.",
        author = "Liz & Elly Fong-Jones",
        author_email = "ellyandliz@gmail.com",
        license = "MIT",
        
        packages = find_packages(),
        include_package_data = True,
        zip_safe = False,
        paster_plugins = ['PasteScript', 'WebCore'],
        namespace_packages = ['sound'],
        
        tests_require = ['nose', 'webtest', 'coverage'],
        test_suite = 'nose.collector',
        
        install_requires = [
                'WebCore>=1.1.2',
                'MongoEngine>=0.7.999',
                'Mako>=0.4.1',
                'beaker>=1.5',
                'requests==1.1.0',
                'blinker',
                'ipython',
                'pudb',
                'babel',
                'futures',
                'scrypt'
            ],
        
    )
