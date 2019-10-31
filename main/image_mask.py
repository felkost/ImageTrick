import numpy as np
import cv2


def image_mask(color, filename, output):
    print(color)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    img = cv2.imread(filename)
    img = cv2.resize(img, (600, 400), interpolation=cv2.INTER_AREA)
    left = np.uint8([[[color[0][0][0] - 2, color[0][0][1] - 10, color[0][0][2] - 10]]])
    # left = np.uint8([[[color[0][0][0] - 10, 100, 100]]])
    left = np.array([left[0][0][0], left[0][0][1], left[0][0][2]])

    top = np.uint8([[[color[0][0][0] + 2, color[0][0][1] + 10, color[0][0][2] + 10]]])
    # top = np.uint8([[[color[0][0][0] + 10, 255, 255]]])
    top = np.array([top[0][0][0], top[0][0][1], top[0][0][2]])
    print(color)
    print(left)
    print(top)
    # convert RGB to HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # create the Mask
    mask = cv2.inRange(imgHSV, left, top)

    res = cv2.bitwise_and(imgHSV, imgHSV, mask=mask)
    cv2.imwrite(output, res)
