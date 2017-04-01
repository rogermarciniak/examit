import argparse

import imutils
import numpy as np
from imutils import contours

import cv2

# creates argument (-i,--image),
# so that command: python examit.py --image sheet.png
# opens and corrects 'sheet.png'
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the input image")
args = vars(ap.parse_args())

# ANSWER_KEY maps question number to correct answer
# AMOUNT is the amount of questions
AMOUNT = 15  # TODO: HARDCODED FOR NOW, CHANGE THIS!

if AMOUNT == 5:
    ANSWER_KEY = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
elif AMOUNT == 10:
    ANSWER_KEY = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4,
                  5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
elif AMOUNT == 15:
    ANSWER_KEY = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4,
                  5: 0, 6: 1, 7: 2, 8: 3, 9: 4,
                  10: 0, 11: 1, 12: 2, 13: 3, 14: 4}
else:
    raise ValueError('Test can only have 5, 10 or 15 questions')

# gets sheet ->
image = cv2.imread(args["image"])

# converts to grayscale ->
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# finds edges ->
edged = cv2.Canny(blurred, 75, 200)

# applies Otsu's thresholding to binarize the grayscale
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

# finds and initialises a list of question circles
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]
questionCnts = []
print('cnts amount: ', len(cnts))

# for every question circle
for c in cnts:
    # create a box around a circle,
    # x,y being top-left coord, w,h its width & height
    (x, y, w, h) = cv2.boundingRect(c)

    # use it to create the aspect ratio
    ar = w / float(h)

    # populates a list with question circles
    # to become a question circle it needs to be:
    # wide & tall enough and have an apect ratio of +-1
    if w >= 50 and h >= 50 and ar >= 0.9 and ar <= 1.1:
        questionCnts.append(c)

# top -> bottom sort question circles
questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
print('questionCnts amount: ', len(questionCnts))

# correct q's count
correct = 0


# each q has 5 (ABCDE) answers, loop over answers in groups of 5
for (q, i) in enumerate(np.arange(0, len(questionCnts), 5)):
    # sort question circles group from left to right
    cnts = contours.sort_contours(questionCnts[i:i + 5])[0]
    # bubbled answer index
    bubbled = None

    # for circle in sorted group of 5, create a mask (only show current circle)
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

# console print score
# TODO: ACTUALLY SAVE TO DB
print("[INFO] score: {}/{} {:.2f}%".format(correct, AMOUNT, score))

# sheet print score
cv2.putText(image, "{}/{} {:.2f}%".format(correct, AMOUNT, score),
            (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 0, 255), 2)


cv2.imwrite('drawresults/imcf.png', image)
cv2.imwrite('drawresults/grf.png', gray)
cv2.imwrite('drawresults/blf.png', blurred)
cv2.imwrite('drawresults/edf.png', edged)
cv2.imwrite('drawresults/thf.png', thresh)
