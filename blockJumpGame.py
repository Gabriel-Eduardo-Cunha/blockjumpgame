from graphics import GraphWin, Rectangle, Point, color_rgb, Text
import time
import random
from NeuralNetwork import Network

class BlockJumpGame(GraphWin):
    def __init__(self, gameMode = 'normal', numOfPlayers = 1, maxFrameRate = 80, popName = False , render = True , screenSize = [800, 600], initialGameSpeed = 20):
        if render == True:
            self.renderization = True
            GraphWin.__init__(self, 'Block-Jump-Game', screenSize[0], screenSize[1])
        else:
            self.renderization = False

        self.gameConfig = {
            'maxFrameRate' : maxFrameRate,
            'screenSize' : screenSize,
            'initialGameSpeed' : initialGameSpeed
        }
        self.gameMode = gameMode
        self.numOfPlayers = numOfPlayers
        self.playersAlive = [x for x in range(numOfPlayers)]
        self.player = []
        for i in range(numOfPlayers):
            if gameMode == 'aitrain':
                self.player.append(Player(self, i, popName))
            else:
                self.player.append(Player(self, i))
        self.initialGameSpeed = initialGameSpeed
        self.gameSpeed = initialGameSpeed
        self.groundLevel = self.gameConfig['screenSize'][1] - 7
        self.obstacle = None
        self.createObstacle()

        self.points = 0
        self.maxFrameRate = maxFrameRate

        self.pointsText = Text(Point(
            0 + screenSize[0] / 10, 0 + screenSize[0] / 50), 'Points: ' + str(self.points))
        if self.renderization:
            self.pointsText.draw(self)

        self.timeWhenGameStarted = time.time()
        self.gameEnd = False
        self.start()

    def start(self):
        while self.gameEnd == False:
            self.render()

    def render(self):
        self.checkPoints()
        self.refreshHUD()
        self.checkObstacle()
        self.detectInput()
        self.moveObjects()
        for i in self.playersAlive:
            self.player[i].fall()
        self.addPoints()
        self.checkColisions()
        if self.renderization:
            time.sleep(1/self.maxFrameRate)

    def checkColisions(self):
        if self.obstacle != None:
            for i in self.playersAlive:
                if self.player[i].getP2().getX() > self.obstacle.getP1().getX() and self.player[i].getP1().getX() < self.obstacle.getP1().getX() or self.player[i].getP2().getX() > self.obstacle.getP2().getX() and self.player[i].getP1().getX() < self.obstacle.getP2().getX() or self.player[i].getP2().getX() > self.obstacle.getCenter().getX() and self.player[i].getP1().getX() < self.obstacle.getCenter().getX():
                    if self.player[i].getP2().getY() > self.obstacle.getP1().getY():
                        self.gameOver(i)

    def gameOver(self, player_id):
        self.player[player_id].move(10000,10000)
        if self.renderization:
            self.player[player_id].undraw()
        self.playersAlive.remove(player_id)
        self.player[player_id].alive = False
        self.player[player_id].points = self.points
        if not self.checkPlayersAlive():
            if self.gameMode == 'normal' and self.renderization:
                self.gameOverText = Text(
                    Point(self.gameConfig['screenSize'][0] / 2, self.gameConfig['screenSize'][1] / 2), 'Game Over\nPress R to restart\nor press any key to quit')
                self.gameOverText.draw(self)
                key = self.getKey()
                self.gameEnd = True
                print('XXXXXXXXXXXXXXXXXXXXXXXXX')
                print('------Game Status------')
                print('Points: ' + str(round(self.points)))
                print('Played for: ' + str(round(time.time() - self.timeWhenGameStarted)) + ' seconds')
                print('XXXXXXXXXXXXXXXXXXXXXXXXX')
                if key == 'r':
                    self.restart()
                else:
                    self.close()
            elif self.gameMode == 'aitrain':
                self.finalPoints = []
                for i in range(self.numOfPlayers):
                    self.finalPoints.append(self.player[i].points)
                self.gameEnd = True
                if self.renderization:
                    self.close()
                        
    def refreshHUD(self):
        self.pointsText.setText('Points: ' + str(round(self.points)))

    def checkPoints(self):
        if int(self.points / 10) - (self.gameSpeed - self.initialGameSpeed) == 1:
            if self.points < 500:
                self.gameSpeed += 1

    def checkPlayersAlive(self):
        for i in range(self.numOfPlayers):
            if self.player[i].alive:
                return True
        return False

    def addPoints(self):
        self.points += 1/self.maxFrameRate * self.gameSpeed/10

    def detectInput(self):
        if self.gameMode == 'normal' and self.renderization:
            input = self.checkKey()
        for i in self.playersAlive:
            if self.gameMode == 'aitrain':
                input = self.player[i].brain.guess(self.generateInput(i))
            if input == 'Up' and self.player[i].status == 'nothing':
                self.player[i].jump()
                self.player[i].status = 'jumping'
            if input == 'Down' and self.player[i].status == 'jumping':
                if self.player[i].speed < 0:
                    self.player[i].speed = 0
                self.player[i].status = 'fastfall'
    
    def generateInput(self, id):
        array = []
        array += self.DecToBinaryArray(int(self.player[id].getDistance()) , 10)
        array += self.DecToBinaryArray(self.obstacleType , 2)
        array += self.DecToBinaryArray(self.gameSpeed , 7)
        # array += self.DecToBinaryArray(self.obstacleHeight , 8)
        return array

    @staticmethod
    def DecToBinaryArray(num, arrayRange):
        array = list(0 for _ in range(arrayRange - len(bin(num)[2:])))
        array.extend(list(int(x) for x in bin(num)[2:]))
        return array

    def checkObstacle(self):
        if self.obstacle != None:
            if self.obstacle.getCenter().getX() < - self.obstacleWidth + 10:
                if self.renderization:
                    self.obstacle.undraw()
                self.obstacle = None
                self.createObstacle()

    def createObstacle(self):
        height = 150
        randomizer = random.randint(1,3)
        if randomizer == 1:
            width = 75
        elif randomizer == 2:
            width = 100
        else:
            width = 125

        self.obstacleType = randomizer
        self.obstacleHeight = height
        self.obstacleWidth = width
        self.obstacle = Rectangle(Point(
            self.gameConfig['screenSize'][0], self.gameConfig['screenSize'][1] - self.obstacleHeight), Point(self.gameConfig['screenSize'][0] + self.obstacleWidth, self.gameConfig['screenSize'][1]))
        self.obstacle.setFill(color_rgb(random.randint(
            0, 255), random.randint(0, 255), random.randint(0, 255)))
        if self.renderization:
            self.obstacle.draw(self)

    def moveObjects(self):
        for i in range(self.numOfPlayers):
            self.player[i].move(0, round(self.player[i].speed/self.maxFrameRate, 1))
            if self.player[i].getP2().getY() >= self.groundLevel:
                self.player[i].move(0, self.groundLevel - self.player[i].getP2().getY())
                self.player[i].speed = 0
                self.player[i].status = 'nothing'

        if self.obstacle != None:
            self.obstacle.move(-self.gameSpeed*10/self.maxFrameRate, 0)

    def restart(self):
        for i in range(self.numOfPlayers):
            self.player[i] = Player(self, i)
            self.player[i].speed = 0
            self.player[i].status = 'nothing'
        self.gameSpeed = self.initialGameSpeed
        self.obstacle.undraw()
        self.gameOverText.undraw()
        self.obstacle = None
        self.createObstacle()

        self.points = 0
        
        self.pointsText.undraw()
        self.pointsText = Text(Point(
            0 + self.gameConfig['screenSize'][0] / 10, 0 + self.gameConfig['screenSize'][0] / 50), 'Points: ' + str(self.points))
        self.pointsText.draw(self)

        self.timeWhenGameStarted = time.time()
        self.gameEnd = False
        self.start()

    @staticmethod
    def playGames(timesToPlay = 1 ,gameMode = 'normal', numOfPlayers = 1, maxFrameRate = 80, popName = False , render = True , screenSize = [800, 600], initialGameSpeed = 20):
        totalPoints = [0 for _ in range(numOfPlayers)]
        for _ in range(timesToPlay):
            gameInstance = BlockJumpGame(gameMode, numOfPlayers, maxFrameRate, popName, render, screenSize, initialGameSpeed)
            for i in range(len(gameInstance.finalPoints)):
                totalPoints[i] += gameInstance.finalPoints[i]
        highestPoints = 0
        betterPlayerId = 0
        for i in range(len(totalPoints)):
            if totalPoints[i] > highestPoints:
                highestPoints = totalPoints[i]
                betterPlayerId = i
        
        print('MAX AVERAGE RECORD: ' + str(round(highestPoints / timesToPlay, 2)))
        return betterPlayerId
        

    
class Player(Rectangle):
    def __init__(self, graphWin, player_id, popName = False, playerSize = 50):
        playerStartingPoint = [30, 540]
        self.player_id = player_id
        Rectangle.__init__(self, Point(playerStartingPoint[0], playerStartingPoint[1]), Point(
            playerStartingPoint[0] + playerSize, playerStartingPoint[1] + playerSize))
        self.graphWin = graphWin
        self.speed = 0
        self.status = 'nothing'
        self.alive = True
        self.setFill(color_rgb(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        self.setOutline(color_rgb(0, 0, 0))
        if self.graphWin.renderization:
            self.draw(graphWin)
        if self.graphWin.gameMode == 'aitrain':
            self.brain = Network(popName + str(player_id))

    
    def fall(self):
        if self.status == 'jumping':
            self.speed += round(480/self.graphWin.maxFrameRate,1)
        if self.status == 'fastfall':
            self.speed += round(4800/self.graphWin.maxFrameRate,1)
    
    def jump(self):
        if self.status == 'nothing':
            self.speed = -480

    def getDistance(self):
        distance = self.getP1().getX() - self.graphWin.obstacle.getP2().getX()
        if distance > 0:
            distance = 0
        return int((distance * -1) / 5)

            

