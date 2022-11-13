import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 150, 300)
    return img_cann

def displayLine(image, lines, color=(0, 0, 255), color2=(0, 0, 255)):
    line_image= np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2=line.reshape(4)
            cv2.line(line_image,(x1,y1),(x2,y2),color,4)
            #cv2.circle(line_image, (x1, y1), 2, color2, 2)
            cv2.circle(line_image, (x2, y2), 3, color2, 3)
    return line_image

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

# ANALIZA OBRAZU Z PIERWSZEJ OSOBY #

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
        elif slope > 0:
            rightFit.append((slope, intercept)) #jeżeli funkcja malejąca dodaj linie do prawego pasa
        else:
            pass
    leftFitAvarage = np.average(leftFit, axis=0) #średnia
    rightFitAverage = np.average(rightFit, axis=0) #średnia
    leftLine = makeCoords(image, leftFitAvarage) #koordynaty lini
    rightLine = makeCoords(image, rightFitAverage) #koordynaty lini
    return np.array([leftLine, rightLine])

def AnalizeForLines(image):
    img_cann=canny(image)  # zastosowanie metody canny
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred=cv2.GaussianBlur(gray, (7, 7), 0)
    (T, thresh)=cv2.threshold(blurred, 150, 255,
                              cv2.THRESH_BINARY)
    img_crop=regionOfIntrest(thresh, 0)  # przycięcie zdjęcia
    try:
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 70, None, minLineLength=60, maxLineGap=20)
        avaraged_lines=avarageSlopeIntersect(image, lines)
        image_lines=displayLine(image, avaraged_lines)
        img_comb=cv2.addWeighted(image, 0.8, image_lines, 1, 1, 1)
        return img_comb, img_crop
    except:
        return image, img_crop

def makeCoords(image, line_params):
    slope, intercept = line_params
    y1 = image.shape[0]
    y2 = int(y1*(2/5))
    x1=int((y1-intercept)/slope)
    x2=int((y2-intercept)/slope)
    return np.array([x1,y1,x2,y2])


def regionOfIntrest(image, normal=0):
    height, width = image.shape
    if normal==1:
        area=np.array([[(70,90), (570,90), (width // 2, height + 20)]])
    else:
        area=np.array([[(0, height), (width - 3, height), (width - 3, int(height * (1 / 3))),(0, int(height * (1 / 3)))]])  # stworzenie prostokąta o punktach
    mask=np.zeros_like(image) #puste zdjęcie o wymiarach oryginału
    cv2.fillPoly(mask,area,255) #wypełnienie pustego zdjęcia białym kolorem wedłóg zadanego kształtu
    img_mask=cv2.bitwise_and(image,mask) #operacja and na podanych obrazach
    return img_mask


def makeCordsBird(image, line_params, qual, cell_nr):
    slope, intercept = line_params
    height, width, _=image.shape
    y1 = int(height*((cell_nr+1)/qual))
    y2 = int(y1-height*(1/qual))
    x1=int((y1 - intercept) / slope)
    x2=int((y2 - intercept) / slope)
    return np.array([x1,y1,x2,y2])


def perspectiveWarp(img):
    IMAGE_H, IMAGE_W, _=img.shape
    src=np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    dst=np.float32([[300, IMAGE_H], [355, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    M=cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
    img=img[int(IMAGE_H*(1/4)):IMAGE_H, 0:IMAGE_W]  # Apply np slicing for ROI crop
    warped_img=cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H))  # Image warping
    return warped_img

#TODO tutaj
def avarageLines(image, lines):
    newLines=[]
    oldLines=[]
    for line_nr in range(len(lines)):
        x1, y1 = lines[line_nr][0][0],lines[line_nr][0][1]
        x2, y2 = lines[line_nr][0][2],lines[line_nr][0][3]

        dx, dy = x2-x1, y2-y1
        lengt = np.sqrt(dx**2+dy**2) #dlugosc lini
        wx=dx/lengt #A
        wy=dy/lengt #B
        if line_nr==0:
            C=-(wx * x2 + wy * y2)  # Ax + By + C = 0 -> C = -(Ax + By)
            A_ = dy
            B_ = dx
            C_ = -(A_*x2+B_*y2)
            lin_prost=np.add(np.array([[x2],[y2]]), np.multiply(np.array([[A_],[B_]]),[1,-1]))
            lin_prost=lin_prost.flatten('F')
        war=wx*x2+wy*y2+C
        war2=wx*x1+wy*y1+C
        if war>0 and war2>0:
            newLines.append(lines[line_nr])
        else:
            oldLines.append(lines[line_nr])
    return newLines, oldLines, [lines[0]], [lin_prost]

def AnalizeForCurve(image):
    image=perspectiveWarp(image)
    img_cann=canny(image)
    #gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred=cv2.GaussianBlur(gray, (7, 7), 0)
    #(T, thresh)=cv2.threshold(blurred, 150, 255,
    #                          cv2.THRESH_BINARY)
    img_crop=regionOfIntrest(img_cann, 1)


    lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=30, maxLineGap=20)
    img_avarageLinesNew, img_avarageLinesOld, analizedLine, help_line = avarageLines(image, lines)
    image_lines2=displayLine(image, img_avarageLinesOld)
    image_lines = displayLine(image, img_avarageLinesNew,(0,255,0),(0,255,0))
    image_analizedLIne = displayLine(image, analizedLine, (255,0,0),(255,0,0))
    image_helpLine = displayLine(image, help_line, (255,255,0),(255,0,0))
    img_comb = cv2.addWeighted(image, 0.5, image_lines2,1,1)
    img_comb2 = cv2.addWeighted(img_comb, 1, image_lines, 1 , 1, 1)
    img_comb3 = cv2.addWeighted(img_comb2, 1, image_analizedLIne, 1 , 1, 1)
    img_comb4 = cv2.addWeighted(img_comb3, 1, image_helpLine, 1, 1, 1)
    return img_comb4, img_crop


img = cv2.imread('../testImg/test3.3.png')
i1, i2 = AnalizeForLines(img)
cv2.imshow("normal",i1)
cv2.imshow("normal_canny",i2)
i3, i4 = AnalizeForCurve(img)
cv2.imshow("warped",i3)
cv2.imshow("warped_canny",i4)
plik = open('img/lines.txt')
np.savetxt('../testImg/lines.txt',i4,delimiter=',',newline='\n')
cv2.waitKey(0)


