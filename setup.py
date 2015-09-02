#!/usr/bin/env python

from setuptools import setup


setup(
    name='python-mp',
    version='0.1.0',
    description='Python bindings for Ministry Platform',
    author='Tim Radke',
    author_email='tim@blackpulp.com',
    url='http://docs.fun.blackpulp.com/pympl',
    install_requires=[
        'inflect>=0.2.5',
        'python-dateutil>=2.4.2',
        'pytz>=2015.4',
        'suds-jurko>=0.6'
    ],
    packages=['pympl']
)
