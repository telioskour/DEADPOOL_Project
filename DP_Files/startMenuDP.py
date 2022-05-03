from scripts import dvptTest, scriptDP, parameters as p
import datetime


# navigation menu in terminal command
def menuInTerminal():
    option = 1
    winLoseRatio = [[0, 0], [0, 0], [0, 0]]
    bestScores = [0, 0, 0]
    totalScore = 654321
    table = ""

    while option != 0:

        print("╒══════════╡[DEADPOOL Menu]╞═══════════╕")
        print("{:38s} │".format("│ 1. GAME 1 : line"))
        print("{:38s} │".format("│ 2. GAME 2 : obstacle"))
        print("{:38s} │".format("│ 3. GAME 3 : two zones"))
        print("{:38s} │".format("│ 4. change finish zone radius"))
        print("{:38s} │".format("│ 5. reset game score "))
        print("{:38s} │".format("│ 6. set projector keystone"))
        print("{:38s} │".format("│ 7. tests"))
        print("{:38s} │".format("│ 8. parameters"))
        print("{:38s} │".format("│ 0. quit program"))
        print("╰──────────────────────────────────────╯")
        cmdInput = input("[menu] Enter you option : ")
        try:
            option = int(cmdInput)
        except ValueError:
            print("<Error> Please enter a valid number")
            option = 999

        # First game
        if option == 1:
            print("[menu] Starting game type 1 : line")
            gmScore, gmState, gmInfo = scriptDP.startGame1(p.gm1LinePath, p.zoneRadius)
            table, totalScore, winLoseRatio, bestScores = scriptDP.displayScore(1, totalScore, winLoseRatio, bestScores,
                                                                                gmScore, gmState, gmInfo)

        # Second game
        elif option == 2:
            print("[menu] Starting game type 2 : obstacle")
            gmScore, gmState, gmInfo = scriptDP.startGame2(p.gm2ObstaclePath, p.zoneRadius)
            table, totalScore, winLoseRatio, bestScores = scriptDP.displayScore(2, totalScore, winLoseRatio, bestScores,
                                                                                gmScore, gmState, gmInfo)
                
        # Third game
        elif option == 3:
            print("[menu] Starting game type 3 : two zones")
            gmScore, gmState, gmInfo = scriptDP.startGame3(p.gm3ContactPath, p.zoneRadius)
            table, totalScore, winLoseRatio, bestScores = scriptDP.displayScore(3, totalScore, winLoseRatio, bestScores,
                                                                                gmScore, gmState, gmInfo)
                
        # modify the radius of the finish zone
        elif option == 4:
            print("[menu] Changing the finish radius")
            p.setZoneRadius()

        # Reset the scores
        elif option == 5:
            print("[menu] Resetting game score")
            choice = input("   > are you sure you want to reset score and the WIN/LOSE ratio ? (y/n) : ")
            if choice == "y":
                winLoseRatio = [[0, 0], [0, 0], [0, 0]]
                bestScores = [0, 0, 0]
                totalScore = 0

        # Setting the projector keystone
        elif option == 6:
            print("[menu] Setting the projector keystone")
            scriptDP.setKstMatrix()

        # Tests menu
        elif option == 7:
            print("[menu] Launching the test menu")
            print("\n \n")
            dvptTest.testsMenu()

        # Parameters menu
        elif option == 8:
            print("[menu] Launching the parameters menu")
            print("\n \n")
            p.parametersMenu()
            
        print("")

    if table != "":
        print("[menu] Saving data...")
        saveScoreToFile("gameSavedData.txt", table)
    print("[menu] Goodbye !")


def saveScoreToFile(filePath, table):
    choice = input("   > do you want to save your score data ? (y/n) : ")
    if choice == "y":
        gmWinLose = [[0, 0], [0, 0], [0, 0]]
        gmBestScore = [0, 0, 0]
        with open(filePath, 'a+') as file:
            # Move read cursor to the start of file.
            file.seek(0)
            # If file is not empty then append '\n'
            data = file.read(100)
            if len(data) > 0:
                file.write("\n")
            # Append text at the end of file
            file.write("\n")
            file.write("Score from {} ".format(datetime.datetime.now()))
            file.write("\n")
            file.write(table)
        print("   > game data has been saved ! Search in the project file")
    else:
        print("   > game data has not been saved !")


menuInTerminal()
