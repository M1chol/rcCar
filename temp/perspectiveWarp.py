import cv2
import numpy as np
import matplotlib.pyplot as plt

def warpImage(img):
    IMAGE_H, IMAGE_W, _ = img.shape
    src = np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    dst = np.float32([[300, IMAGE_H+45], [340, IMAGE_H+45], [0, 0], [IMAGE_W, 0]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    img = img[IMAGE_H//2:IMAGE_H, 0:IMAGE_W] # Apply np slicing for ROI crop
    warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H)) # Image warping
    return warped_img

cap = cv2.VideoCapture('http://192.168.8.199:8081/')
while cap.isOpened():
    _, frame=cap.read()
    temp=warpImage(frame)
    cv2.imshow("warped",temp)
    cv2.imshow("normal",frame)
    cv2.waitKey(1)