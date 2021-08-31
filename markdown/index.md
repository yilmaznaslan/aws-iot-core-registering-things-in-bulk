# AWS IoT Core 

# Introduction 

The Internet of Things (IoT) offers the potential for data acquisition and digital interaction in areas previously inaccessible at an unprecedented scale. The magnitude of this opportunity affects individuals, organizations, and governments in many different ways. 

In order to address the complexity of provisioning and managing connected things manufacturers need ways to simplify and automate tasks like provisioning device identities and providing those identities to the devices as they are being manufactured in a secure and repeatable fashion. Enabling this formidable task is a new feature from the **AWS IoT Device Management service** that enables **bulk provisioning of connected things**.

This new feature allows users to register large number of devices at once. **Certificates, things, and policy resources** make up the principal and permissions configuration for each thing within AWS IoT Core. Regardless of the specific nature of the application, when developing a solution using AWS IoT Services, you will need to create a ‘thing’ to store information about each device, create a certificate to provide secure credentials for the ‘thing’, and set up permissions by attaching the certificate to an appropriate policy for the ‘thing’. AWS IoT bulk provisioning feature simplifies and automates the registration process.

AWS IoT Service provides three options for provisioning multiple devices.

- Bulk Provisioning
- Fleet Provisioning
- Just in time Provisioning(JITP)

This documents provides scripts to automate creating multiple things in your account using the AWS SDK for python (boto3).

