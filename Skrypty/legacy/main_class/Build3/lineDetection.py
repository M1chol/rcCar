import cv2
import numpy as np
import lineDetectionHandleImage as Image
import lineDetectionHandleLines as Lines

img = cv2.imread('../../../testImg/test3.4.png')
if img is None: quit('No image on set path')

def AnalizeImage(img, retAngle = True, retFrame = False, retStream = False):
    """
    :param img: klatka do analizy
    :param retAngle: if True func returns raw turning angles
    :param retFrame: if True func returns window with graphical interpretation
    :param retStream if True func streams return to site
    :return: zanalizowana klatka
    """

    avr_dist=75

    img_warped=Image.perspectiveWarp(img)                                                                   # rozciągnięcie obrazu do perspektywy
    img_canny=Image.canny(img_warped)                                                                       # użycie filtru canny
    img_crop=Image.regionOfIntrest(img_canny, 1)                                                            # wycięcie fragmentu obrazu poza strefą interesująca

    lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=40, maxLineGap=20)              # wykrycie lini na obrazie
    lines=np.array(lines).reshape(-1, 4)                                                                    # transformacja macierzy do łatwiejszej analizy
    lines=Lines.swapInvertedLines(lines)                                                                    # odwrócenie lini skierowanych w złą stronę
    print('All lines detected on Image: ',len(lines))

    detected_starting_lines=Lines.detectStartingLines(lines)                                                # wykrycie lini początkowych
    lines = Lines.deleteElements(lines, detected_starting_lines)                                            # usuniecie wyrytych lini poczatkowych
    detected_lines=Lines.detectBirdLines(detected_starting_lines, lines)
    center_line=Lines.centerLines(detected_starting_lines, detected_lines, img, maxDist=avr_dist)
    avr_center_line, av_slope = Lines.avarageSlopeIntersect(img, center_line, avr_dist)

    if retFrame or retStream: #wyświetlanie lini na obrazach
        img_statingLinesLeft=Image.displayLine(img, detected_starting_lines[0], (0, 255, 0), (0, 225, 0), list=False)
        img_statingLinesRight=Image.displayLine(img, detected_starting_lines[1], list=False)
        img_detectedLeftLines=Image.displayLine(img, detected_lines[0], (0, 255, 0), (0, 225, 0))
        img_detectedRightLines=Image.displayLine(img, detected_lines[1])
        img_centerLines=Image.displayLine(img, center_line, (255, 0, 0), (255, 0, 0))
        img_avr_center_line=Image.displayLine(img, avr_center_line, (255, 0, 0), (255, 0, 0), list=False)
        # łączenie uzyskanych obrazów w jedno
        combine=[img_warped, img_statingLinesLeft, img_statingLinesRight, img_detectedLeftLines, img_detectedRightLines, img_centerLines, img_avr_center_line]
        weight = [0.6,0.4,0.4,0.4,0.4,0,1]
        if retStream:
            pass #Handle stream
        else:
            cv2.imshow('final', Image.combineImages(combine, weight))
            cv2.waitKey(0)

    if retAngle:
        return av_slope+24
    else:
        return None

if __name__ == "__main__":
    angle = AnalizeImage(img, retFrame=True, retAngle=True)
    print(angle)