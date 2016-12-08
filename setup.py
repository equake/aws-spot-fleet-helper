#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='aws-spot-helpers',
    version='0.2.0',
    description='Python library to help launching a fleet of Spot instances within AWS infrastructure',
    packages=find_packages(),
    license='MIT',
    author='Marcos Araujo Sobrinho',
    author_email='marcos.sobrinho@vivareal.com.br',
    url='https://github.com/VivaReal/aws-spot-helpers/',
    download_url='https://pypi.python.org/pypi/aws-spot-helpers',
    keywords=['aws', 'boto3', 'spot-fleet', 'spot', 'fleet', 'amazon web services'],
    long_description=open('README').read(),
    scripts=['vivareal/aws_spot_fleet_helper/spot_fleet_config.py'],
    install_requires=open('requirements.txt').read().strip('\n').split('\n')
)
