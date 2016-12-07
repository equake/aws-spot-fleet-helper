#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import re
from base64 import b64encode
from datetime import datetime, timedelta
from string import Template

from mcmweb import aws_spot_fleet_helper

BASE_PATH = os.path.dirname(os.path.realpath(aws_spot_fleet_helper.__file__))

DEFAULT_FLEET_ROLE = 'aws-ec2-spot-fleet-role'

INSTANCE_WEIGHT = {
    'nano': 1,
    'micro': 1,
    'small': 1,
    'medium': 1,
    'large': 2,
    'xlarge': 4,
    '2xlarge': 8,
    '4xlarge': 16,
    '8xlarge': 36,
    '10xlarge': 40
}

FLEET_ROLE_ARN = 'arn:aws:iam::%(_account_id)i:role/%(_fleet_role)s'
INSTANCE_PROFILE_ARN = 'arn:aws:iam::%(_account_id)i:instance-profile/%(_iam_role)s'

PATTERN_AMI_ID = re.compile('^ami-[0-9a-f]{8,}$')
PATTERN_INSTANCE_TYPE = re.compile('^[a-z]+[0-9]+\.([0-9]+)?(nano|micro|small|medium|large|xlarge)$')
PATTERN_SECURITY_GROUP_ID = re.compile('^sg-[0-9a-f]{8,}$')
PATTERN_SUBNET_ID = re.compile('^subnet-[0-9a-f]{8,}$')


class SpotFleetConfig(object):
    _instance_types = []
    _monitoring = True
    _security_groups = []
    _subnet_ids = []
    _target_capacity = 1
    _user_data = None

    def __init__(self, account_id, bid_value, ssh_key_name, ami_id, iam_role, tags=None, assign_public_ip=None, fleet_role=DEFAULT_FLEET_ROLE):
        """
        SpotFleet
        Generate the LaunchSpecification JSON config file for deploying spot fleets
        :param account_id: AWS account id
        :param bid_value: Maximum bid value per VCPU in USD
        :param ssh_key_name: SSH key name to be used
        :param ami_id: Amazon Machine Image id to deploy
        :param iam_role: Instance IAM role
        :param assign_public_ip: Assign public ip to launched instances
        :param fleet_role: IAM role used to deploy assets
        """
        self._account_id = int(account_id)
        self._bid_value = bid_value
        self._ssh_key_name = ssh_key_name
        self._ami_id = ami_id
        self._iam_role = iam_role
        self._assign_public_ip = assign_public_ip
        self._fleet_role = fleet_role
        self._tags = self.__parse_tags(tags)

    @staticmethod
    def __parse_tags(tags):
        if not tags:
            return {}
        if isinstance(tags, list):
            return {key.strip(): value.strip() for key, value in [tag.strip().split('=') for tag in args.tags]}
        elif isinstance(tags, dict):
            return tags
        else:
            raise ValidationException('Unknown tag format: %s' % tags)

    @staticmethod
    def __instance_weight(instance_type_name):
        """ Infer instance weight/cpu count based on instance type name """
        size = instance_type_name.rsplit('.', 1)[1]
        weight = INSTANCE_WEIGHT.get(size)
        if not weight:
            raise ValidationException('Invalid instance type: %s' % instance_type_name)
        return weight

    def _build_base_object(self):
        now = datetime.now()
        return {
            'AllocationStrategy': 'lowestPrice',
            'IamFleetRole': FLEET_ROLE_ARN % self.__dict__,
            'SpotPrice': str(self._bid_value),
            'TargetCapacity': self._target_capacity,
            'TerminateInstancesWithExpiration': True,
            'Type': 'maintain',
            'ValidFrom': now.isoformat().split('.')[0] + 'Z',
            'ValidUntil': (now + timedelta(weeks=520)).isoformat().split('.')[0] + 'Z',
            'LaunchSpecifications': []
        }

    def _build_security_groups_object(self):
        if not self._security_groups:
            raise ValidationException('Please provide at least one security_group')
        sgs = []
        for sg in self._security_groups:
            sgs.append(sg)
        return sgs

    def _build_launch_specs_object(self):
        if not self._instance_types:
            raise ValidationException('Please provide at least one instance_type')
        if not self._subnet_ids:
            raise ValidationException('Please provide at least one subnet_id')
        sg_config = self._build_security_groups_object()

        encoded_user_data = None
        if self._tags or self._user_data:
            with open(os.path.join(BASE_PATH, 'spot_fleet_tagger.py'), 'r') as f_tmpl:
                raw_template = f_tmpl.read()
            template = Template(raw_template)
            template_data = {'tags': '', 'original_script': ''}
            if self._tags:
                template_data['tags'] = json.dumps(self._tags)
            if self._user_data:
                template_data['original_script'] = self._user_data
            encoded_user_data = b64encode(template.substitute(template_data))

        for it in self._instance_types:
            for sid in self._subnet_ids:
                spec = {
                    'ImageId': self._ami_id,
                    'InstanceType': it,
                    'KeyName': self._ssh_key_name,
                    'WeightedCapacity': self.__instance_weight(it),
                    'Monitoring': {'Enabled': bool(self._monitoring)},
                    'IamInstanceProfile': {'Arn': INSTANCE_PROFILE_ARN % self.__dict__},
                    'NetworkInterfaces': [{
                        'DeviceIndex': 0,
                        'Groups': sg_config,
                        'SubnetId': sid
                    }]
                }

                if self._assign_public_ip is not None:
                    spec['NetworkInterfaces'][0]['AssociatePublicIpAddress'] = bool(self._assign_public_ip)
                if encoded_user_data:
                    spec['UserData'] = encoded_user_data

                yield spec

    def add_instance_type(self, instance_type):
        if not PATTERN_INSTANCE_TYPE.match(instance_type):
            raise ValidationException('Invalid instance type "%s"' % instance_type)
        self._instance_types.append(instance_type)

    def add_security_group_id(self, security_group):
        if not PATTERN_SECURITY_GROUP_ID.match(security_group):
            raise ValidationException('Invalid security group "%s"' % security_group)
        self._security_groups.append(security_group)

    def add_subnet_id(self, subnet_id):
        if not PATTERN_SUBNET_ID.match(subnet_id):
            raise ValidationException('Invalid subnet "%s"' % subnet_id)
        self._subnet_ids.append(subnet_id)

    def should_assign_public_ip(self, public_ip):
        self._assign_public_ip = bool(public_ip)

    def set_user_data(self, user_data):
        if not user_data:
            return
        self._user_data = user_data

    def generate(self):
        """
        Build an configuration object
        :rtype: dict
        """
        fleet_config = self._build_base_object()
        fleet_config['LaunchSpecifications'] = list(self._build_launch_specs_object())
        return fleet_config

    def __str__(self):
        """
        Full json output!
        :rtype: str
        """
        return json.dumps(self.generate(), indent=2)


class ValidationException(Exception):
    pass


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Tool to launch a fleet of Spot instances within AWS infrastructure')
    parser.add_argument('account_id', metavar='account-id', type=int, help='AWS account id')
    parser.add_argument('-bid-value', type=float, required=True, help='Maximum bid value per VCPU in USD')
    parser.add_argument('-ssh-key-name', type=str, required=True, help='SSH key name to be used')
    parser.add_argument('-ami-id', type=str, required=True, help='Amazon Machine Image id to deploy')
    parser.add_argument('-iam-role', type=str, required=True, help='Instance IAM role')
    parser.add_argument('-instance-type', type=str, required=True, nargs='+', help='Instance types to deploy (ex: c3.4xlarge, m3.medium)')
    parser.add_argument('-security-group', type=str, required=True, nargs='+', help='Security Group ids to deploy')
    parser.add_argument('-subnet-id', type=str, required=True, nargs='+', help='Subnet ids to deploy')
    parser.add_argument('--assign-public-ip', type=bool, help='Assign public ip to launched instances')
    parser.add_argument('--fleet-role', type=str, default=DEFAULT_FLEET_ROLE, help='IAM role used to deploy assets (default: %s)' % DEFAULT_FLEET_ROLE)
    parser.add_argument('--tags', type=str, nargs='+', help='AMI tags. Format: "key=value"')
    parser.add_argument('--user-data', type=str, help='User data to be included in instance launch configuration. File name or "-" for reading from stdin')

    args = parser.parse_args()

    config = SpotFleetConfig(args.account_id, args.bid_value, args.ssh_key_name, args.ami_id, args.iam_role, args.tags, args.assign_public_ip, args.fleet_role)
    try:
        for arg_instance_type in args.instance_type:
            config.add_instance_type(arg_instance_type)
        for arg_security_group in args.security_group:
            config.add_security_group_id(arg_security_group)
        for arg_subnet_id in args.subnet_id:
            config.add_subnet_id(arg_subnet_id)

        if args.user_data:
            user_data = ''
            if args.user_data == '-':
                for line in sys.stdin:
                    user_data += line
            else:
                with open(args.user_data, 'r') as user_data_file:
                    user_data += user_data_file.readline()
            config.set_user_data(user_data)

        print(config)
        sys.exit(0)
    except Exception as e:
        print('%s: %s' % (e.__class__.__name__, str(e)), file=sys.stderr)
        print('Please verify if all of your parameters are right!', file=sys.stderr)
        sys.exit(100)

