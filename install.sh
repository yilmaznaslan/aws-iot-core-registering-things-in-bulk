INFO="#Define env variable for the AWS IoT Core Tutorial"

SCRIPT="export AWS_IOT_CORE_REGISTERING_THINGS_IN_BULK="$(pwd)

echo $INFO >> ~/.bashrc
echo $SCRIPT >> ~/.bashrc
