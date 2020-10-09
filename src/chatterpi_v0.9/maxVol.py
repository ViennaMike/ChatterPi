# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 17:39:05 2020

@author: mikem
"""
import wave
import numpy as np
import os
from multiprocessing import Process

# Using multiprocessing so that large memory use if freed when done.
def maximize(prefix, fileName):
    MAXVALUE = 32767
    if fileName.endswith('.wav'):
        wf = wave.open(prefix+fileName, 'rb')
        params = wf.getparams()
        frameCount = params[3] 
        sound = wf.readframes(frameCount)
        wf.close()
                
        sound = np.frombuffer(sound, np.int16) 
        levels = abs(sound)
        maxVolume = np.max(levels)
        factor = MAXVALUE / maxVolume
        sound = sound*factor
        sound = sound.astype(np.int16)
        sound = sound.tobytes() 
                
        # Save
        wf = wave.open(prefix+fileName,"wb")
        wf.setparams(params)
        wf.writeframes(sound)
        wf.close()

def multimax(fName):
    """ opens each wav file in the folder and maximizes the volume"""
    with os.scandir(fName) as folder:
        prefix = fName+'/'
        for file in folder:
            p = Process(target=maximize, args=(prefix, file.name,))
            p.start()
            p.join()
                            
if __name__ == '__main__':
    getInput = True
    while getInput == True:
        folderName = input("""Enter "ambient" or "vocals" to specify which files
to maximize the volumes of: """)
        if folderName not in ('ambient', 'vocals'):
            print('\nEnter either "ambient" or "vocals" (without quotes)')
        else:
            getInput = False       
    multimax(folderName)


