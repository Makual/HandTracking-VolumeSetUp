import cv2
import mediapipe as mp
import time
import os
import math
import numpy as np



from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume  =  cast(interface, POINTER(IAudioEndpointVolume))
volume.GetMute()
volume.GetMasterVolumeLevel()
volume.GetVolumeRange()


clear = lambda : os.system('cls')

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

basicDistS = 200
minVolDistS = 10
maxVolDistS = 280

lmsDct = {}

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        for id, lm in enumerate(handLms.landmark):
            h, w, c = img.shape
            cx, cy = (int(lm.x*w),int(lm.y*h))

            lmsDct[id] = {'x': cx, 'y': cy}
                
        distVol = math.sqrt((lmsDct[8]['y'] - lmsDct[4]['y'])**2 + (lmsDct[8]['x'] - lmsDct[4]['x'])**2)
        distPer = math.sqrt((lmsDct[9]['y'] - lmsDct[0]['y'])**2 + (lmsDct[9]['x'] - lmsDct[0]['x'])**2)
        distIf = math.sqrt((lmsDct[9]['y'] - lmsDct[12]['y'])**2 + (lmsDct[9]['x'] - lmsDct[12]['x'])**2)    
        
        cv2.circle(img, (lmsDct[8]['x'],lmsDct[8]['y']), 10, (0,255,0), cv2.FILLED)
        cv2.circle(img, (lmsDct[4]['x'],lmsDct[4]['y']), 10, (0,255,0), cv2.FILLED)
        cv2.line(img, (lmsDct[8]['x'],lmsDct[8]['y']),(lmsDct[4]['x'],lmsDct[4]['y']), (0,255,0), 3)
        
              
        mpDraw.draw_landmarks(img, handLms,mpHands.HAND_CONNECTIONS)

        if distIf > 0:
            if distPer/distIf > 1.8:
                koef = (basicDistS/distPer)
                minVolDist = minVolDistS / koef
                maxVolDist = maxVolDistS / koef

                vol = distVol // ((maxVolDist-minVolDist) / 100) 

                if vol > 100:
                    vol = 100
                if vol < 14:
                    vol = 0
                cv2.putText(img, "Volume: " + str(vol),(50,50),cv2.FONT_HERSHEY_PLAIN,2,(255,255,255),1)
                vol = np.interp(vol, [0,100], [-60,0])
                
                volume.SetMasterVolumeLevel(int(vol),None)
    
        
 
    cv2.imshow("Image", img)
    cv2.waitKey(1)


clear()
