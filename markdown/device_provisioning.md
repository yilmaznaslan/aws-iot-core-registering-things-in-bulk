# Security

Each connected **device** or **client** must have a **credential** to interact with AWS IoT. All traffic to and from AWS IoT is sent securely over **Transport Layer Security (TLS)**. AWS cloud security mechanisms protect data as it moves between AWS IoT and other AWS services.

#  Notes
You are responsible for managing device credentials (X.509 certificates, AWS credentials, Amazon Cognito identities, federated identities, or custom authentication tokens) and policies in AWS IoT. For more information, see Key management in AWS IoT. You are responsible for assigning unique identities to each device and managing the permissions for each device or group of devices.