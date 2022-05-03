""" Test scripts
This file is used for different test when developping the program to avoid to clustering the main menu
"""

from scripts import scriptDP, imgProcess, parameters as p
import cv2
import datetime as t


# FUNCTION to display the test menu
def testsMenu():
    option = 1

    while option != 0:
        print("╭─────────────────── Tests Menu ───────────────────╮")
        print("{:50s} │".format("│ 1. camera : circle detection"))
        print("{:50s} │".format("│ 2. camera : take picture"))
        print("{:50s} │".format("│ 3. show keystone template"))
        print("{:50s} │".format("│ 4. test image : circle detection"))
        print("{:50s} │".format("│ 5. test image : projector keystone"))
        print("{:50s} │".format("│ 6. batch test : tag detection"))
        print("{:50s} │".format("│ 0. go to main menu"))
        print("╰──────────────────────────────────────────────────╯")
        cmdInput = input("[tests] Enter you option : ")
        if cmdInput == "":
            option = 0
        else:
            try:
                option = int(cmdInput)
            except ValueError:
                print("<Error> Please enter a valid number or press 'Enter' to go back")
                option = -1

        # camera : circle detection
        if option == 1:
            print("[tests] Circle detection from the camera")
            scriptDP.imgTake(p.pathCamIN)
            listBalls = scriptDP.detectBall(p.pathCamIN)
            print("   > detected circles are : " + str(listBalls))

        # camera : taking a picture
        elif option == 2:
            print("[tests] Taking a picture with the camera")
            scriptDP.imgTake(p.testCamIN)
            print("   > image stored in " + str(p.testCamIN))

        # show keystone template (fullscreen test)
        elif option == 3:
            print("[test] Test fullscreen keystone input image")
            scriptDP.imgShow(p.kstTemplateOUT, waitTime=0)

        # test image : circle detection
        elif option == 4:
            print("[tests] Ball(s) detection from test image")
            listBalls = scriptDP.detectBall(p.testImgPath)
            print("   > detected circles are : " + str(listBalls))

        # test image : projector keystone
        elif option == 5:
            print("[tests] Projector keystone from test image")
            imgProcess.getPrjMatrix(fromTestImg=True)

        # batch testing : detection of the aruco tags
        elif option == 6:
            print("   [test] Tags detection : batch testing")
            cycle = int(input("      > how many cycles ? : "))
            timeStart = t.datetime.now()
            timeList = []
            itOK = 0
            idFile = 0
            for i in range(1, cycle + 1):
                timeInter = t.datetime.now()

                print("      > test N° " + str(i))
                scriptDP.imgTake(p.pathCamIN)
                print("         > picture taken")
                image = cv2.imread(p.pathCamIN)
                dictTag, image = imgProcess.tagDetect(image, p.tagType)
                if dictTag != {}:
                    itOK += 1
                    print("         > tag detected")
                    timeList.append(t.datetime.now() - timeInter)
                else:
                    print("         > tag(s) not detected")

            timeTotal = t.datetime.now() - timeStart
            timeMax = max(timeList)
            for j in range(1, len(timeList)):
                if timeList[j] == timeMax:
                    idFile = j + 1

            print("      > batch test finished : {} succes of {}".format(itOK, cycle))
            print("      > time | total of {} with average time of {} and max (N°{}) of {}".format(
                timeTotal, timeTotal / len(timeList), idFile, timeMax))

        # go back to main menu
        elif option == 0:
            print("[tests] Going back to main menu")

        print()

    print("\n")
