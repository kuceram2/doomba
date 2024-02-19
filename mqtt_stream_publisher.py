#!/usr/bin/env python
"""Stream_publisher.py: Send video stream via Mosquitto Mqtt topic """


# dataPublisher = posílá video na broker na topic "cam-data"
# cmdReciever = přijímá příkazy z brokeru z topicu "cam-cmd"



import cv2
import threading
import paho.mqtt.client as mqtt
from time import sleep
import time
import sys


#servo = Servo(14)

servoState = 0
servoStateOld = 0
i = 0
frame_rate = 10
prev = 0
run = True

#servo = AngularServo(12, initial_angle=0, min_angle=-90, max_angle=90,min_pulse_width=0.0006, max_pulse_width=0.0023)

host = str(sys.argv[1])
port = 1883
class Stream_publisher:
    
    def __init__(self,topic, video_address=0) -> None :
        global host, port
        """
        Construct a new 'stream_publisher' object to broadcast a video stream using Mosquitto_MQTT

        :return: returns nothing
        """
        
        self.dataPublisher = mqtt.Client()  # create new instance
        
        self.dataPublisher.connect(host, port)
        self.topic=topic
        self.video_source=video_address
        
        #self.cam = cv2.VideoCapture(0)  # webcam
        #self.cam = cv2.VideoCapture("example_video.mkv")  # place video file 
        self.cam = cv2.VideoCapture(self.video_source)  

        self.streaming_thread= threading.Thread(target=self.stream).start()
        print("stream thread active")
    


    def stream(self):
        global frame_rate, prev, i
        
        time_elapsed = time.time() - prev
        res, image = self.cam.read()

        if time_elapsed > 1./frame_rate:
            prev = time.time()
    
            _ , img = self.cam.read()
            img = cv2.resize(img, (480 ,360))  # to reduce resolution 
            try:
                img_str = cv2.imencode('.jpg', img)[1].tobytes()

                self.dataPublisher.publish(self.topic, img_str)
                print("frame sent:", i)
                i += 1
            except cv2.error:
                print("waiting for video")

class Cmd_receiver:

    def __init__(self, topic=''):
        global host, port
        
        
        print("init of reciever")
        self.topic=topic
        
        self.cmdReciever = mqtt.Client()  # Create instance of client 

        self.cmdReciever.on_connect = self.on_connect  # Define callback function for successful connection
        
        self.cmdReciever.message_callback_add(self.topic,self.on_message)
        
        self.cmdReciever.connect(host,port)  # connecting to the broking server
        
        t=threading.Thread(target=self.subscribe).start()
        
    def subscribe(self):
        self.cmdReciever.loop_start() # Start networking daemon
        print("Opened reciever thread")
        
    def on_connect(self,client, userdata, flags, rc):  # The callback for when the client connects to the broker
        client.subscribe(self.topic)  # Subscribe to the topic, receive any messages published on it
        print("RECIEVING CMD's from:",self.topic)


    def on_message(self,client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
        global i
        global servoState
        print("recieved CMD num: ", i)
        i=i+1
        command = str(msg.payload.decode("utf-8"))
        print("CMD: ", command)
        if "a" in command and servoState < 78:
            servoState = servoState + 10
        elif "d" in command and servoState > -78:
            servoState = servoState - 10
        print("servoState: ",servoState)
            

if __name__ == "__main__":
    webcam= Stream_publisher(topic="cam-data")  # streaming from webcam (0) to  topic : "test"
    reciever = Cmd_receiver(topic="cam-cmd")
    while True:
        try:
            webcam.stream()
            # if servoState != servoStateOld:
            #     servo.angle = servoState
            #     servoStateOld = servoState
        except KeyboardInterrupt: 
            print("\nterminating...")
            reciever.cmdReciever.loop_stop()
            sys.exit()
      #  servo.angle = servoState
        
        
    
    

