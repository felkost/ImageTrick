# import the necessary packages
from skimage.measure import compare_ssim
import imutils
import cv2
import os


def image_diff(image1, image2, label1, label2):
    # load the two input image
    path = os.getcwd()+'/Output5/'
    imageA = cv2.imread(image1)
    imageA = resize_image(imageA)
    imageB = cv2.imread(image2)
    imageB = resize_image(imageB)

    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    print("SSIM: {}".format(score))

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # show the output images
    cv2.imwrite(path+label1, imageA)
    cv2.imwrite(path+label2, imageB)
    cv2.waitKey(0)


def resize_image(image):
    width = 1920
    height = 1440
    dim = (width, height)
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
    return resized
