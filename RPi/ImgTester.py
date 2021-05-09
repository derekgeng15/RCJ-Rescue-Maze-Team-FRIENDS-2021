import numpy as np
import cv2
from LetterDetector import *

 
#frame = cv2.imread("img-tests/H-sideways-small.jpg")
#frame = cv2.imread("img-tests/S-test.png")
#frame = cv2.imread("img-tests/Nothing-test.png")
#frame = cv2.imread("img-tests/Nothing-test2.png")
#frame = cv2.imread("img-tests/Nothing-test3.png")
#frame = cv2.imread("Camera1 - 5.png")
frame = cv2.imread("H-sideways-small.jpg")
#frame = cv2.imread("imgs/Camera1 - 133.png")
cv2.imshow("frame", frame)

print("Got:", getLetter(frame))

cv2.waitKey()
cv2.destroyAllWindows()
