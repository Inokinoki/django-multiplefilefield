#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='django-multiplefilefield',
    version=__import__('multiplefilefield').__version__,
    description='Django Model and Form fields which can store multiple files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Inokinoki/django-multiplefilefield',
    author='Weixuan XIAO(BNBLord)',
    author_email='veyx.shaw@gmail.com',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    package_data={
        'multiplefilefield': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
)