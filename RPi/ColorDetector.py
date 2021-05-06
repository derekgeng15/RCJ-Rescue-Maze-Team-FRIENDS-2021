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
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("thresh", thresh)
    #print(img[height//2][width//2])
    blueChannel = img[:,:,0]
    greenChannel = img[:,:,1]
    redChannel = img[:,:,2]

    # Filtering for Red
    redFilter = np.zeros((height, width), dtype="uint8")
    redFilterBool = redChannel * 0.435 > greenChannel
    redFilter[redFilterBool == True] = 255
    redFiltered = np.bitwise_and(thresh, redFilter)
    cv2.imshow('redFiltered', redFiltered)

    # Area Filter Contours
    redAreaFiltered = areaFilter(redFiltered)

    # Contour Detection
    contours, h = cv2.findContours(redAreaFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Should only be one contour because of image
    foundRedVictim = False
    for i, c in enumerate(contours):
        if(cv2.contourArea(c)>500):
            #GETTING BOUNDING RECTANGLE
            rect = cv2.boundingRect(c)
            x,y,w,h = rect
            if 1.6*h < w or 1.6*w < h: # If image dimensions are unreasonable
                continue
            else:
                foundRedVictim = True
            cv2.imshow("ROI", img[y:y+h, x:x+w])
    
    # Victim Detection Logic
    if foundRedVictim:
        return "RED"
    else:
        return None
    
    #cv2.waitKey()

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