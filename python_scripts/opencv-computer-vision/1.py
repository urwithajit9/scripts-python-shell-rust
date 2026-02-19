import cv2

# Read image
img = cv2.imread('/home/ajit/Pictures/ajit.jpg')

# Show image
cv2.imshow('My Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
