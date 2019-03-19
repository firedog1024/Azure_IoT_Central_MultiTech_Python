# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

# Sample code to attach a client to Azure IoT Central using the Device Provisioning Service (DPS).
# Uses Paho MQTT client to connect to Azure IoT Hub MQTT broker.
# 
# Handles the following:
#   + Connect to IoT Hub/Central using DPS symetric key
#   + Reconnect on SAS token expiration
#   + Sending telemetry data
#   + Digital Twin Desired (settings) and Reported (properties) properties () = IoT Central terminology
#   + Direct method handling
#   + Cloud to Device calls
#   

import paho.mqtt.client as mqtt
import time
import base64
import hmac 
import hashlib
import binascii
import ssl
import random
import json

# local code imports 
import azure_iot_dps as dps
import config

# global variables
got_twin = False
connected = False
reported_rid = 10
get_twin_rid = 20
retain_policy = False
qos_policy = 1
iot_hub_hostname = ''
client = None

# compute a device key using the application key and the device identity
def _computeDrivedSymmetricKey(app_key, deviceId):
    app_key = base64.b64decode(app_key)
    return base64.b64encode(hmac.new(app_key, msg=deviceId.encode('utf8'), digestmod=hashlib.sha256).digest())

# Generate an Azure SAS token for presenting as the password in MQTT connect
def gen_sas_token(hub_host, device_name, key, token_timeout):
    global token_expiry
    token_expiry = int(time.time() + token_timeout)
    uri = '{}/devices/{}'.format(hub_host, device_name)
    string_to_sign = ('{}\n{}'.format(uri, token_expiry)).encode('utf-8')
    signed_hmac_sha256 = hmac.new(binascii.a2b_base64(key), string_to_sign, hashlib.sha256)
    signature = urlencode(binascii.b2a_base64(signed_hmac_sha256.digest()).decode('utf-8'))
    if signature.endswith('\n'):  # somewhere along the crypto chain a newline is inserted
        signature = signature[:-1]
    return 'SharedAccessSignature sr={}&sig={}&se={}'.format(uri, signature, token_expiry)

# Simple URL Encoding routine
def urlencode(string):
    badChar = [';', '?', ':', '@', '&', '=', '+', '$',  ',']
    goodChar = ['%3B', '%3F', '3A', '%40', '%26', '%3D', '%2B', '%24', '%2C']
    strArray = list(string)
    i = 0
    for ch in strArray:
        if ch in badChar:
            strArray[i] = goodChar[badChar.index(ch)]
        i += 1
    return ''.join(strArray)

# Paho MQTT standard callback handlers for connect, disconnect, messgae publishing
def on_connect(client, userdata, flags, rc):
    global connected
    print('Connected rc: {}'.format(rc))
    connected = True

def on_disconnect(client, userdata, rc):
    global connected
    print('Disconnected rc: {}'.format(rc))
    connected = False

    # reconnect the client
    connect()

def on_message(client, userdata, msg):
    if msg.retain == 1:
        print('message retained')
    print(' - '.join((msg.topic, str(msg.payload))))

def on_publish(client, userdata, mid):
    print('Published - id:{}'.format(mid))

# Handler for Azure IoT Digital Twin responses
def get_twin_callback(client, userdata, msg):
    global twin
    if msg.topic.index('res/20') > -1:
        if msg.topic.find('$rid=20') > -1: # get twin property response
            twin = msg.payload.decode('utf-8')
            print('Twin: \n{}'.format(twin))
        elif msg.topic.find('$rid=10') > -1: # reported property response
            print('reported property accepted')
    else:
        print('Error: {} - {}'.format(msg.topic, msg.payload))

# Send acknowledgement on receipt of a desired property
def desired_ack(json_data, status_code, status_text):
    # respond with IoT Central confirmation
    key_index = json_data.keys().index('$version')
    if key_index == 0:
        key_index = 1
    else:
        key_index = 0

    the_value = json_data[json_data.keys()[key_index]]['value']
    if type(the_value) is bool:
        if the_value:
            the_value = "true"
        else:
            the_value = "false" 
    reported_payload = '{{"{}":{{"value":{},"statusCode":{},"status":"{}","desiredVersion":{}}}}}'.format(json_data.keys()[key_index], the_value, status_code, status_text, json_data['$version'])
    send_reported_property(reported_payload)

# Handler for Azure IoT Digital Twin deired properties (settings in IoT Central terminology)
def desired_twin_callback(client, userdata, msg):
    desired = msg.payload.decode('utf-8')
    print('Desired property: \n{}'.format(desired))
    json_data = json.loads(desired)
    # must acknowledge the receipt of the desired property for IoT Central
    desired_ack(json_data, 200, 'completed')

# Handler for Azure IoT Hub Cloud to Device message - not available from IoT Central
def c2d_callback(client, userdata, msg):
    print('Cloud to Device message')

# Handler for IoT Central Direct Method
def direct_method_callback(client, userdata, msg):
    start_idx = msg.topic.index('/POST/')+6
    method_name = msg.topic[start_idx:msg.topic.index('/', start_idx)]
    parameters = msg.payload
    print('Direct method - method: {}, parameters: {}'.format(method_name, parameters))

    # acknowledge receipt of the command
    request_id = msg.topic[msg.topic.index('?$rid=')+6:]
    client.publish('$iothub/methods/res/{}/?$rid={}'.format('200', request_id), '', qos=qos_policy, retain=retain_policy)

# Force pull the digital twin for the device
def get_twin():
    global got_twin
    client.publish('$iothub/twin/GET/?$rid={}'.format(get_twin_rid), None, qos=qos_policy, retain=retain_policy)
    got_twin = True

# Send a telemetry to IoT Central
def send_telemetry(device_id, payload):
    client.publish('devices/{}/messages/events/'.format(device_id), payload, qos=qos_policy, retain=False)
    print('sent a message: {}'.format(payload))

# Send a reported property to IoT Central
def send_reported_property(payload):
    client.publish('$iothub/twin/PATCH/properties/reported/?$rid={}'.format(reported_rid), payload, qos=qos_policy, retain=retain_policy)
    print('sent a reported property: {}'.format(payload))

# Connect to the IoT Hub MQTT broker
def connect():
    # compute the device key
    device_key = _computeDrivedSymmetricKey(config.APP_KEY, config.DEVICE_NAME)

    # set username and compute the password
    username = '{}/{}/api-version=2016-11-14'.format(iot_hub_hostname, config.DEVICE_NAME)
    password = gen_sas_token(iot_hub_hostname, config.DEVICE_NAME, device_key, config.SAS_TOKEN_TTL)
    client.username_pw_set(username=username, password=password)
    
    # connect to Azure IoT Hub via MQTT
    client.connect(iot_hub_hostname, port=8883)

# DPS registration callback
def myCallback(error, hub):
    global registration_done
    global iot_hub_hostname

    if error != None:
        print('FAILED: ')
        print(error)
    else:
        if iot_hub_hostname == '':
            iot_hub_hostname = hub
    registration_done = True

# Main function for the program logic including message loop
def start():
    global registration_done
    global client

    startup = True
    registration_done = False
    last_telemetry_sent = int(time.time())
    last_reported_property_sent = int(time.time())

    if config.MODEL_ID == '':
        # call without model identifier if not using auto associate or the device is already registered and assigned to a template
        dps.getConnectionString(config.DEVICE_NAME, config.APP_KEY, config.SCOPE_ID, True, myCallback)
    else:
        # call with a model identifier if doing auto association
        dps.getConnectionString(config.DEVICE_NAME, config.APP_KEY, config.SCOPE_ID, True, myCallback, config.MODEL_ID)

    while not registration_done:
        time.sleep(0.05)

    print('creating new MQTT instance')
    client = mqtt.Client(client_id=config.DEVICE_NAME, protocol=mqtt.MQTTv311)

    # setup Paho for secure MQTT
    if config.VALIDATE_CERT:
        # validate the cert from Azure IoT Hub
        client.tls_set(ca_certs=config.PATH_TO_ROOT_CERT, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
    else:
        # dont bother validating the cert from Azure IoT Hub
        client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=None, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
    client.tls_insecure_set(False)

    # set callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_publish = on_publish

    # initial connect to Azure IoT Hub
    connect()

    # loop forever, user should change to terminate cleanly on a system event
    while True:
        # initialize the needed subscriptions and force pull the digital twin
        if connected and startup:
            # initialize twin support
            client.subscribe('$iothub/twin/res/#')
            client.message_callback_add('$iothub/twin/res/#', get_twin_callback)

            # desired properties subscribe
            client.subscribe('$iothub/twin/PATCH/properties/desired/#')
            client.message_callback_add('$iothub/twin/PATCH/properties/desired/#', desired_twin_callback)

            # Direct method subscribe
            client.subscribe('$iothub/methods/POST/#')
            client.message_callback_add('$iothub/methods/POST/#', direct_method_callback)

            # Cloud to Device message subscribe
            client.subscribe('devices/{}/messages/devicebound/#'.format(config.DEVICE_NAME))
            client.message_callback_add('devices/{}/messages/devicebound/#'.format(config.DEVICE_NAME), c2d_callback)
            startup = False

            # force a twin pull
            get_twin()

        # every 5 seconds send a telemetry message
        if connected and (int(time.time()) - last_telemetry_sent >= 5):
            temp = random.randint(20, 50)
            payload = '{{"temp":{}}}'.format(temp)

            # send the telemetry payload
            send_telemetry(config.DEVICE_NAME, payload)

            last_telemetry_sent = time.time()

        # every 15 seconds send a reported property
        if connected and (int(time.time()) - last_reported_property_sent >= 15):
            # generate a random die roll for the payload
            die_number = random.randint(1, 6)
            payload = '{{"dieNumber": {}}}'.format(die_number)

            # send the reported property
            send_reported_property(payload)
            
            last_reported_property_sent = time.time()

        # yield to handle MQTT messaging    
        client.loop()

    # disconnect cleanly from the MQTT broker
    client.disconnect()
