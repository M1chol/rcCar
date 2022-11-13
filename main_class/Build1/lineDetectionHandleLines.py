import cv2
import numpy as np
OK ='\033[92m'
WARN ='\033[93m'
ERR = '\033[91m'
RESET = '\033[00m'

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

def distaceBetweenPoints(starting_line, lines, returnSorted=False, displacement=False, checkForEnds=False):
    newLine=starting_line.copy()
    if displacement:
        swapLine(newLine)
    lineArr=abs(lines-newLine)                                                                  # obliczenie odleglosci wszystkich lini od lini pocz
    index=np.arange(len(lines)).reshape(-1,1)                                                   # stworzenie indexów
    xPoints, yPoints = lineArr[:,0], lineArr[:,1]                                               # odseparowanie punktów x i y szukanego punktu
    pointDist=np.sqrt(xPoints**2+yPoints**2)                                                    # obliczenie odleglosci
    retArr=np.concatenate((pointDist.reshape(-1,1),lineArr.T[0].reshape(-1,1)), axis=1)         #dolaczenie wynikow to macierzy koncowej
    retArr=np.concatenate((retArr,index),axis=1)                                                # dolaczenie indexow do macierzy koncowej
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
    print(f'{WARN}Detecting lines...{RESET}')
    maxDist=40
    detectedLines=[[],[]]
    for lineNr, line in enumerate(line_start):
        if line is None:
            continue
        linesSorted=distaceBetweenPoints(line, lines, True, displacement=True)
        if linesSorted[0][0] < maxDist:
            detectedLines[lineNr].append(lines[int(linesSorted[0][2])])
    print(f'Found {len(detectedLines[0])+len(detectedLines[1])} lines')
    return detectedLines

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
