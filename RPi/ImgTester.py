import numpy as np
import cv2
from ColorDetector import *
from LetterDetector import *

#frame = cv2.imread("img-tests/H-sideways-small.jpg")
#frame = cv2.imread("img-tests/S-test.png")
#frame = cv2.imread("img-tests/Nothing-test.png")
#frame = cv2.imread("img-tests/Nothing-test2.png")
#frame = cv2.imread("img-tests/Nothing-test3.png")
#frame = cv2.imread("Camera1 - 5.png")
#frame = cv2.imread("H-sideways-small.jpg")
frame = cv2.imread("imgs/Camera1 - Left32.png")
#frame = cv2.imread("imgs/Camera1 - Right30.png")
#frame = cv2.imread("imgs/Camera1 Left - 32.png")
#frame = cv2.imread("imgs/Camera1 Right - 645.png")
cv2.imshow("frame", frame)

#print("Got:", getLetter(frame))
#print("Got:", getColorVictimVectorized(frame))

color = getColorVictimVectorized(frame, direction = 'right', showFrame=True)
if color == None:
    print(getLetter(frame, direction='right'))
else:
    print(color)

cv2.waitKey()
cv2.destroyAllWindows()
