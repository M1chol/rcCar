import cv2
import matplotlib.pyplot as plt
import numpy as np

#colors
OK ='\033[92m'
WARN ='\033[93m'
ERR = '\033[91m'
RESET = '\033[00m'

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 150, 300)
    return img_cann

# def threshold(image):
#     gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blurred=cv2.GaussianBlur(gray, (7, 7), 0)
#     (T, thresh)=cv2.threshold(blurred, 120, 255,cv2.THRESH_BINARY)
#     return thresh

def displayLine(image, lines, color=(0, 0, 255), color2=(0, 0, 255),list=True):
    def draw(x1,y1,x2,y2):
        cv2.line(line_image, (x1, y1), (x2, y2), color, 4)
        cv2.circle(line_image, (x2, y2), 3, color2, 3)
    line_image= np.zeros_like(image)
    if lines is not None:
        if list:
            for line in lines:
                if line is not None:
                    x1,y1,x2,y2=line.reshape(4)
                    draw(x1,y1,x2,y2)
        else:
            x1, y1, x2, y2=lines
            draw(x1, y1, x2, y2)
    return line_image

# def displayPoints(image, points, color=(0,0,255)):
#     points_image=np.zeros_like(image)
#     if points is not None:
#         for point in points:
#             x1,y1 = point
#             cv2.circle(points_image, (x1, y1), 3, color, 3)
#     return points_image

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
    img_crop=regionOfIntrest(img_cann, 0)  # przycięcie zdjęcia
    try:
        lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 70, None, minLineLength=60, maxLineGap=20)
        avaraged_lines=avarageSlopeIntersect(image, lines)
        image_lines=displayLine(image, lines)
        cv2.imshow("Detected lines", image_lines)
        image_lines=displayLine(image, avaraged_lines)
        cv2.imshow("Avaraged lines", image_lines)
        img_comb=cv2.addWeighted(image, 0.6, image_lines, 1, 1, 1)
        return img_comb, img_crop
    except:
        return image

def makeCoords(image, line_params):
    slope, intercept = line_params
    y1 = image.shape[0]
    y2 = int(y1*(2/5))
    x1=int((y1-intercept)/slope)
    x2=int((y2-intercept)/slope)
    return np.array([x1,y1,x2,y2])

def regionOfIntrest(image, normal=0):
    height, width = image.shape[0], image.shape[1]
    if normal==1:
        area=np.array([[(70,90), (570,90), (width // 2, height + 20)]]) # trójkąt
    elif normal == 2:
        area=np.array([[(0, height), (width - 3, height), (width - 3, int(height * (2 / 3))),(0, int(height * (2 / 3)))]])  #prostokąt dolna 1/3
    else:
        area=np.array([[(0, height), (width - 3, height), (width - 3, int(height * (1 / 3))),(0, int(height * (1 / 3)))]])  # prostokąt dolne 2/3
    mask=np.zeros_like(image) #puste zdjęcie o wymiarach oryginału
    cv2.fillPoly(mask,area,(255,255,255)) #wypełnienie pustego zdjęcia białym kolorem wedłóg zadanego kształtu
    img_mask=cv2.bitwise_and(image,mask) #operacja and na podanych obrazach
    return img_mask

def perspectiveWarp(image):
    IMAGE_H, IMAGE_W, _=image.shape
    src=np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    dst=np.float32([[300, IMAGE_H], [355, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    M=cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
    image=image[int(IMAGE_H * (1 / 4)):IMAGE_H, 0:IMAGE_W]  # Apply np slicing for ROI crop
    warped_img=cv2.warpPerspective(image, M, (IMAGE_W, IMAGE_H))  # Image warping
    return warped_img

def swapInvertedLines(lines):
    B=lines[:,3]-lines[:,1]
    index=np.where(B>0)
    lines_copy=np.copy(lines)
    lines[index, 0]=lines_copy[index, 2]
    lines[index, 1]=lines_copy[index, 3]
    lines[index, 2]=lines_copy[index, 0]
    lines[index, 3]=lines_copy[index, 1]
    return lines

def swapLine(line):
    line[0], line[2]=line[2], line[0]
    line[1], line[3]=line[3], line[1]
    return line

def distaceBetweenPoints(starting_line, lines, returnSorted=False, displacement=False):
    newLine=starting_line.copy()
    if displacement:
        swapLine(newLine)
    lineArr=abs(lines-newLine)
    index=np.arange(len(lines)).reshape(-1,1)
    xPoints, yPoints = lineArr[:,0], lineArr[:,1]
    pointDist=np.sqrt(xPoints**2+yPoints**2)
    retArr=np.concatenate((pointDist.reshape(-1,1),lineArr.T[0].reshape(-1,1)), axis=1)
    retArr=np.concatenate((retArr,index),axis=1)
    if returnSorted:
        sort=retArr[:,0].argsort()
        retArr=retArr[sort]
    return retArr

def detectStartingLines(lines, lastLineLeft=None, lastLineRight=None):
    if lastLineLeft is not None and lastLineRight is not None:
        return np.array([lastLineLeft,lastLineRight])
    else:
        maxDist=70
        maxXDisp=30
        print(f'{WARN}Detecting starting lines...')
        startingPoints=[[266, 460, 0, 0], [381, 460, 0, 0]]
        lineLeftDist=distaceBetweenPoints(startingPoints[0], lines, True)
        lineRightDist=distaceBetweenPoints(startingPoints[1], lines, True)
        if lineLeftDist[0][0] < maxDist and lineLeftDist[0][1] < maxXDisp:
            lineLeft=lines[int(lineLeftDist[0][2])]
            print(f'{OK}Left lane - OK{RESET}')
        else:
            print(f'{ERR}Left lane - Out of bounds{RESET}')
            lineLeft=None
        if lineRightDist[0][0] < maxDist and lineRightDist[0][1] < maxXDisp:
            lineRight=lines[int(lineRightDist[0][2])]
            print(f'{OK}Right lane - OK{RESET}')
        else:
            print(f'{ERR}Right lane - Out of bounds{RESET}')
            lineRight=None
        return np.array([lineLeft,lineRight])

def detectBirdLines(line_start, lines, image):
    maxDist=40
    detectedLines=[[],[]]
    for lineNr, line in enumerate(line_start):
        if line is None:
            continue
        linesSorted=distaceBetweenPoints(line, lines, True, displacement=True)
        if linesSorted[0][0] < maxDist:
            detectedLines[lineNr].append(lines[int(linesSorted[0][2])])
    return detectedLines


def calculatePerpendVector(line):
    x1,y1,x2,y2 = line.reshape(4)
    vector=[x2-x1,y2-y1]
    perpVector=np.empty_like(vector)
    perpVector[0]=-vector[1]
    perpVector[1]=vector[0]
    return perpVector/np.linalg.norm(perpVector)

def shiftLinesOnPerpendVector(line, road_width, kier=1):
    vx, vy=calculatePerpendVector(line) * (road_width / 2)
    vx, vy=round(vx)*kier, round(vy)*kier
    line=[line[0] + vx, line[1] + vy,
                         line[2] + vx, line[3] + vy] # przesuniecie po wektorze prostopadlym w prawo
    return line

def centerLines(startingLines, lines, image):
    center_lines=[]
    road_width=100
    if startingLines[0] is not None and startingLines[1] is not None:
        road_width=abs(startingLines[0][0] - startingLines[1][0])
        center_lines.append(shiftLinesOnPerpendVector(startingLines[0], road_width, 1))
        center_lines.append(shiftLinesOnPerpendVector(startingLines[1], road_width, -1))
    elif startingLines[0] is None and startingLines[1] is None:
        return [None, None]
    elif startingLines[0] is None:
        center_lines.append(shiftLinesOnPerpendVector(startingLines[1], road_width, -1))
    else:
        center_lines.append(shiftLinesOnPerpendVector(startingLines[0], road_width, 1))

    for kier in range(2):
        for line in lines[kier]:
            if kier==0:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, 1))
            elif kier==1:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, -1))

    center_lines.append([image.shape[1]//2,image.shape[0], image.shape[1]//2,center_lines[0][1]])

    return np.array(center_lines)

def analizeBirdView(image):
    img_warped=perspectiveWarp(image)
    img_canny=canny(img_warped)
    img_crop=regionOfIntrest(img_canny, 1)
    lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=40, maxLineGap=20)
    lines=np.array(lines).reshape(-1, 4)
    lines=swapInvertedLines(lines)
    print('Lines detected on Image: ',len(lines))

    detected_starting_lines=detectStartingLines(lines)
    for line in detected_starting_lines:
        ind_log=np.where(4 == np.sum(lines == line, axis=1), False, True)
        lines=lines[ind_log]
    print(f'{WARN}Detecting next lines...{RESET}')
    detected_lines=detectBirdLines(detected_starting_lines, lines, image)
    print(f'Found {len(detected_lines)} lines')
    center_line=centerLines(detected_starting_lines,detected_lines, image)

    #wyświetlanie lini na obrazie
    img_statingLinesLeft=displayLine(image, detected_starting_lines[0],(0,255,0),(0,225,0), list=False)
    img_statingLinesRight=displayLine(image, detected_starting_lines[1], list=False)
    img_detectedLeftLines=displayLine(image, detected_lines[0], (0,255,0),(0,225,0))
    img_detectedRightLines=displayLine(image, detected_lines[1])
    img_centerLines=displayLine(image, center_line,(255,0,0),(255,0,0))

    #łączenie uzyskanych obrazów w jedno
    img_comb=cv2.addWeighted(img_warped, 0.6, img_statingLinesLeft,1,1,1)
    img_comb2=cv2.addWeighted(img_comb, 1, img_statingLinesRight,1,1,1)
    img_comb3=cv2.addWeighted(img_comb2, 1, img_detectedLeftLines, 1, 1, 1)
    img_comb4=cv2.addWeighted(img_comb3, 1, img_detectedRightLines, 1, 1, 1)
    img_comb5=cv2.addWeighted(img_comb4, 1, img_centerLines, 1, 1, 1)
    return img_comb5, img_crop


img = cv2.imread('../testImg/test3.3.png')
i1, i2 = AnalizeForLines(img)
cv2.imshow("Input image",img)
cv2.imshow("normal_canny",i2)
cv2.imshow("Final image",i1)
i3, i4 = analizeBirdView(img)
cv2.imshow("warped",i3)
cv2.imshow("warped_canny",i4)
plik = open('img/lines.txt')
plt.show()
cv2.waitKey(0)