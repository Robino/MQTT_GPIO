#!/usr/bin/python3
import sys
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import  time

broker="192.168.0.8"
#define callback
def on_message(client, userdata, message):
   msg=str(message.payload.decode("utf-8"))
   #on ne garde que le dernier champs du topic correspondant au numéro de GPIO
   topic=message.topic.rsplit('/',1)[1]
   print ("topic transfo GPIO", topic)
   messages.append([topic,msg])
def on_connect(client, userdata, flags, rc):

    if rc==0:
        client.connected_flag=True
        client.subscribe(sub_topic)
    else:
        client.bad_connection_flag=True
        client.connected_flag=False

GPIO.setwarnings(False)
GPIO.cleanup()

cpio_channels=[18,17,15,14]# base channels
print("using ",sys.version) #what version of python
GPIO.setmode(GPIO.BCM)

#on indique toutes les GPIO sont de type OUTPUT
for i in range(len(cpio_channels)):
    print("SETUP GPIO " + str(cpio_channels[i]))
    GPIO.setup(cpio_channels[i],GPIO.OUT)
    GPIO.output(cpio_channels[i],GPIO.HIGH)
    


##MQTT
messages=[]
sub_topic="maison/piscine/set/#" # on attend les ordres de la centrale
pub_topic="maison/piscine/status/" # on informe du statut réel du device
client= mqtt.Client("GPIO-client-001")  #create client object client1.on_publish = on_publish                          #assign function to callback client1.connect(broker,port)                                 #establish connection client1.publish("house/bulb1","on")  
######
client.on_message=on_message
client.on_connect=on_connect
client.connected_flag=False
client.connect(broker)#connect
while True:
    client.loop(0.01)
    time.sleep(1)
    if len(messages)>0:
        m=messages.pop(0)
        print("received ",m)
        GPIO.output(int(m[0]),int(m[1])) #set
        print("GPIO activé "+ m[0] + " value is " + m[1])
    else:
       #On publie le status réel du GPIO (en cas de panne ou d'arret pour que la centrale ait la bonne information" 
       for i in range(len(cpio_channels)):
           client.publish(pub_topic + str(cpio_channels[i]),GPIO.input(cpio_channels[i])) 
