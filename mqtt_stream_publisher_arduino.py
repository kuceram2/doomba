#!/usr/bin/env python
"""
IMPORTANT
vyžaduje 2 parametry - ip adresa brokeru, COM port kde je arduino
"""

import cv2
import threading
import paho.mqtt.client as mqtt
import time
import sys
import serial

# Inicializace globálních proměnných
frame_count = 0
cmd_count = 0
frame_rate = 10
prev = 0
run = True

# Získání ip adresy brokeru a sériového portu z argumentů příkazové řádky
host = str(sys.argv[1])
serialPort = serial.Serial(port=sys.argv[2], baudrate=9600)
port = 1883

# Třída pro streamování snímků z kamery a odesílání příkazů k pohybu
class Stream_publisher:
    
    def __init__(self,host, port) -> None :
          
        self.client = mqtt.Client()  # vytvoření nové instance mqtt clienta
        
        # názvy mqtt topiců
        self.data_topic = "doomba/robot-data"
        self.movement_topic = "doomba/robot-movement"
        self.speed_topic = "doomba/robot-speed"
        self.light_topic ="doomba/robot-light"
        self.spotlight_topic = "doomba/robot-spotlight"
        
        self.client.on_connect = self.on_connect  # definice callback funkce pro úspěšné připojení

        self.client.message_callback_add("doomba/robot-movement",self.on_movement) # callback funkce pro přijetí příkazu k pohybu
        self.client.message_callback_add("doomba/robot-speed",self.on_speed) # callback funkce pro změnu rychlosti
        self.client.message_callback_add("doomba/robot-light",self.on_light) # callback funkce pro zapnutí/vypnutí podsvícení
        self.client.message_callback_add("doomba/robot-spotlight",self.on_spotlight) # callback funkce pro zapnutí/vypnutí hledáčku
        
        self.client.connect(host, port) # připojení klienta k brokeru
        
        self.client.loop_start() # spuštění smyčky pro příjem zpráv z brokeru
        
        self.video_source=0 # index webkamery
        
        self.cam = cv2.VideoCapture(self.video_source)  # inicializace kamery
       
    def on_connect(self,client, userdata, flags, rc):  # callback funkce pro připojení klienta k brokeru
        self.client.subscribe(self.movement_topic)  # přihlášení k odběru příkazů k pohybu
        self.client.subscribe(self.speed_topic) # přihlášení k odběru zpráv o změně rychlosti
        self.client.subscribe(self.light_topic) # přihlášení k odběru zpráv o zapnutí/vypnutí podsvícení
        self.client.subscribe(self.spotlight_topic) # přihlášení k odběru zpráv o zapnutí/vypnutí hledáčku
        print("PŘÍJÍMÁNÍ CMD's z: ", self.movement_topic)
    
    def stream(self, frame_count):  # funkce pro streamování snímků z kamery
        _ , img = self.cam.read() # čtení snímku z kamery
        
        try:
            img_str = cv2.imencode('.jpg', img)[1].tobytes() # převod snímku na string

            self.client.publish(self.data_topic, img_str) # publikování snímku na topic
            print("frame sent:", frame_count)
            
        except cv2.error:
            print("waiting for video")
            
        count = frame_count + 1
        return count

    def on_movement(self,client, userdata, msg):  # callback funkce pro příjem příkazů k pohybu
        global cmd_count
        print("přijat cmd číslo: ", cmd_count)
        command = str(msg.payload.decode("utf-8"))
        serialPort.write(bytes(command, 'utf-8'))
        print("CMD: ", command)
        cmd_count += 1
           
    def on_speed(self,client, userdata, msg): # callback funkce pro příjem zpráv o změně rychlosti
        print("změněna rychlost")
        command = str("r" + msg.payload.decode("utf-8"))
        print(command)
        serialPort.write(bytes(command, 'utf-8'))
        
    def on_light(self,client, userdata, msg): # callback funkce pro příjem zpráv o zapnutí/vypnutí podsvícení
        command = str(msg.payload.decode("utf-8"))
        if command == "True":
            serialPort.write(bytes("t", 'utf-8'))
        elif command == "False":    
            serialPort.write(bytes("f", 'utf-8'))
        print("podsvícení: ", command)
        
    def on_spotlight(self,client, userdata, msg): # callback funkce pro příjem zpráv o zapnutí/vypnutí hledáčku
        command = str(msg.payload.decode("utf-8"))
        if command == "True":
            serialPort.write(bytes("g", 'utf-8'))
        elif command == "False":    
            serialPort.write(bytes("h", 'utf-8'))
        print("reflektor: ", command)
        
if __name__ == "__main__":
    webcam = Stream_publisher(host=host, port=port)  # inicializace instance Stream_publisher
    while True:
        # posílání snímků z kamery, frekvence odesílání je dána proměnnou frame_rate, aby nedocházelo k zahlcení
        try:
            time_elapsed = time.time() - prev
            if time_elapsed > 1./frame_rate:
                frame_count = webcam.stream(frame_count=frame_count)
                prev = time.time()
                
        except KeyboardInterrupt: 
            print("\nterminating...")
            webcam.client.loop_stop()
            sys.exit()