#!/usr/bin/env python
"""
IMPORTANT
vyžaduje 2 parametry - ip adresa brokeru, COM port kde je arduino
"""

"""Stream_publisher.py: Odesílá video stream přes Mosquitto Mqtt topic """

import cv2
import threading
import paho.mqtt.client as mqtt
import time
import sys
import serial

# Set initial variables
frame_count = 0
cmd_count = 0
frame_rate = 10
prev = 0
run = True

# Get host and serial port from command line arguments
host = str(sys.argv[1])
serialPort = serial.Serial(port=sys.argv[2], baudrate=9600)
port = 1883
pub_topic = "cam-data"
sub_topic = "cam-cmd"
speed_topic = "cam-speed"
light_topic = "cam-light"

# Define Stream_publisher class
class Stream_publisher:
    
    def __init__(self,host, port, pub_topic, sub_topic, speed_topic, light_topic) -> None :
          
        self.client = mqtt.Client()  # vytvoření nové instance
        
        self.pub_topic = pub_topic
        self.sub_topic = sub_topic
        self.speed_topic = speed_topic
        self.light_topic = light_topic
        
        self.client.on_connect = self.on_connect  # definice callback funkce pro úspěšné připojení

        self.client.message_callback_add("cam-cmd",self.on_command)
        self.client.message_callback_add("cam-speed",self.on_speed)
        self.client.message_callback_add("cam-light",self.on_light)
        
        self.client.connect(host, port)
        
        self.client.loop_start() # spuštění loopu
        
        self.video_source=0 # index webkamery
        
        self.cam = cv2.VideoCapture(self.video_source)  

        
    def on_connect(self,client, userdata, flags, rc):  # callback funkce pro připojení klienta k brokeru
        self.client.subscribe(self.sub_topic)  # přihlášení k odběru zpráv z daného topicu
        self.client.subscribe(self.speed_topic) # přihlášení k odběru zpráv z daného topicu
        self.client.subscribe(self.light_topic) # přihlášení k odběru zpráv z daného topicu
        print("PŘÍJÍMÁNÍ CMD's z: ", self.sub_topic)
    
    def stream(self, frame_count):
        
        """
        Streamuje video na zadaný Mqtt topic

        :return: None
        """
        _ , img = self.cam.read() # čtení snímku z kamery
        
        try:
            img_str = cv2.imencode('.jpg', img)[1].tobytes() # převod snímku na string

            self.client.publish(self.pub_topic, img_str) # publikování snímku na topic
            print("frame sent:", frame_count)
            
        except cv2.error:
            print("waiting for video")
            
        prev = time.time()
        count = frame_count + 1
        return count

    def on_command(self,client, userdata, msg):  # callback funkce pro příjem zprávy z brokeru
        global cmd_count
        print("přijat cmd číslo: ", cmd_count)
        command = str(msg.payload.decode("utf-8"))
        serialPort.write(bytes(command, 'utf-8'))
        print("CMD: ", command)
        cmd_count += 1
           
    def on_speed(self,client, userdata, msg):
        print("změněna rychlost")
        command = str("r" + msg.payload.decode("utf-8"))
        print(command)
        serialPort.write(bytes(command, 'utf-8'))
        
    def on_light(self,client, userdata, msg):
        print("světlo zapnuto")
        command = str(msg.payload.decode("utf-8"))
        if command == "True":
            serialPort.write(bytes("t", 'utf-8'))
        elif command == "False":    
            serialPort.write(bytes("f", 'utf-8'))
        print("světlo: ", command)
        
if __name__ == "__main__":
    webcam = Stream_publisher(host=host, port=port, pub_topic=pub_topic, sub_topic=sub_topic, speed_topic=speed_topic)  # streamování z webkamery (0) na topic: "test"
    while True:
        try:
            time_elapsed = time.time() - prev
            if time_elapsed > 1./frame_rate:
                frame_count = webcam.stream(frame_count=frame_count)
                prev = time.time()
                
        except KeyboardInterrupt: 
            print("\nterminating...")
            webcam.client.loop_stop()
            sys.exit()
        #  servo.angle = servoState