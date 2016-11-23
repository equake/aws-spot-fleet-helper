#!/usr/bin/env python2.7
import json
import re
from base64 import b64encode
from datetime import datetime, timedelta

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
INSTANCE_PROFILE_ARN = 'arn:aws:iam::%(account_id)i:instance-profile/%(instance_profile)s'


class SpotFleet(object):

    instance_types = []
    monitoring = True
    security_groups = []
    subnet_ids = []
    target_capacity = 1

    def __init__(self, account_id, spot_price, key_name, image_id, instance_profile, associate_public_ip=None, fleet_role='aws-ec2-spot-fleet-role'):
        """
        :param account_id:
        :param fleet_role:
        :param spot_price:
        :param key_name:
        :param image_id:
        :param instance_profile:
        """
        self.account_id = account_id
        self.associate_public_ip = associate_public_ip
        self.fleet_role = fleet_role
        self.image_id = image_id
        self.instance_profile = instance_profile
        self.key_name = key_name
        self.spot_price = spot_price

    def __instance_weight(self, instance_type):
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
            'SpotPrice': str(self.spot_price),
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
        for security_group in self.security_groups:
            sgs.append(security_group)
        return sgs

    def _build_launch_specs_object(self):
        if not self.instance_types:
            raise Exception('Please provide at least one instance_type')
        if not self.subnet_ids:
            raise Exception('Please provide at least one subnet_id')
        sg_config = self._build_security_groups_object()
        for instance_type in self.instance_types:
            for subnet_id in self.subnet_ids:
                spec = {
                    'ImageId': self.image_id,
                    'InstanceType': instance_type,
                    'KeyName': self.key_name,
                    'WeightedCapacity': self.__instance_weight(instance_type),
                    'Monitoring': {'Enabled': bool(self.monitoring)},
                    'IamInstanceProfile': {'Arn': INSTANCE_PROFILE_ARN % self.__dict__},
                    'NetworkInterfaces': [{
                        'DeviceIndex': 0,
                        'Groups': sg_config,
                        'SubnetId': subnet_id
                    }]
                }
                if self.associate_public_ip is not None:
                    spec['NetworkInterfaces'][0]['AssociatePublicIpAddress'] = bool(self.associate_public_ip)
                if self.user_data:
                    spec['UserData'] = self.user_data
                yield spec

    def generate(self):
        config = self._build_base_object()
        config['LaunchSpecifications'] = list(self._build_launch_specs_object())
        return config

    def __str__(self):
        return json.dumps(self.generate(), indent=2)


if __name__ == '__main__':
    import argparse
    import os

    fleet = SpotFleet(444914307613, 0.025, 'solr', 'ami-f9e97795', 'satiro_permissions_role', True)

    fleet.monitoring = False

    fleet.instance_types.append('c3.large')
    fleet.instance_types.append('m3.medium')
    fleet.instance_types.append('c4.large')
    fleet.instance_types.append('m4.large')
    fleet.instance_types.append('m3.large')
    fleet.instance_types.append('m4.xlarge')
    fleet.instance_types.append('c4.xlarge')
    fleet.instance_types.append('m3.xlarge')
    fleet.instance_types.append('c3.xlarge')

    fleet.security_groups.append('sg-1a731e7e')

    fleet.subnet_ids.append('subnet-2372a946')
    fleet.subnet_ids.append('subnet-137d8e64')
    fleet.subnet_ids.append('subnet-7fce9339')

    with open('aws_spot_fleet_user_data.py.tmpl', 'r') as user_data_tmpl:
        user_data = user_data_tmpl.read() % {'env': 'prod', 'version': '1.5.3', 'es_hostname': 'searchelk.vivareal.com'}

    fleet.user_data = b64encode(user_data)

    print json.dumps(fleet.generate(), indent=4, sort_keys=True)

