""" Image Processing part of the project
This script is responsible for the image processing aspect of the project such as :
detecting tags, warp the perspective, detection and color identification
"""

import cv2
import cv2.aruco
import numpy as np
import shutil
import sys
from scripts import parameters as p

width = p.width
height = p.height


# FUNCTION to detect ArUCo tags
def tagDetect(image, tagType):
    """ Function to detect ArUCo tags

    Source : MULNARD T. and https://www.pyimagesearch.com/2020/12/21/detecting-aruco-markers-with-opencv-and-python/

    :param image: image array : coming from cv2.imread
    :param tagType: string : used aruco tag type
    :return: list of the centers of each tags, image array with the detected tags
    """

    tagList = []
    tempList = []
    tagCenters = {}

    # ArUco dictionaries built into the OpenCV library.
    ARUCO_DICT = {
        "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
        "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
        "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
        "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
        "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
        "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
        "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
        "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
        "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
        "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
        "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
        "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    }

    # verify that the supplied ArUCo tag exists and is supported by OpenCV to prevent errors
    if ARUCO_DICT.get(tagType, None) is None:
        print("[info] ArUCo tag of '{}' is not supported".format(tagType))
        sys.exit(0)

    # load the ArUCo dictionary, instantiate the ArUCo parameters, and detect the markers
    # corners = (x,y) coordinates of the markers, ids = identifiers of the markers, rejected = potential rejected marks
    arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[tagType])
    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(image, arucoDict, parameters=arucoParams)

    # verify at least one ArUco marker was detected
    if len(corners) > 0:
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in)
            # top-left, top-right, bottom-right, bottom-left  border
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # convert the useful (x,y)-coordinate pairs to integers
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))

            # draw the bounding box of the ArUCo detection
            # cv2.rectangle(destination, start, end, color, thickness)
            cv2.rectangle(image, bottomRight, topLeft, (0, 255, 0), 4)

            # compute and draw the center (x,y)-coordinates of the ArUCo marker
            # cv2.circle(destination, (cX, cY), radius, color, thickness
            cX = int((bottomRight[0] + topLeft[0]) / 2.0)
            cY = int((bottomRight[1] + topLeft[1]) / 2.0)
            cv2.circle(image, (cX, cY), 3, (0, 0, 255), -1)

            # draw the ArUCo marker ID on the image
            # cv2.putText( destination, text, start_point, font, size, color, thickness
            cv2.putText(image, str(markerID), (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # append the value to the list
            tagList.append((cX, cY))

    # algorithm to identify the position of each tags base on the sum of x+y values
    try:
        for i in range(0, 4):
            # id used to set each (x,y) to its original location in tagCenters
            tempList.append((tagList[i][0] + tagList[i][1], i))
        # assignation based on the id
        tempList.sort()
        tagCenters["TOP_R"] = tagList[tempList[0][1]]
        tagCenters["BOT_R"] = tagList[tempList[1][1]]
        tagCenters["TOP_L"] = tagList[tempList[2][1]]
        tagCenters["BOT_L"] = tagList[tempList[3][1]]
    except IndexError:
        return tagCenters, image

    return tagCenters, image


# FUNCTION to warp perspective of the image
def warpPerspective(image, tagList, offset=0):
    """ FUNCTION to warp perspective of the image

    Source : Mulnard T. and Vachaudez J.

    :param image: image array : coming from cv2.imread
    :param tagList: list : with the coordinates tuple of the 4 detected tags
    :param offset: integer : horizontal offset if the tags are not exactly in the corner
    :return: image array : unwarped image
    """
    original = np.float32([[tagList["TOP_R"][0] - offset, tagList["TOP_R"][1]],
                           [tagList["TOP_L"][0] + offset, tagList["TOP_L"][1]],
                           [tagList["BOT_L"][0] + offset, tagList["BOT_L"][1]],
                           [tagList["BOT_R"][0] - offset, tagList["BOT_R"][1]]])
    unwarped = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    matrix = cv2.getPerspectiveTransform(original, unwarped)
    unwarped_img = cv2.warpPerspective(image, matrix, (width, height))

    # return the image array
    return unwarped_img


# FUNCTION to remove the background in an image using the most dominant color
def removeBackground(image, rectOffset, circOffset, onlyCountour=False):
    """ FUNCTION to remove the background in an image using the most dominant color

    Source : Mulnard T. and https://stackoverflow.com/a/56878194

    :param image: image array : coming from cv2.imread
    :param rectOffset: integer : width of the black rectangle on the four sides
    :param circOffset: integer : radius of the black circles in each corners for holes removal
    :param onlyCountour: boolean : to bypass the background removing process and only show the black circles/rectangles
    :return: image array : unwarped image
    """
    domColors = __dominantcolor(image)

    # threshold based on the most dominant color of the image
    # define the lower and upper limits based on the most dominant color of the image
    if not onlyCountour:
        if (domColors[1] > domColors[0]) and (domColors[1] > domColors[2]):   # Pool table is green
            lower = np.array(p.tableGREENMin)
            upper = np.array(p.tableGREENMax)
        elif (domColors[0] > domColors[1]) and (domColors[0] > domColors[2]):  # Pool table is blue
            lower = np.array(p.tableBLUEMin)
            upper = np.array(p.tableBLUEMax)
        elif (domColors[2] > domColors[1]) and (domColors[2] > domColors[0]):  # Pool table is red
            lower = np.array(p.tableREDMin)
            upper = np.array(p.tableREDMax)
        else:
            print("<error> pool table color not correctly detected")
            lower = np.array([0, 0, 0])
            upper = np.array([255, 255, 255])

        # Create mask to only select the desired color
        thresh = cv2.inRange(image, lower, upper)

        # apply morphology and creating mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40))
        mask = 255 - cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # apply mask to image
        image = cv2.bitwise_and(image, image, mask=mask)

    # create black rectangles on the 4 sides
    clR = (0, 0, 0)
    h, w, channels = image.shape
    cv2.rectangle(image, (0, 0), (w, rectOffset), clR, -1)
    cv2.rectangle(image, (0, 0), (rectOffset, h), clR, -1)
    cv2.rectangle(image, (0, h), (w, h - rectOffset), clR, -1)
    cv2.rectangle(image, (w, 0), (w - rectOffset, h), clR, -1)

    # create black circles in the 4 corners
    clC = (0, 0, 0)
    cv2.circle(image, (0, 0), circOffset, clC, -1)
    cv2.circle(image, (0, height), circOffset, clC, -1)
    cv2.circle(image, (width, 0), circOffset, clC, -1)
    cv2.circle(image, (width, height), circOffset, clC, -1)
    # return results
    return image


# FUNCTION to detect the most dominant color
def __dominantcolor(image):
    """ FUNCTION to detect the most dominant color

    Source : https://stackoverflow.com/a/50900494

    :param image: image array : coming from cv2.imread
    :return: list : detected BGR (blue, green, red) value
    """
    listBGR = []
    data = np.reshape(image, (-1, 3))
    data = np.float32(data)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 5, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 5, flags)
    listBGR.append(int(centers[0][0]))  # blue value of most dominant color in the image
    listBGR.append(int(centers[0][1]))  # green value of most dominant color in the image
    listBGR.append(int(centers[0][2]))  # red value of most dominant color in the image

    return listBGR


# FUNCTION to see if the detected BGR color is in range of the threshold
def __colorInRange(listBGR, colorMIN, colorMAX):
    """ PRIVATE FUNCTION to see if the detected BGR color is in range of the threshold

    Source : Mulnard T.

    :param listBGR: list of BGR (blue, green, red) value
    :param colorMIN: parameter : minimum threshold
    :param colorMAX: parameter : maximum threshold
    :return: boolean (true if in range)
    """
    inRange = True
    for i in range(0, 3):
        if colorMIN[i] > listBGR[i] or colorMAX[i] < listBGR[i]:
            inRange = False

    return inRange


# FUNCTION to detect circles in the image
def circleDetection(image, dp=7, minDist=50, minRadius=15, maxRadius=70, imgDisplayOut=True):
    """ FUNCTION to detect circles in the image

    Source : Mulnard T.

    :param image: image array coming from cv2.imread
    :param dp: integer - parameter of cv2.HoughCircles
    :param minDist: integer - parameter of cv2.HoughCircles
    :param minRadius: integer - parameter of cv2.HoughCircles
    :param maxRadius : integer - parameter of cv2.HoughCircles
    :param imgDisplayOut: boolean : if the modification should be done on the output image
    :return: image array with results, list of the detected circles with their data
    """

    listCircles = {}
    circText = ""
    circColor = (255, 255, 255)
    grayImg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(grayImg, cv2.HOUGH_GRADIENT, dp, minDist, minRadius=minRadius, maxRadius=maxRadius)

    # ensure at least some circles were found
    if circles is not None:

        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # creating an image by taking the zone where the circle is
            # offset is there to detect the best color possible
            offset = 0.8
            imgTemp = image[(y - int(r * offset)):(y + int(r * offset)), (x - int(r * offset)):(x + int(r * offset))]

            # detecting the most dominant color then check for every color
            listBGR = __dominantcolor(imgTemp)

            if (listBGR[0] != 0) or (listBGR[1] != 0) or (listBGR[2] != 0):
                # check if WHITE ball
                if __colorInRange(listBGR, p.colWHITEMin, p.colWHITEMax):
                    circText = "WHITE"
                    circColor = p.colWHITEMax

                # check if YELLOW ball
                elif __colorInRange(listBGR, p.colYELLOWMin, p.colYELLOWMax):
                    circText = "YELLOW"
                    circColor = p.colYELLOWMax

                # check if WHITE target
                elif __colorInRange(listBGR, p.gmColWHITEMin, p.gmColWHITEMax):
                    circText = "WHITE"
                    circColor = p.gmColWHITEMax

                # check if YELLOW target
                elif __colorInRange(listBGR, p.gmColYELLOWMin, p.gmColYELLOWMax):
                    circText = "YELLOW"
                    circColor = p.gmColYELLOWMax

                # check if CYAN target
                elif __colorInRange(listBGR, p.gmColCYANMin, p.gmColCYANMax):
                    circText = "CYAN"
                    circColor = p.gmColCYANMax

                # check if BROWN target
                elif __colorInRange(listBGR, p.gmColBROWNMin, p.gmColBROWNMax):
                    circText = "BROWN"
                    circColor = p.gmColBROWNMax

                # check if BLUE ball
                elif __colorInRange(listBGR, p.colBLUEMin, p.colBLUEMax):
                    circText = "BLUE"
                    circColor = p.colBLUEMax

                # check if RED ball
                elif __colorInRange(listBGR, p.colREDMin, p.colREDMax):
                    circText = "RED"
                    circColor = p.colREDMax

                listCircles[circText] = (x, y)

            # draw the circle in the output image, then draw a rectangle corresponding to the center of the circle
            # put text to know the color of the ball as stated in the dictionnary
            if imgDisplayOut:
                cv2.putText(image, circText, (x, y + r), cv2.FONT_HERSHEY_SIMPLEX, 2, circColor, 2)
                cv2.circle(image, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    return image, listCircles


# FUNCTION to warp the image send via the projector onto the table
def getPrjMatrix(fromTestImg=False):
    """ FUNCTION to warp the image send via the projector onto the table

    Source : Mulnard T.

    :param fromTestImg: boolean
    :return: transformation matrix

    """
    # loading the image in normal mode. Resize in each case to avoid problems with the matrix
    # if statement to be able to send a custom image path for testing
    if fromTestImg:
        imgPath = p.testKstIN
    else:
        imgPath = p.kstImgPath

    imgIN = cv2.imread(imgPath)
    imgIN = cv2.resize(imgIN, (p.width, p.height))

    # offset for each set of tags if necessary in the future
    offsetPRJ = (0, 0)
    offsetTAB = (0, 0)

    # detecting and sorting the tags to get their positions + output of an image
    print("   > detecting the tags...")
    tagListTAB, image = tagDetect(imgIN, p.tagType)
    cv2.imwrite(p.kstTagged, image)
    tagListPRJ, image = tagDetect(image, p.tagTypePRJ)
    cv2.imwrite(p.kstTagged, image)

    # tags on the pool table, target positions
    print("   > analysing the data...")
    try:
        original = np.float32([[tagListPRJ["TOP_R"][0] - offsetPRJ[0], tagListPRJ["TOP_R"][1] - offsetPRJ[1]],
                               [tagListPRJ["TOP_L"][0] + offsetPRJ[0], tagListPRJ["TOP_L"][1] + offsetPRJ[1]],
                               [tagListPRJ["BOT_L"][0] + offsetPRJ[0], tagListPRJ["BOT_L"][1] + offsetPRJ[1]],
                               [tagListPRJ["BOT_R"][0] - offsetPRJ[0], tagListPRJ["BOT_R"][1] + offsetPRJ[1]]])
        # tags on the projected image, initial positions
        unwarped = np.float32([[tagListTAB["TOP_R"][0] - offsetTAB[0], tagListTAB["TOP_R"][1] - offsetTAB[1]],
                               [tagListTAB["TOP_L"][0] + offsetTAB[0], tagListTAB["TOP_L"][1] + offsetTAB[1]],
                               [tagListTAB["BOT_L"][0] + offsetTAB[0], tagListTAB["BOT_L"][1] + offsetTAB[1]],
                               [tagListTAB["BOT_R"][0] - offsetTAB[0], tagListTAB["BOT_R"][1] + offsetTAB[1]]])

        # matrix to modify the image
        matrix = cv2.getPerspectiveTransform(original, unwarped)

        # output of the image for a visual representation
        image = cv2.imread(p.kstTemplateIN)
        image = cv2.resize(image, (p.width, p.height))
        image = cv2.warpPerspective(image, matrix, (p.width, p.height))
        cv2.imwrite(p.kstTemplateOUT, image)
    except KeyError:
        print("<Error> Incorrect tags detection. Make sure everything is correctly placed and try again")
        matrix = 0
        
    return matrix
