# How to automate registering things in bulk to AWS IoT Core

## Introduction

This documents provides scripts to automate **registering things in bulk** with a **fleet provisioning process** into AWS IoT Core by using the AWS SDK for Python (boto3). In addition to the tools used for the registeration process it also provides **ready to use** methods to handle things, certificates and policies in large scale numbers.

The main aim of the repository is to automate process of registering things in bulks to `AWS IoT Core` using a `fleet provisioning template` and a provision file stored in a `AWS S3 ` bucket. After succesfully deploying the example application, any number of thing(s), certificate(s), an IoT thing type and a policy will be created in the `AWS IoT Core`. Once the **Certificates, things, and policy resources** are createted, it will also attach them to each other.


After running the sample application, all the certificates and keys(private/public) are saved locally. With the help of the `mqtt_connection_test.py` script, connecitivity feature of the created things associated with certificates can be validated. 

>Important: This application uses `AWS IoT Core` and `AWS S3` services and there are costs associated with these services after the Free Tier usage - please see the AWS Pricing page for details. You are responsible for any AWS costs incurred. No warranty is implied in this example.


## Prerequests & Requirements

- An AWS IAM User with  Programmatic access and following permissions policies attached.
  - `AWSS3FullAccess` ,`AWSIoTFullAccess` policies. These are the minimum permission required to run the application. More comphrensive policies such as `AWSS3FullAccess` and `AWSIoTFullAccess` can also be applied.
- An IoT Service **IAM role** to allow AWS IoT Core to call other AWS services. It is necessary to use `start_thing_registration_task()` function. Created IAM role must have minimum the following permission policies attached.
  - `AWSIoTThingsRegistration (AWS managed policy)`
  - `AmazonS3ReadOnlyAccess (AWS managed policy)`
- [Python](https://www.python.org/downloads/)


## Installation

For installation, simply download the repository and follow the instructions depending on your operating system.

### Ubuntu 
#### 1) Run the installation script 
```
cd YOUR_WORKING_DIRECTORY
source installation.sh
```

#### 2) Store the AWS User creditentials 
Save the AWS Access Key Id and AWS Secret Access Key into `creditentials` file under `~/.aws`

```
[default]
aws_access_key_id = REPLACE_IT_WITH_YOUR_KEY_ID
aws_secret_access_key = REPLACE_IT_WITH_YOUR_ACCESS_KEY

```

#### 3) Save the ARN of the created IAM Role into `config.py`
```
ROLE_ARN = "arn:aws:iam::xxxxx..."
```

### Windows
> Not Tested yet.


## Usage 

Once the installation of the application is completed, you can run the `/scripts/main.py` script to register 
- Thing(s),
- Certificate(s),
- Thing Type and 
- Policy to AWS IoT Core.

After succesfully execution of the `main.py` script, by default 10 Things, 10 Certificates, `wastebin` named thing type and a policy named `free_policy` will be created in the AWS IoT Core. Sample application will also attach the created `things,certificates and policy`.

## Configuring the paremeters
---
The developed solution provides different options to adjust the code to your needs. The complete list of the configuration parameters can be found in the `config.py` file. Depending in your need, you can modify the following paramaters.

| Parameter       | Default Value | Description                                                                                                                                                        |
| --------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| REGION          | `"us-east1"`  | `AWS Region where the IoT Core Application wanted to be developed`                                                                                                 |
| IAM_ARN         | `"us-east1"`  | `ARN of the the created IAM Role`                                                                                                                                  |
| THING_TYPE_NAME      | `vehicle`    | `Type of the created thing(s)`                                                                                                                                     |
| THING_NAME_PREFIX      | `bus`    | `A name prefix to be used when creating your things.`                                                                                                                                     |
| THING_COUNT     | 10            | `Number of things to be created in AWS IoT Core`                                                                                                                   |
| SET_CERT_UNIQUE | True          | `If set to True, a seperate certificate for each thing will be created. If set to False, one certificate will be created and shared by the all registered things.` |


## How does it work ? 


The application executes as below;

### Step 0) Resetting/Deleting the AWS IoT Core(Optional)
Although this step is marked as optional, it is a good practice use for experimenting the tools provided by this repository. Since it deletes all the registered `things,certificates and policies`, use it carefully. In order to prevent deleting important resources by accident, this feature is not implemented by default to the execution flow in the `main.py`. You can call the following method for resetting the `AWS IoT Core`.

```
aws_iot_core_reset()
```

### Step 1) Creating provisioning files
The very first step in the execution of `main.py` is to create a `provisioning template` and a `provision file`. Provision file includes all the necessary informations for each thing. When registering the things in bulk, provisionung template and provision file are used together to register things. As an output of this method, two files are create under `secure/provision`. This operation is done by calling the method below.

```
create_provision_files()
```

### Step 2) Configuring a S3 bucket
Once the provisioning files created locally now it is time to upload these files into `AWS S3` bucket. In order to register things in bulk, it is a **must** to upload the `provision file` to a S3 bucket.

The method below creates a bucket in your account and uploads the file into it.
```
aws_s3_config()
```
### Step 3) Create things in the Iot Core registery

After provisioning file is created locally and provision file is uploaded into S3 bucket, things can be created in the IoT Core Registery. The  method below creates a bulk thing provisioning task.

aws_iot_core_create_bulk_things()

### Step 4) Create certificates in the Iot Core registery
In order to connect things using the MQTT protocoll, things needed to be associated with X.509 Certificates. We can either create a different certificate for the each registered things or we can also create one certificate and share it among the things. Based on the flag `set_cert_unique`, the method below take cares to create certificates.

```
aws_iot_core_create_certificates()
```

### Step 6) Create policy
For ensuring the connectivity features of the created things, a simple policy is also created in the IoT Core Registery called **free_policy**. This policy allows all the connection, publishing and subscribing features.

```
aws_iot_core_create_policy()
```

### Step 7): Attach everything
Creating things, certificates and policies is not enough for connecting things to the AWS IoT Core. Final step in this application is to attach `things,certificates and the policy`. The method below handles this task.
```
aws_iot_core_attach_certificates()
```
### Summary
```


```
## Quick Tips
- Creating large the number of objects also increases the time required to setup the resources. For experimenting the tool try to keep the number of things to be creates less than 100 to prevent excessive load on the IoT Core. Creating 1000 things takes approximetly ~20 minutes.
- Once everything is set in the AWS IoT Core, you can run the `mqtt_test.py` to test the connectivity of the created things. Since it takes approximetly 1 seconds to create a connection for a MQTT Client, it also takes quite a lot of time to execute the script if the number of the things are large. 


## Documentation

For fully documentation please visit the [Github Page](https://yilmaznaslan.github.io/aws-iot-core-registering-things-in-bulk/)
> Coming soon


## See also
> Coming soon.Here my other tutorials / repositories

