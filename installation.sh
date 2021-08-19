#export SMART_WASTE_MANAGEMENT=/home/aslan/aws/use-cases/smart-waste-management
# Change here to pwd >

INFO="#Define env variable for the smart-waste-management project"

SCRIPT="export SMART_WASTE_MANAGEMENT="$(pwd)

echo $INFO >> ~/.bashrc
echo $SCRIPT >> ~/.bashrc
