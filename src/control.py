"""
Created on Sun May 17 22:19:49 2020
Updated to fix bad calls to audio.play_audio Sat Dec 26 2020
@author: Mike McGurrin
"""

from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device, Button, DigitalOutputDevice
Device.pin_factory = PiGPIOFactory()

import time

import config as c
import tracks as t
import audio

tracks = t.Tracks()
a = audio.AUDIO()

pir = Button(c.PIR_PIN, pull_up=False)
triggerOut = DigitalOutputDevice(c.TRIGGER_OUT_PIN)
eyesPin = DigitalOutputDevice(c.EYES_PIN)
ambient_interrupt = False   # set to True when timer goes off or PIR triggered
trigger_time = time.time()

def event_handler():
    c.update()
    if c.EYES == 'ON':
        eyesPin.on()
    if c.TRIGGER_OUT == 'ON':
        triggerOut.on()
        time.sleep(0.5)
        triggerOut.off()
    if c.SOURCE == 'FILES':
        tracks.play_vocal()
    else:
        a.play_vocal_track()
    if c.EYES == 'ON':
        eyesPin.off()
        
def controls():
    global trigger_time
    global ambient_interrupt
    try:
        if c.AMBIENT == 'ON':
            if c.PROP_TRIGGER == 'START': # No ambient tracks play with this setting
                if c.TRIGGER_OUT == 'ON':
                    triggerOut.on()
                if c.EYES == 'ON':
                    eyesPin.on()
                a.play_vocal_track()  
            elif c.PROP_TRIGGER == 'TIMER' or c.PROP_TRIGGER == 'PIR':         
                    while True:
                        if c.PROP_TRIGGER == 'PIR':
                            time.sleep(c.DELAY) 
                        elif c.PROP_TRIGGER == 'TIMER':
                            trigger_time = time.time() + c.DELAY
                        tracks.play_ambient()
                        if ambient_interrupt == True:
                            event_handler()
                            ambient_interrupt = False
                            if c.PROP_TRIGGER == 'PIR':
                                time.sleep(c.DELAY)
        elif c.AMBIENT == 'OFF':
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
                    time.sleep(c.DELAY) 
            elif c.PROP_TRIGGER == 'START':
                if c.TRIGGER_OUT == 'ON':
                    triggerOut.on()
                if c.EYES == 'ON':
                    eyesPin.on()
                a.play_vocal_track() 

    except Exception as e:
        print(e)  
    finally:
        pir.close()
        eyesPin.close()
        triggerOut.close()
        a.jaw.close()
