from logging import log
import boto3
from config import *
import subprocess
import json
import glob


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
    logger_aws_iot_core.info('Listing iam roles ...')
    # print(response.keys()) #prints keys
    #print (json.dumps(response['Roles'], indent=2, default=str))
    for Role in response['Roles']:
        # print(type(Role),Role)
        logger_aws_iot_core.info('RoleName: '+Role['RoleName'])
        logger_aws_iot_core.info('RoleArn: '+Role['Arn']+"\n")
        #print (json.dumps(Role, indent=2, default=str))


def s3_list_buckets():
    logger_aws_iot_core.info(f"Listing Buckets ... ")
    s3_client = boto3.client('s3')
    s3_response = s3_client.list_buckets()
    for bucket in s3_response['Buckets']:
        logger_aws_iot_core.info(f"Found S3 Bucket: {bucket['Name']}")


def generate_certificates(thing_name, things):
    """
    Dont use it for now.
    """
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


def aws_iot_core_get_all_policies(detail=False):
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

    # Parameters used to count policies and search pages
    policies_count = 0
    page_count = 0

    # Log Info
    if(detail):
        logger_aws_iot_core.info("aws-iot-core: Getting policies ...")

    # Send the first request
    response = iot_client.list_policies(pageSize=pageSize)

    # Count the number of the things until no more things are present on the search pages
    while(1):
        # Increment policy count
        policies_count = policies_count + len(response['policies'])
        if(detail):
            logger_aws_iot_core.info("aws-iot-core: " + f"\t\t{len(response['policies'])} policies are found on the {page_count+1}. page. Checking the next page ...")

        # Append found policies to the lists
        for policy in response['policies']:
            policyArns.append(policy['policyArn'])
            policyNames.append(policy['policyName'])

        # Increment Page number
        page_count += 1

        # Check if nextMarker is present for next search pages
        if("nextMarker" in response):
            response = iot_client.list_policies(pageSize=pageSize, Marker=response["nextMarker"])
        else:
            break

    if(detail):
        logger_aws_iot_core.info("aws-iot-core: "+f"\t\tGetting policies is completed. In total {policy_count} policies are found.")
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
    if(detail):
        logger_aws_iot_core.info("aws-iot-core: Getting certificates ...")

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
            logger_aws_iot_core.info(json.dumps(response['certificates'], indent=2, default=str))

        # Increment Page number
        page_count += 1

        # Check if nextMarker is present for next search pages
        if("nextMarker" in response):
            response = iot_client.list_certificates(pageSize=pageSize, marker=response["nextMarker"])
        else:
            break

    if(detail):
        logger_aws_iot_core.info("aws-iot-core: "+f"\t\tGetting certificates is completed. In total {certificates_count} certificates are found.")
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

    # Parameters used to count things and search pages
    things_count = 0
    page_count = 0

    # Log Info
    if(detail):
        logger_aws_iot_core.info("Getting things")

    # Send the first request
    response = iot_client.list_things(maxResults=pageSize)

    # Count the number of the things until no more things are present on the search pages
    while(1):
        # Increment thing count
        things_count = things_count + len(response['things'])
        if(detail):
            logger_aws_iot_core.info(f"\t{len(response['things'])} things are found on the {page_count+1}. page. Checking the next page ...")

        # Append found things to the lists
        for thing in response['things']:
            thingArns.append(thing['thingArn'])
            thingNames.append(thing['thingName'])

        # Increment Page number
        page_count += 1

        # Check if nextToken is present for next search pages
        if("nextToken" in response):
            response = iot_client.list_things(maxResults=pageSize, nextToken=response["nextToken"])
        else:
            break

    if(detail):
        logger_aws_iot_core.info(f"\tGetting things is completed. In total {things_count} things are found.")
    return {"thingArns": thingArns, "thingNames": thingNames}


def aws_iot_core_get_all_thing_types(detail=False):
    """
    returns all the thing types registerd in the aws iot core
    """

    # Return parameters
    thingTypeNames = []
    thingTypeArns = []


    # Create client
    iot_client = boto3.client('iot', REGION)

    # Parameter used to count thingType names
    types_count = 0
    page_count = 0

    # Log Info
    if(detail):
        logger_aws_iot_core.info("Getting thing types")

    # Send the first request
    response = iot_client.list_thing_types(maxResults=pageSize)

    # Count the number of the things until no more things are present on the search pages
    while(1):
        # Increment thing count
        types_count = types_count + len(response['thingTypes'])
        if(detail):
            logger_aws_iot_core.info(f"\t{types_count} thingTypes are found on the {page_count+1}. page. Checking the next page ...")

        # Append found thingTypes to the lists
        for thingType in response['thingTypes']:
            thingTypeArns.append(thingType['thingTypeArn'])
            thingTypeNames.append(thingType['thingTypeName'])

        # Increment Page number
        page_count += 1

        # Check if nextToken is present for next search pages
        if("nextToken" in response):
            response = iot_client.list_thing_types(maxResults=pageSize, nextToken=response["nextToken"])
        else:
            break

    if(detail):
        logger_aws_iot_core.info(f"\tGetting thingTypes is completed. In total {types_count} thingTypes are found.")
    return {"thingTypeArns": thingTypeArns, "thingTypeNames": thingTypeNames}


def aws_iot_core_delete_all_policies():
    """
    Deletes all the registerd things, certificates and policies in the client region. 
    Doesn't delete thing types hence it takes 5 mins to delete it 

    """
    # # Create client
    iot_client = boto3.client('iot', REGION)

    # Log info
    logger_aws_iot_core.info("Deleting policies ")


    # Step 0: Get the policies
    logger_aws_iot_core.info(f"\tStep 0: Checking policies ...")
    policies = aws_iot_core_get_all_policies()
    policies_count = len(policies["policyNames"])
    if(policies_count == 0):
        logger_aws_iot_core.info(f"\t\tThere are no policiy registered. Exiting")
        return 0
    else:
        logger_aws_iot_core.info(f"\t\t{policies_count} policies are found.")


    # Step : Deleting policies 
    logger_aws_iot_core.info("\tStep 2: Deleting policies ...")
    for policyName in policies["policyNames"]:
        iot_client.delete_policy(policyName=policyName)
        logger_aws_iot_core.info(f"\t\tDeleting the policyName: {policyName}")


def aws_iot_core_create_certificates():
    """Create certificate/s for the things registered in the IoT core.

    :param set_unique: Flag to to create unique certificates for each thing or not.


    :return: True if everythings goes right,otherwise False.
    """

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Log Info
    logger_aws_iot_core.info("Creating certificates ...")

    # Step 0: Delete the existing files under secure/keys and secure/certificates
    logger_aws_iot_core.info(f"\tStep 0: Deleting existing key and certificates in the local directory")
    logger_aws_iot_core.info("\t\tDeleting private keys ...")
    for file in glob.glob(home_dir+"/secure/keys/private/*"):
        os.remove(file)

    logger_aws_iot_core.info("\t\tDeleting public keys ...")
    for file in glob.glob(home_dir+"/secure/keys/public/*"):
        os.remove(file)

    logger_aws_iot_core.info("\t\tDeleting certificates ...")
    for file in glob.glob(home_dir+"/secure/certificates/*"):
        os.remove(file)


    # Get things registered in the IoT core
    things = aws_iot_core_get_all_things(detail=False)

    # Create certificate and keys for things
    logger_aws_iot_core.info(f"\tStep 1: Creating the certificates based on configuration")
    if(set_unique):
        for thing in things['thingNames']:
            # Create keys and certificates
            response = iot_client.create_keys_and_certificate(setAsActive=True)

            # Get the certificate and key contents
            certificateArn = response["certificateArn"]
            certificate = response["certificatePem"]
            key_public = response["keyPair"]["PublicKey"]
            key_private = response["keyPair"]["PrivateKey"]

            # log information
            logger_aws_iot_core.info(f"\t\tCreating the certificate {certificateArn[:50]}...")

            # Storing the private key
            f = open(home_dir+"/secure/keys/private/"+thing+".pem.key", "w")
            f.write(key_private)
            f.close()

            # Storing the public key
            f = open(home_dir+"/secure/keys/public/"+thing+".pem.key", "w")
            f.write(key_public)
            f.close()

            # Storing the certificate
            f = open(home_dir+"/secure/certificates/"+thing+".pem.crt", "w")
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
        logger_aws_iot_core.info("\t\tCreating the certificate {certificateArn[:50]}...")
        thing = "general"

        # Storing the private key
        f = open(home_dir+"/secure/keys/private/"+thing+".pem.key", "w")
        f.write(key_private)
        f.close()

        # Storing the public key
        f = open(home_dir+"/secure/keys/public/"+thing+".pem.key", "w")
        f.write(key_public)
        f.close()

        # Storing the certificate
        f = open(home_dir+"/secure/certificates/"+thing+".pem.crt", "w")
        f.write(certificate)
        f.close()


def aws_iot_core_delete_all_certificates(detail=True):
    """
    Deletes all the registerd certificates 

    """

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Log Info
    if(detail):
        logger_aws_iot_core.info(f"Deleting certificates")

    # Step 0: Get the certificates
    logger_aws_iot_core.info(f"\tStep 0: Checking certificates ...")
    certificates = aws_iot_core_get_all_certificates(detail=False)
    certificate_count = len(certificates["certificateIds"])
    if(certificate_count == 0):
        logger_aws_iot_core.info(f"\t\tThere are no certificiates registered. Exiting")
        return 0
    else:
        logger_aws_iot_core.info(f"\t\t{certificate_count} certificates are found.")


    # Step 1: Detach things from certificates.
    logger_aws_iot_core.info(f"\tStep 1: Detaching associated things and certificates ...")
    for certificateArn in certificates["certificateArns"]:
        attached_things = aws_iot_core_get_all_principal_things(principal=certificateArn)
        for attached_thing in attached_things:
            iot_client.detach_thing_principal(thingName=attached_thing, principal=certificateArn)
            logger_aws_iot_core.info(f"\t\tDetaching thing {attached_thing} from the certificate certificate {certificateArn[:50]}...")
        if(not attached_things):
            logger_aws_iot_core.info(f"\t\tThere isn't any associated principal for the certificate {certificateArn[:50]}...")

    # Step 2: Delete the certificates from IoT Core registery if is there any
    logger_aws_iot_core.info(f"\tStep 2: Deleting certificates...")
    for certificateId in certificates["certificateIds"]:
        iot_client.update_certificate(
            certificateId=certificateId, newStatus='INACTIVE')
        iot_client.delete_certificate(
            certificateId=certificateId, forceDelete=True)
        logger_aws_iot_core.info(f"\t\tDeleting certificateId: {certificateId}")

    logger_aws_iot_core.info(f"\t\tDeleting certificates is completed.")


def aws_iot_core_get_all_principal_things(principal, detail=False):
    """
    Lists all the things associated with the specified principal.

    """

    # Return parameters
    thingNames = []

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Parameters used to count things and search pages
    things_count = 0
    page_count = 0

    # Log Info
    if(detail):
        logger_aws_iot_core.info("aws-iot-core: Getting things associated with the principal ...")

    # Send the first request
    response = iot_client.list_principal_things(principal=principal, maxResults=pageSize)

    # Count the number of the things until no more things are present on the search pages
    while(1):
        # Increment thing count
        things_count = things_count + len(response['things'])
        if(detail):
            logger_aws_iot_core.info("aws-iot-core: " + f"\t\t{len(response['things'])} things are found on the {page_count+1}. page. Checking the next page ...")

        # Append found things to the lists
        for thing in response['things']:
            thingNames.append(thing)

        # Increment Page number
        page_count += 1

        # Check if nextToken is present for next search pages
        if("nextToken" in response):
            response = iot_client.list_principal_things(principal=principal, maxResults=pageSize, nextToken=response["nextToken"])
        else:
            break

    if(detail):
        logger_aws_iot_core.info("aws-iot-core: "+f"\t\tGetting things is completed. In total {things_count} things are found associated with the principal.")
    return thingNames


def aws_iot_core_delete_all_things(detail=True):
    """
    Deletes all the registered things from aws-iot-core registery 
    """

    # Create client
    iot_client = boto3.client('iot', REGION)

    # Log Info
    if(detail):
        logger_aws_iot_core.info(f"Deleting things")

    # Step 0: Get the things
    logger_aws_iot_core.info(f"\tStep 0: Checking things ...")
    things = aws_iot_core_get_all_things(detail=False)
    things_count = len(things["thingNames"])
    if(things_count == 0):
        logger_aws_iot_core.info(f"\t\tThere are no things registered. Exiting")
        return 0
    else:
        logger_aws_iot_core.info(f"\t\t{things_count} things are found.")

    # Step 1: Detach principals associated with the things
    logger_aws_iot_core.info("\tStep 1: Detaching associated things and certificates ...")
    for thingName in things["thingNames"]:
        associated_principals = iot_client.list_thing_principals(thingName=thingName)["principals"]
        for associated_principal in associated_principals:
            iot_client.detach_thing_principal(thingName=thingName, principal=associated_principal)
            logger_aws_iot_core.info(f"\t\tDetaching the principal {associated_principal[:50]}... from the thingName: {thingName}")
        if(not associated_principals):
            logger_aws_iot_core.info(f"\t\tThere isn't any associated principal for the thing {thingName}")

    # Step 2: Deleting things from IoT Core registery
    logger_aws_iot_core.info(f"\tStep 2: Deleting the things from iot-core registery ...")
    for thingName in things["thingNames"]:
        iot_client.delete_thing(thingName=thingName)
        logger_aws_iot_core.info(f"\t\tDeleting thingName: {thingName}")


# aws_iot_core_reset()
# aws_iot_core_get_all_things()
# aws_iot_core_create_certificates()
# aws_iot_core_get_policies()
# aws_iot_core_delete_all_certificates(detail=True)
# aws_iot_core_get_all_principle_things("arn:aws:iot:us-east-1:250602908823:cert/e2d078fef274b4c275ca8b9cf61119d2b8178d14ce5238732caa3df286ab10ff",True)
# aws_iot_core_delete_all_things()
# aws_iot_core_delete_all_certificates()
# aws_iot_core_get__all_thing_types(True)
# aws_iot_core_get_all_certificates(True)
# aws_iot_core_get_all_things(True)
