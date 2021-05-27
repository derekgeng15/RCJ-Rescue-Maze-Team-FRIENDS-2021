import cv2
import numpy as np
import time
#import pytesseract

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def areaFilter(img, maxArea=400):
    contours, h = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Get all contours for areaFilter to calculate area via contours
    
    # Calculating areas of each contour
    #areas = [cv2.contourArea(c) for c in contours]
    areas = []
    for i in range(0,len(contours)):        
        area = cv2.contourArea(contours[i])
        areas.append(area)

    #print(areas)

    if len(areas) > 0:
        for i in range(0, len(contours)):
            if areas[i] < maxArea:
                cv2.drawContours(img, contours, i, (0,0,0), cv2.FILLED)
    
    return img

def RotateImage(i,angle, scale, border_mode=cv2.BORDER_CONSTANT):
    """
    Return the rotated and scaled image. 
    By default the border_mode arg is BORDER_CONSTANT
    """
    (h, w) = i.shape[:2]
    print ("h:{0}  w:{1}".format(h,w))
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    return cv2.warpAffine(i, M, (w,h) ,flags=cv2.INTER_CUBIC, borderMode=border_mode )

def cuts(img, direction, height, width, value = 0):
    LRCUT = 35
    TBCUT = 15
    modifier = 55
    if direction=="left":
        img[:, 0:LRCUT+modifier] = value # Cut more left of the image
    else:
        img[:, 0:LRCUT] = value
    
    if direction=="right":
        img[:, width-LRCUT-modifier:width] = value
    else:
        img[:, width-LRCUT:width] = value
        
    img[0:TBCUT, :] = value
    img[height-TBCUT:height, :] = value
    return img

# Fixes angle of HSU given the image, the contour analyzed, and the index of contour
def fixContourAngle(img, c, showFrame=True):
    x,y,w,h = cv2.boundingRect(c)
    if x>5:
        x -= 5
    if y>5:
        y -= 5
    w += 10
    h += 10
    sliced = img[y:y+h, x:x+w]
    angle = cv2.minAreaRect(c)[-1]
    print("Angle:", angle)
    fixedImg = RotateImage(img, angle, 1.0)
    if showFrame:
        cv2.imshow("Rotated", fixedImg)
    return fixedImg

#------------------------------------------------------------------------------------------------------

height = 0
width = 0
depth = 0
hwRatio = 1.7

def getLetter(img, direction="right", showFrame=True, frameCounting=False, frameCount=1): #if we want to export imgs
    global height, width, depth
    (height, width, depth) = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cuts(gray, direction, height, width, 255)
    
    blurred = cv2.GaussianBlur(gray, (9, 9), 6)
    thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)[1]
    gbr = processLetter(thresh, showFrame, frameCounting, frameCount)
    
    return gbr

def processLetter(thresh, showFrame=True, frameCounting=False, frameCount=1):
    #Cutting to get rid of treads and stuff
    #Current Cuts are for sideways-angled camera
    #thresh[:, 0:70] = 255
    #thresh[height-55:height, :] = 255
    '''
    thresh[:, width-50:width] = 255
    thresh[:, 0:50] = 255
    '''
    
    if showFrame:
        cv2.imshow("thresh", thresh)
    if frameCounting:
        cv2.imwrite("imgs/thresh - " + str(frameCount) + ".png", thresh)
    #dum, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)


    # IMAGE INVERTING
    thresh = cv2.bitwise_not(thresh.copy()) # Convert from mostly white to mostly black (since letter is black, and contour detection is on white)

    # AREA FILTER TO ELIMINATE NOISE
    areaFiltered = areaFilter(thresh)
    areaFilteredCopy = areaFiltered.copy()

    if showFrame:
        cv2.imshow("areaFilteredCopy", areaFilteredCopy)
    if frameCounting:
        cv2.imwrite("imgs/areaFilteredCopy - " + str(frameCount) + ".png", areaFilteredCopy)

    #PROCESSING STEP
    contours, h = cv2.findContours(areaFilteredCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>1850 and cv2.contourArea(c) < 5700):

            # Fix angle of contour
            areaFilteredCopy = fixContourAngle(areaFilteredCopy, c, showFrame=True)
            areaFilteredCopy = areaFilter(areaFilteredCopy)
            contours, h = cv2.findContours(areaFilteredCopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
            c = max(contours, key = cv2.contourArea) # Give the largest contour

            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            '''cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2) # draw the book contour (in green)
            cv2.imshow("Thresh", thresh)'''
            angle = 0 #cv2.minAreaRect(c)[-1]
            #print("Angle:", angle)
            #cropped = thresh[max(y-10,0):min(y+h+10,height), max(x-10,0):min(x+w+10, width)]
            cropped = areaFilteredCopy[y:y+h, x:x+w]
            if hwRatio*h < w or hwRatio*w < h: # If image dimensions are unreasonable
                continue
            
            #CHECKING IF WE NED TO ROTATE ROI 
            if (w >= h):  #width must be smaller than height
                cropped = RotateImage(cropped,angle+90,1.0)
            else:
                cropped = RotateImage(cropped,angle,1.0)
                
            print("Area of ROI Contour:", cv2.contourArea(c))
            print("HW Ratio:", h/w, "WH Ratio:", w/h) 
            
            if showFrame:
                cv2.imshow("ROI", cropped)
            if frameCounting:
                cv2.imwrite("imgs/ROI - " + str(frameCount) + ".png", cropped)
            #   cv2.imwrite("imgs/ROI.png", cropped)
            croppedCopy = cropped.copy()

            # SLICING TO GET THE THREE REGIONS
            roiy, roix = croppedCopy.shape
            top = croppedCopy[0:int(roiy*0.20),0:roix]
            #mid = croppedCopy[int(roiy*0.37):int(roiy*0.67),0:roix]
            mid = croppedCopy[int(roiy*0.43):int(roiy*0.57),0:roix]
            bot = croppedCopy[int(roiy*0.80):roiy,0:roix]

            '''cv2.imwrite("RPi/HSU Stuff/H-Top.jpg", top)
            cv2.imwrite("RPi/HSU Stuff/H-Mid.jpg", mid)
            cv2.imwrite("RPi/HSU Stuff/H-Bot.jpg", bot)'''

            # Filter again (get rid of random micro-contours)
            areaFilter(top, maxArea=40)
            areaFilter(mid, maxArea=40)
            areaFilter(bot, maxArea=40)

            if showFrame:
                cv2.imshow("top", top)
                cv2.imshow("mid", mid)
                cv2.imshow("bot", bot)

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
        else:
            cv2.drawContours(thresh, contours, i, (0,0,0), cv2.FILLED)

    return None
