import cv2
import numpy as np
import mediapipe as mp
import math 
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volumne = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volumne.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

screenW, screenH = pyautogui.size()

tipIds = [4, 8, 12, 16, 20]

prevX, prevY = 0, 0
smoothering = 5

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    lmList = []

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                
        if len(lmList) != 0:
            # x1, y1 = lmList[4][1], lmList[4][2] #thumbs
            x1, y1 = lmList[8][1], lmList[8][2] #index finger
            
            h, w, _= img.shape
            
            currX = int(x1 * screenW / w)
            currY = int(y1 * screenH / h)
            
            screenX = prevX + (currX - prevX) / smoothering
            screenY = prevY + (currY - prevY) / smoothering
            
            pyautogui.moveTo(screenX, screenY)
            pyautogui.FAILSAFE = False
            
            prevX, prevY = screenX, screenY
            
            x2, y2 = lmList[4][1], lmList[4][2] #thumbs
            length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
            
            if length < 40:
                pyautogui.click()
                
            #length = math.hypot(x2 - x1, y2 - y1)
            
            #vol = np.interp(length, [20, 200], [minVol, maxVol])
            #volumne.SetMasterVolumeLevel(vol, None)
            
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            
                    
    cv2.imshow("Volumne Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()