import cv2

image = cv2.imread('test5.jpg')
cv2.imshow("Image", image)
# convert the image to grayscale and blur it slightly
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (7, 7), 0)
cv2.imshow("blur", blurred)
(T, thresh) = cv2.threshold(blurred, 100, 255,
	cv2.THRESH_BINARY)
cv2.imshow("Simple Thresholding", thresh)
cv2.waitKey(0)