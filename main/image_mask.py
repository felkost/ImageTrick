import numpy as np
import cv2
import os


def image_mask(color, filename):
    mydir = os.getcwd()
    rgb_color = np.array([color])
    img = cv2.imread(filename)
    img = cv2.resize(img, (600, 400), interpolation=cv2.INTER_AREA)
    def_color = np.array([0, 0, 0])
    # convert RGB to HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # create the Mask
    mask = cv2.inRange(img, def_color, rgb_color)
    mask = 255-mask

    res = cv2.bitwise_and(img, img, mask=mask)
    cv2.imwrite(mydir + '/Output6/res.jpg', res)
