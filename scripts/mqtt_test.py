import paho.mqtt.client as mqtt
import json
import ssl
import time
import glob
from main_config import *

IoT_protocol_name = "x-amzn-mqtt-ca"
thing = "dustbin_2"
ENDPOINT = "a2h3iir2hinzvl-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
CLIENT_ID = "esp32"
PATH_TO_CERT = home_dir+"/secure/certificates/"+thing+".pem.crt"
PATH_TO_PRIVATE_KEY = home_dir+"/secure/keys/private/"+thing+".pem.key"
PATH_TO_ROOT_CA = home_dir+"/secure/certificates/aws-root-ca.pem"
MESSAGE = "Hello World"
TOPIC = "sensor/data"


def create_ssl_contexts():
    file_counter = 0
    path_to_private_keys = []
    path_to_certificates = []
    for private_key_file in sorted(glob.glob(home_dir+'/secure/keys/private/*.key')):
        print(private_key_file)
        path_to_private_keys.append(private_key_file) 
        file_counter += 1

    # Go through the certificates
    for certificate_file in sorted(glob.glob(home_dir+'/secure/certificates/*.crt')):
        print(certificate_file)
        path_to_certificates.append(certificate_file) 
    
    ssl_contexts = [ssl.create_default_context()]*file_counter

    for i in range(file_counter):
        ssl_contexts[i].set_alpn_protocols([IoT_protocol_name])
        ssl_contexts[i].load_verify_locations(cafile=PATH_TO_ROOT_CA)
        ssl_contexts[i].load_cert_chain(certfile=path_to_certificates[i], keyfile=path_to_private_keys[i])

    return ssl_contexts


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc,properties=None):
    #print("Connected with result code "+str(rc))
    logger.info(f"Connected with the result code {rc}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logger.info(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    logger.info(f"Message Published, ID:{mid}")


def create_mqtt_clients(ssl_contexts):
    ssl_count = len(ssl_contexts)



    mqtt_clients = []
    for i in range(ssl_count):
        mqtt_clients.append(mqtt.Client(str(i)))
        mqtt_clients[-1].tls_set_context(context=ssl_contexts[i])
        mqtt_clients[-1].on_connect = on_connect
        mqtt_clients[-1].on_message = on_message
        mqtt_clients[-1].on_publish = on_publish
        logger.info(f"mqtt client is created:{i}")

    return mqtt_clients


def connect_mqtt_clients(mqtt_clients):

    for mqtt_client in mqtt_clients:
        mqtt_client.connect(ENDPOINT, PORT, 60)
        mqtt_client.loop_start()
        logger.info("Loop started")


    temperature = 0
    humidity = 10
    serialNumber = 124
    deviceType = "dustbinf"
    sensorModel = 2021
    deviceName = "aslan"

    while(1):
        print("sd")
        for mqtt_client in mqtt_clients:
            if(mqtt_client.is_connected()):
                message = {"deviceName":deviceName,"temperature":temperature,"humidity":humidity,"serialNumber":serialNumber,"sensorType":deviceType,"sensorModel":sensorModel}
                mqtt_client.publish(topic = TOPIC,payload = json.dumps(message))
                print(message)
                temperature += 1
            time.sleep(1)


if __name__ == "__main__":
    ssl_contexts = create_ssl_contexts()
    mqtt_clients = create_mqtt_clients(ssl_contexts)
    connect_mqtt_clients(mqtt_clients)