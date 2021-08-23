INFO="#Define env variable for the AWS IoT Core Tutorial"

SCRIPT="export AWS_IOT_CORE_CREATE_MANY_THINGS="$(pwd)

echo $INFO >> ~/.bashrc
echo $SCRIPT >> ~/.bashrc