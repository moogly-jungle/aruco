# Standard imports
import cv2
import numpy as np;

clic_pt = None

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        click_pt = (x,y)
        print('click on point ', click_pt)
        print('HSV : ', hsv[y,x])
        
# Read image
# im = cv2.imread("tags/x.png", cv2.IMREAD_GRAYSCALE)
im = cv2.imread("tags/x.png")

hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
cv2.imshow("image", im)
cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)
cv2.waitKey(0)


# Threshold of blue in HSV space
lower_blue = np.array([5, 200, 200])
upper_blue = np.array([20, 255, 255])
 
# preparing the mask to overlay
mask = cv2.inRange(hsv, lower_blue, upper_blue)
     
# The black region in the mask has the value of 0,
# so when multiplied with original image removes all non-blue regions
result = cv2.bitwise_and(im, im, mask = mask)
gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

cv2.imshow("filtered", gray)
cv2.waitKey(0)


def init_blob_detector():
    params = cv2.SimpleBlobDetector_Params()
    params.minDistBetweenBlobs = 1
    params.minThreshold = 10
    params.maxThreshold = 255
    params.filterByArea = False
    params.minArea = 10
    params.maxArea = 2000
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    # #detector = cv2.SimpleBlobDetector(params)
    detector = cv2.SimpleBlobDetector_create(params)
    return detector 

# Set up the detector with default parameters.
# detector = cv2.SimpleBlobDetector()

detector = init_blob_detector()

# detector = cv2.SimpleBlobDetector()

# Detect blobs.
keypoints = detector.detect(gray)
print(keypoints)
# Draw detected blobs as red circles.
# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# Show keypoints
cv2.imshow("Keypoints", im_with_keypoints)
cv2.waitKey(0)
