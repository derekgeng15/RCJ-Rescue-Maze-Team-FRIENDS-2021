import numpy as np
import cv2
from ColorDetector import *


frame = cv2.imread("testColorImg.png")
cv2.imshow("Frame", frame)
getColorVictimVectorized(frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
#cap.release()
