import cv2
import numpy as np
import lineDetectionHandleImage as Image
import lineDetectionHandleLines as Lines

img = cv2.imread('../../../testImg/test3.3.png')
if type(img) == 'NoneType': quit('No image on set path')

img_warped=Image.perspectiveWarp(img)                                                                   # rozciągnięcie obrazu do perspektywy
img_canny=Image.canny(img_warped)                                                                       # użycie filtru canny
img_crop=Image.regionOfIntrest(img_canny, 1)                                                            # wycięcie fragmentu obrazu poza strefą interesująca

lines=cv2.HoughLinesP(img_crop, 2, np.pi / 180, 30, None, minLineLength=40, maxLineGap=20)              # wykrycie lini na obrazie
lines=np.array(lines).reshape(-1, 4)                                                                    # transformacja macierzy do łatwiejszej analizy
lines=Lines.swapInvertedLines(lines)                                                                    # odwrócenie lini skierowanych w złą stronę
print('Lines detected on Image: ',len(lines))

detected_starting_lines=Lines.detectStartingLines(lines)                                                # wykrycie lini początkowych
# for line in detected_starting_lines:                                                                    #
#     ind_log=np.where(4 == np.sum(lines == line, axis=1), False, True)
#     lines=lines[ind_log]
detected_lines=Lines.detectBirdLines(detected_starting_lines, lines, img)
center_line=Lines.centerLines(detected_starting_lines, detected_lines, img)

#wyświetlanie lini na obrazach
img_statingLinesLeft=Image.displayLine(img, detected_starting_lines[0], (0, 255, 0), (0, 225, 0), list=False)
img_statingLinesRight=Image.displayLine(img, detected_starting_lines[1], list=False)
img_detectedLeftLines=Image.displayLine(img, detected_lines[0], (0, 255, 0), (0, 225, 0))
img_detectedRightLines=Image.displayLine(img, detected_lines[1])
img_centerLines=Image.displayLine(img, center_line, (255, 0, 0), (255, 0, 0))

#łączenie uzyskanych obrazów w jedno
combine = [img_warped, img_statingLinesLeft, img_statingLinesRight, img_detectedLeftLines, img_detectedRightLines, img_centerLines]

cv2.imshow('input', img)
cv2.imshow('final', Image.combineImages(combine))
cv2.waitKey(0)

# img_comb=cv2.addWeighted(img_warped, 0.6, img_statingLinesLeft,1,1,1)
# img_comb2=cv2.addWeighted(img_comb, 1, img_statingLinesRight,1,1,1)
# img_comb3=cv2.addWeighted(img_comb2, 1, img_detectedLeftLines, 1, 1, 1)
# img_comb4=cv2.addWeighted(img_comb3, 1, img_detectedRightLines, 1, 1, 1)
# img_comb5=cv2.addWeighted(img_comb4, 1, img_centerLines, 1, 1, 1)