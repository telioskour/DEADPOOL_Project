import cv2
import time
from scripts import imgProcess, parameters as p
from numpy import loadtxt, savetxt
from tabulate import tabulate

# try to import and setup the PiCamera (used to avoid errors when developing on another computer than the raspberry
try:
    from picamera import PiCamera
    camera = PiCamera()
    camera.resolution = p.camRes
    camera.rotation = p.camRot
except NameError and ModuleNotFoundError:
    print("   <WARNING> camera module not found")


# FUNCTION to take a picture with the camera
def imgTake(camPath, preview=False):
    """ Take a picture with the Pi camera

    Source : Mulnard T. and https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0

    :param camPath: string : with output path for the camera
    :param preview: boolean : if preview is wanted or not
    :return: nothing
    """

    print("   > taking picture...")
    try:
        if preview:
            camera.start_preview()
        camera.rotation = p.camRot 
        time.sleep(p.camWait)
        camera.capture(camPath)
        if preview:
            camera.stop_preview()
    except NameError:
        print("<WARNING> camera module not found")
    

# FUNCTION to show an image in fullscreen
def imgShow(imgPath, windowName="window", waitTime=0, fullscreen=True):
    """ Show an image on the screen (default in fullscreen)

    Source : MULNARD T. and https://gist.github.com/ronekko/dc3747211543165108b11073f929b85e

    :param imgPath: string : path of the image to show
    :param windowName: string : name of the window
    :param waitTime: integer : wait time before the window is closed. Default 0 = wait for key press
    :param fullscreen: boolean : if the output should be in full screen
    """

    print("   > showing image...")
    image = cv2.imread(imgPath)
    if fullscreen:
        cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(windowName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(windowName, image)
    cv2.waitKey(waitTime)
    cv2.destroyAllWindows()


# FUNCTION to set the keystone matrix
def setKstMatrix(fromTesting=False):
    """ FUNCTION to set the keystone matrix

    Source : MULNARD T.

    :param fromTesting: boolean : is the keystone done from testing or not
    :return: Nothing
    """
    imgShow(p.kstTemplateIN)
    imgTake(p.kstImgPath)
    matrix = imgProcess.getPrjMatrix(fromTestImg=fromTesting)
    try:
        savetxt(p.kstData, matrix, delimiter=",")
        print("   > keystone done")
    except ValueError:
        matrix = 0

# FUNCTION perspective correction and detecting the ball(s)
def detectBall(imgPath):
    """ FUNCTION to correct the perspective adn detect the balls

    Source : Mulnard T.

    :param imgPath: string : path of the start image
    :return: dictionary : name and coordinates of the detected balls
    """

    image = cv2.imread(imgPath)

    print("   > detecting tags...")
    tagCenters = imgProcess.tagDetect(image, p.tagType)[0]
    if tagCenters == {}:
        print("<WARNING> Failed to detect the tags")
        dictCircles = {}
        return dictCircles

    print("   > warping image...")
    image = imgProcess.warpPerspective(image, tagCenters, p.warpOffset)
    cv2.imwrite(p.pathWarped, image)

    # removing background
    print("   > removing background...")
    image = imgProcess.removeBackground(image, p.bRectDist, p.bCircRad)
    cv2.imwrite(p.pathNoBack, image)

    # detecting the white ball using circle detection
    print("   > detecting the circles...")
    image, dictCircles = imgProcess.circleDetection(image)
    cv2.imwrite(p.pathCircleDtct, image)

    return dictCircles


# PRIVATE FUNCTION to detect if the centers of the detected ball is in the target zone
def __inZone(ballCenter, targetCenter, targetRadius):
    """ Detect if the centers of the detected ball is in the target zone (variable radius)

    Source : Mulnard T.

    :param ballCenter: integer tuple : coordinates of the ball
    :param targetCenter: integer tuple : coordinates of the target
    :param targetRadius: integer : target radius
    :return: boolean value (true if in zone)
    """
    isInZone = False
    if ((ballCenter[0] - targetCenter[0]) ** 2) + ((ballCenter[1] - targetCenter[1]) ** 2) <= (targetRadius ** 2):
        isInZone = True
    return isInZone


# PRIVATE FUNCTION to get the score based on the coordinates
def __getScore(ballCenter, targetCenter):
    """ FUNCTION to get the score based on the ball and the target coordinates

    Source : Mulnard T.

    :param ballCenter: integer tuple :  coordinates of the ball
    :param targetCenter: integer tuple : coordinates of the target
    :return: integer : the calculated score
    """
    score = abs(ballCenter[0] - targetCenter[0])
    score += abs(ballCenter[1] - targetCenter[1])
    return score


# PRIVATE FUNCTION to set the score
def displayScore(gameType, score, winLose, gmBestScore, gmScoreData, gmStateData, gmDisplayData):
    """ FUNCTION to display the score of the cumulated games

    Source : Mulnard T.

    :param gameType : integer : id of the game played
    :param score: integer : current player score
    :param winLose : integer table : the number of game win and lose per game
    :param gmBestScore: integer list : best score for each game
    :param gmScoreData: integer : score of the last played game
    :param gmStateData: byte : game state of the last played game
    :param gmDisplayData: string : info if win or lose
    """
    if gmStateData != -1:
        score += gmScoreData
        winLose[gameType - 1][gmStateData] += 1
            
        if gmScoreData < gmBestScore[gameType - 1] or gmBestScore[gameType - 1] == 0:
            gmBestScore[gameType - 1] = gmScoreData

        tableData = [["Win", winLose[0][0], winLose[1][0], winLose[2][0]],
                     ["Defeat", winLose[0][1], winLose[1][1], winLose[2][1]],
                     ["Best Score ", gmBestScore[0], gmBestScore[1], gmBestScore[2]]]

        tableHeaders = [" Game 1", " Game 2", " Game 3"]
        table = tabulate(tableData, tableHeaders, tablefmt="fancy_grid")
        print("╒═══════════════════════════╤════════════════════╕")
        print("│ {:>4s} with score : {:>7} │ Total : {:>9}  │".format(gmDisplayData.split(" ", 1)[0], gmScoreData, score))
        print("╘═══════════════════════════╧════════════════════╛")
        print(table)
        print("[GAME {}] {}".format(gameType, gmDisplayData))
        input("[GAME {}] Here are you results ! Press 'Enter' to go to the main menu : ".format(gameType))
        print("")

        return table, score, winLose, gmBestScore

    else:
        return "", score, winLose, gmBestScore


# FUNCTION for the first game
def startGame1(imgGamePath, targetRadius, placementRadius=100):
    """ FUNCTION to play the first game (one ball / one target)

    Source : Mulnard T.

    :param imgGamePath: parameter : path of the game picture
    :param targetRadius: parameter : radius of the zone's target
    :param placementRadius: optional radius for the correct start position
    :return: score and data if win or lose game + string with infos to display
    """

    print("[GAME 1] Welcome to the first game type : send the ball in the zone with the best accuracy")

    image = cv2.imread(imgGamePath)
    image = cv2.resize(image, (p.width, p.height))

    # getting the matrix data
    try:
        matrixTransform = loadtxt(p.kstData, delimiter=",")
    except IOError:
        print("   > matrix data not found, please set the keystone before playing")
        return 0, -1, "ERROR"
    try:
        # warping the image and detecting the tags
        image = cv2.warpPerspective(image, matrixTransform, (p.width, p.height))
        image, listTargets = imgProcess.circleDetection(image, dp=7, minDist=100, minRadius=20, maxRadius=80,
                                                        imgDisplayOut=False)

        cv2.imwrite(p.gmToDisplay, image)

        # drawing the zone around the target

        cv2.circle(image, listTargets["BROWN"], targetRadius, p.gmColBROWNMax, 4)
        cv2.imwrite(p.gmToDisplay, image)

        # start ball position
        print("[GAME 1] Initial ball position. Press 'Enter' when done")
        time.sleep(2)
        correctPlacement = False
        while not correctPlacement:
            imgShow(p.gmToDisplay)
            imgTake(p.pathCamIN)
            listBalls = detectBall(p.pathCamIN)

            # checking if the placement is correct
            if __inZone(listBalls["WHITE"], listTargets["WHITE"], placementRadius):
                correctPlacement = True
                print("   > the ball is correctly placed")
            else:
                print("   > the ball is no correctly placed, please try again")

        # playing the game and processing data
        print("[GAME 1] Start playing ! Press 'Enter' when done")
        time.sleep(2)
        imgShow(p.gmToDisplay)
        imgTake(p.pathCamIN)
        listBalls = detectBall(p.pathCamIN)
        print("   > processing data...")

        # getting the score
        score = __getScore(listBalls["WHITE"], listTargets["BROWN"])
        if __inZone(listBalls["WHITE"], listTargets["BROWN"], targetRadius):
            displayInfo = "WIN ! You are the best"
            gameStat = 0
        else:
            displayInfo = "LOSE ! Better luck next time"
            gameStat = 1
        return score, gameStat, displayInfo

    except KeyError or cv2.Error:
        print("<Error> An error occurred during the game, please make sure everything is set correctly")
        return 0, -1, "ERROR"


# FUNCTION for the second game
def startGame2(imgGamePath, targetRadius, placementRadius=100):
    """ FUNCTION to play the first game (one ball / one target)

    Source : Mulnard T.

    :param imgGamePath: parameter : path of the game picture
    :param targetRadius: parameter : radius of the zone's target
    :param placementRadius: optional radius for the correct start position
    :return: score and data if win or lose game + string with infos to display
    """

    print("[GAME 2] Welcome to the second game type : send the ball in the zone without touching the red one")

    image = cv2.imread(imgGamePath)
    image = cv2.resize(image, (p.width, p.height))

    # getting the matrix data
    try:
        matrixTransform = loadtxt(p.kstData, delimiter=",")
    except IOError:
        print("   > matrix data not found, please set the keystone before playing")
        return 0, -1, "ERROR"

    # warping the image and detecting the tags
    image = cv2.warpPerspective(image, matrixTransform, (p.width, p.height))
    image, listTargets = imgProcess.circleDetection(image, dp=7, minDist=100, minRadius=20, maxRadius=80,
                                                    imgDisplayOut=False)

    # drawing the zone around the target
    try:
        cv2.circle(image, listTargets["BROWN"], targetRadius, p.gmColBROWNMax, 4)
        cv2.imwrite(p.gmToDisplay, image)

        # start ball position
        print("[GAME 2] Initial ball position. Press 'Enter' when done")
        time.sleep(2)
        correctPlacement = False
        while not correctPlacement:
            imgShow(p.gmToDisplay)
            imgTake(p.pathCamIN)
            listBalls = detectBall(p.pathCamIN)

            # checking if the placement is correct
            if __inZone(listBalls["WHITE"], listTargets["WHITE"], placementRadius):
                if __inZone(listBalls["YELLOW"], listTargets["YELLOW"], placementRadius):
                    correctPlacement = True
                    print("   > the balls are correctly placed")
                else:
                    print("   > the white ball is correctly placed but not the yellow one, please try again")
            else:
                if __inZone(listBalls["YELLOW"], listTargets["YELLOW"], placementRadius):
                    print("   > the yellow ball is correctly placed but not the white one, please try again")
                else:
                    print("   > none of the balls are correctly placed, please try again")

        # playing the game and processing data
        print("[GAME 2] Start playing ! Press 'Enter' when done")
        time.sleep(2)
        imgShow(p.gmToDisplay)
        imgTake(p.pathCamIN)
        listBalls = detectBall(p.pathCamIN)
        print("   > processing data...")

        # getting the score
        score = __getScore(listBalls["WHITE"], listTargets["BROWN"])
        if __inZone(listBalls["YELLOW"], listTargets["YELLOW"], placementRadius):
            if __inZone(listBalls["WHITE"], listTargets["BROWN"], targetRadius):
                displayInfo = "WIN ! You are the best"
                gameStat = 0
            else:
                displayInfo = "LOSE ! Better luck next time"
                gameStat = 1
        else:
            displayInfo = "LOSE ! The yellow ball moved"
            gameStat = 1
            score = __getScore(listBalls["YELLOW"], listTargets["YELLOW"])*2

        return score, gameStat, displayInfo

    except KeyError:
        print("<Error> An error occurred during the game, please make sure everything is set correctly")
        return 0, -1, "ERROR"


# FUNCTION for the third game
def startGame3(imgGamePath, targetRadius, placementRadius=100):
    """ FUNCTION to play the first game (one ball / one target)

    Source : Mulnard T.

    :param imgGamePath: parameter : path of the game picture
    :param targetRadius: parameter : radius of the zone's target
    :param placementRadius: optional radius for the correct start position
    :return: score and data if win or lose game + string with infos to display
    """

    print("[GAME 3] Welcome to the third game type : send the balls in their zones by only touching the white one")

    image = cv2.imread(imgGamePath)
    image = cv2.resize(image, (p.width, p.height))

    # getting the matrix data
    try:
        matrixTransform = loadtxt(p.kstData, delimiter=",")
    except IOError:
        print("   > matrix data not found, please set the keystone before playing")
        return 0, -1, "ERROR"

    # warping the image and detecting the tags
    image = cv2.warpPerspective(image, matrixTransform, (p.width, p.height))
    image, listTargets = imgProcess.circleDetection(image, dp=7, minDist=100, minRadius=20, maxRadius=80,
                                                    imgDisplayOut=False)

    # drawing the zone around the target
    try:
        cv2.circle(image, listTargets["BROWN"], targetRadius, p.gmColBROWNMax, 4)
        cv2.circle(image, listTargets["CYAN"], targetRadius, p.gmColCYANMax, 4)
        cv2.imwrite(p.gmToDisplay, image)

        # start ball position
        print("[GAME 3] Initial ball position. Press 'Enter' when done")
        time.sleep(2)
        correctPlacement = False
        while not correctPlacement:
            imgShow(p.gmToDisplay)
            imgTake(p.pathCamIN)
            listBalls = detectBall(p.pathCamIN)

            # checking if the placement is correct
            if __inZone(listBalls["WHITE"], listTargets["WHITE"], placementRadius):
                if __inZone(listBalls["YELLOW"], listTargets["YELLOW"], placementRadius):
                    correctPlacement = True
                    print("   > the balls are correctly placed")
                else:
                    print("   > the white ball is correctly placed but not the yellow one, please try again")
            else:
                if __inZone(listBalls["YELLOW"], listTargets["YELLOW"], placementRadius):
                    print("   > the yellow ball is correctly placed but not the white one, please try again")
                else:
                    print("   > none of the balls are correctly placed, please try again")

        # playing the game and processing data
        print("[GAME 3] Start playing ! Press 'Enter' when done")
        time.sleep(2)
        imgShow(p.gmToDisplay)
        imgTake(p.pathCamIN)
        listBalls = detectBall(p.pathCamIN)
        print("   > processing data...")

        # getting the score
        score = __getScore(listBalls["WHITE"], listTargets["BROWN"])
        score += __getScore(listBalls["YELLOW"], listTargets["CYAN"])
        score /= 2
        if __inZone(listBalls["WHITE"], listTargets["BROWN"], placementRadius):
            if __inZone(listBalls["YELLOW"], listTargets["CYAN"], targetRadius):
                displayInfo = "WIN ! You are the best"
                gameStat = 0
            else:
                displayInfo = "LOSE ! The yellow ball is not in his target"
                gameStat = 1
        else:
            if __inZone(listBalls["YELLOW"], listTargets["CYAN"], targetRadius):
                displayInfo = "LOSE ! The white ball is not in his target"
                gameStat = 1
            else:
                displayInfo = " LOSE ! None of the balls are in their target"
                gameStat = 1

        return score, gameStat, displayInfo

    except KeyError:
        print("<Error> An error occurred during the game, please make sure everything is set correctly")
        return 0, -1, "ERROR"
