import cv2
import numpy as np

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 100, 300)
    return img_cann

def displayLines(image, lines, color=(0, 0, 255)):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),color,6)
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

def avarageSlopeBird(image, lines, qual=4):
    height, width, _ = image.shape
    areas=[[] for i in range(qual)]
    for line in lines:
        x1, y1, x2, y2=line.reshape(4)
        parameters=np.polyfit((x1, x2), (y1, y2), 1)
        slope=parameters[0]  # nachylenie linii
        intercept=parameters[1]
        cell=((y1+y2)//2)//(height//qual) #wyliczenie w której części ekranu znajduje się środek wysokości lini
        areas[cell].append((slope, intercept))
    areasAverages=[np.average(cell, axis=0) for cell in areas]
    lines=[makeCordsBird(image, cell, qual, cell_nr) for cell_nr, cell in enumerate(areasAverages) if cell!=[]]
    return np.array(lines)

def AnalizeForLines(image, normal):
    if normal==1: image=perspectiveWarp(image)
    img_cann=canny(image)  # zastosowanie metody canny
    img_crop=regionOfIntrest(img_cann,normal)  # przycięcie zdjęcia
    try:
        if normal == 1: lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 20, None, minLineLength=10, maxLineGap=20)  # wykrycie lini
        else: lines=cv2.HoughLinesP(img_crop, 1, np.pi / 180, 70, None, minLineLength=45, maxLineGap=20)  # wykrycie lini
        if normal==0: avaraged_lines=avarageSlopeIntersect(image, lines)
        else: avaraged_lines=avarageSlopeBird(image, lines)
        img_line=displayLines(image, avaraged_lines)
        img_line2=displayLines(image, lines,(255, 0, 0)) # wydrukowanie lini na czarnym tle
        img_comb=cv2.addWeighted(img_line2, 1, img_line, 1, 1, 1)  # połączenie lini z oryginałem
        img_comb2=cv2.addWeighted(image,.8, img_comb,1,1,1)
        return img_comb2, img_crop
    except:
        return image, img_crop

cap = cv2.VideoCapture('http://192.168.8.199:8081/')
while cap.isOpened():
    _, frame=cap.read()
    i1, i2 = AnalizeForLines(frame,0)
    cv2.imshow("normal",i1)
    cv2.imshow("normal_canny",i2)
    i3, i4 = AnalizeForLines(frame,1)
    cv2.imshow("warped",i3)
    cv2.imshow("warped_canny",i4)
    cv2.waitKey(1)

