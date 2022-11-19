import cv2
import numpy as np
import lineDetectionHandleImage as Image
import lineDetectionHandleLines as Lines

img = cv2.imread('../../../testImg/test3.5.png')
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

    startingPoints=[[266, 460, 266, 461], [381, 460, 381, 461]]
    left_line = Lines.detectBirdLines(startingPoints[0], lines, 80)
    right_line = Lines.detectBirdLines(startingPoints[1], lines, 80)
    detected_lines=[left_line, right_line]
    center_line=Lines.centerLines(detected_lines, img, maxDist=avr_dist)
    avr_center_line, av_slope = Lines.avarageSlopeIntersect(img, center_line, avr_dist)

    if retFrame or retStream: #wyświetlanie lini na obrazach
        img_detectedLeftLines=Image.displayLine(img, detected_lines[0], (0, 255, 0), (0, 225, 0))
        img_detectedRightLines=Image.displayLine(img, detected_lines[1])
        img_centerLines=Image.displayLine(img, center_line, (255, 0, 0), (255, 0, 0))
        img_avr_center_line=Image.displayLine(img, avr_center_line, (255, 0, 0), (255, 0, 0), list=False)
        # łączenie uzyskanych obrazów w jedno
        combine=[img_warped, img_detectedLeftLines, img_detectedRightLines, img_centerLines, img_avr_center_line]
        weight = [0.6,0.4,0.4,0,1]
        if retStream:
            pass #Handle stream
        else:
            cv2.imshow('final', Image.combineImages(combine, weight))
            cv2.waitKey(0)

    if retAngle:
        return av_slope
    else:
        return None

if __name__ == "__main__":
    angle = AnalizeImage(img, retFrame=True, retAngle=True)
    print(angle)