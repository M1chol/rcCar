import cv2
import numpy as np

def canny(image):
    img_gray=cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    img_blur=cv2.GaussianBlur(img_gray, (5, 5), 0)
    img_cann=cv2.Canny(img_blur, 150, 300)
    return img_cann

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
    height, width = image.shape[0], image.shape[1]
    src=np.float32([[0, height], [width, height], [0, 0], [width, 0]])
    dst=np.float32([[300, height], [355, height], [0, 0], [width, 0]])
    M=cv2.getPerspectiveTransform(src, dst)  # The transformation matrix
    image=image[int(height * (1 / 4)):height, 0:width]  # Apply np slicing for ROI crop
    warped_img=cv2.warpPerspective(image, M, (width, height))  # Image warping
    return warped_img

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

def combineImages(images, weight):
    finalFrame=np.zeros_like(images[0])
    for inx, image in enumerate(images):
        finalFrame=cv2.addWeighted(finalFrame, 1, image, weight[inx], 1, 1)
    return finalFrame