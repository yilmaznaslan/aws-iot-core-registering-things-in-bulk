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
    logger.info("aws-iot-core: " +
                f"{len(response['policies'])} policies are found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['policies'], indent=2, default=str))
    for policy in response['policies']:
        policyArns.append(policy['policyArn'])
        policyNames.append(policy['policyName'])

    while("nextMarker" in response):
        response = iot_client.list_policies(
            ascendingOrder=True, pageSize=pageSize, marker=response["nextMarker"])
        policy_count = policy_count + len(response['policies'])
        logger.info("aws-iot-core: " +
                    f"{len(response['policies'])} policies found.")

        if detail:
            logger.info(json.dumps(
                response['policies'], indent=2, default=str))
        for policy in response['policies']:
            policyArns.append(policy['policyArn'])
            policyNames.append(policy['policyName'])
    else:
        logger.info(
            f"aws-iot-core: Checking is completed. Total certificate count {policy_count}")

    return {"policyArns": policyArns, "policyNames": policyNames}


def aws_iot_core_get_all_certificates(detail=False):
    """
    returns all the certificates registered in the aws-iot-core
    """

    # Return parameters
    certificateArns = []
    certificateIds = []

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Parameter used to count certificates and search pages
    certificates_count = 0
    page_count = 0

    # Log Info
    logger.info("aws-iot-core: Getting certificates ...")

    # Send the first request
    response = iot_client.list_certificates(pageSize=pageSize)

    # Count the number of the certificates until no more certificates are present on the search pages
    while(1):
        # Increment certificate count
        certificates_count = certificates_count + len(response['certificates'])
        
        # Append found certificates to the lists
        for certificate in response['certificates']:
            certificateArns.append(certificate['certificateArn'])
            certificateIds.append(certificate['certificateId'])

        # Print details if the 'detail'flag is set to True
        if detail:
            logger.info(json.dumps(response['certificates'], indent=2, default=str))


        # Increment Page number
        page_count += 1


        # Check if nextMarker is present for next search pages
        if("nextMarker" in response):
            response = iot_client.list_certificates(pageSize=pageSize,marker=response["nextMarker"])
        else:
            break


    logger.info("aws-iot-core: "+f"\t\tGetting certificates is completed. In total {certificates_count} certificates are found.")
    return {"certificateArns": certificateArns, "certificateIds": certificateIds}


def aws_iot_core_get_all_things(detail=False):
    """
    returns all the things registered in the aws-iot-core
    """

    # Return parameters
    thingNames = []
    thingArns = []

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Parameters used to count things, pages and to check if next is page is present
    things_count = 0
    page_count = 1
    exist_nextPage = False

    # Log Info
    logger.info("aws-iot-core: Getting things ...")

    # Count the number of the things until no more things are present on the search pages
    response = iot_client.list_things(maxResults=pageSize)

    while(1):
        # Increment thing count
        things_count = things_count + len(response['things'])
        logger.info("aws-iot-core: " + f"\t\t{len(response['things'])} things are found on the {page_count} page. Checking the next page...")

        # Append found things to the lists
        for thing in response['things']:
            thingArns.append(thing['thingArn'])
            thingNames.append(thing['thingName'])

        # Print details if flag is set to True
        if detail:
            logger.info(json.dumps(response['things'], indent=2, default=str))

        # Increment Page number
        page_count += 1

        # Check if nextToken is present for next search pages
        if("nextToken" in response):
            response = iot_client.list_things(maxResults=pageSize, nextToken=response["nextToken"])
        else:
            break

    logger.info("aws-iot-core: "+f"\t\tGetting things is completed. In total {things_count} things are found.")
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
    response = iot_client.list_thing_types(maxResults=pageSize)

    # Count the number of the policies until no more thing types are present on the page
    # do while loop. This can be improved

    logger.info("aws-iot-core: Listing thing types ...")
    type_count = type_count + len(response['thingTypes'])
    logger.info("aws-iot-core: " +
                f"{type_count} thing types are found. Checking next pages ...")

    if detail:
        logger.info(json.dumps(response['thingTypes'], indent=2, default=str))
    for thingType in response['thingTypes']:
        thingTypeArns.append(thingType['thingTypeArn'])
        thingTypeNames.append(thingType['thingTypeName'])

    while("nextToken" in response):
        response = iot_client.list_policies(
            ascendingOrder=True, pageSize=pageSize, marker=response["nextMarker"])
        response = iot_client.list_thing_types(
            maxResult=pageSize, nextToken=response["nextToken"])
        type_count = type_count + len(response['thingTypes'])
        logger.info(
            "aws-iot-core: "+f"{len(response['thingTypes'])} more thing types are found.")

        if detail:
            logger.info(json.dumps(
                response['thingTypes'], indent=2, default=str))
        for thingType in response['thingTypes']:
            thingTypeArns.append(thingType['thingTypeArn'])
            thingTypeNames.append(thingType['thingTypeName'])
    else:
        logger.info(
            f"aws-iot-core: Checking is completed. Total thing type count is: {type_count}")

    return {"thingTypeArns": thingTypeArns, "thingTypeNames": thingTypeNames}


def aws_iot_core_reset():
    """
    Deletes all the registerd things, certificates and policies in the client region. 
    Doesn't delete thing types hence it takes 5 mins to delete it 

    """

    # Log info
    logger.info("Resetting IoT Core ... ")

    # # Create client
    iot_client = boto3.client('iot', REGION)

    # Get certificates, things and policies
    certificates = aws_iot_core_get_all_certificates()
    things = aws_iot_core_get_all_things()
    policies = aws_iot_core_get_policies()
    thingTypes = aws_iot_core_get_thing_types()

    # Step 1: Detach things from certificates. ( improve here) First inactivate the certificates and then force to delete by ignoring attached policies
    logger.info("aws-iot-core: Detaching things from certificates ...")
    for certificateArn in certificates["certificateArns"]:
        attached_things = iot_client.list_principal_things(
            principal=certificateArn, maxResults=pageSize)["things"]
        if(len(attached_things) > 1):
            for attached_thing in attached_things:
                iot_client.detach_thing_principal(
                    thingName=attached_thing, principal=certificateArn)
                logger.info(
                    "aws-iot-core: " + f"detaching certificate {certificateArn[:30]}... from thing {attached_thing}")
        else:
            logger.info(
                f"aws-iot-core: certificate {certificateArn} doesn't have any attached thing")

    # Step 2: Detach policies from certificates
    logger.info("aws-iot-core: Detaching policies from certificates ...")
    for certificateArn in certificates["certificateArns"]:
        attached_policies = iot_client.list_principal_policies(
            principal=certificateArn)["policies"]
        if(len(attached_policies) == 1):
            attached_policy = attached_policies[0]
            asd = "fdcffa1d2a923e7e2c93863d9f83f38f8d523e594aacf24e74e5364a1139ef68"
            # iot_client.detach_policy(policyName=attached_policy,target=asd)
            #logger.info("aws-iot-core: " + f"detaching {attached_policy} from certificate {certificateArn}")
        else:
            logger.info(
                f"aws-iot-core: certificate {certificateArn} doesn't have any attached policy")

    # Step 3: Delete the certificates from IoT Core registery if is there any
    logger.info(
        "aws-iot-core: Deleting the certificates from iot-core registery ...")
    for certificateId in certificates["certificateIds"]:
        iot_client.update_certificate(
            certificateId=certificateId, newStatus='INACTIVE')
        iot_client.delete_certificate(
            certificateId=certificateId, forceDelete=True)
        logger.info("aws-iot-core: " +
                    f"Deleting certificateId: {certificateId}")

    # Step 4: Deleting things from IoT Core registery if is there any
    logger.info("aws-iot-core: Deleting the things from iot-core registery ...")
    for thingName in things["thingNames"]:
        iot_client.delete_thing(thingName=thingName)
        logger.info("aws-iot-core: "+f"Deleting thingName: {thingName}")

    # Step 5: Deleting policies from IoT Core registery if is there any
    logger.info("aws-iot-core: Deleting the policies from iot-core registery ...")
    for policyName in policies["policyNames"]:
        iot_client.delete_policy(policyName=policyName)
        logger.info("aws-iot-core: "+f"Deleting the policyName: {policyName}")



#aws_iot_core_reset()
#aws_iot_core_get_all_things()
aws_iot_core_get_all_certificates()
