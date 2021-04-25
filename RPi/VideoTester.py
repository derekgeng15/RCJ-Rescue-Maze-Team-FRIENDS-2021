import numpy as np
import cv2
from LetterDetector import *

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS,30)

while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Display the resulting frame
    cv2.imshow('Camera1',frame)
    print(getLetter(frame))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

# Sampling Distribution??? (i.e. 86% of frames saw H, 12% of frames saw S)
# getLetters2 is not good at the moment
# thresholding was useful