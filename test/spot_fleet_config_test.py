# -*- coding: utf-8 -*-

import json
import unittest
from base64 import b64decode

from mcmweb.aws_spot_fleet_helper.spot_fleet_config import SpotFleetConfig


class SpotFleetConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = SpotFleetConfig(12345, 0.2, 'ssh_key', 'ami-f81a5826', 'iam_role')
        self.config.add_instance_type('t2.micro')
        self.config.add_subnet_id('subnet-6d84ff3badfb')
        self.config.add_security_group_id('sg-371d865db3fb')

    def assign_public_ip_flag_test(self):
        # not set, field should not exist
        config_obj = self.config.generate()
        self.assertIsNone(config_obj['LaunchSpecifications'][0]['NetworkInterfaces'][0].get('AssociatePublicIpAddress'))

        # set to false
        self.config.should_assign_public_ip(False)
        config_obj = self.config.generate()
        self.assertFalse(config_obj['LaunchSpecifications'][0]['NetworkInterfaces'][0]['AssociatePublicIpAddress'])

        # set to true
        self.config.should_assign_public_ip(True)
        config_obj = self.config.generate()
        self.assertTrue(config_obj['LaunchSpecifications'][0]['NetworkInterfaces'][0]['AssociatePublicIpAddress'])

    def should_validate_instance_type_test(self):
        self.config.add_instance_type('c4.large')  # should work
        self.assertRaises(Exception, self.config.add_instance_type, 't.nano')  # should raise exception
        self.assertRaises(Exception, self.config.add_instance_type, 't2.none')  # should raise exception
        self.assertRaises(Exception, self.config.add_instance_type, 'c4large')  # should raise exception
        self.assertRaises(Exception, self.config.add_instance_type, 'large.c4')  # should raise exception
        self.assertRaises(Exception, self.config.add_instance_type, 'bananinha')  # should raise exception

    def should_validate_subnet_id_test(self):
        self.config.add_subnet_id('subnet-f38a4036f41d')  # should work
        self.assertRaises(Exception, self.config.add_subnet_id, 'subnet-zzzzzzzzz')  # should raise exception
        self.assertRaises(Exception, self.config.add_subnet_id, 'sg-512290a31ceb')  # should raise exception

    def should_validate_security_group_id_test(self):
        self.config.add_security_group_id('sg-512290a31ceb')  # should work
        self.assertRaises(Exception, self.config.add_security_group_id, 'sg-zzzzzzzzz')  # should raise exception
        self.assertRaises(Exception, self.config.add_security_group_id, 'subnet-f38a4036f41d')  # should raise exception

    def validate_str_representation_test(self):
        untouched = self.config.generate()
        serialized = str(self.config)
        rebuilt = json.loads(serialized)
        self.assertDictEqual(untouched, rebuilt)
