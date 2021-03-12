#!/usr/bin/env python

import os
from setuptools import setup, find_packages


PACKAGES = ['biofb']
PACKAGES += [f'biofb.{p}' for p in find_packages('./biofb')]  # discover sub-packages in the biofb package


# Utility function to read the README file.
def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


with open('requirements.txt') as f:
    required = [line.strip()
                for line in f.read().splitlines()
                if not line.startswith('#') and line != ''
                ]


setup(name='Bio-Feedback',
      install_requires=required,
      version='0.1',
      description='Data-Capturing and Signal Processing Library for Bio-Feedback Purposes.',
      author='Benedikt Hartl',
      author_email='hartl.bene@gmail.com',
      url='https://github.com/bhartl/bio-feedback/',
      packages=PACKAGES,
      long_description=read('README.md'),
      platforms='linux',
      classifiers=["Development Status :: 1 - Planning",
                   "Programming Language :: Python",
                   ],
      )
