from logging import log
import os
import json
import glob
import boto3
from config import *
from utils import *
import time


def create_wastebins(instance_amount):
    # Create Instances
    berlin_wastebins = [None]*instance_amount
    for i in range(instance_amount):
        berlin_wastebins[i] = ThingWasteBin()

    return berlin_wastebins


def create_provision_file(things):
    """
    Creates a provision data file under /secure/provision
    """
    # Clear the provisioning json file by simply opening for writing
    bulk_provision_file = PATH_TO_PROVISION
    f = open(bulk_provision_file, "w")
    f.close()

    # Reopen the provision data file to attend lines
    f = open(bulk_provision_file, "a")

    # Loop through things and create a provision data for each thing
    for thing in things:
        ThingName = "wastebin_"+str(thing.serial_number)
        ThingId = thing.serial_number
        message = {"ThingName": ThingName, "SerialNumber": ThingId}
        json.dump(message, f)
        f.write("\n")

    # Close the file after operation
    f.close()


def aws_s3_config():
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    bucket_name = 'iot-use-cases'
    bucket_region = "us-east-1"
    s3_client = boto3.client('s3', region_name=bucket_region)
    s3_response = s3_client.list_buckets()
    is_bucket_exist = False
    is_reset = True
    for bucket in s3_response['Buckets']:
        if(bucket['Name'] == bucket_name):
            logger.info("aws-s3: "+f"Found S3 Bucket: {bucket['Name']} no need to create a new one.")
            #is_bucket_exist = True
        else:
            logger.info("aws-s3: "+f"Found S3 Bucket: {bucket['Name']}")

    if(not is_bucket_exist):
        s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} is created")

        obj_project = 'smart-waste-management/'
        obj_secure = obj_project+'secure/'
        obj_private_keys = obj_secure+'keys/private'
        obj_provision = obj_secure+'provision/'
        obj_certificates = obj_secure+'certificates/'
        obj_provision_file = obj_provision+PROVISION_FILE_NAME

        # Create Objects in the bucket
        s3_client.put_object(Bucket=bucket_name, Key=obj_project)
        s3_client.put_object(Bucket=bucket_name, Key=obj_secure)
        s3_client.put_object(Bucket=bucket_name, Key=obj_private_keys)
        s3_client.put_object(Bucket=bucket_name, Key=obj_certificates)
        s3_client.put_object(Bucket=bucket_name, Key=obj_provision)
        s3_client.put_object(Body=open(PATH_TO_PROVISION, 'rb'),
                             Bucket=bucket_name, Key=obj_provision_file)


def aws_s3_reset():
    print("asd")


def aws_iot_core_create_bulk_things():
    """
     Registers mupltiple things in aws iot core registery
    """
    logger_aws_iot_core.info(f"Registering bulky things ...")

    # Read provision template
    f = open(PATH_TO_PROVISIONING_TEMPLATE, "r")

    # Create Client
    iot_client = boto3.client('iot', REGION)

    # Step 0: Create a thing type prior to start thing registiration
    logger_aws_iot_core.info(f"\tChecking thingType")
    thingType_name = "wastebin"
    thingTypes = aws_iot_core_get_all_thing_types()
    if(thingType_name in thingTypes["thingTypeNames"]):
        logger_aws_iot_core.info(f"\t\tThing type Name {thingType_name} is already present no need to crete new one.")
    else:
        iot_client.create_thing_type(thingTypeName='wastebin', thingTypeProperties={'thingTypeDescription': 'Generic wastebin thing type'})

    # Start registerign things
    response = iot_client.start_thing_registration_task(templateBody=f.read(
    ), inputFileBucket='iot-use-cases', inputFileKey=obj_provision_file, roleArn=ROLE_ARN)
    logger_aws_iot_core.info("\tSuccesfully created things")


def aws_iot_core_create_policy(detail = True):
    """"
    The purpose of this method is to create a policy to allow things to connect, publish and subcribe to AWS IoT Core.
    """


    # Create client
    iot_client = boto3.client('iot', REGION)    

    # Log Info
    logger_aws_iot_core.info("Creating a policy")

    # Step 0: Get the policies
    logger_aws_iot_core.info(f"\tStep 0: Checking policies ...")
    policies = aws_iot_core_get_all_policies()
    policies_count = len(policies["policyNames"])
    if(policies_count == 0):
        logger_aws_iot_core.info(f"\t\tThere are no policiy registered. Creating a new one")
        f = open(PATH_TO_POLICY, "r")
        policyDoc_str = f.read()
        policyName = "free_policy"
        # print(policyDoc_str)
        iot_client.create_policy(policyName='free_policy', policyDocument=policyDoc_str)
        logger_aws_iot_core.info(f"\t\tPolicy {policyName} is succesfully created.")
        
    else:
        logger_aws_iot_core.info(f"\t\t{policies_count} policies are found. No need to create")
        return 0

    # Create policy docuement. Still needs improvement
    policyDoc = {}
    policyDoc["Version"] = "2012-10-17"
    policyDoc["Statement"] = {}
    policyDoc["Statement"]["Effect"] = "Allow"
    policyDoc["Statement"]["Action"] = "iot*"
    policyDoc["Statement"]["Resource"] = "*"
    policyDoc_str = json.dumps(policyDoc)
    # print(policyDoc_str)


    


def aws_iot_core_attach_certificates(detail = True):
    """
    Attach certificates to things
    """

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Log info
    logger_aws_iot_core.info("Attaching certificates and things ")



    thingNames = aws_iot_core_get_all_things()["thingNames"]
    certificateArns = aws_iot_core_get_all_certificates()["certificateArns"]
    policyNames = aws_iot_core_get_all_policies()["policyNames"]

    if(set_unique):
        # Attach unique certificates to things and policy to certificates
        if(len(thingNames) == len(certificateArns)):
            for i in range(len(thingNames)):
                # Attach certificate to things
                iot_client.attach_thing_principal(thingName=thingNames[i], principal=certificateArns[i])
                if(detail):
                    logger_aws_iot_core.info(f"\tAttaching thing {thingNames[i]} and certificate {certificateArns[i][:50]}...")

                # Attach policy to things
                iot_client.attach_principal_policy(policyName=policyNames[0], principal=certificateArns[i])
        else:
            logger_aws_iot_core.info("aws-iot-core: " + "Total number of the things and certificates missmatch")

    else:
        # Attach one and only certificate to things.
        if(len(certificateArns) > 1):
            logger_aws_iot_core.error("More than one certificate is registered. Can't decide which one to use.")
        else:
            for i in range(len(thingNames)):
                iot_client.attach_thing_principal(thingName=thingNames[i], principal=certificateArns[0])
                iot_client.attach_principal_policy(policyName=policyNames[0], principal=certificateArns[0])


if __name__ == "__main__":
    wastebin_amount = 10
    berlin_wastebins = create_wastebins(wastebin_amount)

    # Step 1: Reset/Delete all the existing things, certificates and policies
    # aws_iot_core_reset()
    aws_iot_core_delete_all_things()
    aws_iot_core_delete_all_certificates()
    aws_iot_core_delete_all_policies()

    # Step 2: Create a provision file
    create_provision_file(berlin_wastebins)

    # # Step 3: Configure the s3 bucket to upload the provision file
    aws_s3_config()

    # # Step 4: Register things in Iot Core registery using the provision file in s3 bucket
    aws_iot_core_create_bulk_things()

    # Step 5: Create certificates
    time.sleep(3)
    aws_iot_core_create_certificates()

    # Step 6: Create policy
    aws_iot_core_create_policy()

    # Step 7: Attach everything
    aws_iot_core_attach_certificates()
