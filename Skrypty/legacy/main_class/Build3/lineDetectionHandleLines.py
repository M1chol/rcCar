import cv2
import numpy as np
OK ='\033[92m'
WARN ='\033[93m'
ERR = '\033[91m'
RESET = '\033[00m'

def calculatePerpendVector(line): # funkcja obliczjąca znormalizowany wektor prostopadły
    x1,y1,x2,y2 = line.reshape(4)
    vector=[x2-x1,y2-y1]
    perpVector=np.empty_like(vector)
    perpVector[0]=-vector[1]
    perpVector[1]=vector[0]
    return perpVector/np.linalg.norm(perpVector)

def shiftLinesOnPerpendVector(line, road_width, kier=1):
    vx, vy=calculatePerpendVector(line) * (road_width / 2)
    vx, vy=round(vx)*kier, round(vy)*kier # obliczenie dlogosci polowy pasa
    line=[line[0] + vx, line[1] + vy,
                         line[2] + vx, line[3] + vy] # przesuniecie po wektorze prostopadlym w prawo
    return line

def swapInvertedLines(lines): # funkcja odwracajaca linie ktore zostaly znalezione w zlym kierunku
    B=lines[:,3]-lines[:,1]
    index=np.where(B>0)
    lines_copy=np.copy(lines)
    lines[index, 0]=lines_copy[index, 2]
    lines[index, 1]=lines_copy[index, 3]
    lines[index, 2]=lines_copy[index, 0]
    lines[index, 3]=lines_copy[index, 1]
    return lines

def swapLine(line): # odwrocenie lini
    line[0], line[2]=line[2], line[0]
    line[1], line[3]=line[3], line[1]
    return line

def distaceBetweenPoints(starting_line, lines, returnSorted=False, displacement=False, checkForEnds=False):
    """
    :param starting_line: lina poczatkowa od ktorej obliczyc odleglosc
    :param lines: zbior lini do przeszukania
    :param returnSorted: jezeli True tablica bedzie posortowana
    :param displacement: odwraca linie przed analiza
    :param checkForEnds: jezeli True oblicza odleglosc do koncow a nie poczatkow lini
    :return: macierz [odleglosc, odleglosc na x, index lini]
    """
    newLine=starting_line.copy()
    if displacement:
        swapLine(newLine)
    lineArr=abs(lines-newLine)                                                                  # obliczenie odleglosci wszystkich lini od lini pocz
    index=np.arange(len(lines)).reshape(-1,1)                                                   # stworzenie indexów
    if checkForEnds: xPoints, yPoints = lineArr[:,2], lineArr[:,3]                              # odseparowanie punktów x i y szukanego punktu
    else: xPoints, yPoints = lineArr[:,0], lineArr[:,1]
    pointDist=np.sqrt(xPoints**2+yPoints**2)                                                    # obliczenie odleglosci
    retArr=np.concatenate((pointDist.reshape(-1,1),lineArr.T[0].reshape(-1,1)), axis=1)         # dolaczenie wynikow to macierzy koncowej
    retArr=np.concatenate((retArr,index),axis=1)                                                # dolaczenie indexow do macierzy koncowej
    if returnSorted:                                                                            # sortowanie
        sort=retArr[:,0].argsort()
        retArr=retArr[sort]
    return retArr

def detectStartingLines(lines,):                          # TODO napisac leprszy algorytm wykrywania lini poczatkowych
    """
    :param lines: wszystkie linie
    :return: wykryte linie poczatkowe (najblizsze do dolu przeszukiwanego obszaru)
    """
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
    return [lineLeft,lineRight] # [ignore] np.array([lineLeft,lineRight])

def deleteElements(table, linesToDel):
    """
    :param table: tabela lini z ktorych chcemy usunac wartosc
    :param linesToDel: konkretna linia lub tablica lini do usuniecia
    :return: tablica poczatkowa bez zadanych lini
    """
    if type(linesToDel[0]) is not np.intc:
        for i in linesToDel:
            table = table[np.where(4 == np.sum(table == i, axis=1), False, True)]
    else:
        table=table[np.where(4 == np.sum(table == linesToDel, axis=1), False, True)]
    return table


def nextLine(starting_line, lines, maxDist, detectedLines):
    all_lines=lines
    closestLine=distaceBetweenPoints(starting_line, all_lines, True, displacement=True)[0]              # wykrycie najblizszej lini
    if closestLine[0] <= maxDist:                                                                       # sprawdzenie odleglosci
        chosenLine=lines[int(closestLine[2])]                                                           # przypisanie lini
        detectedLines.append(chosenLine)                                                                # dodanie lini do tablicy koncowej
        all_lines = deleteElements(all_lines, chosenLine)                                               # usuniecie znalezionej lini z listy wszystkich lini
        return nextLine(chosenLine, all_lines, maxDist, detectedLines)
    else: return detectedLines

def detectBirdLines(line_start, lines):
    print(f'{WARN}Detecting lines...{RESET}')
    maxDist=40
    detectedLines=[]
    for line in line_start:
        if line is None:
            detectedLines.append([])
            continue
        detectedLines.append(nextLine(line, lines, maxDist,[]))
    print(f'Found {len(detectedLines[0])+len(detectedLines[1])} lines')
    return detectedLines

def centerLines(startingLines, lines, image, maxDist=50):
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
            if line[2]>maxDist: continue
            if kier==0:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, 1))
            elif kier==1:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, -1))

    center_lines.append([image.shape[1]//2,image.shape[0], image.shape[1]//2,center_lines[0][1]])

    return np.array(center_lines)

def makeCoords(image, slope, maxDist):
    y1 = image.shape[0]
    x1 = int(image.shape[1]//2)
    y2= int(y1 - maxDist*np.sin(np.deg2rad(slope)))
    x2= int(x1 - maxDist*np.cos(np.deg2rad(slope)))
    return [x1,y1,x2,y2]

def avarageSlopeIntersect(image, lines, maxDist):                               # wyciąganie średniej z lini
    avrLine=[]
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        slope = x2-x1              # określenie nachylenia
        avrLine.append(slope+90)                                                   # dodaje linie pasa
    slopeAvarage = np.average(avrLine)                                # średnia
    newAvrLine = makeCoords(image, slopeAvarage, maxDist=maxDist)   # koordynaty lini
    return np.array(newAvrLine), slopeAvarage
