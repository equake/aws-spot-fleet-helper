# AWS Spot Fleet Helper #

### Python library to help launching a fleet of Spot instances within AWS infrastructure ###

Functionality is also available via CLI:

```
$ spot_fleet_config.py --help
usage: spot_fleet_config.py [-h] -bid-value BID_VALUE -ssh-key-name
                            SSH_KEY_NAME -ami-id AMI_ID -iam-role IAM_ROLE
                            -instance-type INSTANCE_TYPE [INSTANCE_TYPE ...]
                            -security-group SECURITY_GROUP
                            [SECURITY_GROUP ...] -subnet-id SUBNET_ID
                            [SUBNET_ID ...]
                            [--assign-public-ip ASSIGN_PUBLIC_IP]
                            [--fleet-role FLEET_ROLE] [--tags TAGS [TAGS ...]]
                            [--user-data USER_DATA]
                            account-id

Tool to launch a fleet of Spot instances within AWS infrastructure

positional arguments:
  account-id            AWS account id

optional arguments:
  -h, --help            show this help message and exit
  -bid-value BID_VALUE  Maximum bid value per VCPU in USD
  -ssh-key-name SSH_KEY_NAME
                        SSH key name to be used
  -ami-id AMI_ID        Amazon Machine Image id to deploy
  -iam-role IAM_ROLE    Instance IAM role
  -instance-type INSTANCE_TYPE [INSTANCE_TYPE ...]
                        Instance types to deploy (ex: c3.4xlarge, m3.medium)
  -security-group SECURITY_GROUP [SECURITY_GROUP ...]
                        Security Group ids to deploy
  -subnet-id SUBNET_ID [SUBNET_ID ...]
                        Subnet ids to deploy
  --assign-public-ip ASSIGN_PUBLIC_IP
                        Assign public ip to launched instances
  --fleet-role FLEET_ROLE
                        IAM role used to deploy assets (default: aws-ec2-spot-
                        fleet-role)
  --tags TAGS [TAGS ...]
                        AMI tags. Format: "key=value"
  --user-data USER_DATA
                        User data to be included in instance launch
                        configuration. File name or "-" for reading from stdin
```
