#!/usr/bin/env python
# -*- coding: utf-8 -*-

SCRIPT = """${original_script}"""

EC2_TAGS = """${tags}"""


def tag_instance(json_tags):
    import json
    import urllib2
    if not json_tags or not json_tags.startswith('{'):
        return True  # no tags
    try:
        import boto3
        try:
            identity_request = urllib2.urlopen('http://169.254.169.254/latest/dynamic/instance-identity/document', timeout=5)
            identity = json.loads(identity_request.read())
            tags = json.loads(json_tags)

            ec2_client = boto3.client('ec2', region_name=identity['region'])
            ec2_client.create_tags(
                Resources=[identity['instanceId']],
                Tags=[{'Key': key, 'Value': tags[key]} for key in tags]
            )

            return True
        except urllib2.HTTPError as e:
            print('# ERROR: Unable to retrieve Instance ID! Http Error: %i. Tagging is disabled. :(' % e.code)
    except ImportError:
        print('# ERROR: Boto3 library is unavailable! Tagging is disabled. :(')
    return False


def run_user_data(script):
    import os
    import subprocess
    if not script:
        return True  # no user_data script
    with open('/tmp/original_user_data', 'w') as original_user_data:
        original_user_data.write(script)
    os.chmod('/tmp/original_user_data', 0700)
    try:
        subprocess.call('/tmp/original_user_data')
        return True
    except OSError as e:
        print('# ERROR: Unable to call original user data script. Reason: %s' % str(e))
    return False


if __name__ == '__main__':
    tag_instance(EC2_TAGS)
    run_user_data(SCRIPT)
