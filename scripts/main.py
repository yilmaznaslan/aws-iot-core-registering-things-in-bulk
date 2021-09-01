from config import *
from utils import *
from sys import exit


if __name__ == "__main__":

    # Step 0.0 : Reset/Delete all the existing things, certificates and policies registered in AWS IoT Core
    aws_iot_core_reset()

    # Step 0.1 : Reset/Delete all the existing buckets and their contents in AWS S3
    #aws_s3_reset()

    # Step 1: Create a provision file
    create_provision_file()

    # Step 2: Configure the s3 bucket 
    aws_s3_config()

    # Step 3: Create things in the Iot Core registery
    status = aws_iot_core_create_bulk_things()
    if(not status):exit

    # Step 4: Create certificates in the Iot Core registery
    aws_iot_core_create_certificates()
    
    # Step 6: Create policy
    aws_iot_core_create_policy()

    # Step 7: Attach everything
    aws_iot_core_attach_certificates()
