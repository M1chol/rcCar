"""
@file hough_lines.py
@brief This program demonstrates line finding with the Hough transform
"""
import sys
import math
import cv2 as cv
import numpy as np
def displayLines(image, lines):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv.line(line_image,(x1,y1),(x2,y2),(0, 0, 255),10)
            return line_image

cap=cv.VideoCapture('http://192.168.8.199:8081/')
while cap.isOpened():
    _, frame=cap.read()
    temp= np.copy(cv.cvtColor(cv.Canny(frame, 100, 300, None, 3), cv.COLOR_GRAY2BGR))
    lines=cv.HoughLinesP(temp, 2, np.pi / 180, 100, None, minLineLength=40, maxLineGap=5)
    #img_line=displayLines(frame, lines)
    cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", temp)
    cv.waitKey(1)


