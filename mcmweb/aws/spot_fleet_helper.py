#!/usr/bin/env python2.7
from __future__ import print_function

import json
from base64 import b64encode
from datetime import datetime, timedelta

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
FLEET_ROLE_ARN = 'arn:aws:iam::%(account_id)i:role/%(fleet_role)s'
INSTANCE_PROFILE_ARN = 'arn:aws:iam::%(account_id)i:instance-profile/%(iam_role)s'


class SpotFleetConfig(object):
    instance_types = []
    monitoring = True
    security_groups = []
    subnet_ids = []
    target_capacity = 1
    user_data = None

    def __init__(self, account_id, bid_value, ssh_key_name, ami_id, iam_role, assign_public_ip=None, fleet_role=DEFAULT_FLEET_ROLE):
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
        self.account_id = account_id
        self.bid_value = bid_value
        self.ssh_key_name = ssh_key_name
        self.ami_id = ami_id
        self.iam_role = iam_role
        self.assign_public_ip = assign_public_ip
        self.fleet_role = fleet_role

    def __instance_weight(self, instance_type):
        """ Infer instance weight/cpu count based on instance type name """
        size = instance_type.rsplit('.', 1)[1]
        weight = INSTANCE_WEIGHT.get(size)
        if not weight:
            raise Exception('Invalid instance type: %s' % instance_type)
        return weight

    def _build_base_object(self):
        now = datetime.now()
        return {
            'AllocationStrategy': 'lowestPrice',
            'IamFleetRole': FLEET_ROLE_ARN % self.__dict__,
            'SpotPrice': str(self.bid_value),
            'TargetCapacity': self.target_capacity,
            'TerminateInstancesWithExpiration': True,
            'Type': 'maintain',
            'ValidFrom': now.isoformat().split('.')[0] + 'Z',
            'ValidUntil': (now + timedelta(weeks=520)).isoformat().split('.')[0] + 'Z',
            'LaunchSpecifications': []
        }

    def _build_security_groups_object(self):
        if not self.security_groups:
            raise Exception('Please provide at least one security_group')
        sgs = []
        for sg in self.security_groups:
            sgs.append(sg)
        return sgs

    def _build_launch_specs_object(self):
        if not self.instance_types:
            raise Exception('Please provide at least one instance_type')
        if not self.subnet_ids:
            raise Exception('Please provide at least one subnet_id')
        sg_config = self._build_security_groups_object()
        for it in self.instance_types:
            for sid in self.subnet_ids:
                spec = {
                    'ImageId': self.ami_id,
                    'InstanceType': it,
                    'KeyName': self.ssh_key_name,
                    'WeightedCapacity': self.__instance_weight(it),
                    'Monitoring': {'Enabled': bool(self.monitoring)},
                    'IamInstanceProfile': {'Arn': INSTANCE_PROFILE_ARN % self.__dict__},
                    'NetworkInterfaces': [{
                        'DeviceIndex': 0,
                        'Groups': sg_config,
                        'SubnetId': sid
                    }]
                }
                if self.assign_public_ip is not None:
                    spec['NetworkInterfaces'][0]['AssociatePublicIpAddress'] = bool(self.assign_public_ip)
                if self.user_data:
                    spec['UserData'] = self.user_data
                yield spec

    def generate(self):
        """ Build configuration object """
        fleet_config = self._build_base_object()
        fleet_config['LaunchSpecifications'] = list(self._build_launch_specs_object())
        return fleet_config

    def __str__(self):
        """ Full json output! """
        return json.dumps(self.generate(), indent=2)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Tool to launch a fleet of Spot instances within AWS infrastructure')
    parser.add_argument('account_id', metavar='account-id', type=int, help='AWS account id')
    parser.add_argument('-bid-value', type=float, required=True, help='Maximum bid value per VCPU in USD')
    parser.add_argument('-ssh-key-name', type=str, required=True, help='SSH key name to be used')
    parser.add_argument('-ami-id', type=str, required=True, help='Amazon Machine Image id to deploy')
    parser.add_argument('-iam-role', type=str, required=True, help='Instance IAM role')
    parser.add_argument('-instance-type', type=str, required=True, nargs='+', help='Instance types to deploy (ex: c3.4xlarge, m3.medium)')
    parser.add_argument('-security-group', type=str, required=True, nargs='+', help='Security Group ids to deploy')
    parser.add_argument('-subnet-id', type=str, required=True, nargs='+', help='Subnet ids to deploy')
    parser.add_argument('--fleet-role', type=str, default=DEFAULT_FLEET_ROLE, help='IAM role used to deploy assets (default: %s)' % DEFAULT_FLEET_ROLE)
    parser.add_argument('--assign-public-ip', type=bool, help='Assign public ip to launched instances')

    args = parser.parse_args()

    config = SpotFleetConfig(args.account_id, args.bid_value, args.ssh_key_name, args.ami_id, args.iam_role, args.assign_public_ip, args.fleet_role)
    for instance_type in args.instance_type:
        config.instance_types.append(instance_type)
    for security_group in args.security_group:
        config.security_groups.append(security_group)
    for subnet_id in args.subnet_id:
        config.subnet_ids.append(subnet_id)

    print(str(config))
