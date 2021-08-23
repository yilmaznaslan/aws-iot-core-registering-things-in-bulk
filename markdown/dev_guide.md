# aws-iot-core-create-many-things-boto3

---
## Using the console
### AWS IoT Core
- Registering bulk devices
- Certification and Authenticating the devices 


#### Bulk Registiration

Using AWS IoT bulk provisioning feature, device manufacturers and suppliers can simplify and automate tasks like provisioning device identities in a secure and repeatable fashion as demonstrated by the examples. While the examples here are a start, there is much more that AWS IoT Device Management offers organizations for deploying and managing large fleets of connected things. I hope you found the blog useful and informative, and I encourage you to learn more about the new features of the AWS IoT Core to help your organization make the most of these and other enabling new technologies from AWS.

Within the scope of this demo application approximetlay 100 dustbins will be connected to cloud

![](/img/aws-bulk-reg-1.png)


In order to make productive use of the AWS IoT Device Management bulk provisioning feature you’ll need to prepare a few AWS resources prior to starting the provisioning task. Those resources include 

1. provisioning template, 
2. an S3 bucket location, 
3. a service role and 
4. a data file. 

Additionally, you will need to create X.509 certificates and generate certificate signing requests (CSRs). We’ll go over each of those resources in greater detail next.

##### Create Provisioning Template

A provisioning template contains variables that are replaced when the template is used to provision a device. A dictionary (map) is used to provide values for the variables used in a template. The bulk provisioning task will use the **JSON data file** as the replacement variable values when the **task** is run.


##### Create Certificates and Certificate Signing Requests (CSRs)

- Write a bash or python script to automatically create .crt and .key files for all objects.
- Create a python script to convert the key into single line string.

```
openssl req -new -newkey rsa:2048 -nodes -keyout keys/device-one.key -out certificates/device-one.csr -subj "/C=US/ST=WA/L=Seattle/O=MyOrg/CN=MyDept"

```
##### 3) Generate JSON data file and copy to S3 bucket

With the provisioning template and CSR files created, we can now build our JSON data file. The data file must be a newline-delimited JSON file. Each line contains all of the parameter values for provisioning a single device. For this example, our data file should appear as follows:

```
{"ThingName": "device-one", "SerialNumber": "001", "CSR": "*** CSR FILE CONTENT ***"}
{"ThingName": "device-two", "SerialNumber": "002", "CSR": "*** CSR FILE CONTENT ***"}
{"ThingName": "device-three", "SerialNumber": "003", "CSR": "*** CSR FILE CONTENT ***"}

```

##### 4) Create Service Role

When the provisioning task is executed, the IoT service will need to locate the data file in an S3 bucket. You can use an existing bucket or create a new one specifically for use in provisioning a device in the AWS IoT Core service. With either choice, you will need to **create a role that allows AWS IoT Core to access the bucket to retrieve the data file.**


First Create a **trust policy** to provide permissions to your S3 bucket. Be sure that your bucket name is properly entered.

Use the example below as a guide:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::smart-waste-management/*"
      ]
    }
  ]
}


```

**Attach the policy to the role.**

---
## Using the SDK (python)


1. S3 Bucket configuration
2. IoT Core Configuration


### Installation
Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2. In order to configure project using python, AWS Python SDK *Boto3* is needed to be installed.

```
pip3 install boto3

```
#### Configuring the creditentials
---
After installing boto3, next step is to set up credentials. Credentials include items

- aws_access_key_id, 
- aws_secret_access_key and 
- aws_session_token. 

Boto3 will look in several locations when searching for credentials. The mechanism in which Boto3 looks for credentials is to search through a list of possible locations and stop as soon as it finds credentials. The order in which Boto3 searches for credentials is:

1. Passing credentials as parameters in the boto.client() method
2. Passing credentials as parameters when creating a Session object
3. Environment variables
4. Shared credential file (~/.aws/credentials)
5. AWS config file (~/.aws/config)
6. Assume Role provider
7. Boto2 config file (/etc/boto.cfg and ~/.boto)
8. Instance metadata service on an Amazon EC2 instance that has an IAM role configured.

#### Shared credential file
The shared credentials file has a default location of ~/.aws/credentials. You can change the location of the shared credentials file by setting the AWS_SHARED_CREDENTIALS_FILE environment variable.

This file is an INI formatted file with section names corresponding to profiles. With each section, the three configuration variables shown above can be specified: aws_access_key_id, aws_secret_access_key, aws_session_token. These are the **only supported values** in the shared credential file.

Below is a minimal example of the shared credentials file:

```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
aws_session_token=baz

```
Then, set up a default region (in e.g. ~/.aws/config):

```
[default]
region=us-east-1

```

###  IAM Role Configuration

In order to grant AWS IoT Core to access S3 service an IAM role needed to be created. The created IAM role must have the following policies;
The created IAM role must have following policies;
Allows IoT to call AWS services on your behalf.

- AWSIoTThingsRegistration (AWS managed policy) ( +)
- AmazonS3ReadOnlyAccess
- 


{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::iot-use-cases/smart-waste-management*"
        }
    ]
}

### S3 Bucket Configuration


fsaf


### IoT Core Configuration

#### Choose the parameter file from the S3 bucket in which it's stored


