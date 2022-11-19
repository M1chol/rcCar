import cv2
import numpy as np
import lineDetectionHandleImage as Image
import lineDetectionHandleLines as Lines
import time

OK ='\033[92m'
WARN ='\033[93m'
ERR = '\033[91m'
RESET = '\033[00m'

def AnalizeImage(img, numberOfSteps=0, retAngle = True, retFrame = False, retStream = False, retLanes=True, retAverMidLane=True, retMiddleLine = False, printInfo=True):
    """
    :param img: orginalne zdjecie do analizy
    :param numberOfSteps: liczba krokow w analizie pasow
    :param retAngle: True - zwraca kat skretu kola
    :param retFrame: True - zwraca obraz
    :param retStream: NIE DZIALA
    :param retLanes: True - linie prawa, lewa wydukowane na obrazie
    :param retAverMidLane: True - linia wizualizujaca kat skretu na obrazie
    :param retMiddleLine: True - linia srodkowa na obrazie
    :return: kat skretu i obraz
    """
    maxDistanceToAver=75

    height = img.shape[0]
    start_time=time.time()
    img_warped=Image.perspectiveWarp(img)                                                                   # rozciągnięcie obrazu do perspektywy
    img_canny=Image.canny(img_warped)                                                                       # użycie filtru canny
    img_crop=Image.regionOfIntrest(img_canny, 1)                                                            # wycięcie fragmentu obrazu poza strefą interesująca

    lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=40, maxLineGap=20)              # wykrycie lini na obrazie
    if lines is None:
        if retStream: pass # handle stream
        if printInfo: print('{:<30} {:<30} {:<30} {:<30}'.format(f'{ERR}All lines: 0', f'Lines used: 0',
                                                    f'Turning angle: 90', f'Time: {round(time.time() - start_time,3)}{RESET}'))
        if retFrame:
            cv2.imshow('final',img_warped)
            cv2.waitKey(1)
        if retAngle: return 90

    lines=np.array(lines).reshape(-1, 4)                                                                    # transformacja macierzy do łatwiejszej analizy
    lines=Lines.swapInvertedLines(lines)                                                                    # odwrócenie lini skierowanych w złą stronę

    startingPoints=[[246, 460, 246, 450], [411, 460, 411, 450]]
    left_line = Lines.detectBirdLines(startingPoints[0], lines, 55, numberOfLines=numberOfSteps)
    right_line = Lines.detectBirdLines(startingPoints[1], lines, 55, numberOfLines=numberOfSteps)
    lines_to_average=[]
    if left_line: lines_to_average+=[line for line in left_line if line[1]>height-maxDistanceToAver]
    if right_line: lines_to_average+=[line for line in right_line if line[1]>height-maxDistanceToAver]
    print(WARN) if len(lines_to_average)==0 else print(OK)
    avr_center_line, av_slope = Lines.avarageSlope(img, lines_to_average, maxDistanceToAver)

    if retFrame or retStream: #wyświetlanie lini na obrazach
        img_detectedLeftLines=Image.displayLine(img, left_line, (0, 255, 0), (0, 225, 0))
        img_detectedRightLines=Image.displayLine(img, right_line)
        img_avr_center_line=Image.displayLine(img, avr_center_line, (255, 0, 0), (255, 0, 0), list=False)

        combine=[img_warped]
        weight=[0.6]

        if retAverMidLane:
            combine.append(img_avr_center_line)
            weight += 1,

        if retLanes:
            combine.append(img_detectedLeftLines)
            combine.append(img_detectedRightLines)
            weight += 0.4, 0.4

        if retMiddleLine:
            mid_line=Lines.centerLines([left_line,right_line], img, 55)
            img_mid_line = Image.displayLine(img, mid_line, (255, 0, 0), (255, 0, 0))
            combine.append(img_mid_line)
            weight+=0.4,

        # łączenie uzyskanych obrazów w jedno
        finalFrame=Image.combineImages(combine, weight)

        if printInfo:
            print('{:<30} {:<30} {:<30} {:<30}'.format(f'All lines: {len(lines)}', f'Lines used: {len(lines_to_average)}',
                                                    f'Turning angle: {round(av_slope,3)}', f'Time: {round(time.time() - start_time,3)}'))

        if retStream:
            pass #Handle stream
        else:
            cv2.imshow('final', finalFrame)
            cv2.waitKey(1)

    if retAngle:
        return av_slope
    else:
        return None


# frame = cv2.imread('../../testImg/test3.4.png')
# if frame is None: quit('No image on set path')
#
# if __name__ == "__main__":
#     angle=AnalizeImage(frame, retAngle=True, retFrame=True)


cap = cv2.VideoCapture('http://192.168.8.199:8081/')
if __name__ == "__main__":
    while cap.isOpened():
        _, frame=cap.read()
        cv2.imshow("normal", frame)
        try:
            angle=AnalizeImage(frame, retAngle=True, retFrame=True)
        except:
            print(f'{ERR} UNKNOWN ERROR SKIPING FRAME...{RESET}')