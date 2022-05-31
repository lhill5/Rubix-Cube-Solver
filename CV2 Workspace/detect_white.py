import cv2
import numpy as np


def nothing(x):
    print(ilowH, ilowS, ilowV, ihighH, ihighS, ihighV)


# Open the camera
cap = cv2.VideoCapture(0)

# Create a window
cv2.namedWindow('image')

# create trackbars for color change
cv2.createTrackbar('lowH', 'image', 0, 179, nothing)
cv2.createTrackbar('highH', 'image', 179, 179, nothing)

cv2.createTrackbar('lowS', 'image', 0, 255, nothing)
cv2.createTrackbar('highS', 'image', 255, 255, nothing)

cv2.createTrackbar('lowV', 'image', 0, 255, nothing)
cv2.createTrackbar('highV', 'image', 255, 255, nothing)

while True:
    ret, frame = cap.read()

    # get current positions of the trackbars
    ilowH = cv2.getTrackbarPos('lowH', 'image')
    ihighH = cv2.getTrackbarPos('highH', 'image')
    ilowS = cv2.getTrackbarPos('lowS', 'image')
    ihighS = cv2.getTrackbarPos('highS', 'image')
    ilowV = cv2.getTrackbarPos('lowV', 'image')
    ihighV = cv2.getTrackbarPos('highV', 'image')

    orange_low_threshold = np.array([0, 18, 226])
    orange_high_threshold = np.array([23, 255, 255])

    green_low_threshold = np.array([46, 59, 0])
    green_high_threshold = np.array([69, 255, 255])

    # 0 48 0 179 255 255
    white_low_threshold = np.array([0, 48, 0])
    white_high_threshold = np.array([179, 255, 255])

    yellow_low_threshold = np.array([14, 15, 208])
    yellow_high_threshold = np.array([41, 255, 255])

    # convert color to hsv because it is easy to track colors in this color model
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array([0, 48, ilowV])
    higher_hsv = np.array([179, ihighS, ihighV])

    # Apply the cv2.inrange method to create a mask
    mask = cv2.bitwise_not(cv2.inRange(hsv, lower_hsv, higher_hsv))
    # Apply the mask on the image to extract the original color
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow('image', frame)
    # Press q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
