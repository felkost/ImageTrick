import numpy as np
import cv2


def image_mask(color, filename):
    rgbcolor = np.uint8([[color]])
    print(rgbcolor)
    hsvcolor = tuple(map(tuple, cv2.cvtColor(rgbcolor, cv2.COLOR_RGB2HSV)))
    print(hsvcolor)
    upperLimit = np.array([hsvcolor[0] + 2, hsvcolor[1] + 2, hsvcolor[2] + 2])
    lowerLimit = np.array([hsvcolor[0] - 2, hsvcolor[1] - 2, hsvcolor[2] - 2])

    print(upperLimit)
    print(lowerLimit)

    img = cv2.imread(filename)
    img = cv2.resize(img, (1920, 1440), interpolation=cv2.INTER_CUBIC)

    # convert RGB to HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # create the Mask
    mask = cv2.inRange(imgHSV, lowerLimit, upperLimit)

    res = cv2.bitwise_and(img, img, mask=mask)
    cv2.imwrite('res.jpg', res)