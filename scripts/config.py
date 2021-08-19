import sys
import logging
import os

# Get the working directory
home_dir = os.environ['AWS_IOT_CORE_CREATE_MANY_THINGS']
# Automate here as well


# Defining the constants
PROVISION_FILE_NAME = "provisioning-data.json"
PROVISIONING_TEMPLATE = 'provisioning-template.json'
POLICY_FILE_NAME = "general_policy.json"

PATH_TO_PROVISION= home_dir+'/secure/provision/'+PROVISION_FILE_NAME
PATH_TO_POLICY = home_dir+'/secure/policy/'+POLICY_FILE_NAME
PATH_TO_PROVISIONING_TEMPLATE = home_dir+'/secure/provision/' + PROVISIONING_TEMPLATE

REGION = "us-east-1"
BUCKET= 'iot-use-cases'
ROLE_ARN = "arn:aws:iam::250602908823:role/iot-use-cases-demo-role"

pageSize = 25

# Logger Settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)


# S3 bucket directory object setup
obj_project = 'smart-waste-management/'
obj_secure = obj_project+'secure/'
obj_provision = obj_secure+'provision/'
obj_provision_file = obj_provision+PROVISION_FILE_NAME
