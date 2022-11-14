import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 150, 300)
    return img_cann

def displayLine(image, lines, color=(0, 0, 255)):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),(0,0,255),8)
    return line_image

def regionOfIntrest(image, normal=0):
    height, width = image.shape
    if normal==1:
        area=np.array([[(70,120), (570,120), (width // 2, height + 45)]])
    else:
        area=np.array([[(0, height), (width - 3, height), (width - 3, int(height * (1 / 2))),(0, int(height * (1 / 2)))]])  # stworzenie prostokąta o punktach
    mask=np.zeros_like(image) #puste zdjęcie o wymiarach oryginału
    cv2.fillPoly(mask,area,255) #wypełnienie pustego zdjęcia białym kolorem wedłóg zadanego kształtu
    img_mask=cv2.bitwise_and(image,mask) #operacja and na podanych obrazach
    return img_mask

def makeCoords(image, line_params):
    print(line_params)
    slope, intercept = line_params
    y1 = image.shape[0]
    y2 = int(y1*(3/5))
    x1=int((y1-intercept)/slope)
    x2=int((y2-intercept)/slope)
    return np.array([x1,y1,x2,y2])

def makeCordsBird(image, line_params, qual, cell_nr):
    slope, intercept = line_params
    height, width, _=image.shape
    y1 = int(height*((cell_nr+1)/qual))
    y2 = int(y1-height*(1/qual))
    x1=int((y1 - intercept) / slope)
    x2=int((y2 - intercept) / slope)
    return np.array([x1,y1,x2,y2])

def avarageSlopeIntersect(image, lines): #wyciąganie średniej z lini
    leftFit=[] #lewy pas
    rightFit=[] #prawy pas
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters= np.polyfit((x1,x2),(y1,y2), 1)
        slope = parameters[0] #nachylenie linii
        intercept = parameters[1]
        if slope < -0.1: #jeżeli funkcja rosnąca
            leftFit.append((slope, intercept)) #dodaj linie do lewego pasa
        elif slope > 0.1:
            rightFit.append((slope, intercept)) #jeżeli funkcja malejąca dodaj linie do prawego pasa
        else:
            pass
    leftFitAvarage = np.average(leftFit, axis=0) #średnia
    rightFitAverage = np.average(rightFit, axis=0) #średnia
    leftLine = makeCoords(image, leftFitAvarage) #koordynaty lini
    rightLine = makeCoords(image, rightFitAverage) #koordynaty lini
    #print(leftLine, 'left')
    #print(rightLine, 'right')
    return np.array([leftLine, rightLine])

def perspectiveWarp(img):
    IMAGE_H, IMAGE_W, _=img.shape
    src=np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    dst=np.float32([[296, IMAGE_H+45], [340, IMAGE_H+45], [0, 0], [IMAGE_W, 0]])
    M=cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
    img=img[IMAGE_H//2:IMAGE_H, 0:IMAGE_W]  # Apply np slicing for ROI crop
    warped_img=cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H))  # Image warping
    return warped_img

def avarageSlopeBird(image, lines, qual=3):
    lane1=[]
    lane2=[]
    threshold=50
    # podzielenie punktów wedłóg "wysokości"
    area=[]
    for line in lines:
        x1, y1, x2, y2=line.reshape(4)
        area.append([x1,y1])
        area.append([x2,y2])
    if area:
        area=sorted(area, key=lambda x: x[1],reverse=True)
        carret=area[0]
        lane1.append(carret)
        for pointNr in range(1,len(area)):
            if abs(area[pointNr][0]-carret[0])<threshold:
                lane1.append(area[pointNr])
                carret=area[pointNr]
            else: lane2.append(area[pointNr])
        index=0
        while index<len(lane2)-1:
            if abs(lane2[index][0]-lane2[index+1][0])>threshold:
                lane2.pop(index+1)
            else:
                index+=1

    return [lane1,lane2]

def displayCurve(image, points, curves):
    line_image=np.zeros_like(image)
    for line in points:
        for point in line:
            cv2.circle(line_image,(point[0],point[1]),2,(0,0,255),6)
    for curve in curves:
        cv2.polylines(image, [curve],False, (0, 255, 255),6)
    return line_image

def avarageCurve(points):
    lines=[[],[]]
    for index, line in enumerate(points):
        x,y = [],[]
        for point in line:
            x.append(point[0])
            y.append(point[1])
        poly=np.poly1d(np.polyfit(x, y, 2))
        sorted=np.sort(x)  # sortowanie
        lines[index]=np.column_stack((sorted.astype(np.int32), poly(sorted).astype(np.int32)))
    return lines

def AnalizeForLines(image):
    img_cann=canny(image)  # zastosowanie metody canny
    img_crop=regionOfIntrest(img_cann, 0)  # przycięcie zdjęcia
    try:
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 70, None, minLineLength=45, maxLineGap=20)
        avaraged_lines=avarageSlopeIntersect(image, lines)
        image_lines=displayLine(image, avaraged_lines)
        img_comb=cv2.addWeighted(image, 0.8, image_lines, 1, 1, 1)
        return img_comb, img_crop
    except:
        return image, img_crop

def AnalizeForCurve(image):
    image=perspectiveWarp(image)
    img_cann=canny(image)
    img_crop=regionOfIntrest(img_cann, 1)
    try:
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 20, None, minLineLength=15, maxLineGap=40)  # wykrycie lini
        points=avarageSlopeBird(image, lines)
        curves=avarageCurve(points)
        img_lines=displayCurve(image, points, curves)
        #img_lines=displayCurve(image, points, curves, [(0, 0, 255),(255,0,0)])
        img_comb=cv2.addWeighted(image, 0.8, img_lines, 1 , 1, 1)
        return img_comb, img_crop
    except:
        return image, img_crop

cap = cv2.VideoCapture('http://192.168.43.199:8081/')
while cap.isOpened():
    _, frame=cap.read()
    i1, i2 = AnalizeForLines(frame)
    cv2.imshow("normal",i1)
    cv2.imshow("normal_canny",i2)
    i3, i4 = AnalizeForCurve(frame)
    cv2.imshow("warped",i3)
    cv2.imshow("warped_canny",i4)
    cv2.waitKey(1)


