#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 22:19:49 2020

@author: Mike McGurrin
"""
import time
import os
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, Button, DigitalOutputDevice
Device.pin_factory = PiGPIOFactory()

import audio
import config as c

pir = Button(c.PIR_PIN, pull_up=False)
triggerOut = DigitalOutputDevice(c.TRIGGER_OUT_PIN)
eyesPin = DigitalOutputDevice(c.EYES_PIN)

class Tracks:
    def __init__(self):
        self.vocalTrackPos = 0
        self.vocalTrackLocation = 'vocals/'
        self.ambientTrackPos = 0
        self.ambientTrackLocation = 'ambient/'
        self.tracksDic = {1:'01', 2: '02', 3: '03', 4: '04', 5: '05', 6: '06',
                         7: '07', 8: '08', 9: '09', 10: '10'}
        # Determine which, if any, files are present
        self.vocalList = []
        self.ambientList = []
        for i in range(1,11):
            vocalTrackFile = self.vocalTrackLocation+'v'+self.tracksDic[i]+'.wav'
            if os.path.isfile(vocalTrackFile):
                self.vocalList.append(i)      
            ambientTrackFile = self.ambientTrackLocation+'v'+self.tracksDic[i]+'.wav'
            if os.path.isfile(ambientTrackFile):
                self.ambientList.append(i)

    def play_vocal(self):
        if self.vocalList != []:
            vocalFileName = 'v'+self.tracksDic[self.vocalList[self.vocalTrackPos]]+'.wav'
            vocalTrackFile = self.vocalTrackLocation+vocalFileName
            a.play_audio(vocalTrackFile)
            if self.vocalTrackPos == len(self.vocalList) - 1:
                self.vocalTrackPos = 0
            else:
                self.vocalTrackPos += 1
              
    def play_ambient(self):
        if self.ambientList != []:
            ambientFileName = 'v'+self.tracksDic[self.ambientList[self.ambientTrackPos]]+'.wav'
            ambientTrackFile = self.ambientTrackLocation+ambientFileName
            a.play_audio(ambientTrackFile)
            if self.ambientTrackPos == len(self.ambientList) - 1:
                self.ambientTrackPos = 0
            else:
                self.ambientTrackPos += 1
  
def event_handler():
    if c.AMBIENT == 'ON':
        a.stop()
    if c.EYES == 'ON':
        eyesPin.on()
    if c.TRIGGER_OUT == 'ON':
        triggerOut.on()
        time.sleep(0.5)
        triggerOut.off()
    if c.SOURCE == 'FILES':
        tracks.play_vocal()
    else:
        a.play_audio()
    if c.EYES == 'ON':
        eyesPin.off()
#     turn on ambient
    
a = audio.AUDIO()

try:
    if c.SOURCE == 'MICROPHONE':
        if c.PROP_TRIGGER == 'TIMER':
            start_time = time.time()
            while True:
                current_time = time.time()
                if current_time > start_time + c.DELAY:
                    event_handler()
                    start_time = time.time()
        elif c.PROP_TRIGGER == 'PIR':
            while True:
                pir.wait_for_press()
                event_handler()   
        elif c.PROP_TRIGGER == 'START':
            if c.TRIGGER_OUT == 'ON':
                triggerOut.on()
            if c.EYES == 'ON':
                eyesPin.on()
            a.play_audio()
        else:
            raise ValueError('PROP_TRIGGER set to improper value for MICROPHONE source')     
    elif c.SOURCE == 'FILES':
    # Loop forewver, when timer or PIR trigger occurs, call audio
    # If ambient tracks are set to play, then play them in between
        tracks = Tracks()
        if c.PROP_TRIGGER == 'TIMER':
            start_time = time.time()
            while True:
                current_time = time.time()
                if current_time > start_time + c.DELAY:
                    event_handler()
                    start_time = time.time()
        elif c.PROP_TRIGGER == 'PIR':
            while True:
                pir.wait_for_press()
                event_handler()           
        else:
            raise ValueError('PROP_TRIGGER set to improper value for FILES source')
except Exception as e:
    print(e)  
finally:
    pir.close()
    eyesPin.close()
    triggerOut.close()
    a.jaw.close()
    
        


    
        
