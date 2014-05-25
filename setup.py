#!/usr/bin/env python

import shutil
from distutils.core import setup

shutil.copyfile('so.py', 'so')

setup(name='Stack Overflow',
      version='0.1',
      description='Text-based Stack Overflow browser',
      author='Mike Pedersen',
      author_email='mipede12@student.aau.dk',
      scripts=['so'],
      license='GPL v3'
     )
