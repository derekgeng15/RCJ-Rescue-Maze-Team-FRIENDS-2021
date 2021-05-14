import numpy as np
import cv2
from LetterDetector import *
from ColorDetector import *

cap = cv2.VideoCapture(1) # Right
#cap1 = cv2.VideoCapture(1) # Left
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) # 320
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) # 240
cap.set(cv2.CAP_PROP_FPS,30)
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
time.sleep(2)

while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    #ret2, frame2 = cap1.read()
    # Display the resulting frame
    cv2.imshow('VideoCapture0',frame)
    #cv2.imshow('Capture1',frame2)

    #print(getLetter(frame, showFrame=True))

    color = getColorVictimVectorized(frame, showFrame=True)
    if color == None:
        print(getLetter(frame))
    else:
        print(color)

    '''letter = getLetter(frame, showFrame=True)
    if letter == None:
        print(getColorVictimVectorized(frame))
    else:
        print(letter)'''

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

# Sampling Distribution??? (i.e. 86% of frames saw H, 12% of frames saw S)
# getLetters2 is not good at the moment
# thresholding was useful