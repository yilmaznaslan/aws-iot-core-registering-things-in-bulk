import sys
import logging
import os

# Get the working directory
home_dir = os.environ['AWS_IOT_CORE_REGISTERING_THINGS_IN_BULK']
# Automate here as well

# Parameters used for creating thing(s) and thing type
THING_TYPE_NAME = "vehicle"
THING_NAME_PREFIX = "bus"
THING_COUNT = 10

# Parameters used for the MQTT Connection
MQTT_ENDPOINT = "a2h3iir2hinzvl-ats.iot.us-east-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "sensor/data"
PATH_TO_ROOT_CA = home_dir+"/secure/ca/AmazonRootCA1.pem"


# Parameter used for creating certificates(s)
SET_CERT_UNIQUE = False

# Local directory paths and files
PROVISION_FILE_NAME = "provisioning-data.json"

PROVISIONING_TEMPLATE = 'provisioning-template.json'
POLICY_FILE_NAME = "general_policy.json"

PATH_TO_PROVISION= home_dir+'/secure/provision/'+PROVISION_FILE_NAME
PATH_TO_POLICY = home_dir+'/secure/policy/'+POLICY_FILE_NAME
PATH_TO_PROVISIONING_TEMPLATE = home_dir+'/secure/provision/' + PROVISIONING_TEMPLATE

REGION = "us-east-1"
BUCKET= 'iot-use-cases'
ROLE_ARN = "arn:aws:iam::250602908823:role/iot-use-cases-demo-role"

# S3 Configuration Parameters
BUCKET_NAME = "aws-iot-tutorials"
BUCKET_REGION = "us-east-1"

obj_project = 'smart-waste-management/'
obj_secure = obj_project+'secure/'
#obj_provision = obj_secure+'provision/'
OBJ_PROVISION_FILE= PROVISION_FILE_NAME
print(OBJ_PROVISION_FILE)


# Define max item sizes for search pages
pageSize = 2


# Logger Settings

logger_aws_iot_core = logging.getLogger('example_logger')

logger_aws_iot_core.setLevel(logging.INFO)


handler = logging.StreamHandler(sys.stdout)
handler_aws_iot_core = logging.StreamHandler(sys.stdout)

log_format_aws_iot_core = logging.Formatter('%(asctime)s - %(levelname)s - AWS-IOT-CORE - %(message)s',datefmt='%H:%M:%S')
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')


handler_aws_iot_core.setFormatter(log_format_aws_iot_core)
handler.setFormatter(log_format)

logger_aws_iot_core.addHandler(handler_aws_iot_core)



