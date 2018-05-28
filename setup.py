#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='plai',
    version='0.1',
    description='Plai Server/Client repo',
    author='Mike Lyons',
    author_email='mdl0394@gmail.com',
    packages=find_packages( exclude=[ 'tmp' ] )
)
