import imutils
import numpy as np
from imutils import contours

import cv2


"""
This tool corrects the image test using the answer key supplied.
"""


def correct(test, key):
    # ANSWER_KEY maps question number to correct answer
    ANSWER_KEY = key

    # AMOUNT is the amount of questions
    AMOUNT = len(key)  # should be 5|10|15
    print("ANSWER_KEY_LENGTH={}".format(AMOUNT))

    # gets sheet
    image = cv2.imread(test)

    # converts to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blurrs the image slightly
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # finds edges ->
    edged = cv2.Canny(blurred, 75, 200)

    # applies Otsu's thresholding to binarize the grayscale
    thresh = cv2.threshold(gray, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # finds and initialises a list of question circles
    cnts = cv2.findContours(thresh.copy(),
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_NONE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    questionCnts = []
    print("CNT_AMOUNT={}".format(len(cnts)))

    # for every question circle
    for c in cnts:
        # create a box around a circle,
        # x, y being top-left coord, w, h its width & height
        (x, y, w, h) = cv2.boundingRect(c)

        # use it to create the aspect ratio
        ar = w / float(h)

        # populates a list with question circles
        # to become a question circle it needs to be:
        # wide & tall enough and have an apect ratio of +-1
        if w >= 50 and h >= 50 and ar >= 0.9 and ar <= 1.1:
            questionCnts.append(c)

    # top -> bottom sort question circles
    questionCnts = contours.sort_contours(questionCnts,
                                          method="top-to-bottom")[0]
    print("QCNT_AMOUNT={}".format(len(questionCnts)))

    # after filtering, the question counts should be either of the three
    # otherwise, the algorithm has failed to locate the right contours
    if AMOUNT * 5 not in [25, 50, 75]:
        # if the algorithm cannot correct the test it will void it (True)
        # the lecturer can manually correct it later

        # sheet print score
        cv2.putText(image, "{}/{} {:.2f}% VOID".format(0, AMOUNT, 0),
                    (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 0, 255), 2)

        # the result image with annotations drawn on it
        location = 'results/temp/corrected.png'
        cv2.imwrite(location, image)
        # return format (location, correct, AMOUNT, score, FLAG)
        return (location, 0, AMOUNT, 0, True)

    # if expected number of contours, correcting begins
    # correct q's count
    correct = 0

    # each q has 5 (ABCDE) answers, loop over answers in groups of 5
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
        # sort question circles group from left to right
        cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
        # bubbled answer index
        bubbled = None

        # for circle in sorted group of 5, create a mask (only show one circle)
        for (j, c) in enumerate(cnts):
            # aka. return a new array of given shape, filled with zeros
            # in this case blank copy of our test
            mask = np.zeros(thresh.shape, dtype="uint8")
            # draw contours of the circle [c] onto our mask
            cv2.drawContours(mask, [c], -1, 255, -1)

            # place the mask on the sheet
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            # count non-zero pixels inside the circle/mask
            total = cv2.countNonZero(mask)

            # if the current total contains a more non-zero pixels
            # then it is the answer (currently)
            if bubbled is None or total > bubbled[0]:
                # bubbled = (amount of nonzero pixels, which circle)
                bubbled = (total, j)

        # colour for the wrong answer contour (red)
        color = (0, 0, 255)

        # answer key at question circle q
        k = ANSWER_KEY[q]

        # is the answer correct according to the answer key? draw (green)
        if k == bubbled[1]:
            color = (0, 255, 0)
            correct += 1

        # draw the contour on the correct answer
        cv2.drawContours(image, [cnts[k]], -1, color, 3)

    # calculate score (OUT OF 5|10|15 Q's)
    score = (correct / AMOUNT) * 100
    print("SCORE={}/{} {:.2f}%".format(correct, AMOUNT, score))

    # sheet print score
    cv2.putText(image, "{}/{} {:.2f}%".format(correct, AMOUNT, score),
                (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 0, 255), 2)

    # the result image with annotations drawn on it
    location = 'results/temp/corrected.png'
    cv2.imwrite(location, image)
    # the following do not need to be saved
    # saved for thr purpose of presenting the steps of the algorithm
    cv2.imwrite('results/temp/grayscale.png', gray)
    cv2.imwrite('results/temp/blurred.png', blurred)
    cv2.imwrite('results/temp/edged.png', edged)
    cv2.imwrite('results/temp/thresholded.png', thresh)
    return (location, correct, AMOUNT, score, False)
