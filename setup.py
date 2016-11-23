#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='aws-spot-fleet-helper',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    author='Marcos Araujo Sobrinho',
    author_email='marcos@mcmweb.com.br',
    url='https://gitlab.com/equake/aws-spot-fleet-helper/',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').read().strip('\n').split('\n')
)
