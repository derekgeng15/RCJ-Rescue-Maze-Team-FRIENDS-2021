import numpy as np
import cv2
import time
from LetterDetector import *

'''def areaFilter(img):
    contours, h = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Get all contours for areaFilter to calculate area via contours
    
    # Calculating areas of each contour
    areas = []
    for i in range(0,len(contours)):        
        area = cv2.contourArea(contours[i])
        areas.append(area)

    if len(areas) > 0:
        for i in range(0, len(contours)):
            if areas[i] < 400:
                cv2.drawContours(img, contours, i, (0,0,0), cv2.FILLED)
    
    return img'''

def getColorVictimVectorized(img, showFrame=True, frameCounting=False, frameCount=1):
    (height, width, depth) = img.shape # BGR Image
    #print("img Shape:", img.shape)

    redLowerBound = np.array([0, 108, 0])
    redUpperBound = np.array([21, 255, 255])

    yellowLowerBound = np.array([0, 118, 108])
    yellowUpperBound = np.array([179, 255, 255])

    greenLowerBound = np.array([35, 43, 0])
    greenUpperBound = np.array([179, 255, 255])

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    redThresh = cv2.inRange(hsv, redLowerBound, redUpperBound)
    yellowThresh = cv2.inRange(hsv, yellowLowerBound, yellowUpperBound)
    greenThresh = cv2.inRange(hsv, greenLowerBound, greenUpperBound)
    
    if showFrame:
        cv2.imshow("redThresh", redThresh)
        cv2.imshow("yellowThresh", yellowThresh)
        cv2.imshow("greenThresh", greenThresh)

    areaFilterMin = 500

    # Contour Detection
    contours, h = cv2.findContours(yellowThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundYellowVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.5*h < w or 1.5*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundYellowVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundYellowVictim:
        return "Yellow"

    # Contour Detection
    contours, h = cv2.findContours(redThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundRedVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.8*h < w or 1.8*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundRedVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundRedVictim:
        return "RED"

    # Contour Detection
    contours, h = cv2.findContours(greenThresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundGreenVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.8*h < w or 1.8*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundGreenVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundGreenVictim:
        return "GREEN"
    
    return None
    
    #cv2.waitKey()

'''def getColorVictimVectorized(img, showFrame=True, frameCounting=False, frameCount=1):
    (height, width, depth) = img.shape # BGR Image
    #print("img Shape:", img.shape)

    blueChannel = img[:,:,0]
    greenChannel = img[:,:,1]
    redChannel = img[:,:,2]
    #lowerBound = np.array([10, 10, 10])
    #upperBound = np.array([255, 255, 255])

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.inRange(img, lowerBound, upperBound)
    
    #Don't detect black letters
    #thresh[np.logical_and(np.logical_and(blueChannel < 35, greenChannel < 35), redChannel < 35)] = 0
    
    if showFrame:
        cv2.imshow("thresh", thresh)

    #thresh += 20
    #print(img[height//2][width//2])
    areaFilterMin = 750

    # Filtering for Yellow
    yellowFilter = np.zeros((height, width), dtype="uint8")
    yellowFilterBool = np.logical_and(np.logical_and((greenChannel * 0.7 > blueChannel), (redChannel * 0.7 > blueChannel)), (np.absolute(greenChannel.astype(int)-redChannel.astype(int)) < 25)) # Make sure both Red and Green are much larger than blue as well as red and gren not too far from each other
    #print("Abs diff:", int(greenChannel[height//2][width//2]) - int(redChannel[height//2][width//2]))
    #yellowFilterBool = np.logical_and((greenChannel * 0.55 > blueChannel), (redChannel * 0.55 > blueChannel))
    yellowFilter[yellowFilterBool == True] = 255
    yellowFiltered = np.bitwise_and(thresh, yellowFilter)
    if showFrame:
        cv2.imshow('yellowFiltered', yellowFiltered)

    # Area Filter Contours
    yellowAreaFiltered = areaFilter(yellowFiltered)

    # Contour Detection
    contours, h = cv2.findContours(yellowAreaFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundYellowVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.5*h < w or 1.5*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundYellowVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundYellowVictim:
        return "Yellow"

    # Filtering for Red
    redFilter = np.zeros((height, width), dtype="uint8")
    redFilterBool = redChannel * 0.75 > greenChannel
    redFilter[redFilterBool == True] = 255
    redFiltered = np.bitwise_and(thresh, redFilter)

    if showFrame:
        cv2.imshow('redFiltered', redFiltered)

    # Area Filter Contours
    redAreaFiltered = areaFilter(redFiltered)

    # Contour Detection
    contours, h = cv2.findContours(redAreaFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundRedVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.8*h < w or 1.8*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundRedVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundRedVictim:
        return "RED"

    # Filtering for Green
    greenFilter = np.zeros((height, width), dtype="uint8")
    greenFilterBool = greenChannel * 0.55 > redChannel
    greenFilter[greenFilterBool == True] = 255
    greenFiltered = np.bitwise_and(thresh, greenFilter)
    if showFrame:
        cv2.imshow('greenFiltered', greenFiltered)

    # Area Filter Contours
    greenAreaFiltered = areaFilter(greenFiltered)

     # Contour Detection
    contours, h = cv2.findContours(greenAreaFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundGreenVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>areaFilterMin):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.8*h < w or 1.8*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundGreenVictim = True
            if showFrame:
                cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundGreenVictim:
        return "GREEN"
    
    return None
    
    #cv2.waitKey()'''

# --------------------------------------------------------------

def getColorVictim(img, showFrame=True, frameCounting=False, frameCount=1):
    (height, width, depth) = img.shape # BGR Image
    #print("img Shape:", img.shape)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("thresh", thresh)
    #print("Thresh Shape:", thresh.shape)
    #print(img[height//2][width//2])
    ratios = np.zeros((height, width, 1), dtype="uint8") # B/G, B/R, G/R
    #print("img Shape:", img.shape)
    '''blueChannel = img[:,:,0]
    greenChannel = img[:,:,1]
    redChannel = img[:,:,2]'''
    #print(redChannel)
    #print("redChannel Shape:", redChannel.shape)
    #filters = redChannel * 0.67 > greenChannel
    #print("Filters Shape:", filters.shape)
    for i in range(height):
        for j in range(width):
            if img[i][j][2] * 0.67 > img[i][j][1]: # Red Channel * 0.67 > Blue Channel
                ratios[i][j] = 255
            else:
                ratios[i][j] = 0
    #print(filter)
    filtered = cv2.bitwise_and(thresh, ratios)
    #filtered = np.bitwise_and(thresh, filters)
    #frame.imshow('img',img) 
    cv2.imshow('filtered', filtered)