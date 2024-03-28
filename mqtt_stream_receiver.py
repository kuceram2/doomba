#!/usr/bin/env python

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
import webbrowser
i = 0
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

camColumn = [
    [sg.Text('CAMERA', size=(7, 1))],
    [sg.Button("↑", size=(7,2), key="camUp")],
    [sg.Button("↓", size=(7,2), key="camDown", )]
]
layout = [
        [sg.Graph(canvas_size=(30, 30), graph_bottom_left=(0, 0), graph_top_right=(30, 30), key='graph'),
         sg.Text("REC")
         ],
        [sg.Image(filename= "./resource/DOOMBA.png", key="-IMAGE-"),
         sg.Column(speedColumn),
         sg.VerticalSeparator(),
         sg.Column(camColumn, element_justification='c')
         ],
        # sg.Graph(canvas_size=(400, 400), graph_bottom_left=(0, 0), graph_top_right=(400, 400), key='radar')],
        [sg.Button("Screenshot", key="PrtScr"),
         sg.Button("Start/Stop recording", key="rec", disabled=True),
         sg.Text("Bottom light:"),
         sg.Button("OFF", size=(3,1), button_color=('white', 'red'), key="light"),
         sg.Text("Spotlight:"),
         sg.Button("OFF", size=(3,1), button_color=('white', 'red'), key="spotlight")],
        [sg.Button("Exit"), 
         sg.Button("Help!", key="help", pad=((650,0),(0,0))) ]
    ]
# inicializace okna
window = sg.Window("D.O.O.M.B.A Controller", layout, resizable=True, finalize=True, icon="./resource/doomba.ico")
graph = window["graph"]
graph.draw_circle((15, 15), 10, fill_color='white', line_color='white')


class Mqtt_client:

    def __init__(self, host, port) -> None:

        self.frame=None  # prázdá proměná pro uložení snímku
        self.movement_topic = "doomba/robot-movement"
        self.data_topic = "doomba/robot-data"
        self.speed_topic = "doomba/robot-speed"
        self.light_topic = "doomba/robot-light"
        self.spotlight_topic = "doomba/robot-spotlight"
        self.rec = False
        self.lightState = False
        self.spotlightState = False
        self.lastCmd = time.time()
        self.videoTimeout = time.time()
        self.videoBegan = False

        self.client = mqtt.Client()  # Vyvoření nové instance mqtt clienta 
        self.client.on_connect = self.on_connect  # nastavení callback funkce pro úspěšné připojení
        #callback funkce pro příjem zpráv na topicu doomba/robot-movement
        self.client.message_callback_add(self.data_topic, self.on_cam_message)
        
        # připojení k brokeru
        self.client.connect(host,port) 
        
        # start smyčky pro příjem zpráv z brokeru
        self.client.loop_start()
        
    def on_connect(self,client, userdata, flags, rc):  # callback funkce pro úspěšné připojení
        print("Success connecting to MQTT broker...")
        self.client.subscribe(self.data_topic)  # přihlášení k odběru zpráv na topicu doomba/robot-data
        print("Subscribed to topic doomba/robot-data")
        
    def rec_video(self): # funkce pro zahájení/zastavení záznamu videa (pouze pro testovací účely)
        if self.rec == False:
            print("recording started")
            os.chdir("./photos")
            fourcc = cv2.VideoWriter_fourcc(*'MP42')
            name = "vid" + str(time.time()) + ".mp4"
            self.out = cv2.VideoWriter(name, fourcc, 3.0, (600, 400))
            graph.draw_circle((15, 15), 10, fill_color='red', line_color='red')
            self.rec = True
        elif self.rec == True:
            print("recording ENDED")
            self.out.release()
            graph.draw_circle((15, 15), 10, fill_color='white', line_color='white')

            self.rec = False
          
    def on_cam_message(self,client, userdata, msg):  # callback funkce pro příjem snímků z kamery
        global i
        self.videoBegan = True
        self.videoTimeout = time.time()
        i=i+1
        nparr = np.frombuffer(msg.payload, np.uint8)
        self.frame = cv2.imdecode(nparr,  cv2.IMREAD_COLOR)
        #self.frame= cv2.resize(self.frame, (600,400))   # možnost změny velikosti snímku
        
        # převod snímku do formátu vhodného pro zobrazení v okně
        img_bytes = cv2.imencode(".png", cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))[1].tobytes()
        queue.put(img_bytes)
        print("Recieved frame num: ", i)
        
        try: 
            self.out.write(self.frame)
            print("frame added")
        except AttributeError: 
            print("RECORDING INACTIVE")

    def save_img(self): # funkce pro uložení snímku
        self.filename = "img" + str(time.time()) + ".jpg"
        os.chdir("./photos")
        cv2.imwrite(self.filename, self.frame)
        print("image saved")

    def showFrame(self): # funkce pro zobrazení snímku v okně
        if not queue.empty():
            img_bytes = queue.get()
            try:
                window["-IMAGE-"].update(data=img_bytes)
                print("frame displayed")
            except sg.exceptions.PySimpleGUIInvalidWidgetOrParent:
                pass

    def check_keyboard(self,event, values): # funkce pro kontrolu stisknutých kláves a událostí v okně
        cmd = ""
        delay = 0.3
        # pohyb doleva
        if keyboard.is_pressed('a'): 
                cmd += "a"
                self.client.publish(self.movement_topic, cmd)
                print("command send: ",cmd)
                self.lastCmd = time.time()

        # pohyb doprava
        elif keyboard.is_pressed('d'): 
            cmd += "d"
            self.client.publish(self.movement_topic, cmd)
            print("command send: ",cmd)
            self.lastCmd = time.time()
            
        # pohyb dopředu
        elif keyboard.is_pressed('w'): 
            cmd += "w"
            self.client.publish(self.movement_topic, cmd)
            print("command send: ",cmd)
            self.lastCmd = time.time()
            
        # pohyb dozadu
        elif keyboard.is_pressed('s'): 
            cmd += "s"
            self.client.publish(self.movement_topic, cmd)
            print("command send: ",cmd)
            self.lastCmd = time.time()

        # náklon kamery nahoru
        elif keyboard.is_pressed('n') or event == "camUp":
            cmd += "n"
            self.client.publish(self.movement_topic, cmd)
            print("command send: ",cmd)
            self.lastCmd = time.time()
            
        # náklon kamery dolů    
        elif keyboard.is_pressed('m') or event == "camDown":
            cmd += "m"
            self.client.publish(self.movement_topic, cmd)
            print("command send: ",cmd)
            self.lastCmd = time.time()
            
        # uložení fotky
        elif keyboard.is_pressed('f') or event == "PrtScr":
            try:
                self.save_img()
                time.sleep(2*delay)
            except cv2.error:
                print("no frames recieved yet...")
            self.lastCmd = time.time() 
            
        # zvýšení rychlosti -tlačítko
        elif keyboard.is_pressed('c') or event == "speedUp":
            speed = int(values['speed'])
            speed += 5
            window['speed'].update(speed)
            self.client.publish(self.speed_topic, speed)
            print("speed increased")
            self.lastCmd = time.time()

        elif keyboard.is_pressed('x') or event == "speedDown":
            speed = int(values['speed'])
            speed -= 5
            window['speed'].update(speed)
            self.client.publish(self.speed_topic, speed)
            print("speed decreased")
            self.lastCmd = time.time()
        
        # nastavení rychlosti - slider
        elif event == "speed":
            speed = int(values['speed'])
            print("speed set to: ", speed)
            self.client.publish(self.speed_topic, speed)
            self.lastCmd = time.time()
            
        # zapnutí/vypnutí podsvícení
        elif keyboard.is_pressed('e') or event == "light":
            self.lightState = not self.lightState
            window['light'].update(text='On' if self.lightState else 'Off', button_color='white on green' if self.lightState else 'white on red')
            self.client.publish(self.light_topic, self.lightState)
            self.lastCmd = time.time()
            
        # zapnutí/vypnutí hledáčku    
        elif keyboard.is_pressed('r') or event == "spotlight":
            self.spotlightState = not self.spotlightState
            window['spotlight'].update(text='On' if self.spotlightState else 'Off', button_color='white on green' if self.spotlightState else 'white on red')
            self.client.publish(self.spotlight_topic, self.spotlightState)
            self.lastCmd = time.time()
            
        elif event == "help":
            webbrowser.open("https://github.com/kuceram2/doomba/blob/main/README.md")       
        # ukončení programu                   
        elif keyboard.is_pressed('p'): 
            print("terminating...")
            self.client.disconnect()
            sys.exit()
        cmd = ""        

     
if __name__ == "__main__":
    Client = Mqtt_client(host, port)
    queue = Queue(maxsize=2)
    for thread in threading.enumerate(): 
        print(thread.name)
    
    while True:
        event, values = window.read(timeout=10)  # Timeout is in milliseconds
        
        if event == sg.WINDOW_CLOSED or event == "Exit":
            print("terminating...")
            Client.client.disconnect()
            break
        
        if (time.time() - Client.lastCmd) > 0.2: Client.check_keyboard(event, values) # příkaz se odesílá maximálně každých 0.2s
        if (time.time() - Client.videoTimeout) > 2 and Client.videoBegan == True: 
            print("Video stream lost! \n Hope it gets fixed soon...¯\_(ツ)_/¯ ")
            window['-IMAGE-'].update(filename="./resource/lostConnImg.png", size=(600,400))
            Client.videoTimeout = time.time()
        Client.showFrame()  # Update the window
        

    
    
