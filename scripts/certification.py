import json
import glob
import boto3
import sys
import logging
from main_config import *

def create_certificates():
    iot_client = boto3.client('iot',REGION)
    response = iot_client.create_keys_and_certificate(setAsActive=True)

    #print (json.dumps(response, indent=2, default=str))
    print(response["certificatePem"])
    print(response["keyPair"]["PublicKey"])
    print(response["keyPair"]["PrivateKey"])

    thing = "dustbin_1"

    # Storing the private key
    f = open(thing+".pem.key", "w")
    f.close()
    f.write("\n")

    # Storing the certificate 
    f = open(thing+".pem.crt", "w")
    f.close()
    f.write("\n")
        

def attach_cert():
    client = boto3.client('iot',REGION)
    certificateArn = "arn:aws:iot:us-east-1:250602908823:cert/9168498fe7cf71217192d680996082b58cfddf01125d58cdc51e4c2cc365ae7d"
    thingName='dustbin_1',
    principal='string'
    response = client.attach_thing_principal(thingName="dustbin_1",principal=certificateArn)

    print (json.dumps(response, indent=2, default=str))

#attach_cert()
create_certificates()