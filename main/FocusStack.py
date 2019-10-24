import numpy as np
import cv2


def findHomography(image_1_kp, image_2_kp, matches):
    image_1_points = np.zeros((len(matches), 1, 2), dtype=np.float32)
    image_2_points = np.zeros((len(matches), 1, 2), dtype=np.float32)

    for i in range(0, len(matches)):
        image_1_points[i] = image_1_kp[matches[i].queryIdx].pt
        image_2_points[i] = image_2_kp[matches[i].trainIdx].pt

    homography, mask = cv2.findHomography(image_1_points, image_2_points, cv2.RANSAC, ransacReprojThreshold=2.0)

    return homography


def align_images(images):
    outimages = []
    detector = cv2.ORB_create(1000)

    #   We assume that image 0 is the "base" image and align everything to it
    outimages.append(images[0])
    image1gray = cv2.cvtColor(images[0], cv2.COLOR_BGR2GRAY)
    image_1_kp, image_1_desc = detector.detectAndCompute(image1gray, None)

    for i in range(1, len(images)):
        image_i_kp, image_i_desc = detector.detectAndCompute(images[i], None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        rawMatches = bf.match(image_i_desc, image_1_desc)

        sortMatches = sorted(rawMatches, key=lambda x: x.distance)
        matches = sortMatches[0:128]

        hom = findHomography(image_i_kp, image_1_kp, matches)
        newimage = cv2.warpPerspective(images[i], hom, (images[i].shape[1], images[i].shape[0]), flags=cv2.INTER_LINEAR)

        outimages.append(newimage)

    return outimages


#
#   Compute the gradient map of the image
def doLap(image):
    # YOU SHOULD TUNE THESE VALUES TO SUIT YOUR NEEDS
    kernel_size = 5  # Size of the laplacian window
    blur_size = 5  # How big of a kernal to use for the gaussian blur
    # Generally, keeping these two values the same or very close works well
    # Also, odd numbers, please...

    blurred = cv2.GaussianBlur(image, (blur_size, blur_size), 0)
    return cv2.Laplacian(blurred, cv2.CV_64F, ksize=kernel_size)


#
#   This routine finds the points of best focus in all images and produces a merged result...
#
def focus_stack(unimages):
    images = align_images(unimages)

    laps = []
    for i in range(len(images)):
        laps.append(doLap(cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)))

    laps = np.asarray(laps)

    output = np.zeros(shape=images[0].shape, dtype=images[0].dtype)

    abs_laps = np.absolute(laps)
    maxima = abs_laps.max(axis=0)
    bool_mask = abs_laps == maxima
    mask = bool_mask.astype(np.uint8)
    for i in range(0, len(images)):
        output = cv2.bitwise_not(images[i], output, mask=mask[i])

    return 255 - output
