import sys
import logging
import os

# Get the working directory
home_dir = os.environ['AWS_IOT_CORE_CREATE_MANY_THINGS']
# Automate here as well

# Application Parameters
THING_TYPE_NAME = "wastebin"
THING_NAME_PREFIX = "wastebin"



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

# Define max item sizes for search pages
pageSize = 2

# Define if a unique certificate for each thing should be created or, only once certificate created
set_unique = True

# Logger Settings
logger = logging.getLogger()
logger_aws_iot_core = logging.getLogger('example_logger')

logger_aws_iot_core.setLevel(logging.INFO)
#logger.setLevel(logging.WARNING)

handler = logging.StreamHandler(sys.stdout)
handler_aws_iot_core = logging.StreamHandler(sys.stdout)

log_format_aws_iot_core = logging.Formatter('%(asctime)s - %(levelname)s - AWS-IOT-CORE - %(message)s',datefmt='%H:%M:%S')
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')


handler_aws_iot_core.setFormatter(log_format_aws_iot_core)
handler.setFormatter(log_format)
#logger.addHandler(handler)
logger_aws_iot_core.addHandler(handler_aws_iot_core)


# S3 bucket directory object setup
obj_project = 'smart-waste-management/'
obj_secure = obj_project+'secure/'
obj_provision = obj_secure+'provision/'
obj_provision_file = obj_provision+PROVISION_FILE_NAME
