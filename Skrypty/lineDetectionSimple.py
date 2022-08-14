import cv2
import numpy as np

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 50, 200)
    return img_cann

def displayLines(image, lines):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),(0, 0, 255),10)
            return line_image

def regionOfIntrest(image):
    height, width = image.shape
    area=np.array([[(0,height),(width-5,height),(width-5,height//2),(0,height//2)]]) #stworzenie prostokąta o punktach
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

def avarageSlopeIntersect(image, lines): #wyciąganie średniej z lini
    leftFit=[] #lewy pas
    rightFit=[] #prawy pas
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters= np.polyfit((x1,x2),(y1,y2), 1)
        slope = parameters[0] #nachylenie linii
        intercept = parameters[1]
        if slope < 0: #jeżeli funkcja rosnąca
            leftFit.append((slope, intercept)) #dodaj linie do lewego pasa
        else:
            rightFit.append((slope, intercept)) #jeżeli funkcja malejąca dodaj linie do prawego pasa

    leftFitAvarage = np.average(leftFit, axis=0) #średnia
    rightFitAverage = np.average(rightFit, axis=0) #średnia
    leftLine = makeCoords(image, leftFitAvarage) #koordynaty lini
    rightLine = makeCoords(image, rightFitAverage) #koordynaty lini
    return np.array([leftLine, rightLine])

cap = cv2.VideoCapture('http://192.168.8.199:8081/')
while cap.isOpened():
    _, frame=cap.read()
    try:
        img_cann=canny(frame)  # zastosowanie metody canny
        img_crop=regionOfIntrest(img_cann)  # przycięcie zdjęcia do dolnej połowy
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 100, None, minLineLength=20, maxLineGap=5)  # wykrycie lini
        avaraged_lines=avarageSlopeIntersect(frame, lines)
        img_line=displayLines(frame, lines)  # wydrukowanie lini na czarnym tle
        img_comb=cv2.addWeighted(frame, 0.8, img_line, 1, 1, 1)  # połączenie lini z oryginałem
        cv2.imshow("test", img_comb)
        cv2.waitKey(10)
    except:
        cv2.imshow("test", frame)