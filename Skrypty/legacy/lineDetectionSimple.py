import cv2
import numpy as np

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 100, 200)
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
    area=np.array([[(0,height),(width-3,height),(width-3,int(height*(1/2))),(0,int(height*(1/2)))]]) #stworzenie prostokąta o punktach
    mask=np.zeros_like(image) #puste zdjęcie o wymiarach oryginału
    cv2.fillPoly(mask,area,255) #wypełnienie pustego zdjęcia białym kolorem wedłóg zadanego kształtu
    img_mask=cv2.bitwise_and(image,mask) #operacja and na podanych obrazach
    return img_mask

def makeCoords(image, line_params):
    slope, intercept = line_params
    y1 = image.shape[0]
    y2 = int(y1*(2/5))
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
    print(leftLine, 'left')
    print(rightLine, 'right')
    return np.array([leftLine, rightLine])

def AnalizeForLines(image, vid=1):
    img_cann=canny(image)  # zastosowanie metody canny
    img_crop=regionOfIntrest(img_cann)  # przycięcie zdjęcia do dolnej połowy
    try:
        lines=cv2.HoughLinesP(img_crop, 1, np.pi / 180, 100, None, minLineLength=40, maxLineGap=10)  # wykrycie lini
        avaraged_lines=avarageSlopeIntersect(image, lines)
        img_line=displayLines(image, lines)  # wydrukowanie lini na czarnym tle
        img_comb=cv2.addWeighted(image, 0.8, img_line, 1, 1, 1)  # połączenie lini z oryginałem
        cv2.imshow("test", img_comb)
        cv2.imshow("canny", img_crop)
        cv2.waitKey(vid)
    except:
        cv2.imshow("test", image)
        cv2.imshow("canny", img_crop)
        cv2.waitKey(vid)

# cap = cv2.VideoCapture('http://192.168.8.199:8081/')
# while cap.isOpened():
#     _, frame=cap.read()
#     AnalizeForLines(frame)
