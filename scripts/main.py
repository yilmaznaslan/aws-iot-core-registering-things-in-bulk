from logging import log
import os
import json
import glob
import boto3
from config import *
from utils import *


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


def aws_iot_core_create_certificates(set_unique):
    """Create certificate/s for the things registered in the IoT core.

    :param set_unique: Flag to to create unique certificates for each thing or not.


    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used

    :return: True if everythings goes right,otherwise False.
    """
    # Delete the existing files under secure/keys and secure/certificates
    logger.info("Deleting private keys ...")
    for file in glob.glob(home_dir+"/secure/keys/private/*"):
        os.remove(file)

    logger.info("Deleting public keys ...")
    for file in glob.glob(home_dir+"/secure/keys/public/*"):
        os.remove(file)

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Get things registered in the IoT core
    things = aws_iot_core_get_things()

    # Create certificate and keys for things
    if(set_unique):
        for thing in things['thingArns']:
            # Create keys and certificates
            response = iot_client.create_keys_and_certificate(setAsActive=True)

            # Get the certificate and key contents
            certificateArn = response["certificateArn"]
            certificate = response["certificatePem"]
            key_public = response["keyPair"]["PublicKey"]
            key_private = response["keyPair"]["PrivateKey"]

            # log information
            logger.info("aws-iot-core: " + f"certificate {certificateArn} is created")
            thing_name = "wastebin"
            thing_id = thing_name+str(thing.serial_number)

            # Storing the private key
            f = open(home_dir+"/secure/keys/private/"+thing_id+".pem.key", "w")
            f.write(key_private)
            f.close()

            # Storing the public key
            f = open(home_dir+"/secure/keys/public/"+thing_id+".pem.key", "w")
            f.write(key_public)
            f.close()

            # Storing the certificate
            f = open(home_dir+"/secure/certificates/"+thing_id+".pem.crt", "w")
            f.write(certificate)
            f.close()
    else:
        # Create keys and certificates
        response = iot_client.create_keys_and_certificate(setAsActive=True)

        # Get the certificate and key contents
        certificateArn = response["certificateArn"]
        certificate = response["certificatePem"]
        key_public = response["keyPair"]["PublicKey"]
        key_private = response["keyPair"]["PrivateKey"]

        # log information
        logger.info("aws-iot-core: " + f"certificate {certificateArn} is created")
        thing_id = "general"

        # Storing the private key
        f = open(home_dir+"/secure/keys/private/"+thing_id+".pem.key", "w")
        f.write(key_private)
        f.close()

        # Storing the public key
        f = open(home_dir+"/secure/keys/public/"+thing_id+".pem.key", "w")
        f.write(key_public)
        f.close()

        # Storing the certificate
        f = open(home_dir+"/secure/certificates/"+thing_id+".pem.crt", "w")
        f.write(certificate)
        f.close()





def aws_iot_core_create_bulk_things():
    """
     Registers mupltiple things in aws iot core registery
    """

    # Read provision template
    f = open(PATH_TO_PROVISIONING_TEMPLATE, "r")

    # Create Client
    iot_client = boto3.client('iot', REGION)

    # Create a thing type prior to start thing registiration
    thingType_name = "wastebin"
    thingTypes = aws_iot_core_get_thing_types()
    if( thingType_name in thingTypes["thingTypeNames"]):
        logger.info(f"aws-iot-core: Thing type Name {thingType_name} is already present no need to crete new one.")
    else:
        iot_client.create_thing_type(thingTypeName='wastebin', thingTypeProperties={'thingTypeDescription': 'Generic wastebin thing type'})


    # Start registerign things
    response = iot_client.start_thing_registration_task(templateBody=f.read(
    ), inputFileBucket='iot-use-cases', inputFileKey=obj_provision_file, roleArn=ROLE_ARN)
    logger.info("aws-iot-core: "+"Succesfully created things")


def aws_iot_core_create_policy():
    """"
    The purpose of this method is to create a policy to allow things to connect, publish and subcribe to AWS IoT Core.
    """
    iot_client = boto3.client('iot', REGION)

    policyDoc = {}
    policyDoc["Version"] = "2012-10-17"
    policyDoc["Statement"] = {}
    policyDoc["Statement"]["Effect"] = "Allow"
    policyDoc["Statement"]["Action"] = "iot*"
    policyDoc["Statement"]["Resource"] = "*"
    policyDoc_str = json.dumps(policyDoc)
    # print(policyDoc_str)

    f = open(PATH_TO_POLICY, "r")
    policyDoc_str = f.read()
    # print(policyDoc_str)
    response = iot_client.create_policy(
        policyName='free_policy', policyDocument=policyDoc_str)


def aws_iot_core_attach_certificates(set_unique):
    """
    Attach certificates to things
    """

    # Create client
    iot_client = boto3.client('iot', REGION)

    thingNames = aws_iot_core_get_things()["thingNames"]
    certificateArns = aws_iot_core_get_certificates()["certificateArns"]
    policyNames = aws_iot_core_get_policies()["policyNames"]

    if(set_unique):
        # Attach unique certificates to things and policy to certificates
        if(len(thingNames) == len(certificateArns)):
            for i in range(len(thingNames)):
                # Attach certificate to things
                iot_client.attach_thing_principal(thingName=thingNames[i], principal=certificateArns[i])

                # Attach policy to things
                iot_client.attach_principal_policy(policyName=policyNames[0], principal=certificateArns[i])
        else:
            logger.info("aws-iot-core: " + "Total number of the things and certificates missmatch")

    else:
        # Attach one and only certificate to things.
        if(len(certificateArns) > 1):
            logger.error("More than one certificate is registered. Can't decide which one to use.")
        else:
            for i in range(len(thingNames)):
                iot_client.attach_thing_principal(thingName=thingNames[i], principal=certificateArns[0])
                iot_client.attach_principal_policy(policyName=policyNames[0], principal=certificateArns[0])


if __name__ == "__main__":
    wastebin_amount = 35
    berlin_wastebins = create_wastebins(wastebin_amount)
    set_unique = False

    # Step 1: Reset/Delete all the existing things, certificates and policies
    aws_iot_core_reset()

    # Step 2: Create a provision file
    create_provision_file(berlin_wastebins)

    # Step 3: Configure the s3 bucket to upload the provision file
    aws_s3_config()

    # Step 4: Register things in Iot Core registery using the provision file in s3 bucket
    aws_iot_core_create_bulk_things()

    # Step 5: Create certificates
    aws_iot_core_create_certificates(set_unique)

    # Step 6: Create policy
    aws_iot_core_create_policy()

    # Step 7: Attach everything
    aws_iot_core_attach_certificates(set_unique)
