# AWS Spot Fleet Helper
Python library to help launching a fleet of Spot instances within AWS infrastructure

## Architecture
![Lib Architecture](/architecture/aws-spot-helpers.png?raw=true "Architecture diagram")

_*for illustrative purposes only_

## Application Checklist
  - [ ] Sonar
  - [ ] Jenkins
  - [X] [Pypi](https://pypi.python.org/pypi/aws-spot-fleet-helper)
  
## How to Build
```sh 
$ make build
```

## How to Run
This library is meant to be imported within your own application, but functionality is also available via CLI:

```sh
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

## How to Test
```sh
$ make test
```

## How to Publish
This lib is available for download via `pip`. If you need to upload an new version to `pypi`, just type:
```sh 
make publish
```

## How to Deploy
If you want to use the `CLI`:
```sh
pip install aws-spot-fleet-helper
```
The `CLI` should now be available in your path.

When using this lib with your own app, just put it as an dependency in your `requirements.txt` file.