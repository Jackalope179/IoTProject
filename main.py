import random
import paho.mqtt.client as mqttclient
import time
import json
import subprocess as sp
import re

accuracy = 3 
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "k5mLqCRJuG5Ho7J2ik4a"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

Longitude = 106.6297
Latitude =  10.8231

while True:
    ''' Random tempernature and humidity '''
    temp = random.randint(30, 100)
    humi = random.randint(50, 100)

    pshellcomm = ['powershell']
    pshellcomm.append('add-type -assemblyname system.device; '\
                      '$loc = new-object system.device.location.geocoordinatewatcher;'\
                      '$loc.start(); '\
                      'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) '\
                      '{start-sleep -milliseconds 100}; '\
                      '$acc = %d; '\
                      'while($loc.position.location.horizontalaccuracy -gt $acc) '\
                      '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; '\
                      '$loc.position.location.latitude; '\
                      '$loc.position.location.longitude; '\
                      '$loc.position.location.horizontalaccuracy; '\
                      '$loc.stop()' %(accuracy))
    p = sp.Popen(pshellcomm, stdin = sp.PIPE, stdout = sp.PIPE, stderr = sp.STDOUT, text=True)
    (out, err) = p.communicate()
    out = re.split('\n', out)

    latitude = float(out[0])
    longitude = float(out[1])

    collect_data = {'temperature': temp, 'humidity': humi, 'longitude':longitude, 'latitude':latitude, 'Longitude':Longitude, 'Latitude':Latitude}
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(1)

