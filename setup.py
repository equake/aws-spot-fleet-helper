#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='vr-seres-satiro',
    version='1.5.3',
    packages=find_packages(),
    license='Commercial',
    author='Marcos Araujo Sobrinho',
    author_email='marcos.sobrinho@vivareal.com',
    url='http://www.vivareal.com.br/',
    scripts=['vivareal/satiro.py', 'vivareal/debug_protobuf_msg.py'],
    long_description=open('README').read(),
    install_requires=open('requirements.txt').read().strip('\n').split('\n')
)
