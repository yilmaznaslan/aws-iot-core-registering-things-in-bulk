import boto3
from config import *
import subprocess
import json


class ThingWasteBin():
    """
    This is a generic object class for dustbin instances
    """
    count = 0

    def __init__(self, latitude=52.165, longitude=13.165):
        self.serial_number = ThingWasteBin.count
        self.latitude = latitude
        self.longitude = longitude
        ThingWasteBin.count += 1


def aws_list_roles():
    # Listing IAM Roles
    client = boto3.client('iam')
    response = client.list_roles()
    logger.info('Listing iam roles ...')
    # print(response.keys()) #prints keys
    #print (json.dumps(response['Roles'], indent=2, default=str))
    for Role in response['Roles']:
        # print(type(Role),Role)
        logger.info('RoleName: '+Role['RoleName'])
        logger.info('RoleArn: '+Role['Arn']+"\n")
        #print (json.dumps(Role, indent=2, default=str))


def s3_list_buckets():
    logger.info(f"Listing Buckets ... ")
    s3_client = boto3.client('s3')
    s3_response = s3_client.list_buckets()
    for bucket in s3_response['Buckets']:
        logger.info(f"Found S3 Bucket: {bucket['Name']}")


def generate_certificates(thing_name, things):
    # Creating command line arguments
    cmd = [None]*12
    cmd[0] = 'openssl'
    cmd[1] = 'req'
    cmd[2] = '-new'
    cmd[3] = '-newkey'
    cmd[4] = 'rsa:2048'
    cmd[5] = '-nodes'
    cmd[6] = '-keyout'
    cmd[8] = '-out'
    cmd[10] = '-subj'
    cmd[11] = '/C=DE/ST=Berlin/L=Berlin/O=MyOrg/CN=MyDept'

    # Define the total number of objects to be created
    total_object_count = len(things)

    # Define generic object name
    obj_name = thing_name

    # Creating private keys(.key) and certificate signing request(.csr) files
    for i in range(total_object_count):
        obj_key = '../security/keys/'+obj_name+"_"+str(i+1)+'.key'
        obj_csr = '../security/csr/'+obj_name+"_"+str(i+1)+'.csr'
        cmd[7] = obj_key
        cmd[9] = obj_csr
        subprocess.run(cmd, capture_output=True)


def aws_iot_core_get_policies(detail=False):
    """
    returns all the policies registerd in the aws iot core
    """

    # Return parameters
    policyArns = []
    policyNames = []

    # Parameter used to count policies
    policy_count = 0

    # Create client
    iot_client = boto3.client('iot', REGION)
    response = iot_client.list_policies(ascendingOrder=True)

    # Count the number of the policies until no more policies are present on the page
    # do while loop. This can be improved

    logger.info("aws-iot-core: Listing policies ...")
    policy_count = policy_count + len(response['policies'])
    logger.info("aws-iot-core: "+f"{len(response['policies'])} policies are found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['policies'], indent=2, default=str))
    for policy in response['policies']:
        policyArns.append(policy['policyArn'])
        policyNames.append(policy['policyName'])

    while("nextMarker" in response):
        response = iot_client.list_policies(ascendingOrder=True, pageSize=pageSize, marker=response["nextMarker"])
        policy_count = policy_count + len(response['policies'])
        logger.info("aws-iot-core: "+f"{len(response['policies'])} policies found.")

        if detail:
            logger.info(json.dumps(response['policies'], indent=2, default=str))
        for policy in response['policies']:
            policyArns.append(policy['policyArn'])
            policyNames.append(policy['policyName'])
    else:
        logger.info(f"aws-iot-core: Checking is completed. Total certificate count {policy_count}")

    return {"policyArns": policyArns, "policyNames": policyNames}


def aws_iot_core_get_certificates(detail=False):
    """
    returns all the certificates registerd in the aws iot core
    """

    # Return parameters
    certificateArns = []
    certificateIds = []

    # Parameter used to count things
    certificate_count = 0

    # Create client
    iot_client = boto3.client('iot', REGION)
    response = iot_client.list_certificates(ascendingOrder=True, pageSize=pageSize)

    # Count the number of the certificates until no more things are present on the page
    # do while loop. This can be improved

    logger.info("aws-iot-core: Listing certificates ...")
    certificate_count = certificate_count + len(response['certificates'])
    logger.info("aws-iot-core: "+f"{len(response['certificates'])} certificates found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['certificates'], indent=2, default=str))
    for certificate in response['certificates']:
        certificateArns.append(certificate['certificateArn'])
        certificateIds.append(certificate['certificateId'])

    while("nextMarker" in response):
        response = iot_client.list_certificates(ascendingOrder=True, pageSize=pageSize, marker=response["nextMarker"])
        certificate_count = certificate_count + len(response['certificates'])
        logger.info("aws-iot-core: "+f"{len(response['certificates'])} certificates found. Total certificate count {certificate_count}")

        if detail:
            logger.info(json.dumps(response['certificates'], indent=2, default=str))
        for certificate in response['certificates']:
            certificateArns.append(certificate['certificateArn'])
            certificateIds.append(certificate['certificateId'])

    return {"certificateArns": certificateArns, "certificateIds": certificateIds}


def aws_iot_core_get_things(detail=False):
    """
    returns all the things registerd in the aws iot core
    """

    # Return parameters
    thingNames = []
    thingArns = []

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Parameters used to count things
    thing_count = 0

    # Count the number of the things until no more things are present on the page
    # do while loop. This can be improved
    response = iot_client.list_things(maxResults=pageSize)
    logger.info("aws-iot-core: Listing things ...")
    thing_count = thing_count + len(response['things'])
    logger.info("aws-iot-core: "+f"{len(response['things'])} things found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['things'], indent=2, default=str))
        for thing in response['things']:
            thingArns.append(thing['thingArn'])
            thingNames.append(thing['thingName'])
    else:
        for thing in response['things']:
            # logger.info(thing['thingArn'])
            thingArns.append(thing['thingArn'])
            thingNames.append(thing['thingName'])

    while("nextToken" in response):
        response = iot_client.list_things(
            maxResults=pageSize, nextToken=response["nextToken"])
        thing_count = thing_count + len(response['things'])
        logger.info("aws-iot-core: "+f"{len(response['things'])} things found. Total thing count {thing_count}")

        if detail:
            logger.info(json.dumps(response['things'], indent=2, default=str))
            for thing in response['things']:
                thingArns.append(thing['thingArn'])
                thingNames.append(thing['thingName'])
        else:
            for thing in response['things']:
                # logger.info(thing['thingArn'])
                thingArns.append(thing['thingArn'])
                thingNames.append(thing['thingName'])

    return {"thingArns": thingArns, "thingNames": thingNames}

def aws_iot_core_get_thing_types(detail=False):
    """
    returns all the thing types registerd in the aws iot core
    """

    # Return parameters
    thingTypeNames = []
    thingTypeArns = []

    # Parameter used to count policies
    type_count = 0

    # Create client
    iot_client = boto3.client('iot', REGION)
    response = iot_client.list_thing_types(maxResults = pageSize)

    # Count the number of the policies until no more thing types are present on the page
    # do while loop. This can be improved

    logger.info("aws-iot-core: Listing thing types ...")
    type_count = type_count + len(response['thingTypes'])
    logger.info("aws-iot-core: "+f"{type_count} thing types are found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['thingTypes'], indent=2, default=str))
    for thingType in response['thingTypes']:
        thingTypeArns.append(thingType['thingTypeArn'])
        thingTypeNames.append(thingType['thingTypeName'])

    while("nextToken" in response):
        response = iot_client.list_policies(ascendingOrder=True, pageSize=pageSize, marker=response["nextMarker"])
        response = iot_client.list_thing_types(maxResult = pageSize,nextToken = response["nextToken"])
        type_count = type_count + len(response['thingTypes'])
        logger.info("aws-iot-core: "+f"{len(response['thingTypes'])} more thing types are found.")

        if detail:
            logger.info(json.dumps(response['thingTypes'], indent=2, default=str))
        for thingType in response['thingTypes']:
            thingTypeArns.append(thingType['thingTypeArn'])
            thingTypeNames.append(thingType['thingTypeName'])
    else:
        logger.info(f"aws-iot-core: Checking is completed. Total thing type count is: {type_count}")

    return {"thingTypeArns": thingTypeArns, "thingTypeNames": thingTypeNames}

# aws_iot_core_get_policies()
aws_iot_core_get_thing_types()
