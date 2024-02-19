#!/usr/bin/env python
"""Stream_publisher.py: Send video stream via Mosquitto Mqtt topic """

import cv2
import threading
import numpy as np
import paho.mqtt.client as mqtt
import keyboard
import PySimpleGUI as sg
import time
import sys
import os
from queue import Queue
i =0
cmd = ""
speed = 30
host = str(sys.argv[1])
port = 1883



speedButtons = [[sg.Button("+", size=(5,1), key="speedUp")],
               [sg.Button("-", size=(5,1), key="speedDown")]]

speedColumn = [
    [sg.Text('SPEED [m/s]', justification="right", size=(10, 1))],
    [sg.Slider(range=(0, 100), orientation='v', size=(10, 20), default_value=30, disabled=True, enable_events=True, key='speed'),
     sg.Column(speedButtons)]
]

layout = [
        [sg.Graph(canvas_size=(30, 30), graph_bottom_left=(0, 0), graph_top_right=(30, 30), key='graph'),
         sg.Text("REC")
         ],
        [sg.Image(filename= "C:/Users/skoka/OneDrive/Dokumenty/robot_smrti/resource/DOOMBA.png", key="-IMAGE-"),
         sg.Column(speedColumn) 
         ],
        # sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400), key='radar')],
        [sg.Button("Screenshot", key="PrtScr"),
         sg.Button("Start/Stop recording", key="rec"),
         sg.Text("Light:"),
         sg.Button("OFF", size=(3,1), button_color=('white', 'red'), key="light")],
        [sg.Button("Exit")]
    ]

window = sg.Window("Live Video Display", layout, resizable=True, finalize=True, icon="C:/Users/skoka/OneDrive/Dokumenty/robot_smrti/resource/doomba.ico")
graph = window["graph"]
graph.draw_circle((15, 15), 10, fill_color='white', line_color='white')


class Mqtt_client:

    def __init__(self, host, port) -> None:

        self.frame=None  # empty variable to store latest message received
        self.cmd_topic = "cam-cmd"
        self.data_topic = "cam-data"
        self.speed_topic = "cam-speed"
        self.light_topic = "cam-light"
        self.rec = False
        self.lightState = False

        self.client = mqtt.Client()  # Create instance of client 
        self.client.on_connect = self.on_connect  # Define callback function for successful connection
        # definice callback funkce pro příjem zpráv na topicu cam-data
        self.client.message_callback_add(self.data_topic, self.on_cam_message)
        
        # connecting to the broking server
        self.client.connect(host,port) 
        
        # starting the loop
        self.client.loop_start()
        
    def on_connect(self,client, userdata, flags, rc):  # The callback for when the client connects to the broker
        print("Success connecting to MQTT broker...")
        self.client.subscribe(self.data_topic)  # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        print("Subscribed to topic cam-data")
        
    def rec_video(self):
        if self.rec == False:
            print("recording started")
            os.chdir("C:/Users/skoka/OneDrive/Dokumenty/robot_smrti/photos")
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            name = "vid" + str(time.time()) + ".avi"
            self.out = cv2.VideoWriter(name, fourcc, 3.0, (600, 400))
            graph.draw_circle((15, 15), 10, fill_color='red', line_color='red')
            self.rec = True
        elif self.rec == True:
            print("recording ENDED")
            self.out.release()
            graph.draw_circle((15, 15), 10, fill_color='white', line_color='white')

            self.rec = False
          
    def on_cam_message(self,client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
        global i
                
        i=i+1
        nparr = np.frombuffer(msg.payload, np.uint8)
        self.frame = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
        #self.frame= cv2.resize(self.frame, (600,400))   # just in case you want to resize the viewing area
        #cv2.imshow('recv', self.frame)
        
         # Convert the OpenCV BGR format to RGB format
        img_bytes = cv2.imencode(".png", cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))[1].tobytes()
        queue.put(img_bytes)
        print("Recieved frame num: ", i)
        
        try: 
            self.out.write(self.frame)
            print("frame added")
        except AttributeError: 
            print("RECORDING INACTIVE")
        
        #self.showFrame()

    def save_img(self):
        self.filename = "img" + str(time.time()) + ".jpg"
        os.chdir("C:/Users/skoka/OneDrive/Dokumenty/robot_smrti/photos")
        cv2.imwrite(self.filename, self.frame)
        print("image saved")

    def showFrame(self):
        #while True:
        if not queue.empty():
            img_bytes = queue.get()
            try:
                window["-IMAGE-"].update(data=img_bytes)
                print("frame displayed")
            except sg.exceptions.PySimpleGUIInvalidWidgetOrParent:
                pass
            # event, values = window.read(timeout=20)  # Timeout is in milliseconds
            # if event == sg.WINDOW_CLOSED or event == "Exit":
            #     break
        
    
            
            #self.check_keyboard(event)
            
            #print("Streaming from video source : {}".format(self.video_source))

    def check_keyboard(self,event, values):
        delay = 0.3
        cmd = ""
        # pohyb doleva
        if keyboard.is_pressed('a'): 
                cmd += "a"
                self.client.publish(self.cmd_topic, cmd)
                print("command send: ",cmd)
                time.sleep(delay)
                
        # pohyb doprava
        elif keyboard.is_pressed('d'): 
            cmd += "d"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay)
            
        # pohyb dopředu
        elif keyboard.is_pressed('w'): 
            cmd += "w"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay)
            
        # pohyb dozadu
        elif keyboard.is_pressed('s'): 
            cmd += "s"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay)
            
        elif keyboard.is_pressed('x'): 
            cmd += "x"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay*4)

        # náklon kamery nahoru
        elif keyboard.is_pressed('n'):
            cmd += "n"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay)
            
        # náklon kamery dolů    
        elif keyboard.is_pressed('m'):
            cmd += "m"
            self.client.publish(self.cmd_topic, cmd)
            print("command send: ",cmd)
            time.sleep(delay)
            
        # uložení fotky
        elif keyboard.is_pressed('f') or event == "PrtScr":
            self.save_img()
            time.sleep(2*delay)

        # start/stop záznamu videa
        elif keyboard.is_pressed('v') or event == "rec":
            self.rec_video()
            time.sleep(delay*2)    
            
        # zvýšení rychlosti -tlačítko
        elif event == "speedUp":
            speed = int(values['speed'])
            speed += 5
            window['speed'].update(speed)
            self.client.publish(self.speed_topic, speed)
            print("speed increased")

        elif event == "speedDown":
            speed = int(values['speed'])
            speed -= 5
            window['speed'].update(speed)
            self.client.publish(self.speed_topic, speed)
            print("speed decreased")
        
        # nastavení rychlosti - slider
        elif event == "speed":
            speed = int(values['speed'])
            print("speed set to: ", speed)
            self.client.publish(self.speed_topic, speed)
            time.sleep(delay)
            
        # zapnutí/vypnutí světla
        elif event == "light":
            self.lightState = not self.lightState
            window['light'].update(text='On' if self.lightState else 'Off', button_color='white on green' if self.lightState else 'white on red')
            self.client.publish(self.light_topic, self.lightState)
            
        # ukončení programu                   
        elif keyboard.is_pressed('q'): 
            print("terminating...")
            self.client.disconnect()
            sys.exit()
        cmd = ""        

     
if __name__ == "__main__":
    Client = Mqtt_client(host, port)
    queue = Queue(maxsize=2)
    for thread in threading.enumerate(): 
        print(thread.name)
    # video_thread = threading.Thread(target=Client.on_cam_message, name="video_thread", daemon=True)
    # video_thread.start()
    
    while True:
        event, values = window.read(timeout=10)  # Timeout is in milliseconds
        
        if event == sg.WINDOW_CLOSED or event == "Exit":
            print("terminating...")
            Client.client.disconnect()
            break
        
        Client.check_keyboard(event, values)
        Client.showFrame()  # Update the window
    
        

    
    
