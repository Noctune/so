#!/usr/bin/env python

import shutil
from distutils.core import setup

try:
    from distutils.command.build_scripts import build_scripts_2to3 as build_scripts
except ImportError:
    from distutils.command.build_scripts import build_scripts

shutil.copyfile('so.py', 'so')

setup(name='Stack Overflow',
      version='0.1',
      description='Text-based Stack Overflow browser',
      author='Mike Pedersen',
      author_email='mipede12@student.aau.dk',
      scripts=['so'],
      license='GPL v3',
      cmdclass = {'build_scripts': build_scripts}
     )
