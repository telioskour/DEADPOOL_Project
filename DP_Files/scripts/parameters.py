""" Parameters scripts
This file is used for parameters that could be changed by the end-user. They might vary from one system
to another. Others parameters aren't subject to change (image  path for example)
"""

import json

# load user-modifiable parameters from the 'parameters.json' file
with open("assets/parameters.json", "r") as parametersFile:
    pFile = json.load(parametersFile)

    # camera parameters
    camRes = pFile['camera_resolution']
    camRot = pFile['camera_rotation'][0]
    camWait = pFile['camera_waitTime'][0]

    # general width and height of the images
    width = pFile['image_resolution'][0]
    height = pFile['image_resolution'][1]

    # offset distance for the tags in the perspective warper
    warpOffset = pFile['tag_horizontal_offset'][0]

    # offset for the contour in the background removing process
    bRectDist = pFile['background_rectangle_offset'][0]
    bCircRad = pFile['background_circle_radius'][0]

    # variable BGR for the color detection of the pool table
    tableGREENMin = pFile['table_GREEN_min_value']
    tableGREENMax = pFile['table_GREEN_max_value']
    tableBLUEMin = pFile['table_BLUE_min_value']
    tableBLUEMax = pFile['table_BLUE_max_value']
    tableREDMin = pFile['table_RED_min_value']
    tableREDMax = pFile['table_RED_max_value']

    # variable BGR for the color detection of the balls
    colYELLOWMin = pFile['ball_YELLOW_min_value']
    colYELLOWMax = pFile['ball_YELLOW_max_value']
    colWHITEMin = pFile['ball_WHITE_min_value']
    colWHITEMax = pFile['ball_WHITE_max_value']
    colBLUEMin = pFile['ball_BLUE_min_value']
    colBLUEMax = pFile['ball_BLUE_max_value']
    colREDMin = pFile['ball_RED_min_value']
    colREDMax = pFile['ball_RED_max_value']

    # variable BGR for the color of the target of the games
    gmColYELLOWMax = pFile['game_YELLOW_max_value']
    gmColYELLOWMin = pFile['game_YELLOW_min_value']
    gmColWHITEMax = pFile['game_WHITE_max_value']
    gmColWHITEMin = pFile['game_WHITE_min_value']
    gmColBROWNMax = pFile['game_BROWN_max_value']
    gmColBROWNMin = pFile['game_BROWN_min_value']
    gmColCYANMax = pFile['game_CYAN_max_value']
    gmColCYANMin = pFile['game_CYAN_min_value']

    # load the radius of the finish zone for the games
    zoneRadius = pFile["game_zone_radius"][0]

# tag type of the projector
tagType = "DICT_5X5_50"
tagTypePRJ = "DICT_7X7_100"

# path for the images
testImgPath = "assets/testImg.png"
testCamIN = "assets/testCamOUT.png"
testKstIN = "assets/keystone/kstInputTEST.png"
pathCamIN = "assets/output/0-cam_input.png"
pathWarped = "assets/output/1-warped.png"
pathNoBack = "assets/output/2-no_background.png"
pathCircleDtct = "assets/output/3-circle_detect.png"
kstTemplateIN = "assets/keystone/kstTemplateIN.png"
kstTemplateOUT = "assets/keystone/kstTemplateOUT.png"
kstImgPath = "assets/keystone/kstInputCAMERA.png"
kstTagged = "assets/keystone/kstTagged.png"
kstData = "assets/keystone/matrix.csv"
gmTemplate = "assets/games/gameTemplate.png"
gmToDisplay = "assets/games/gameDisplay.png"
gm1LinePath = "assets/games/game01_Line.png"
gm2ObstaclePath = "assets/games/game02_Obstacle.png"
gm3ContactPath = "assets/games/game03_Contact.png"


# FUNCTION to play the first game (one ball / one target)
def __modifyValues(paramFile, nbrValues, condValues, strInfo):
    """ FUNCTION to play the first game (one ball / one target)

    Source : Mulnard T.

    :param paramFile: string : name of the parameters as specified in json file
    :param nbrValues: integer : number of value to look for in the user input
    :param condValues: string list : string with acceptable values
    :param strInfo: string : information to display at the input
    :return: integer list : modified values
    """
    inputOK = False
    newValues = []

    # verify the input is correct
    while not inputOK:
        strValues = input(strInfo).split()

        # if the user has pressed 'Enter'
        if not strValues:
            inputOK = True
            with open("assets/parameters.json", "r") as jsonFile:
                file = json.load(jsonFile)
                newValues = file[paramFile]
        # if the user has entered "default"
        elif strValues[0] == "default":
            inputOK = True
            with open("assets/defaultParameters.json", "r") as jsonFile:
                defaultFile = json.load(jsonFile)
                newValues = defaultFile[paramFile]
        # check if the input data are correct
        elif len(strValues) == nbrValues:
            for i in range(0, len(strValues)):
                if strValues[i] not in condValues:
                    inputOK = False
                else:
                    inputOK = True
                    newValues.append(int(strValues[i]))

    # read all the data in the file
    with open("assets/parameters.json", "r") as jsonFile:
        newData = json.load(jsonFile)

    newData[paramFile] = newValues

    # write the new data into the file
    with open("assets/parameters.json", "w") as jsonFile:
        json.dump(newData, jsonFile)

    return newValues


# PRIVATE FUNCTION to play the set an integer parameter
def __setInteger(paramValue, paramFile, condValues, strInfo):
    """ PRIVATE FUNCTION to play the set an integer parameter

    Source : Mulnard T.

    :param paramValue: integer list : current value of the parameter
    :param paramFile: string : name of the parameters as specified in json file
    :param condValues: string list : string with acceptable values
    :param strInfo: string : information to display at the input
    :return: integer list : modified values
    """
    print("      > Current value for the parameter is : {}".format(paramValue))
    paramValue = __modifyValues(paramFile, 1, condValues, strInfo)
    print("      > Updated value for the parameter is : {}".format(paramValue))

    return paramValue[0]


# PRIVATE FUNCTION to play the set the resolution
def __setResolution(paramValues, paramNames):
    """ PRIVATE FUNCTION to play the set the resolution

    Source : Mulnard T.

    :param paramValue: integer list : current value of the parameter
    :param strInfo: string : information to display at the input
    :return: integer list : modified values
    """
    condValues = ["default"]
    condValues.extend(["{:01d}".format(x) for x in range(1, 3000)])

    print("      > Current value for the parameter is : ({}, {})".format(paramValues[0], paramValues[1]))
    strInfo = "      > Enter the resolution (w h) with space as separator (max = 3280x2464 / default / 'Enter') : "
    paramValues = __modifyValues(paramNames, 2, condValues, strInfo)
    print("      > Updated value for the parameter is : ({}, {})".format(paramValues[0], paramValues[1]))

    return paramValues[0], paramValues[1]


# PRIVATE FUNCTION to play the set the RGB threshold
def __setRGBThreshold(paramValues, paramNames):
    """ PRIVATE FUNCTION to play the set the RGB threshold

    Source : Mulnard T.

    :param paramValue: integer list : current value of the parameter
    :param strInfo: string : information to display at the input
    :return: integer list : modified values
    """
    condValues = ["default"]
    condValues.extend(["{:01d}".format(x) for x in range(0, 256)])

    print("      > Current color threshold is set to : ({}, {})".format(paramValues[0], paramValues[1]))
    strInfo = "      > Enter the MIN BGR with space as separator (0-256 / default / 'Enter') : "
    paramValues[0] = __modifyValues(paramNames[0], 3, condValues, strInfo)
    strInfo = "      > Enter the MAX BGR with space as separator (0-256 / default / 'Enter') : "
    paramValues[1] = __modifyValues(paramNames[1], 3, condValues, strInfo)
    print("      > Updated color threshold is set to : ({}, {})".format(paramValues[0], paramValues[1]))

    return paramValues[0], paramValues[1]


# FUNCTION to set the finish zone radius in the games
def setZoneRadius():
    """ FUNCTION to set the finish zone radius in the games

    Source : Mulnard T.

    :return: nothing
    """
    global zoneRadius
    condValues = ["default"]
    condValues.extend(["{:01d}".format(x) for x in range(1, 5001)])
    print("   > Current value for the parameter is : {}".format(zoneRadius))
    zoneRadius = __modifyValues("game_zone_radius", 1, condValues,
                                "   > Enter the wait time (0-10 / default / 'Enter') : ")[0]
    print("   > Updated value for the parameter is : {}".format(zoneRadius))


# FUNCTION to display the configuration menu
def parametersMenu():
    option = 1

    while option != 0:
        print("╭──── Configuration Menu ──────╮")
        print("{:30s} │".format("│ 1. camera parameters"))
        print("{:30s} │".format("│ 2. general image size"))
        print("{:30s} │".format("│ 3. ArUCo tags offset"))
        print("{:30s} │".format("│ 4. removing background"))
        print("{:30s} │".format("│ 5. colors threshold"))
        print("{:30s} │".format("│ 0. go to main menu"))
        print("╰──────────────────────────────╯")
        cmdInput = input("[config] Enter you option : ")
        if cmdInput == "":
            option = 0
        else:
            try:
                option = int(cmdInput)
            except ValueError:
                print("<Error> Please enter a valid number or press 'Enter' to go back")
                option = -1

        condValues = ["", "default"]

        # modify camera related parameters
        if option == 1:
            print("[config] Camera Configuration Menu")
            print("   [config] 1. change camera rotation value")
            print("   [config] 2. change camera waiting time")
            print("   [config] 3. change camera resolution")
            cmdInput = input("[menu] Enter you option : ")
            try:
                option = int(cmdInput)
            except ValueError:
                option = -1

            # camera parameters : rotation
            if option == 1:
                global camRot
                condValues.extend(["0", "90", "180", "270"])
                strInfo = "      > Enter the rotation angle (0 / 90 /180 / 270 / default / 'Enter') : "
                print("   [config] Configuration of the rotation of the camera")
                camRot = __setInteger(camRot, "camera_rotation", condValues, strInfo)

            # camera parameters : wait time
            elif option == 2:
                global camWait
                condValues.extend(["{:01d}".format(x) for x in range(1, 11)])
                strInfo = "      > Enter the wait time (0-10 / default / 'Enter') : "
                print("   [config] Configuration of the waiting time of the camera")
                camWait = __setInteger(camWait, "camera_waitTime", condValues, strInfo)

            # camera parameters : resolution
            elif option == 3:
                global camRes
                print("[config] Configuration of the camera resolution")
                camRes = __setResolution(camRes, "camera_resolution")

        # modify the general image size
        elif option == 2:
            global width
            global height
            print("[config] Configuration of the image resolution")
            width, height = __setResolution([width, height], "image_resolution")

        # modify the horizontal offset of the tags
        elif option == 3:
            global warpOffset
            condValues.extend(["{:01d}".format(x) for x in range(1, height // 2)])
            strInfo = "      > Enter the horizontal offset (0-" + str(height // 2) + " / default / 'Enter') : "
            print("   [config] Configuration of the horizontal offset of the tags")
            warpOffset = __setInteger(warpOffset, "tag_horizontal_offset", condValues, strInfo)

        # modify parameters related to the background removing process
        elif option == 4:
            print("[config] Removing background Configuration Menu")
            print("   [config] 1. width of black rectangle on the sides")
            print("   [config] 2. radius of the corner circles")
            cmdInput = input("[menu] Enter you option : ")
            try:
                option = int(cmdInput)
            except ValueError:
                option = -1

            # modify the black rectangle offset in the background removing
            if option == 1:
                global bRectDist
                condValues.extend(["{:01d}".format(x) for x in range(1, height // 2)])
                strInfo = "      > Enter the width of the rectangle (0-" + str(height // 2) + " / default / 'Enter') : "
                print("   [config] Configuration of the width of the black rectangle")
                bRectDist = __setInteger(bRectDist, "background_rectangle_offset", condValues, strInfo)

            # modify the black circle radius in the background removing
            elif option == 2:
                global bCircRad
                condValues.extend(["{:01d}".format(x) for x in range(1, height // 2)])
                strInfo = "      > Enter the new radius (0-" + str(height // 2) + " / default / 'Enter') : "
                print("   [config] Configuration of the radius of the black circle")
                bCircRad = __setInteger(bCircRad, "background_circle_radius", condValues, strInfo)

        # modify parameters related to color threshold
        elif option == 5:
            print("[config] Color Threshold Configuration Menu")
            print("   [config] 1. yellow ball color threshold")
            print("   [config] 2. white ball color threshold")
            print("   [config] 3. blue ball color threshold")
            print("   [config] 4. red ball color threshold")
            print("   [config] 5. green background color threshold")
            print("   [config] 6. blue background color threshold")
            print("   [config] 7. red background color threshold")
            print("   [config] 8. pink game-target color threshold")
            cmdInput = input("[menu] Enter you option : ")
            try:
                option = int(cmdInput)
            except ValueError:
                option = -1

            # modify the yellow threshold values for the ball
            if option == 1:
                global colYELLOWMin
                global colYELLOWMax
                print("   [config] Configuration of the BGR threshold values for the yellow ball")
                colYELLOWMin, colYELLOWMax = __setRGBThreshold([colYELLOWMin, colYELLOWMax],
                                                               ["ball_YELLOW_min_value", "ball_YELLOW_max_value"])

            # modify the white threshold values for the ball
            elif option == 2:
                global colWHITEMin
                global colWHITEMax
                print("   [config] Configuration of the BGR threshold values for the white ball")
                colWHITEMin, colWHITEMax = __setRGBThreshold([colWHITEMin, colWHITEMax],
                                                             ["ball_WHITE_min_value", "ball_WHITE_max_value"])

            # modify the blue threshold values for the ball
            elif option == 3:
                global colBLUEMin
                global colBLUEMax
                print("   [config] Configuration of the BGR threshold values for the blue ball")
                colBLUEMin, colBLUEMax = __setRGBThreshold([colBLUEMin, colBLUEMax],
                                                           ["ball_BLUE_min_value", "ball_BLUE_max_value"])

            # modify the red threshold values for the ball
            elif option == 4:
                global colREDMin
                global colREDMax
                print("   [config] Configuration of the BGR threshold values for the red ball")
                colREDMin, colREDMax = __setRGBThreshold([colREDMin, colREDMax],
                                                         ["ball_RED_min_value", "ball_RED_max_value"])

            # modify the green threshold values for the pool table
            elif option == 5:
                global tableGREENMin
                global tableGREENMax
                print("   [config] Configuration of the BGR threshold values for the green table")
                tableGREENMin, tableGREENMax = __setRGBThreshold([tableGREENMin, tableGREENMax],
                                                                 ["table_GREEN_min_value", "table_GREEN_max_value"])

            # modify the blue threshold values for the pool table
            elif option == 6:
                global tableBLUEMin
                global tableBLUEMax
                print("   [config] Configuration of the BGR threshold values for the blue table")
                tableBLUEMin, tableBLUEMax = __setRGBThreshold([tableBLUEMin, tableBLUEMax],
                                                               ["table_BLUE_min_value", "table_BLUE_max_value"])

            # modify the red threshold values for the pool table
            elif option == 7:
                global tableREDMin
                global tableREDMax
                print("   [config] Configuration of the BGR threshold values for the red table")
                tableREDMin, tableREDMax = __setRGBThreshold([tableREDMin, tableREDMax],
                                                             ["table_RED_min_value", "table_RED_max_value"])

            # modify the green threshold values for the target in game
            elif option == 8:
                global gmColPINKMin
                global gmColPINKMax
                print("   [config] Configuration of the BGR threshold values for the pink target")
                gmColPINKMinn, gmColPINKMax = __setRGBThreshold([gmColPINKMin, gmColPINKMax],
                                                                 ["game_PINK_min_value", "game_PINK_max_value"])

        # go back to main menu
        elif option == 0:
            print("[config] Going back to main menu")

        print()

    print("\n")
