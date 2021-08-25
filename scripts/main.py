from logging import log
import os
import json
import glob
import boto3
from config import *
from utils import *
import time







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

    # Step 0 : Reset/Delete all the existing things, certificates and policies
    aws_iot_core_reset()

    # Step 1: Create a provision file
    create_provision_file()

    # Step 2: Configure the s3 bucket 
    aws_s3_config()

    # Step 3: Create things in the Iot Core registery
    aws_iot_core_create_bulk_things()

    # Step 4: Create certificates in the Iot Core registery
    time.sleep(3)
    aws_iot_core_create_certificates()

    # Step 6: Create policy
    aws_iot_core_create_policy()

    # Step 7: Attach everything
    aws_iot_core_attach_certificates()
