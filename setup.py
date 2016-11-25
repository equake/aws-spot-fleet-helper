#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='aws_spot_fleet_helper-spot-fleet-helper',
    version='0.0.1',
    description='Python library to help launching a fleet of Spot instances within AWS infrastructure',
    packages=find_packages(),
    license='MIT',
    author='Marcos Araujo Sobrinho',
    author_email='marcos@mcmweb.com.br',
    url='https://gitlab.com/equake/aws_spot_fleet_helper-spot-fleet-helper/',
    keywords=['aws_spot_fleet_helper', 'boto3', 'spot-fleet', 'spot', 'fleet'],
    long_description=open('README').read(),
    scripts=['mcmweb/aws_spot_fleet_helper/spot_fleet_config.py'],
    install_requires=open('requirements.txt').read().strip('\n').split('\n')
)
