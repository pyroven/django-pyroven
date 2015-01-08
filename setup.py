#!/usr/bin/env python

# Copyright 2011 Andrew Ryrie (amr66)

from distutils.core import setup

setup(name='django-pyroven',
      description='A Django authentication backend for Ucam-WebAuth / Raven',
#     No long_description due to http://bugs.python.org/issue13614
#     long_description=open('README.md').read(),
      url='https://github.com/pyroven/django-pyroven',
      version='0.9',
      license='MIT',
      author='Andrew Ryrie',
      author_email='smb314159@gmail.com',
      maintainer='Kristian Glass',
      maintainer_email='pyroven@doismellburning.co.uk',
      packages=['pyroven'],
      install_requires=[
          'Django<1.7',
          'pyOpenSSL',
      ],
      )
