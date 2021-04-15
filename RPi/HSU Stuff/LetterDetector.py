import cv2
import numpy as np
import time
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def areaFilter(img):
    contours, h = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Get all contours for areaFilter to calculate area via contours
    
    # Calculating areas of each contour
    areas = []
    for i in range(0,len(contours)):        
        area = cv2.contourArea(contours[i])
        areas.append(area)

    if len(areas) > 0:
        correctContour = areas.index(max(areas)) # Index of correct contour (the contour that contains the letter)
        for i in range(0, len(contours)):
            if i != correctContour:
                cv2.drawContours(img, contours, i, (0,0,0), cv2.FILLED)
    
    return img

def getLetter(img):
    (height, width, depth) = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 6)
    thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)[1]
    #dum, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # IMAGE INVERTING
    thresh = cv2.bitwise_not(thresh.copy()) # Convert from mostly white to mostly black (since letter is black, and contour detection is on white)

    # AREA FILTER TO ELIMINATE NOISE
    areaFiltered = areaFilter(thresh)
    areaFilteredCopy = areaFiltered.copy()

    #PROCESSING STEP
    contours, h = cv2.findContours(areaFilteredCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>65):

            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            cropped = thresh[y:y+h, x:x+w]
            #cv2.imwrite("RPi/HSU Stuff/H-cropped " + str(i) + " .jpg", cropped)
            cv2.imshow("ROI", cropped)
            croppedCopy = cropped.copy()

            # SLICING TO GET THE THREE REGIONS
            roiy, roix = croppedCopy.shape
            top = croppedCopy[0:(roiy//4),0:roix]
            mid = croppedCopy[int(roiy*0.37):int(roiy*0.67),0:roix]
            bot = croppedCopy[int(3*roiy//4):roiy,0:roix]

            '''cv2.imwrite("RPi/HSU Stuff/H-Top.jpg", top)
            cv2.imwrite("RPi/HSU Stuff/H-Mid.jpg", mid)
            cv2.imwrite("RPi/HSU Stuff/H-Bot.jpg", bot)'''

            #CONTOURS FOR HSU DETECTION
            (contop, h) = cv2.findContours(top.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            (conmid, h) = cv2.findContours(mid.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            (conbot, h) = cv2.findContours(bot.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #Determing HSU
            print("Top: {}, Mid: {}, Bot: {}".format(len(contop), len(conmid), len(conbot)))
            if len(contop) == 2 and len(conmid) == 1 and len(conbot) == 2:
                return "H"
            elif len(contop) == 1 and len(conmid) == 1 and len(conbot) == 1:
                return "S"
            elif (len(contop) == 2 and len(conmid) == 2 and len(conbot) == 1) or (len(contop) == 1 and len(conmid) == 2 and len(conbot) == 2):
                return "U"
            else:
                return None
            


'''img = cv2.imread("RPi/HSU Stuff/H.jpg")
print(getLetter(img))'''

# USING PYTESSERACT -------------------------------------------------------------

def getLetter2(img):
    (height, width, depth) = img.shape
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray, (9, 9), 6)
    #thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)[1]
    #dum, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # IMAGE INVERTING
    # thresh = cv2.bitwise_not(thresh.copy()) # Convert from mostly white to mostly black (since letter is black, and contour detection is on white)

    (height, width, depth) = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 6)
    thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)[1]
    #dum, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # IMAGE INVERTING
    thresh = cv2.bitwise_not(thresh.copy()) # Convert from mostly white to mostly black (since letter is black, and contour detection is on white)

    # AREA FILTER TO ELIMINATE NOISE
    areaFiltered = areaFilter(thresh)
    areaFilteredCopy = areaFiltered.copy()

    #PROCESSING STEP
    contours, h = cv2.findContours(areaFilteredCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>65):

            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            cropped = thresh[y:y+h, x:x+w]
            #cv2.imwrite("RPi/HSU Stuff/H-cropped " + str(i) + " .jpg", cropped)
            cropped = cv2.bitwise_not(cropped.copy())
            cv2.imshow("ROI", cropped)
            croppedCopy = cropped.copy()

            custom_config = r'--oem 3 --psm 10'
            text = pytesseract.image_to_string(croppedCopy, config=custom_config)
            if("S" in text or "s" in text):
                return "S"
            elif("H" in text):
                return "H"
            elif("U" in text):
                return "U"
            else:
                return None