import numpy as np
from cmath import rect, phase
from math import radians, degrees

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

def detectBirdLines(line_start, lines, maxDist=40):
    #print(f'{WARN}Detecting lines...{RESET}')
    detectedLines=nextLine(line_start, lines, maxDist,[])
    #print(f'Found {len(detectedLines[0])+len(detectedLines[1])} lines')
    return detectedLines

def centerLines(lines, image, maxDist=80, road_width=100):
    center_lines=[]
    height = image.shape[0]
    for kier in range(2):
        for line in lines[kier]:
            if line[1]<height-maxDist: continue
            if kier==0:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, 1))
            elif kier==1:
                center_lines.append(shiftLinesOnPerpendVector(line, road_width, -1))

    if len(center_lines) != 0:
        if center_lines[0][1] < height - 5:
            center_lines.append([image.shape[1]//2,image.shape[0], image.shape[1]//2, center_lines[0][1]])
    else:
        center_lines.append([image.shape[1] // 2, image.shape[0], image.shape[1] // 2, height-maxDist])

    return np.array(center_lines)

def makeCoords(image, angle, maxDist):
    if angle<0: angle+=180
    y1 = image.shape[0]
    x1 = int(image.shape[1]//2)
    y2= int(y1 - maxDist*np.sin(radians(angle)))
    x2= int(x1 - maxDist*np.cos(radians(angle)))
    return [x1,y1,x2,y2]

def mean_angle(deg):                                                            # średnia wartość kątów
    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))       # https://rosettacode.org/wiki/Averages/Mean_angle

def avarageSlopeIntersect(image, lines, maxDist):                               # wyciąganie średniej z lini
    avrLine=[]
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        angle = np.rad2deg(np.arctan2(y2 - y1, x2 - x1))                        # https://stackoverflow.com/questions/35825421/calculate-angle-degrees-in-python-between-line-with-slope-x-and-horizontal
        avrLine.append(angle)                                                   # dodaj nachylenie do tablicy
    slopeAvarage = mean_angle(avrLine)                                          # średnia z kątów tablicy
    newAvrLine = makeCoords(image, slopeAvarage, maxDist=maxDist)               # koordynaty lini
    return np.array(newAvrLine), slopeAvarage
