import paho.mqtt.client as mqtt
import json
import ssl
import sys
import logging, traceback
import os
import time


# Logger Settings
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)


# Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT, MESSAGE, TOPIC, and RANGE
root_path = os.environ['AWS']+"use-cases/smart-waste-management"


ENDPOINT = "a2h3iir2hinzvl-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
CLIENT_ID = "dustbin_2"
PATH_TO_CERT = root_path+"/security/certificates/dustbin_2-certificate.pem.crt"
PATH_TO_KEY = root_path+"/security/keys/dustbin_2.key"
PATH_TO_ROOT = root_path+"/security/certificates/aws-root-ca.pem"
MESSAGE = "Hello World"
TOPIC = "sensor/data"

print(root_path,PATH_TO_ROOT)

# Create SSL Context
IoT_protocol_name = "x-amzn-mqtt-ca"
ssl_context = ssl.create_default_context()
ssl_context.set_alpn_protocols([IoT_protocol_name])
ssl_context.load_verify_locations(cafile=PATH_TO_ROOT)
ssl_context.load_cert_chain(certfile=PATH_TO_CERT, keyfile=PATH_TO_KEY)

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


client = mqtt.Client()
client.tls_set_context(context=ssl_context)
#client.username_pw_set("test")
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect(ENDPOINT, PORT, 60)


# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_start()


while not client.is_connected():
    logger.error("Waiting to connect")
    time.sleep(1)
temperature = 0
humidity = 10
while(1):
    if(client.is_connected()):
        message = {"temperature":temperature,"humidity":humidity}
        client.publish(topic = TOPIC,payload = json.dumps(message))
        temperature += 1
    time.sleep(1)
    