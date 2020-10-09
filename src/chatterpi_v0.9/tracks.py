import os
import control

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
            ambientTrackFile = self.ambientTrackLocation+'a'+self.tracksDic[i]+'.wav'
            if os.path.isfile(ambientTrackFile):
                self.ambientList.append(i)

    def play_vocal(self):
        if self.vocalList != []:
            vocalFileName = 'v'+self.tracksDic[self.vocalList[self.vocalTrackPos]]+'.wav'
            vocalTrackFile = self.vocalTrackLocation+vocalFileName
            control.a.play_vocal_track(vocalTrackFile)
            if self.vocalTrackPos == len(self.vocalList) - 1:
                self.vocalTrackPos = 0
            else:
                self.vocalTrackPos += 1
              
    def play_ambient(self):
        while control.ambient_interrupt == False:
            if self.ambientList != []:
                ambientFileName = 'a'+self.tracksDic[self.ambientList[self.ambientTrackPos]]+'.wav'
                ambientTrackFile = self.ambientTrackLocation+ambientFileName
                control.a.play_ambient_track(ambientTrackFile)
                if self.ambientTrackPos == len(self.ambientList) - 1:
                    self.ambientTrackPos = 0
                else:
                    self.ambientTrackPos += 1
            

